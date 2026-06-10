#!/bin/bash
set -e

ENDPOINT=${1:-'http://localhost:8080/webhook'}
SIGNING_TOKEN=${NIGHTSHIFT_SIGNING_TOKEN:-''}

if [ -z '$SIGNING_TOKEN' ]; then
  echo 'Error: Set NIGHTSHIFT_SIGNING_TOKEN environment variable'
  exit 1
fi

MESSAGE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)
BODY='{"object_kind":"push","event_name":"push","ref":"refs/heads/main","checkout_sha":"abc123def456","project":{"id":99999,"name":"test-repo","http_url":"https://gitlab.com/testuser/test-repo","default_branch":"main"}}'

RAW_KEY=$(echo -n $SIGNING_TOKEN | sed 's/whsec_//' | base64 -d | xxd -p -c 256)
MESSAGE="${MESSAGE_ID}.${TIMESTAMP}.${BODY}"
DIGEST=$(echo -n $MESSAGE | openssl dgst -sha256 -mac HMAC -macopt hexkey:$RAW_KEY -binary | base64)
SIGNATURE="v1,${DIGEST}"

curl -X POST $ENDPOINT \
  -H 'Content-Type: application/json' \
  -H 'X-Gitlab-Event: Push Hook' \
  -H "webhook-id: ${MESSAGE_ID}" \
  -H "webhook-timestamp: ${TIMESTAMP}" \
  -H "webhook-signature: ${SIGNATURE}" \
  -d "$BODY" \
  -v

