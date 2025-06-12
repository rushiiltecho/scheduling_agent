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

from typing import Any, Dict, Optional

from typing_extensions import override
from google.genai.types import FunctionDeclaration

from google.adk.tools.base_tool import BaseTool
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth, HttpAuth, HttpCredentials
from google.adk.tools.openapi_tool import RestApiTool
from google.adk.tools.tool_context import ToolContext


class AtlassianApiTool(BaseTool):
    """
    Wraps a generated OpenAPI operation (RestApiTool) and handles authentication for Atlassian APIs.
    """

    def __init__(
        self,
        rest_api_tool: RestApiTool,
        access_token: str,
    ):
        super().__init__(
            name=rest_api_tool.name,
            description=rest_api_tool.description,
            is_long_running=rest_api_tool.is_long_running,
        )
        self._rest_api_tool = rest_api_tool
        self.configure_access_token_auth(access_token)

    @override
    def _get_declaration(self) -> FunctionDeclaration:
        return self._rest_api_tool._get_declaration()

    @override
    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: Optional[ToolContext]
    ) -> Dict[str, Any]:
        return await self._rest_api_tool.run_async(
            args=args, tool_context=tool_context
        )

    def configure_auth(self, client_id: str, client_secret: str):
        """Configure OAuth2 client credentials (if using OIDC flow)."""
        self._rest_api_tool.auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
            oauth2=OAuth2Auth(
                client_id=client_id,
                client_secret=client_secret,
            ),
        )

    def configure_access_token_auth(self, access_token: str):
        """Configure a bearer token for direct HTTP auth."""
        self._rest_api_tool.auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="bearer",
                credentials=HttpCredentials(token=access_token),
            ),
        )
