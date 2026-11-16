from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

playwright_client = MCPClient(
    lambda: stdio_client(  # pyright: ignore[reportArgumentType]
        StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@playwright/mcp@latest",
                "--isolated",
            ],
        )
    )
)
