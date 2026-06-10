import pytest
import sys
import os
from unittest.mock import MagicMock, patch, call


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
def test_create_job_returns_document_id():
    mock_db = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = 'test-job-id-123'
    mock_db.collection.return_value.document.return_value = mock_doc_ref


    with patch('job_manager._db', mock_db):
        from backend.job_manager import create_job
        job_id = create_job(
            repo_url='https://gitlab.com/user/repo',
            project_id='12345',
            commit_sha='abc123',
            branch_ref='refs/heads/main',
            gitlab_event_type='Push Hook'
        )
    assert job_id == 'test-job-id-123'




def test_create_job_sets_pending_status():
    mock_db = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = 'test-job-id-123'
    mock_db.collection.return_value.document.return_value = mock_doc_ref


    with patch('job_manager._db', mock_db):
        from backend.job_manager import create_job
        create_job(
            repo_url='https://gitlab.com/user/repo',
            project_id='12345',
            commit_sha='abc123',
            branch_ref='refs/heads/main',
            gitlab_event_type='Push Hook'
        )
    call_args = mock_doc_ref.set.call_args[0][0]
    assert call_args['status'] == 'PENDING'
    assert call_args['repo_url'] == 'https://gitlab.com/user/repo'
    assert call_args['mr_url'] is None