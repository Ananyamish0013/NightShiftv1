from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import json
from signature import verify_gitlab_signature
from job_manager import create_job, write_audit_log
from agent_runner import run_agent
from config import config

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/webhook')
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    source_ip = request.client.host if request.client else ''
    gitlab_event_type = request.headers.get('X-Gitlab-Event', 'unknown')

    try:
        raw_body = await request.body()
    except Exception as e:
        logger.error(f'Failed to read request body: {e}')
        raise HTTPException(status_code=400, detail='Could not read request body')

    try:
        signing_token = config.webhook_signing_token
        is_valid = await verify_gitlab_signature(
            request, signing_token, raw_body
        )
    except Exception as e:
        logger.error(f'Signature verification error: {e}')
        raise HTTPException(status_code=500, detail='Signature verification failed')

    if not is_valid:
        try:
            write_audit_log(
                event_type='signature_invalid',
                source_ip=source_ip,
                gitlab_event_type=gitlab_event_type,
                details={'reason': 'HMAC-SHA256 verification failed'}
            )
        except Exception:
            pass
        raise HTTPException(status_code=401, detail='Invalid webhook signature')

    try:
        payload = json.loads(raw_body)
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid JSON body')

    object_kind = payload.get('object_kind', '')
    if object_kind != 'push':
        return JSONResponse(
            status_code=200,
            content={
                'status': 'ignored',
                'reason': f'Event type {object_kind} not handled'
            }
        )

    project = payload.get('project', {})
    repo_url = project.get('http_url', '')
    project_id = str(project.get('id', ''))
    default_branch = project.get('default_branch', 'main')
    commit_sha = payload.get('checkout_sha', '')
    branch_ref = payload.get('ref', '')

    if not repo_url or not project_id or not commit_sha:
        raise HTTPException(
            status_code=400,
            detail='Missing required fields'
        )

    try:
        job_id = create_job(
            repo_url=repo_url,
            project_id=project_id,
            commit_sha=commit_sha,
            branch_ref=branch_ref,
            gitlab_event_type=gitlab_event_type
        )
    except Exception as e:
        logger.error(f'Failed to create job: {e}')
        raise HTTPException(status_code=500, detail='Failed to create job')

    try:
        write_audit_log(
            event_type='job_created',
            job_id=job_id,
            source_ip=source_ip,
            gitlab_event_type=gitlab_event_type,
            details={'repo_url': repo_url, 'commit_sha': commit_sha}
        )
    except Exception:
        pass

    background_tasks.add_task(
        run_agent,
        job_id=job_id,
        repo_url=repo_url,
        project_id=project_id,
        commit_sha=commit_sha,
        default_branch=default_branch
    )

    logger.info(f'Job {job_id} created for {repo_url}')

    return JSONResponse(
        status_code=202,
        content={
            'status': 'accepted',
            'job_id': job_id,
            'message': 'NightShift job queued successfully'
        }
    )