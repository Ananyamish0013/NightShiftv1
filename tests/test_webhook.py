import pytest
import base64
import hashlib
import hmac
import sys
import os

from backend.signature import _valid_signature

def test_valid_signature_accepted(signing_token, make_signature):
    message_id = 'test-id-001'
    timestamp = '2024-01-15T02:30:00.000000Z'
    body = '{"object_kind": "push"}'
    sig = make_signature(signing_token, message_id, timestamp, body)
    assert _valid_signature(signing_token, message_id, timestamp, body, sig) is True




def test_tampered_body_rejected(signing_token, make_signature):
    message_id = 'test-id-001'
    timestamp = '2024-01-15T02:30:00.000000Z'
    original_body = '{"object_kind": "push"}'
    tampered_body = '{"object_kind": "merge_request"}'
    sig = make_signature(signing_token, message_id, timestamp, original_body)
    assert _valid_signature(signing_token, message_id, timestamp, tampered_body, sig) is False




def test_wrong_token_rejected(make_signature):
    correct_token = 'whsec_' + base64.b64encode(b'correct-secret-key-32bytes!!!!').decode()
    wrong_token = 'whsec_' + base64.b64encode(b'wrong-secret-key-32bytes-!!!!!!').decode()
    message_id = 'test-id-001'
    timestamp = '2024-01-15T02:30:00.000000Z'
    body = '{"object_kind": "push"}'
    sig = make_signature(correct_token, message_id, timestamp, body)
    assert _valid_signature(wrong_token, message_id, timestamp, body, sig) is False
def test_multiple_signatures_in_header(signing_token, make_signature):
    message_id = 'test-id-001'
    timestamp = '2024-01-15T02:30:00.000000Z'
    body = '{"object_kind": "push"}'
    sig = make_signature(signing_token, message_id, timestamp, body)
    multi_sig = f'v1,invalidsig {sig} v1,anotherbadsig'
    assert _valid_signature(signing_token, message_id, timestamp, body, multi_sig) is True




def test_missing_whsec_prefix_rejected():
    token_without_prefix = base64.b64encode(b'test-secret-key-32bytes-minimum!').decode()
    with pytest.raises(Exception):
        _valid_signature(token_without_prefix, 'id', 'ts', 'body', 'v1,sig')




def test_empty_signature_rejected(signing_token):
    assert _valid_signature(signing_token, 'id', 'ts', 'body', '') is False



