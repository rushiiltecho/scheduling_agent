# Copyright 2025 Your Company
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

from __future__ import annotations

import inspect
import json
import logging
import os
from typing import Any, List, Optional, Union

from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from jira_agent.shared_libraries.constants import JIRA_OPENAPI_SPEC
import requests
from typing_extensions import override

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth import OpenIdConnectWithConfig, OAuth2Auth
from google.adk.tools.base_toolset import BaseToolset, ToolPredicate
from google.adk.tools.openapi_tool import OpenAPIToolset
from .converter import AtlassianApiFetcher
from .atlassian_api_tool import AtlassianApiTool

CLOUD_ID = os.getenv("JIRA_CLOUD_ID")

# Convert boolean enums to strings in the spec
def convert_boolean_enums(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'enum' and any(isinstance(x, bool) for x in value):
                obj[key] = [str(x).lower() for x in value]
            elif isinstance(value, (dict, list)):
                convert_boolean_enums(value)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                convert_boolean_enums(item)

# convert_boolean_enums(spec_dict)
class AtlassianApiToolset(BaseToolset):
    """Atlassian API Toolset contains tools for interacting with Jira or Confluence.
    
    Usually one toolset will contain tools only related to one Atlassian product, 
    e.g. Jira Platform or Confluence, with each OpenAPI operation wrapped in an AtlassianApiTool.
    """

    def __init__(
        self,
        product: str,
        spec_dict: dict,
        access_token: str,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        self.product = product
        self._access_token = access_token
        self._openapi_toolset = self.load_toolset()
        self.tool_filter = tool_filter
        self.spec_dict = spec_dict
        # self.convert_boolean_enums(self.spec_dict)
        logging.info(f"Atlassian API TOOLSET __ ACCESS TOKEN: {self._access_token}")
        # CLOUD_ID = os.getenv("JIRA_CLOUD_ID")

    def _is_tool_selected(
        self, tool: Any, readonly_context: ReadonlyContext
    ) -> bool:
        if not self.tool_filter:
            return True

        if isinstance(self.tool_filter, ToolPredicate):
            return self.tool_filter(tool, readonly_context)

        if isinstance(self.tool_filter, list):
            return tool.name in self.tool_filter

        return False

    def convert_boolean_enums(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'enum' and any(isinstance(x, bool) for x in value):
                    obj[key] = [str(x).lower() for x in value]
                elif isinstance(value, (dict, list)):
                    convert_boolean_enums(value)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    convert_boolean_enums(item)

    @override
    def get_tools(
      self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[AtlassianApiTool]:
        """Get all tools in the toolset."""
        all_tools = self._openapi_toolset.get_tools()
        return [
            AtlassianApiTool(tool, access_token=self._access_token)
            for tool in all_tools
            # if self._is_tool_selected(tool, readonly_contextj)
        ]

    def set_tool_filter(self, tool_filter: Union[ToolPredicate, List[str]]):
        self.tool_filter = tool_filter

    def load_toolset_orig(self) -> OpenAPIToolset:
        # # Fetch the OpenAPI spec JSON for the specified Atlassian product
        # fetcher = AtlassianApiFetcher(self.product, CLOUD_ID)
        # # fetcher.fetch_swagger()
        # spec_dict = fetcher.convert()  # type: ignore
        # spec_dict["servers"] = [{
        #     "url":f'https://api.atlassian.com/ex/{self.product.split('-')[0]}/{CLOUD_ID}'
        # }]
        # self.convert_boolean_enums(self.spec_dict)

        # Build an OpenAPIToolset without OIDC; AtlassianApiTool will attach the bearer token.
        return OpenAPIToolset(
            spec_str=json.dumps(self.spec_dict),
            spec_str_type='json',
            auth_scheme=OAuth2(
                flows=OAuthFlows(
                    authorizationCode=OAuthFlowAuthorizationCode(
                        authorizationUrl="https://auth.atlassian.com/authorize",
                        tokenUrl="https://auth.atlassian.com/oauth/token",
                        scopes={
                            "offline_access": "Refresh token",
                            "read:jira-work": "Read Jira data",
                            "write:jira-work": "Write Jira data",
                            "manage:jira-project": "Manage Jira projects",
                            "manage:jira-configuration": "Manage Jira configuration"
                        },
                    )
                )
            ),
            auth_credential=None
        )
    
    def load_toolset(self) -> OpenAPIToolset:
        response = requests.get("https://developer.atlassian.com/cloud/jira/platform/swagger-v3.v3.json")
        graph_spec_json = response.text

        # Parse as dictionary to modify servers
        # spec_dict = json.loads(graph_spec_json)
        spec_dict = JIRA_OPENAPI_SPEC
        # Modify servers to use OAuth2 bearer token
        cloudId = os.getenv("JIRA_CLOUD_ID")
        spec_dict['servers'] = [{
            'url': f'https://api.atlassian.com/ex/jira/{cloudId}'
        }]

        # Convert boolean enums to strings in the spec
        def convert_boolean_enums(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'enum' and any(isinstance(x, bool) for x in value):
                        obj[key] = [str(x).lower() for x in value]
                    elif isinstance(value, (dict, list)):
                        convert_boolean_enums(value)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        convert_boolean_enums(item)

        convert_boolean_enums(spec_dict)

        # Convert back to JSON string
        graph_spec_json = json.dumps(spec_dict)
        self.spec_dict = spec_dict
        # Build an OpenAPIToolset without OIDC; AtlassianApiTool will attach the bearer token.
        return OpenAPIToolset(
            spec_str=graph_spec_json,
            spec_str_type='json',
            auth_scheme=OAuth2(
                flows=OAuthFlows(
                    authorizationCode=OAuthFlowAuthorizationCode(
                        authorizationUrl="https://auth.atlassian.com/authorize",
                        tokenUrl="https://auth.atlassian.com/oauth/token",
                        scopes={
                            "offline_access": "Refresh token",
                            "read:jira-work": "Read Jira data",
                            "write:jira-work": "Write Jira data",
                            "manage:jira-project": "Manage Jira projects",
                            "manage:jira-configuration": "Manage Jira configuration"
                        },
                    )
                )
            ),
            auth_credential=None
        )
    
    def get_toolset(self, auth_scheme, auth_credential) -> OpenAPIToolset:
        # # Fetch the OpenAPI spec JSON for the specified Atlassian product
        # fetcher = AtlassianApiFetcher(self.product, CLOUD_ID)
        # # fetcher.fetch_swagger()
        # spec_dict = fetcher.convert()  # type: ignore
        # spec_dict["servers"] = [{
        #     "url":f"https://api.atlassian.com/ex/{self.product.split('-')[0]}/{CLOUD_ID}"
        # }]
        # Build an OpenAPIToolset without OIDC; AtlassianApiTool will attach the bearer token.
        return OpenAPIToolset(
            spec_dict=self.spec_dict,
            spec_str_type='json',
            auth_scheme=auth_scheme,
            auth_credential=auth_credential
        )

    def configure_access_token_auth(self, access_token: str):
        """Set a bearer token for all calls."""
        self._access_token = access_token

    @override
    async def close(self):
        if self._openapi_toolset:
            await self._openapi_toolset.close()


class JiraPlatformToolset(AtlassianApiToolset):
    """Auto-generated Jira Platform toolset based on Jira Cloud REST API v3 OpenAPI spec."""

    def __init__(
        self,
        access_token: str,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None
    ):
        logging.info(f"JIRA PLATFORM TOOLSET __ ACCESS TOKEN: {access_token}")
        self.spec_dict = JIRA_OPENAPI_SPEC
        super().__init__("jira-platform", access_token=access_token, tool_filter=tool_filter, spec_dict=self.spec_dict)


# class JiraSoftwareToolset(AtlassianApiToolset):
#     """Auto-generated Jira Software toolset based on Jira Software Cloud REST API v3 OpenAPI spec."""

#     def __init__(
#         self,
#         access_token: Optional[str] = None,
#         tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
#     ):
#         super().__init__("jira-software", access_token, tool_filter)


# class ConfluenceToolset(AtlassianApiToolset):
#     """Auto-generated Confluence toolset based on Confluence Cloud REST API v3 OpenAPI spec."""

#     def __init__(
#         self,
#         access_token: Optional[str] = None,
#         tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
#     ):
#         super().__init__("confluence", access_token, tool_filter)
