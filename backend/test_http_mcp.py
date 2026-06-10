import asyncio
import os

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

async def main():
    mcp = McpToolset(
        connection_params=SseServerParams(
            url="https://gitlab.com/api/v4/mcp",
            headers={
                "Authorization": f"Bearer {os.environ['GITLAB_TOKEN']}"
            }
        )
    )

    tools = await mcp.get_tools()

    print("TOOLS FOUND:", len(tools))

    for tool in tools[:10]:
        print(tool.name)

asyncio.run(main())