import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["app/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}")

            result = await session.call_tool(
                "scan_repo",
                {"path": "target_repo"},
            )

            print("\nMCP tool result:")
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())