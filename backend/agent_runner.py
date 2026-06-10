import asyncio
import logging
import os

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types as genai_types
from config import config
from job_manager import update_job_status


logger = logging.getLogger(__name__)


def _load_agent_instructions() -> str:
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'agent', 'agent_instructions.txt'),
        os.path.join(os.path.dirname(__file__), '..', 'agent', 'agent_instructions.txt'),
        os.path.join(os.path.dirname(__file__), 'agent_instructions.txt'),
        '/app/agent/agent_instructions.txt',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    raise FileNotFoundError(
        f'agent_instructions.txt not found. Checked: {possible_paths}'
    )


async def run_agent(
    job_id: str,
    repo_url: str,
    project_id: str,
    commit_sha: str,
    default_branch: str
) -> None:
    """
    Main agent entry point. Defined as async def so FastAPI BackgroundTasks
    awaits it directly — no sync wrapper, no asyncio.run().
    """
    try:
        await _run_agent_async(
            job_id=job_id,
            repo_url=repo_url,
            project_id=project_id,
            commit_sha=commit_sha,
            default_branch=default_branch,
        )
    except Exception as exc:
        error_msg = str(exc)
        update_job_status(job_id, 'FAILED', error_message=error_msg)
        logger.error(f'Job {job_id} failed: {error_msg}')
        raise


async def _run_agent_async(
    job_id: str,
    repo_url: str,
    project_id: str,
    commit_sha: str,
    default_branch: str
) -> None:

    gitlab_token = os.environ.get("GITLAB_TOKEN", "")
    if not gitlab_token:
        raise ValueError("GITLAB_TOKEN environment variable is not set")

    # --- MCP Toolset via bearer token (no OAuth browser flow) ---
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "mcp-remote",
                    "https://gitlab.com/api/v4/mcp",
                    "--header",
                    f"Authorization: Bearer {gitlab_token}"
                ]
            ),
            timeout=120
        )
    )

    logger.info(f'Job {job_id}: initializing MCP toolset')
    tools = await mcp_toolset.get_tools()
    logger.info(f'Job {job_id}: loaded {len(tools)} MCP tools')

    agent_instructions = _load_agent_instructions()

    agent = LlmAgent(
        model='gemini-2.5-flash',
        name='nightshift_agent',
        instruction=agent_instructions,
        tools=tools,
    )

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    runner = Runner(
        agent=agent,
        session_service=session_service,
        artifact_service=artifact_service,
        app_name='nightshift',
    )

    session = await session_service.create_session(
        app_name='nightshift',
        user_id='nightshift-system',
    )

    prompt = (
        f'Repository URL: {repo_url}\n'
        f'GitLab project ID: {project_id}\n'
        f'Commit SHA: {commit_sha}\n'
        f'Job ID: {job_id}\n'
        f'Default branch: {default_branch}\n'
        f'Branch to create: nightshift/fix-{job_id}\n'
        f'\n'
        f'Follow your instructions exactly. Analyze the repository, '
        f'fix all issues you find, create the branch '
        f'nightshift/fix-{job_id}, commit the fixes, and create a '
        f'Merge Request targeting {default_branch}. '
        f'When finished output MR_URL: followed by the full Merge '
        f'Request URL on its own line. '
        f'If no issues are found output only: NO_ISSUES_FOUND'
    )

    message = genai_types.Content(
        role='user',
        parts=[genai_types.Part(text=prompt)]
    )

    final_response_text = ''

    logger.info(f'Job {job_id}: starting ADK agent run')

    async for event in runner.run_async(
        session_id=session.id,
        user_id='nightshift-system',
        new_message=message,
    ):
        if hasattr(event, 'tool_call') and event.tool_call:
            logger.info(
                f'Job {job_id}: agent calling tool '
                f'{event.tool_call.name}'
            )

        if hasattr(event, 'tool_response') and event.tool_response:
            logger.info(
                f'Job {job_id}: tool response received for '
                f'{event.tool_response.name}'
            )

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                logger.info(f'Job {job_id}: agent final response received')

    logger.info(f'Job {job_id}: agent run complete')

    # --- Parse agent output ---
    if 'NO_ISSUES_FOUND' in final_response_text:
        update_job_status(
            job_id,
            'COMPLETED',
            files_analyzed=0,
            fixes_generated=0
        )
        logger.info(f'Job {job_id}: no issues found in repository')
        return   # <-- intentional early return, only for NO_ISSUES case

    mr_url = None
    mr_iid = None
    for line in final_response_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('MR_URL:'):
            mr_url = stripped.replace('MR_URL:', '').strip()
            break

    if mr_url:
        parts = mr_url.rstrip('/').split('/')
        try:
            mr_iid = int(parts[-1])
        except (ValueError, IndexError):
            mr_iid = None
        update_job_status(
            job_id,
            'COMPLETED',
            mr_url=mr_url,
            mr_iid=mr_iid
        )
        logger.info(f'Job {job_id} completed. MR: {mr_url}')
    else:
        update_job_status(
            job_id,
            'COMPLETED',
            error_message='Agent completed but no MR URL in response'
        )
        logger.warning(
            f'Job {job_id}: agent finished but MR URL not found in output'
        )