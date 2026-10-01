import json
import sys

from mcp.server.mcpserver import MCPServer

from scanner import scan_repository


mcp = MCPServer("RepoGuard AI")


@mcp.tool()
def scan_repo(path: str) -> str:
    """Scan a local repository and return structured engineering findings."""
    result = scan_repository(path)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()