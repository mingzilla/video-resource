from mcp.server.fastmcp import FastMCP, Context

# use stateless_http to avoid the need of submitting session ID
mcp = FastMCP("Calculator", stateless_http=True)


@mcp.tool()
def add(a: int, b: int, ctx: Context) -> int:
    """Add two numbers"""
    headers = ctx.request_context.request.headers
    print(f"HTTP Headers: {headers}")
    print(f"TOOL CALLED: a: {a}, b: {b}")
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
