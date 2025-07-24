from fastmcp import FastMCP
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_instance import mcp


@mcp.prompt()
def systemPrompt():
    return "This is a sys Prom"
