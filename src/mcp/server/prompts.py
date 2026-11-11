from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts."""

    @mcp.prompt()
    def system_diagnostic() -> str:
        """
        Creates a prompt for diagnosing the MCP server.
        """

        return """
        Perform a diagnostic of the MCP server.

        Verify:

        1. Server connectivity
        2. Available tools
        3. Available resources
        4. Server health
        """