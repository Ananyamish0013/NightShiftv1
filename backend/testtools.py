import asyncio

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

async def main():
    mcp = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "mcp-remote",
                    "https://gitlab.com/api/v4/mcp",
                    "--static-oauth-client-metadata",
                    '{"scope":"mcp"}'
                ]
            ),
            timeout=60
        )
    )

    tools = await mcp.get_tools()

    print("TOOLS FOUND:", len(tools))

    for tool in tools[:10]:
        print(tool.name)

asyncio.run(main())