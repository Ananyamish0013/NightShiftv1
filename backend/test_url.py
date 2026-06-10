import httpx
from config import config

r = httpx.get(
    config.gitlab_mcp_url,
    headers={
        "Authorization": f"Bearer {config.gitlab_token}"
    }
)

print(r.status_code)
print(r.text)