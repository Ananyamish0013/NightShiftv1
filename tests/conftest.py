import pytest
import base64
import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

MOCK_SIGNING_TOKEN = 'whsec_' + base64.b64encode(b'test-secret-key-32bytes-minimum!').decode()

@pytest.fixture
def signing_token():
    return MOCK_SIGNING_TOKEN

@pytest.fixture
def sample_push_payload():
    return {
        'object_kind': 'push',
        'event_name': 'push',
        'before': '0000000000000000000000000000000000000000',
        'after': 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
        'ref': 'refs/heads/main',
        'checkout_sha': 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
        'project': {
            'id': 12345678,
            'name': 'test-project',
            'http_url': 'https://gitlab.com/testuser/test-project',
            'default_branch': 'main'
        },
        'commits': [{'id': 'a1b2c3d4', 'message': 'Test commit'}]
    }

@pytest.fixture
def make_signature():
    def _make(token: str, message_id: str, timestamp: str, body: str) -> str:
        raw_key = base64.b64decode(token.removeprefix('whsec_'))
        message = f'{message_id}.{timestamp}.{body}'.encode('utf-8')
        digest = hmac.new(raw_key, message, hashlib.sha256).digest()
        return 'v1,' + base64.b64encode(digest).decode('utf-8')
    return _make