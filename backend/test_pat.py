import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams


async def main():
    print("TOKEN FOUND:", bool(os.getenv("GITLAB_TOKEN")))

    mcp = MCPToolset(
        connection_params=SseServerParams(
            url="https://gitlab.com/api/v4/mcp",
            headers={
                "Authorization": f"Bearer {os.getenv('GITLAB_TOKEN')}"
            },
            timeout=60,
        )
    )

    tools = await mcp.get_tools()

    print("TOOLS FOUND:", len(tools))

    for tool in tools:
        print(tool.name)


asyncio.run(main())