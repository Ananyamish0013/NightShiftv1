from google.cloud import firestore
from datetime import datetime, timezone
from typing import Optional
from config import config
_db = firestore.Client(project=config.project_id)
def create_job(
    repo_url: str,
    project_id: str,
    commit_sha: str,
    branch_ref: str,
    gitlab_event_type: str
) -> str:
    job_ref = _db.collection(config.firestore_collection_jobs).document()
    job_ref.set({
        'status': 'PENDING',
        'repo_url': repo_url,
        'project_id': project_id,
        'commit_sha': commit_sha,
        'branch_ref': branch_ref,
        'gitlab_event_type': gitlab_event_type,
        'mr_url': None,
        'mr_iid': None,
        'error_message': None,
        'files_analyzed': 0,
        'fixes_generated': 0,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
    })
    return job_ref.id
def update_job_status(
    job_id: str,
    status: str,
    mr_url: Optional[str] = None,
    mr_iid: Optional[int] = None,
    error_message: Optional[str] = None,
    files_analyzed: Optional[int] = None,
    fixes_generated: Optional[int] = None
) -> None:
    update_data = {
        'status': status,
        'updated_at': firestore.SERVER_TIMESTAMP,
    }
    if mr_url is not None:
        update_data['mr_url'] = mr_url
    if mr_iid is not None:
        update_data['mr_iid'] = mr_iid
    if error_message is not None:
        update_data['error_message'] = error_message
    if files_analyzed is not None:
        update_data['files_analyzed'] = files_analyzed
    if fixes_generated is not None:
        update_data['fixes_generated'] = fixes_generated
    _db.collection(config.firestore_collection_jobs).document(job_id).update(update_data)
def get_recent_jobs(limit: int = 20) -> list:
    docs = (
        _db.collection(config.firestore_collection_jobs)
        .order_by('created_at', direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()
        if data.get('updated_at'):
            data['updated_at'] = data['updated_at'].isoformat()
        result.append(data)
    return result




def write_audit_log(
    event_type: str,
    job_id: Optional[str] = None,
    source_ip: str = '',
    gitlab_event_type: str = '',
    details: Optional[dict] = None
) -> None:
    _db.collection(config.firestore_collection_audit).add({
        'event_type': event_type,
        'job_id': job_id,
        'source_ip': source_ip,
        'gitlab_event_type': gitlab_event_type,
        'details': details or {},
        'timestamp': firestore.SERVER_TIMESTAMP,
    })



