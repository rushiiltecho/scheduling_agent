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

# """Agent module for the customer service agent."""
import os
import asyncio
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")

from customer_service.shared_libraries.google_api_toolset import CalendarToolset
# from customer_service.shared_libraries.google_api_toolset import CalendarToolset
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# def before_agent_callback(callback_context:CallbackContext):
#     logging.info(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
calendar_tool_set = CalendarToolset()
# calendar_tool_set.configure_auth(
#     client_id=CLIENT_ID, client_secret=CLIENT_SECRET
# )
# Run gcloud command and capture output
from subprocess import run
# process = run(['gcloud', 'auth', 'print-access-token'], 
#                         capture_output=True, 
#                         text=True)
# print(f"{'*'*60}\nACCESS TOKEN:\n{access_token}\n{'*'*60}")
# calendar_tool_set.configure_access_token_auth(access_token)

import logging
import warnings
from google.adk import Agent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
import subprocess

# from .shared_libraries.callbacks import (
#     rate_limit_callback,
#     before_agent,
#     before_tool,
#     after_tool
# )
# from .tools.tools import (
#     send_call_companion_link,
#     approve_discount,
#     sync_ask_for_approval,
#     update_salesforce_crm,
#     access_cart_information,
#     modify_cart,
#     get_product_recommendations,
#     check_product_availability,
#     schedule_planting_service,
#     get_available_planting_times,
#     send_care_instructions,
#     generate_qr_code,
# )

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


def before_agent_callback(callback_context:CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (Before agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context.state:
        for key, value in callback_context.state.__dict__.items():  
            if key.startswith('temp:googl'):
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{callback_context.state.__dict__}\n{'*'*60}\n{value}\n{'*'*60}\n")
                calendar_tool_set.configure_access_token_auth(value)
    # Create logging directory if it doesn't exist
    # print(f"[BeforeAgent] Callback Context: {callback_context.__dict__}")
    # os.makedirs('logging/agent_logs', exist_ok=True)

    # Save before agent log
    # with open(f'logging/agent_logs/before_agent_{callback_context.invocation_id}.txt', 'w') as f:
    #     f.write(f"Callback Context: {callback_context.__dict__}\n")
        # f.write(f"Request: {callback_context.request}\n")
        # f.write(f"Response: {callback_context.response}\n")
        # f.write(f"Tool Calls: {callback_context.tool_calls}\n")


def after_agent_callback(callback_context:CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT (After agent):\n{callback_context.__dict__}\n\n{'*'*60}\n{'*'*60}\n")
    # print(f"[AfterAgent] Callback Context: {callback_context.__dict__}")
    # os.makedirs('logging/agent_logs', exist_ok=True)
    # with open(f'logging/agent_logs/after_agent_{callback_context.invocation_id}.txt', 'w') as f:
    #     f.write(f"Callback Context: {callback_context.__dict__}\n")

root_agent = Agent(
    model="gemini-2.0-flash-001",
    global_instruction=GLOBAL_INSTRUCTION,
    # instruction=INSTRUCTION,
    name="AgentSpace_root_agent",
    # tools=[
    #     send_call_companion_link,
    #     approve_discount,
    #     sync_ask_for_approval,
    #     update_salesforce_crm,
    #     access_cart_information,
    #     modify_cart,
    #     get_product_recommendations,
    #     check_product_availability,
    #     schedule_planting_service,
    #     get_available_planting_times,
    #     send_care_instructions,
    #     generate_qr_code,
    # ],
    tools=calendar_tool_set.get_tools(),
    # before_tool_callback=before_tool,
    # after_tool_callback=after_tool,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    # before_model_callback=rate_limit_callback,
)

# root_agent = Agent(
#     name=configs.agent_settings.name,    
#     model="gemini-2.0-flash",              # or your preferred LLM
#     before_agent_callback=before_agent_callback,
#     after_agent_callback=after_agent_callback,
#     tools=calendar_tool_set.get_tools()
# )
