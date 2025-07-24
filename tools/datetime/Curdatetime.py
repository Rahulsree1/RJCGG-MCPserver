
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from datetime import datetime
import pytz
from mcp_instance import mcp

IST = pytz.timezone("Asia/Kolkata")


@mcp.tool()
def CurrentDate() -> str:
    """Returns current Date"""
    now = datetime.now(IST)
    return f"Current Date: {now.day}/{now.month}/{now.year}"

@mcp.tool()
def CurrentDay() -> str:
    """Returns current Day"""
    now = datetime.now(IST)
    return f"Current Day: {now.strftime('%A')}"

@mcp.tool()
def CurrentTime() -> str:
    """Returns current Time"""
    now = datetime.now(IST)
    return f"Current Time: {now.hour}:{now.minute}:{now.second}"
