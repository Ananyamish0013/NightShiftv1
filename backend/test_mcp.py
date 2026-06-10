import asyncio

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from config import config


async def main():
    mcp_toolset = MCPToolset(
        connection_params=SseServerParams(
            url=config.gitlab_mcp_url,
            headers={
                "Authorization": f"Bearer {config.gitlab_token}",
                "X-Gitlab-Duo-Namespace": config.gitlab_username,
            },
        )
    )

    tools = await mcp_toolset.get_tools()

    print(f"Found {len(tools)} tools")

    for tool in tools:
        print(tool.name)


asyncio.run(main())