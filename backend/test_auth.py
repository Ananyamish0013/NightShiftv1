import httpx
from config import config

headers = {
    "Authorization": f"Bearer {config.gitlab_token}",
    "X-Gitlab-Duo-Namespace": config.gitlab_username,
}

r = httpx.get(
    config.gitlab_mcp_url,
    headers=headers,
    follow_redirects=False,
)

print("STATUS:", r.status_code)
print("BODY:", r.text[:1000])