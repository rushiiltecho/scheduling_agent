# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.§

import os
import asyncio
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")

from drive_service.shared_libraries.google_api_toolset import CalendarToolset, DriveToolset
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

calendar_tool_set = CalendarToolset()
drive_tool_set = DriveToolset()

import logging
import warnings
from google.adk import Agent
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")


# configure logging __name__
logger = logging.getLogger(__name__)
access_token = os.getenv("ACCESS_TOKEN") or "DEFAULT"
calendar_tool_set.configure_access_token_auth(access_token)
drive_tool_set.configure_access_token_auth(access_token)
print(f"ACCESS TOKEN: {access_token}")
def before_agent_callback(callback_context:CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    # global calendar_tool_set 
    # if callback_context._invocation_context.session.state:
    #     print(callback_context._invocation_context.session.state)
    #     for key, value in callback_context._invocation_context.session.state.items():  
    #         if 'temp:googl' in key:
    #             print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{callback_context._invocation_context.session.state}\n{'*'*60}\n{value}\n{'*'*60}\n")
    #             calendar_tool_set.configure_access_token_auth(value)
    #             drive_tool_set.configure_access_token_auth(value)
    #             tools = [*calendar_tool_set.get_tools(),*drive_tool_set.get_tools()]
    #             callback_context._invocation_context.agent.tools= tools
    #         if "openIdConnect" in key:
    #             print(f"UPDATED LOCAL ACCESS TOKEN STATE: {callback_context._invocation_context.session.state[key].get("http",{}).get("credentials",{}).get("token","")}")
    #             access_token = callback_context._invocation_context.session.state[key].get("http",{}).get("credentials",{}).get("token","") or ""
    #             calendar_tool_set.configure_access_token_auth(access_token)
    #             drive_tool_set.configure_access_token_auth(access_token)
    #             tools = [*calendar_tool_set.get_tools(),*drive_tool_set.get_tools()]
    #             callback_context._invocation_context.agent.tools= tools

def after_agent_callback(callback_context:CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (After agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")


from google.adk.agents import Agent
from drive_service.tools import jira_tool


JIRA_AGENT_INSTRUCTIONS = "you're the Jira Agent."

import asyncio

def jiraa_tools():
    print("function start")
    tools = jira_tool.get_tools()
    while True:
        print(tools)

# ====================================
root_agent = Agent(
    name="jira_agent",
    model="gemini-2.0-flash",
    description=("Agent to provide assistance for JIRA services."),
    instruction=JIRA_AGENT_INSTRUCTIONS,
    tools=jira_tool.get_tools()
)

