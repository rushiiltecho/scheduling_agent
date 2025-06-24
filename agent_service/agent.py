# # Copyright 2025 Google LLC
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

# import os
# import logging
# import warnings
# from typing import Optional, Union, List

# from google.adk.agents import Agent
# from google.adk.agents.callback_context import CallbackContext
# from google.adk.tools.tool_context import ToolContext

# from agent_service.shared_libraries.atlassian_api_toolset_new import JiraApiToolset
# from agent_service.entities.prompt_instruction import INSTRUCTIONS, CONFLUENCE_INSTRUCTIONS, jira_knowledge_extraction_functions, confluence_tool_filter
# # from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION


# JIRA_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or "DEFAULT"



# # Initialize Jira toolset and attach token
# jira_tool_set = JiraApiToolset(
#     access_token=JIRA_ACCESS_TOKEN,
#     tool_filter=jira_knowledge_extraction_functions#confluence_tool_filter#["search_content_by_cql","get_current_user","get_audit_records"]
# )
# jira_tool_set.configure_access_token_auth(JIRA_ACCESS_TOKEN)

# # Configure logging and warnings
# logger = logging.getLogger(__name__)
# warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# # Define callbacks to refresh token if session state updates

# def after_agent_callback(callback_context: CallbackContext):
#     print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (After agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
#     if callback_context._invocation_context.session.state:
#         state = callback_context._invocation_context.session.state.copy()
#         # for key, value in state.items():  
#             # if 'temp:jiraAuthRush7' in key:
#             #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
#             #     jira_tool_set.configure_access_token_auth(value)
#             #     tools = jira_tool_set.get_tools()[:10]
#             #     callback_context._invocation_context.agent.tools = tools
#             #    print("REINITIALIZED TOOLS 1")
#             # if 'temp:jira' in key:
#             #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
#             #     jira_tool_set.configure_access_token_auth(value)
#             #     tools = jira_tool_set.get_tools()[:10]
#             #     callback_context._invocation_context.agent.tools = tools
#             #     print("REINITIALIZED TOOLS 2")
#             # elif "openIdConnect" in key:
#             #     access_token = ACCESS_TOKEN
#             #     jira_tool_set.configure_access_token_auth(access_token)
#             #     tools = jira_tool_set.get_tools()[:10]
#             #     callback_context._invocation_context.agent.tools = tools
#             #     print("REINITIALIZED TOOLS 3")

# def before_agent_callback(callback_context: CallbackContext):
#     # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context._invocation_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
#     # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [SESSION] (Before agent):\n{callback_context._invocation_context.session.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
#     print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
#     if callback_context._invocation_context.session.state:
#         state = callback_context._invocation_context.session.state.copy()
#         for key, value in state.items():  
#             # if 'temp:jiraAuthRush7' in key:
#             #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
#             #     jira_tool_set.configure_access_token_auth(value)
#             #     tools = jira_tool_set.get_tools()[:10]
#             #     callback_context._invocation_context.agent.tools = tools
#             #     print("REINITIALIZED TOOLS 1")
#             if 'temp:jira' in key:
#                 print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
#                 jira_tool_set.configure_access_token_auth(value)
#                 tools = jira_tool_set.get_tools()[:512]
#                 callback_context._invocation_context.agent.tools = tools
#                 print("REINITIALIZED TOOLS 2")
#             # elif "openIdConnect" in key:
#             #     access_token = ACCESS_TOKEN
#             #     jira_tool_set.configure_access_token_auth(access_token)
#             #     tools = jira_tool_set.get_tools()[:10]
#             #     callback_context._invocation_context.agent.tools = tools
#             #     print("REINITIALIZED TOOLS 3")
#                 # callback_context._invocation_context.session.state["temp:jiraAuth"] = ACCESS_TOKEN

# # Build the agent with Jira tools
# root_agent = Agent(
#     model="gemini-2.0-flash-001",
#     global_instruction="You are a jira Agent",
#     instruction=INSTRUCTIONS,#"You have access to tools for being a Jira Agent",
#     name="jira_agent",
#     tools=jira_tool_set.get_tools()[:512],
#     before_agent_callback=before_agent_callback,
#     after_agent_callback=after_agent_callback,
# )



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

from agent_service.shared_libraries.google_api_toolset import CalendarToolset, DriveToolset
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

calendar_tool_set = CalendarToolset()
drive_tool_set = DriveToolset()

import logging
import warnings
# from google.adk import Agent
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION as GOOGLE_INSTRUCTION

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")


# configure logging __name__
logger = logging.getLogger(__name__)


# =======================================================================
# Jira Agent Code
# =======================================================================

from agent_service.shared_libraries.atlassian_api_toolset_new import JiraApiToolset
from agent_service.entities.prompt_instruction import INSTRUCTIONS, CONFLUENCE_INSTRUCTIONS, jira_knowledge_extraction_functions, confluence_tool_filter
# from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION


JIRA_ACCESS_TOKEN = os.getenv("JIRA_ACCESS_TOKEN") or "DEFAULT"
GOOGLE_ACCESS_TOKEN = os.getenv("GOOGLE_ACCESS_TOKEN")


calendar_tool_set.configure_access_token_auth(GOOGLE_ACCESS_TOKEN)
drive_tool_set.configure_access_token_auth(GOOGLE_ACCESS_TOKEN)


