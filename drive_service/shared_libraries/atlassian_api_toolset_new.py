import json
import os
import requests
from typing import Any, List, Optional, Union

from typing_extensions import override
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_toolset import BaseToolset, ToolPredicate
from google.adk.tools.openapi_tool import OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials
from drive_service.shared_libraries.atlassian_api_tool import AtlassianApiTool
from google.adk.auth import OpenIdConnectWithConfig
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from drive_service.shared_libraries.constants import SCOPES

class AtlassianApiToolset(BaseToolset):
    """
    Base toolset for Atlassian APIs (Jira, Confluence) using OpenAPI spec
    and ADK's OpenIdConnectWithConfig for OAuth2 bearer-token flows.
    """
    def __init__(
        self,
        spec_url: str,
        access_token: Optional[str],
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        self.spec_url = spec_url
        self._access_token = access_token
        self.tool_filter = tool_filter
        self._openapi_toolset = self._load_toolset_with_oidc_auth(access_token)

    @override
    def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None
    ) -> List[AtlassianApiTool]:
        # Wrap each OpenAPI tool in a GoogleApiTool, injecting the bearer token
        # return [
        #     AtlassianApiTool(tool, access_token=self._access_token)
        #     for tool in self._openapi_toolset.get_tools(readonly_context)
        # ]
        auth_credential= AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="bearer",
                credentials=HttpCredentials(token=self._access_token),
            ),
        )
        oidc = OpenIdConnectWithConfig(
            authorization_endpoint="https://auth.atlassian.com/authorize",
            token_endpoint="https://auth.atlassian.com/oauth/token",
            userinfo_endpoint="https://api.atlassian.com/me",
            revocation_endpoint="https://auth.atlassian.com/oauth/revoke",
            token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
            grant_types_supported=["authorization_code"],
            scopes=SCOPES.keys()#["write:jira-work","read:jira-work","offline_access"]
        )
        auth_scheme = OAuth2(
            flows=OAuthFlows(
                authorizationCode=OAuthFlowAuthorizationCode(
                    authorizationUrl="https://auth.atlassian.com/authorize",
                    tokenUrl="https://auth.atlassian.com/oauth/token",
                    scopes=SCOPES,
                )
            )
        )
        self._openapi_toolset._configure_auth_all(oidc,auth_credential)
        tools = self._openapi_toolset.get_tools(readonly_context)
        return tools

    def _load_toolset_with_oidc_auth(self, access_token) -> OpenAPIToolset:
        # Fetch the OpenAPI spec from Atlassian
        resp = requests.get(self.spec_url)
        resp.raise_for_status()
        spec_dict = resp.json()
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

        # Extract a default scope for the OAuth2 flow
        scopes = spec_dict.get('components', {}) \
            .get('securitySchemes', {}) \
            .get('OAuth2', {}) \
            .get('flows', {}) \
            .get('authorizationCode', {}) \
            .get('scopes', {})
        default_scope = next(iter(scopes.keys()), None)
        # Configure OIDC auth using ADK's built-in support

        auth_scheme = OAuth2(
            flows=OAuthFlows(
                authorizationCode=OAuthFlowAuthorizationCode(
                    authorizationUrl="https://auth.atlassian.com/authorize",
                    tokenUrl="https://auth.atlassian.com/oauth/token",
                    scopes=SCOPES,
                )
            )
        )
        # oidc = OpenIdConnectWithConfig(
        #     authorization_endpoint="https://auth.atlassian.com/authorize",
        #     token_endpoint="https://auth.atlassian.com/oauth/token",
        #     userinfo_endpoint="https://api.atlassian.com/me",
        #     revocation_endpoint="https://auth.atlassian.com/oauth/revoke",
        #     token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
        #     grant_types_supported=["authorization_code"],
        #     scopes=[default_scope] if default_scope else []
        # )
        auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="bearer",
                credentials=HttpCredentials(token=access_token),
            ),
        )

        return OpenAPIToolset(
            spec_str=json.dumps(spec_dict),
            spec_str_type="json",
            auth_scheme=auth_scheme,
            tool_filter=self.tool_filter,
            auth_credential=auth_credential
        )

    def configure_access_token_auth(self, access_token: str):
        """
        Update the bearer token for all subsequent requests.
        """
        self._access_token = access_token

    async def close(self):
        if hasattr(self, '_openapi_toolset') and self._openapi_toolset:
            await self._openapi_toolset.close()


class JiraApiToolset(AtlassianApiToolset):
    """
    Toolset for Atlassian Jira Cloud API (OpenAPI v3).
    """
    def __init__(
        self,
        access_token: Optional[str] = None,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        super().__init__(
            spec_url="https://developer.atlassian.com/cloud/jira/platform/swagger-v3.v3.json",
            access_token=access_token,
            tool_filter=tool_filter,
        )


# class ConfluenceApiToolset(AtlassianApiToolset):
#     """
#     Toolset for Atlassian Confluence Cloud API (OpenAPI v1).
#     """
#     def __init__(
#         self,
#         access_token: Optional[str] = None,
#         tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
#     ):
#         super().__init__(
#             spec_url="https://developer.atlassian.com/cloud/confluence/openapi.json",
#             access_token=access_token,
#             tool_filter=tool_filter,
#         )
