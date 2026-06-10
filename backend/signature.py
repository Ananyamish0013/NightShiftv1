import base64
import hashlib
import hmac
from fastapi import Request


async def verify_gitlab_signature(
    request: Request,
    signing_token: str,
    raw_body: bytes = None
) -> bool:
    message_id = request.headers.get('webhook-id', '')
    timestamp = request.headers.get('webhook-timestamp', '')
    received_signature = request.headers.get('webhook-signature', '')

    if not message_id or not timestamp or not received_signature:
        return False

    if raw_body is None:
        raw_body = await request.body()

    body_str = raw_body.decode('utf-8')

    return _valid_signature(
        signing_token, message_id, timestamp, body_str, received_signature
    )


def _valid_signature(
    signing_token: str,
    message_id: str,
    timestamp: str,
    body: str,
    received_signature: str
) -> bool:
    raw_key = base64.b64decode(signing_token.removeprefix('whsec_'))
    message = f'{message_id}.{timestamp}.{body}'.encode('utf-8')
    digest = hmac.new(raw_key, message, hashlib.sha256).digest()
    expected = 'v1,' + base64.b64encode(digest).decode('utf-8')
    return any(
        hmac.compare_digest(expected, sig)
        for sig in received_signature.split(' ')
    )