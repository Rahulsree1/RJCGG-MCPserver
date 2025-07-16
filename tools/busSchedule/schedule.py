from mcp.server.fastmcp import FastMCP

mcp = FastMCP.instance()

@mcp.tool()
def busSchedule(location: str) -> str:
    """Updated and latest Bus Schedule of IIT Mandi"""
    with open("./BusS.md") as f:
        return f.read()