# Initialize Jira toolset and attach token
jira_tool_set = JiraApiToolset(
    access_token=JIRA_ACCESS_TOKEN,
    tool_filter=jira_knowledge_extraction_functions#confluence_tool_filter#["search_content_by_cql","get_current_user","get_audit_records"]
)
jira_tool_set.configure_access_token_auth(JIRA_ACCESS_TOKEN)

# Configure logging and warnings
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# Define callbacks to refresh token if session state updates

def jira_after_agent_callback(callback_context: CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nJIRA CALLBACK_CONTEXT [STATE] (After agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context._invocation_context.session.state:
        state = callback_context._invocation_context.session.state.copy()
        

def jira_before_agent_callback(callback_context: CallbackContext):
    # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context._invocation_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [SESSION] (Before agent):\n{callback_context._invocation_context.session.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    global calendar_tool_set 
    print(f"\n{'*'*60}\n{'*'*60}\n\nJIRA CALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context._invocation_context.session.state:
        jira_tools = jira_tool_set.get_tools()
        google_tools = drive_tool_set.get_tools()
        state = callback_context._invocation_context.session.state.copy()
        for key, value in state.items():  
            if 'temp:jira' in key:
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
                jira_tool_set.configure_access_token_auth(value)
                jira_tools = jira_tool_set.get_tools()[:512]
                # callback_context._invocation_context.agent.tools = jira_tools
                print("REINITIALIZED JIRA TOOLS 2")
            if 'temp:google' in key:
                print(f"\n{'*'*60}\nUPDATED GOOGLE ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{callback_context._invocation_context.session.state}\n{'*'*60}\n{value}\n{'*'*60}\n")
                calendar_tool_set.configure_access_token_auth(value)
                drive_tool_set.configure_access_token_auth(value)
                google_tools = [*drive_tool_set.get_tools()]
                # callback_context._invocation_context.agent.tools= tools
        tools = [*google_tools, *jira_tools]
        callback_context._invocation_context.agent.tools= tools
        

# Build the agent with Jira tools
root_agent = Agent(
    model="gemini-2.0-flash-001",
    # global_instruction="You are a jira Agent",
    # instruction=INSTRUCTIONS,#"You have access to tools for being a Jira Agent",
    global_instruction="You are a helpful Parent/Root agent having access to all tools and capabilities. Always Modify the final response as Markdown Tables wherever possible, without the Markdown triple quotes.",
    instruction="You are a helpful Jira and Drive Agent, where you have access to Jira and Drive agents, which you call accordingly wherever necessary." + f"\n{INSTRUCTIONS}\n\n{GOOGLE_INSTRUCTION}\n\n"+"Always Modify the final response as Markdown Tables wherever possible and applicable, without the Markdown triple quotes",
    name="jira_agent",
    tools=[*jira_tool_set.get_tools(), *drive_tool_set.get_tools()],
    before_agent_callback=jira_before_agent_callback,
    after_agent_callback=jira_after_agent_callback,
)
# =======================================================================
# =======================================================================

# drive_tool_set.configure_access_token_auth(GOOGLE_ACCESS_TOKEN)
# print(f"ACCESS TOKEN: {GOOGLE_ACCESS_TOKEN}")
# def before_agent_callback(callback_context:CallbackContext):
#     # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
#     print(f"\n{'*'*60}\n{'*'*60}\n\n DRIVE-CALENDAR CALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
#     global calendar_tool_set 
#     if callback_context._invocation_context.session.state:
#         print(callback_context._invocation_context.session.state)
#         for key, value in callback_context._invocation_context.session.state.items():  
#             if 'temp:googl' in key:
#                 print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{callback_context._invocation_context.session.state}\n{'*'*60}\n{value}\n{'*'*60}\n")
#                 calendar_tool_set.configure_access_token_auth(value)
#                 drive_tool_set.configure_access_token_auth(value)
#                 tools = [*calendar_tool_set.get_tools(),*drive_tool_set.get_tools()]
#                 callback_context._invocation_context.agent.tools= tools

# def after_agent_callback(callback_context:CallbackContext):
#     # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (After agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
#     print(f"\n{'*'*60}\n{'*'*60}\n\n DRIVE-CALENDAR CALLBACK_CONTEXT [STATE] (After agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")


# drive_agent = Agent(
#     model="gemini-2.0-flash-001",
#     global_instruction=GLOBAL_INSTRUCTION,
#     instruction=GOOGLE_INSTRUCTION,
#     name="drive_agent_testing",#"AgentSpace_root_agent",
#     tools=[*calendar_tool_set.get_tools(),*drive_tool_set.get_tools()],
#     before_agent_callback=before_agent_callback,
#     after_agent_callback=after_agent_callback,
# )
# =======================================================================
# =======================================================================

# root_agent = Agent(
#     model="gemini-2.0-flash-001",
#     global_instruction="You are a helpful Parent/Root Agent with Drive Agent and Jira Agent as child agents. Whenever failing to execute something, always transfer back to parent agent and thent try again, only for at most 3 times.",
#     instruction="You are a helpful Jira and Drive Agent, where you have access to Jira and Drive agents, which you call accordingly wherever necessary.",
#     name="drive_jira_agent_testing",#"AgentSpace_root_agent",
#     # tools=[*calendar_tool_set.get_tools(),*drive_tool_set.get_tools()],
#     sub_agents=[jira_agent, drive_agent],
#     # before_agent_callback=before_agent_callback,
#     # after_agent_callback=after_agent_callback,
# )


# =======================================================================
# =======================================================================
