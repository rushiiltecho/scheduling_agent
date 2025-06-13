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
# limitations under the License.

import os
import logging
import warnings
from typing import Optional, Union, List

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

from drive_service.shared_libraries.atlassian_api_toolset_new import JiraApiToolset
# from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION

# Environment configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or "DEFAULT"

# Initialize Jira toolset and attach token
jira_tool_set = JiraApiToolset(
    access_token=ACCESS_TOKEN,
)
jira_tool_set.configure_access_token_auth(ACCESS_TOKEN)

# Configure logging and warnings
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# Define callbacks to refresh token if session state updates

def before_agent_callback(callback_context: CallbackContext):
    # print debug info
    # print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    state = callback_context._invocation_context.session.state or {}
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (Before agent):\n{state}\n\n{'*'*60}\n{'*'*60}\n")
    # Look for updated OAuth2 state
    for key, value in state.items():
        if "temp:" in key:
            token = value
            if token:
                jira_tool_set.configure_access_token_auth(token)
                callback_context._invocation_context.agent.tools = jira_tool_set.get_tools()[:512]
                logger.info("Updated Jira access token from session state.")


def after_agent_callback(callback_context: CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.__dict__}\n\n{'*'*60}\n{'*'*60}\n")


# Build the agent with Jira tools
root_agent = Agent(
    model="gemini-2.0-flash-001",
    global_instruction="You are a jira Agent",
    instruction="You have access to tools for being a Jira Agent",
    name="jira_agent",
    tools=jira_tool_set.get_tools()[:512],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
