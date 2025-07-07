import json
import os
from typing import Any, List, Optional, Union

from typing_extensions import override
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_toolset import BaseToolset, ToolPredicate
from google.adk.tools.openapi_tool import OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials
from google.adk.auth import OpenIdConnectWithConfig
from fastapi.openapi.models import OAuth2, OAuthFlows, OAuthFlowAuthorizationCode
import yaml

# Define the scopes for the Slack API.
# A comprehensive list can be found at: https://api.slack.com/scopes
SLACK_SCOPES = {
    "channels:history": "View messages and other content in public channels that your app has been added to.",
    "channels:read": "View basic information about public channels in a workspace.",
    "chat:write": "Send messages as your app.",
    "chat:write.public": "Send messages to a channel your app is not a member of.",
    "commands": "Add shortcuts and/or slash commands that people can use.",
    "users:read": "View basic information about users in a workspace.",
    "users:read.email": "View email addresses of users in a workspace."
}

# TODO: Fill these in with your Slack App's credentials from https://api.slack.com/apps
os.environ["SLACK_CLIENT_ID"] = "YOUR_SLACK_CLIENT_ID"
os.environ["SLACK_CLIENT_SECRET"] = "YOUR_SLACK_CLIENT_SECRET"


class SlackApiToolset(BaseToolset):
    """
    Toolset for Slack APIs using a local OpenAPI spec and ADK's
    OpenIdConnectWithConfig for OAuth2 bearer-token flows.
    """

    def __init__(
        self,
        spec_path: str = "./slack_openapi_spec.yaml",
        access_token: Optional[str] = None,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        """
        Initializes the SlackApiToolset.

        Args:
            spec_path: The local file path to the Slack OpenAPI JSON specification.
            access_token: The initial OAuth2 access token (xoxp-...).
            tool_filter: A predicate or list of operation IDs to filter the tools.
        """
        self.spec_path = spec_path
        self._access_token = access_token
        self.tool_filter = tool_filter
        self._openapi_toolset = self._load_toolset_from_spec(access_token)

    @override
    def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None
    ) -> List[Any]:
        """
        Retrieves the list of tools generated from the OpenAPI specification.
        """
        return self._openapi_toolset.get_tools(readonly_context)

    def _load_toolset_from_spec(self, access_token: Optional[str]) -> OpenAPIToolset:
        """
        Loads the OpenAPI spec from a file, configures authentication,
        and creates the OpenAPIToolset.
        """
        # Load the OpenAPI spec from the local file
        try:
            with open(self.spec_path, 'r') as f:
                spec_dict = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"OpenAPI specification file not found at: {self.spec_path}")
        except yaml.YAMLError:
            raise ValueError(f"Could not decode YAML from the spec file: {self.spec_path}")


        # Override the server URL to point to the correct Slack API endpoint.
        # The OpenAPI spec might have a generic or incorrect server URL.
        spec_dict['servers'] = [{'url': 'https://slack.com/api'}]

        # Configure OIDC auth for Slack using ADK's built-in support.
        # These URLs are standard for Slack's OAuth v2 flow.
        oidc = OpenIdConnectWithConfig(
            authorization_endpoint="https://slack.com/oauth/v2/authorize",
            token_endpoint="https://slack.com/api/oauth.v2.access",
            # Slack does not have standard userinfo/revocation endpoints in the same way
            userinfo_endpoint=None,
            revocation_endpoint=None,
            token_endpoint_auth_methods_supported=["client_secret_post"],
            grant_types_supported=["authorization_code"],
            scopes=list(SLACK_SCOPES.keys())
        )

        # Define the authentication credential using the provided bearer token.
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
            auth_scheme=oidc,
            tool_filter=self.tool_filter,
            auth_credential=auth_credential
        )

    def configure_access_token_auth(self, access_token: str):
        """
        Update the bearer token for all subsequent API requests.
        This is useful for token refresh scenarios.
        """
        self._access_token = access_token
        auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="bearer",
                credentials=HttpCredentials(token=self._access_token),
            ),
        )
        oidc = OpenIdConnectWithConfig(
            authorization_endpoint="https://slack.com/oauth/v2/authorize",
            token_endpoint="https://slack.com/api/oauth.v2.access",
            # Slack does not have standard userinfo/revocation endpoints in the same way
            userinfo_endpoint=None,
            revocation_endpoint=None,
            token_endpoint_auth_methods_supported=["client_secret_post"],
            grant_types_supported=["authorization_code"],
            scopes=list(SLACK_SCOPES.keys())
        )
        # Re-configure the authentication on the underlying toolset
        self._openapi_toolset._configure_auth_all(oidc,auth_credential=auth_credential)

    async def close(self):
        """
        Clean up any resources used by the toolset, if necessary.
        """
        if hasattr(self, '_openapi_toolset') and self._openapi_toolset:
            await self._openapi_toolset.close()
