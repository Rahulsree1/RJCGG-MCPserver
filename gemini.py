import asyncio
import os
from datetime import datetime
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = genai.Client(api_key="AIzaSyA4A87j7bw4eUEz3lxFjfoKXS1jE4kSxNk")

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",  # Executable
    args=["mcp-remote", "http://localhost:1729/mcp/"],  # MCP Server
    env=None,  # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Prompt to get the weather for the current day in London.
            
            # Initialize the connection between client and server
            await session.initialize()

            # Get tools from MCP session and convert to Gemini Tool objects
            mcp_tools = await session.list_tools()
            tools = [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
             
                for tool in mcp_tools.tools
            ]

            #print(tools)

            tool_config = types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO"
                )
            )


            contents = [
                types.Content(
                        role="user", parts=[types.Part(text='''System: You are a helpful assistant. When asked about events or information related to "today," "yesterday," "tomorrow," or similar time references, first determine the current date using available tools. Use this to accurately identify and respond with the correct day of the week or calendar date. Ensure that relative dates (e.g., "yesterday," "tomorrow," "day after tomorrow") are interpreted in context based on the current date.
''')]
                    )
                    
                ]
            

            while True:
                prompt = input("User: ")
                if prompt == 'q': break

                contents.append(types.Content(
                        role="user", parts=[types.Part(text=prompt)]
                    ))

            # Send request to the model with MCP function declarations
                response = await client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.7,
                        tools=[session],  # uses the session, will automatically call the tool
                        # Uncomment if you **don't** want the sdk to automatically call the tool
                        # automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                        #     disable=True
                        # ),
                        tool_config=tool_config,
                        
                    ),
                    
                )

                
                contents.append(response.candidates[0].content)
                #print(contents)
                #contents.append(response)
                print(response.candidates[0].content.parts[0].text)
               
# Start the asyncio event loop and run the main function
asyncio.run(run())