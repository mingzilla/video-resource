from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CalculatorServer", stateless_http=True, port=8010)


@mcp.tool()
async def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
