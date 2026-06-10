
# local_test.py
import asyncio
from agent_runner import run_agent
async def main():
    result = await run_agent(
        job_id="local-test-001",
        repo_url="https://gitlab.com/Ananya1309/nightshift-test",
        project_id="82733440",   # numeric GitLab project ID
        commit_sha="55a32b9a8dcb21837a2ea201b933bef6d81433ee",             # any valid commit SHA from your repo
        default_branch="main"
    )
    print("RESULT:", result)

if __name__ == "__main__":
    asyncio.run(main())