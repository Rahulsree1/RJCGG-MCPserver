# mcp_instance.py
from mcp.server.fastmcp import FastMCP

# Create a single shared instance of FastMCP
mcp = FastMCP("RJCGG",host="0.0.0.0", port=1729, debug=True)
