from mcp.server.fastmcp import FastMCP
 

mcp = FastMCP("my_test_mcp_server")

@mcp.tool()
async def funny_response() -> str:
    """Get a funny response if the user asks for a funny message

    Args:
        None
    """
    return "This is the funny response"

 



if __name__ == "__main__":
    mcp.run(transport='stdio')