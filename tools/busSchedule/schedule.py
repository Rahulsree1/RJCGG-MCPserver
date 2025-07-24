from mcp_instance import mcp

@mcp.tool()
def busSchedule(location: str) -> str:
    """Updated and latest Bus Schedule of IIT Mandi"""
    with open("./BusS.md") as f:
        return f.read()
