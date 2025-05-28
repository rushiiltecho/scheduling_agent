import asyncio
import os
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")

from google.adk.tools.google_api_tool import calendar_tool_set
from google.adk.agents import Agent

# # 1. Configure your OAuth2 credentials for the Google Calendar toolset
# calendar_tool_set.configure_auth(
#     client_id=f"{CLIENT_ID}",
#     client_secret="{CLIENT_SECRET}"
# )

# # 2. Pull out all generated calendar tools
# calendar_tools = calendar_tool_set.get_tools()

# # 3. Create your LLM agent and give it the calendar tools
# agent = LlmAgent(
#     name="my_calendar_agent",
#     model="gemini-2.0-flash",              # or your preferred LLM
#     tools=calendar_tools,
#     system_prompt="""
#     You have access to Google Calendar via the calendar tools. 
#     Use them to list, create, update, or delete events as the user requests.
#     """
# )

from google.adk.tools.google_api_tool import  calendar_tool_set

# client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
# client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"
# calendar_tool_set = CalendarToolset()
# Use the specific configure method for this toolset type
calendar_tool_set.configure_auth(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

# async def get_tools():
#     return await calendar_tool_set.get_tools()

agent = Agent(
    name="calendar_agent",
    model="gemini-2.0-flash",              # or your preferred LLM
    # system_prompt="""
    # You have access to Google Calendar via the calendar tools. 
    # Use them to list, create, update, or delete events as the user requests.
    # """,
    tools=calendar_tool_set.get_tools()
)