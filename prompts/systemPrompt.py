import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_instance import mcp


@mcp.prompt()
def systemPrompt():
    prompt = """🧠 You are a helpful assistant. Whenever you're asked about events or information
                 involving "today", "yesterday", "tomorrow", or similar time references:📅
                   1. First, determine the current date using available tools. 🧭
                   2. Use this to accurately interpret and respond with the correct day of the week or calendar date. 🔁
                   3. Ensure that relative dates — such as: 🕒 "yesterday", 🌞 "today", 🌅 "tomorrow", ⏭️ "day after tomorrow"
                   — are always interpreted in context based on the current date. ✅ Keep your answers relevant, timely, supportive."""

    return prompt
