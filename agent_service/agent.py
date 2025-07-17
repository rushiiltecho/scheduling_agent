
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
import logging
import warnings

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from agent_service.shared_libraries.salesforce_api_toolset import SalesforceAPIToolset
from agent_service.shared_libraries.google_api_toolset import CalendarToolset, DriveToolset
from agent_service.prompts import INSTRUCTION

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")
# configure logging __name__
logger = logging.getLogger(__name__)


# # =======================================================================
# # Jira Agent Code
# # =======================================================================

# from agent_service.shared_libraries.atlassian_api_toolset_new import JiraApiToolset
# from agent_service.entities.prompt_instruction import INSTRUCTIONS, CONFLUENCE_INSTRUCTIONS, salesforce_knowledge_extraction_functions, confluence_tool_filter
# # from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION


SALESFORCE_ACCESS_TOKEN = os.getenv("SALESFORCE_ACCESS_TOKEN")
ATLASSIAN_ACCESS_TOKEN = os.getenv("ATLASSIAN_ACCESS_TOKEN")
GOOGLE_ACCESS_TOKEN = os.getenv("GOOGLE_ACCESS_TOKEN")

# Initialize Jira toolset and attach token
salesforce_tool_set = SalesforceAPIToolset(
    access_token=SALESFORCE_ACCESS_TOKEN,
    # tool_filter=salesforce_knowledge_extraction_functions#confluence_tool_filter#["search_content_by_cql","get_current_user","get_audit_records"]
)

drive_toolset = DriveToolset(
    access_token=GOOGLE_ACCESS_TOKEN,
)

calendar_toolset = CalendarToolset(
    access_token=GOOGLE_ACCESS_TOKEN,
)

salesforce_tool_set.configure_access_token_auth(SALESFORCE_ACCESS_TOKEN)
drive_toolset.configure_access_token_auth(GOOGLE_ACCESS_TOKEN)
calendar_toolset.configure_access_token_auth(GOOGLE_ACCESS_TOKEN)
# Define callbacks to refresh token if session state updates


google_tools = [*drive_toolset.get_tools(), *calendar_toolset.get_tools()]


def salesforce_after_agent_callback(callback_context: CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nSALESFORCE CALLBACK_CONTEXT [STATE] (After agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
        

def salesforce_before_agent_callback(callback_context: CallbackContext):
    # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context._invocation_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [SESSION] (Before agent):\n{callback_context._invocation_context.session.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    print(f"\n{'*'*60}\n{'*'*60}\n\nSALESFORCE CALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context._invocation_context.session.state:
        salesforce_tools = salesforce_tool_set.get_tools()
        google_tools = [*drive_toolset.get_tools(), *calendar_toolset.get_tools()]
        state = callback_context._invocation_context.session.state.copy()
        for key, value in state.items():  
            if 'temp:salesforce' in key:
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
                salesforce_tool_set.configure_access_token_auth(value)
                salesforce_tools = salesforce_tool_set.get_tools()
                print("REINITIALIZED SALESFORCE TOOLS")
            if 'temp:google' in key:
                print(f"\n{'*'*60}\nUPDATED GOOGLE ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{callback_context._invocation_context.session.state}\n{'*'*60}\n{value}\n{'*'*60}\n")
                drive_toolset.configure_access_token_auth(value)
                calendar_toolset.configure_access_token_auth(value)
                google_tools = [*drive_toolset.get_tools(), *calendar_toolset.get_tools()]
                print("REINITIALIZED GOOGLE TOOLS")
        tools = [*salesforce_tools, *google_tools]
        callback_context._invocation_context.agent.tools= tools
        

# Build the agent with Jira tools
salesforce_agent = Agent(
    model="gemini-2.0-flash-001",
    # global_instruction="You are a Salesforce Agent",
    # instruction=INSTRUCTION,
    name="salesforce_agent",
    # tools=[*salesforce_tool_set.get_tools(), *drive_tool_set.get_tools()],
    tools=[*salesforce_tool_set.get_tools()],
    before_agent_callback=salesforce_before_agent_callback,
    after_agent_callback=salesforce_after_agent_callback,
)


# =======================================================================
# =======================================================================
root_agent = salesforce_agent
