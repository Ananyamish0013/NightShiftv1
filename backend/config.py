from dotenv import load_dotenv
load_dotenv()

import os
import logging

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID', 'clean-abacus-497115-g2')
        self.region = os.environ.get('GCP_REGION', 'us-central1')
        self.gitlab_mcp_url = os.environ.get(
            'GITLAB_MCP_URL',
            'https://gitlab.com/api/v4/mcp'
        )
        self.gitlab_username = os.environ.get('GITLAB_USERNAME', '')
        self.gitlab_token = os.environ.get('GITLAB_TOKEN', '')
        self.webhook_signing_token = os.environ.get('WEBHOOK_SIGNING_TOKEN', '')
        self.firestore_collection_jobs = 'jobs'
        self.firestore_collection_repos = 'repositories'
        self.firestore_collection_executions = 'executions'
        self.firestore_collection_mrs = 'merge_requests'
        self.firestore_collection_audit = 'audit_logs'


config = Config()