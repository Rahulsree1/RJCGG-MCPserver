# main.py
from mcp_instance import mcp

# Import your tool modules to ensure their tools are registered
import tools.mess.messMenu
import tools.datetime.Curdatetime
import prompts.systemPrompt
import tools.contacts.contacts









if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_streamable_http_async())
