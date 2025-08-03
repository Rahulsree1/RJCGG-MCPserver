# main.py
from mcp_instance import mcp






# Import your tool modules to ensure their tools are registered
import tools.mess.main_tools
import tools.datetime.main_tools
import prompts.systemPrompt
import tools.contacts.main_tools
import tools.courses.main_tools







if __name__ == "__main__":
    import asyncio
    
    asyncio.run(mcp.run_streamable_http_async())
