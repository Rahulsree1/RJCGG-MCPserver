# mcp_instance.py
from mcp.server.fastmcp import FastMCP

# Create a single shared instance of FastMCP
mcp = FastMCP("RJCGG", debug=True)
