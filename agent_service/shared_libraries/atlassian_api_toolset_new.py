import json
import os
import requests
from typing import Any, List, Optional, Union

from typing_extensions import override
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_toolset import BaseToolset, ToolPredicate
from google.adk.tools.openapi_tool import OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials, OAuth2Auth
from agent_service.shared_libraries.atlassian_api_tool import AtlassianApiTool
from google.adk.auth import OpenIdConnectWithConfig
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

SCOPES = {
        "delete:async-task:jira": "Delete asynchronous task.",
        "delete:attachment:jira": "Delete issue attachments.",
        "delete:avatar:jira": "Delete system and custom avatars.",
        "delete:comment.property:jira": "Delete issue comment properties.",
        "delete:comment:jira": "Delete issue comments.",
        "delete:dashboard.property:jira": "Delete dashboard properties.",
        "delete:dashboard:jira": "Delete dashboards.",
        "delete:field-configuration-scheme:jira": "Delete field configuration schemes.",
        "delete:field-configuration:jira": "Delete field configurations.",
        "delete:field.option:jira": "Delete field options.",
        "delete:field:jira": "Delete fields.",
        "delete:filter.column:jira": "Delete filter columns.",
        "delete:filter:jira": "Delete filters.",
        "delete:group:jira": "Delete user groups.",
        "delete:issue-link-type:jira": "Delete issue link types.",
        "delete:issue-link:jira": "Delete issue links.",
        "delete:issue-type-scheme:jira": "Delete issue type schemes.",
        "delete:issue-type-screen-scheme:jira": "Delete issue type screen schemes.",
        "delete:issue-type.property:jira": "Delete issue type properties.",
        "delete:issue-type:jira": "Delete issue types.",
        "delete:issue-worklog.property:jira": "Delete issue worklog properties.",
        "delete:issue-worklog:jira": "Delete issue worklogs.",
        "delete:issue.property:jira": "Delete issue properties.",
        "delete:issue.remote-link:jira": "Delete issue remote links.",
        "delete:issue:jira": "Delete issues.",
        "delete:permission-scheme:jira": "Delete permission schemes.",
        "delete:permission:jira": "Delete permissions.",
        "delete:project-category:jira": "Delete project categories.",
        "delete:project-role:jira": "Delete project roles.",
        "delete:project-version:jira": "Delete project versions.",
        "delete:project.avatar:jira": "Delete project avatars.",
        "delete:project.component:jira": "Delete project components.",
        "delete:project.property:jira": "Delete project properties.",
        "delete:project:jira": "Delete projects and their details, such as issue types, project lead, and avatars.",
        "delete:screen-scheme:jira": "Delete screen schemes.",
        "delete:screen-tab:jira": "Delete screen tabs.",
        "delete:screen:jira": "Delete screens.",
        "delete:screenable-field:jira": "Delete screenable fields.",
        "delete:user-configuration:jira": "Delete user configurations.",
        "delete:user.property:jira": "Delete user properties.",
        "delete:webhook:jira": "Delete webhooks.",
        "delete:workflow-scheme:jira": "Delete workflow schemes.",
        "delete:workflow.property:jira": "Delete workflow properties.",
        "delete:workflow:jira": "Delete workflows.",
        "manage:jira-configuration": "Configure Jira settings that require the Jira administrators permission, for example, create projects and custom fields, view workflows, manage issue link types.",
        "manage:jira-project": "Create and edit project settings and create new project-level objects, for example, versions, components.",
        "manage:jira-webhook": "Manage Jira webhooks. Enables an OAuth app to register and unregister dynamic webhooks in Jira. It also provides for fetching of registered webhooks.",
        "read:app-data:jira": "Read app data.",
        "read:application-role:jira": "View application roles.",
        "read:attachment:jira": "View issue attachments.",
        "read:audit-log:jira": "View audit logs.",
        "read:avatar:jira": "View system and custom avatars.",
        "read:comment.property:jira": "View issue comment properties.",
        "read:comment:jira": "View issue comments.",
        "read:custom-field-contextual-configuration:jira": "Read custom field contextual configurations.",
        "read:dashboard.property:jira": "View dashboard properties.",
        "read:dashboard:jira": "View dashboards.",
        "read:email-address:jira": "View email addresses of all users regardless of the user's profile visibility settings.",
        "read:field-configuration-scheme:jira": "View field configuration schemes.",
        "read:field-configuration:jira": "Read field configurations.",
        "read:field.default-value:jira": "View field default values.",
        "read:field.option:jira": "View field options.",
        "read:field.options:jira": "Read field options.",
        "read:field:jira": "View fields.",
        "read:filter.column:jira": "View filter columns.",
        "read:filter.default-share-scope:jira": "View filter default share scopes.",
        "read:filter:jira": "View filters.",
        "read:group:jira": "View user groups.",
        "read:instance-configuration:jira": "View instance configurations.",
        "read:issue-details:jira": "View issue details.",
        "read:issue-event:jira": "Read issue events.",
        "read:issue-field-values:jira": "View issue field valueses.",
        "read:issue-link-type:jira": "View issue link types.",
        "read:issue-link:jira": "View issue links.",
        "read:issue-meta:jira": "View issue meta.",
        "read:issue-security-level:jira": "View issue security levels.",
        "read:issue-security-scheme:jira": "View issue security schemes.",
        "read:issue-status:jira": "View issue statuses.",
        "read:issue-type-hierarchy:jira": "Read issue type hierarchies.",
        "read:issue-type-scheme:jira": "View issue type schemes.",
        "read:issue-type-screen-scheme:jira": "View issue type screen schemes.",
        "read:issue-type.property:jira": "View issue type properties.",
        "read:issue-type:jira": "View issue types.",
        "read:issue-worklog.property:jira": "View issue worklog properties.",
        "read:issue-worklog:jira": "View issue worklogs.",
        "read:issue.changelog:jira": "View issue changelogs.",
        "read:issue.property:jira": "View issue properties.",
        "read:issue.remote-link:jira": "View issue remote links.",
        "read:issue.time-tracking:jira": "View issue time trackings.",
        "read:issue.transition:jira": "View issue transitions.",
        "read:issue.vote:jira": "View issue votes.",
        "read:issue.votes:jira": "View issue voteses.",
        "read:issue.watcher:jira": "View issue watchers.",
        "read:issue:jira": "View issues.",
        "read:jira-expressions:jira": "View jira expressions.",
        "read:jira-user": "View user information in Jira that you have access to, including usernames, email addresses, and avatars.",
        "read:jira-work": "Read project and issue data. Search for issues and objects associated with issues (such as attachments and worklogs).",
        "read:jql:jira": "View JQL.",
        "read:label:jira": "View labels.",
        "read:license:jira": "View licenses.",
        "read:notification-scheme:jira": "View notification schemes.",
        "read:permission-scheme:jira": "View permission schemes.",
        "read:permission:jira": "View permissions.",
        "read:priority:jira": "View priorities.",
        "read:project-category:jira": "View project categories.",
        "read:project-role:jira": "View project roles.",
        "read:project-type:jira": "View project types.",
        "read:project-version:jira": "View project versions.",
        "read:project.avatar:jira": "Read project avatars.",
        "read:project.component:jira": "View project components.",
        "read:project.email:jira": "View project emails.",
        "read:project.feature:jira": "Read project features.",
        "read:project.property:jira": "View project properties.",
        "read:project:jira": "View projects.",
        "read:resolution:jira": "View resolutions.",
        "read:role:jira": "View roles.",
        "read:screen-field:jira": "View screen fields.",
        "read:screen-scheme:jira": "View screen schemes.",
        "read:screen-tab:jira": "View screen tabs.",
        "read:screen:jira": "View screens.",
        "read:screenable-field:jira": "View screenable fields.",
        "read:status:jira": "View statuses.",
        "read:user-configuration:jira": "View user configurations.",
        "read:user.columns:jira": "View user columnses.",
        "read:user.property:jira": "View user properties.",
        "read:user:jira": "View users.",
        "read:webhook:jira": "View webhooks.",
        "read:workflow-scheme:jira": "View workflow schemes.",
        "read:workflow.property:jira": "View workflow properties.",
        "read:workflow:jira": "View workflows.",
        "send:notification:jira": "Send notifications.",
        "validate:jql:jira": "Validate JQL.",
        "write:app-data:jira": "Write app data.",
        "write:attachment:jira": "Create and update issue attachments.",
        "write:avatar:jira": "Create and update system and custom avatars.",
        "write:comment.property:jira": "Create and update issue comment properties.",
        "write:comment:jira": "Create and update issue comments.",
        "write:custom-field-contextual-configuration:jira": "Save custom field contextual configurations.",
        "write:dashboard.property:jira": "Create and update dashboard properties.",
        "write:dashboard:jira": "Create and update dashboards.",
        "write:field-configuration-scheme:jira": "Create and update field configuration schemes.",
        "write:field-configuration:jira": "Save field configurations.",
        "write:field.default-value:jira": "Create and update field default values.",
        "write:field.option:jira": "Create and update field options.",
        "write:field:jira": "Create and update fields.",
        "write:filter.column:jira": "Create and update filter columns.",
        "write:filter.default-share-scope:jira": "Create and update filter default share scopes.",
        "write:filter:jira": "Create and update filters.",
        "write:group:jira": "Create and update user groups.",
        "write:instance-configuration:jira": "Create and update instance configurations.",
        "write:issue-link-type:jira": "Create and update issue link types.",
        "write:issue-link:jira": "Create and update issue links.",
        "write:issue-type-scheme:jira": "Create and update issue type schemes.",
        "write:issue-type-screen-scheme:jira": "Create and update issue type screen schemes.",
        "write:issue-type.property:jira": "Create and update issue type properties.",
        "write:issue-type:jira": "Create and update issue types.",
        "write:issue-worklog.property:jira": "Create and update issue worklog properties.",
        "write:issue-worklog:jira": "Create and update issue worklogs.",
        "write:issue.property:jira": "Create and update issue properties.",
        "write:issue.remote-link:jira": "Create and update issue remote links.",
        "write:issue.time-tracking:jira": "Create and update issue time trackings.",
        "write:issue.vote:jira": "Create and update issue votes.",
        "write:issue.watcher:jira": "Create and update issue watchers.",
        "write:issue:jira": "Create and update issues.",
        "write:jira-work": "Create and edit issues in Jira, post comments, create worklogs, and delete issues.",
        "write:permission-scheme:jira": "Create and update permission schemes.",
        "write:permission:jira": "Create and update permissions.",
        "write:project-category:jira": "Create and update project categories.",
        "write:project-role:jira": "Create and update project roles.",
        "write:project-version:jira": "Create and update project versions.",
        "write:project.avatar:jira": "Create and update project avatars.",
        "write:project.component:jira": "Create and update project components.",
        "write:project.email:jira": "Create and update project emails.",
        "write:project.feature:jira": "Save project features.",
        "write:project.property:jira": "Create and update project properties.",
        "write:project:jira": "Create and update projects.",
        "write:screen-scheme:jira": "Create and update screen schemes.",
        "write:screen-tab:jira": "Create and update screen tabs.",
        "write:screen:jira": "Create and update screens.",
        "write:screenable-field:jira": "Create and update screenable fields.",
        "write:user-configuration:jira": "Create and update user configurations.",
        "write:user.property:jira": "Create and update user properties.",
        "write:webhook:jira": "Create and update webhooks.",
        "write:workflow-scheme:jira": "Create and update workflow schemes.",
        "write:workflow.property:jira": "Create and update workflow properties.",
        "write:workflow:jira": "Create and update workflows."
            }
scopes_to_give= ["read:jira-user","read:jira-work","offline_access"]


#TODO: Modify the atlassianapitoolset such that it only requires the product name and scopes + spec_url should be automatically prodvided
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
        product:str = ""
    ):
        self.product = product
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
        # auth_credential= AuthCredential(
        #     auth_type=AuthCredentialTypes.OAUTH2,
        #     oauth2=OAuth2Auth(
        #             client_id=os.getenv("JIRA_CLIENT_ID"),
        #             client_secret=os.getenv("JIRA_CLIENT_SECRET"),
        #         )
        # )
        oidc = OpenIdConnectWithConfig(
            authorization_endpoint="https://auth.atlassian.com/authorize",
            token_endpoint="https://auth.atlassian.com/oauth/token",
            userinfo_endpoint="https://api.atlassian.com/me",
            revocation_endpoint="https://auth.atlassian.com/oauth/revoke",
            token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
            grant_types_supported=["authorization_code"],
            scopes=["read:jira-user","read:jira-work","offline_access"]#SCOPES.keys()#["write:jira-work","read:jira-work","offline_access"]
        )

        self._openapi_toolset._configure_auth_all(oidc,auth_credential)
        tools = self._openapi_toolset.get_tools(readonly_context)
        return tools

    def _load_toolset_with_oidc_auth(self, access_token) -> OpenAPIToolset:
        # Fetch the OpenAPI spec from Atlassian
        resp = requests.get(self.spec_url)
        resp.raise_for_status()
        spec_dict = resp.json()
        cloudId = os.getenv("JIRA_CLOUD_ID") or "c094642b-a0f8-4b0b-b88e-aa8bc1c5fbf6"
        spec_dict['servers'] = [{
            'url': f'https://api.atlassian.com/ex/{self.product}/{cloudId}'
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
                    scopes={k:v for k,v in SCOPES.items() if k in scopes_to_give},
                )
            )
        )
        oidc = OpenIdConnectWithConfig(
            authorization_endpoint="https://auth.atlassian.com/authorize",
            token_endpoint="https://auth.atlassian.com/oauth/token",
            userinfo_endpoint="https://api.atlassian.com/me",
            revocation_endpoint="https://auth.atlassian.com/oauth/revoke",
            token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
            grant_types_supported=["authorization_code"],
            scopes=[default_scope] if default_scope else []
        )
        auth_credential = AuthCredential(
            auth_type=AuthCredentialTypes.HTTP,
            http=HttpAuth(
                scheme="bearer",
                credentials=HttpCredentials(token=access_token),
            ),
        )
        # auth_credential= AuthCredential(
        #     auth_type=AuthCredentialTypes.OAUTH2,
        #     oauth2=OAuth2Auth(
        #             client_id=os.getenv("JIRA_CLIENT_ID"),
        #             client_secret=os.getenv("JIRA_CLIENT_SECRET"),
        #         )
        # )
        return OpenAPIToolset(
            spec_str=json.dumps(spec_dict),
            spec_str_type="json",
            auth_scheme=oidc,
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
            product="jira"
        )


class ConfluenceApiToolset(AtlassianApiToolset):
    """
    Toolset for Atlassian Confluence Cloud API (OpenAPI v1).
    """
    def __init__(
        self,
        access_token: Optional[str] = None,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        super().__init__(
            spec_url="https://developer.atlassian.com/cloud/confluence/swagger.v3.json",
            access_token=access_token,
            tool_filter=tool_filter,
            product="confluence"
        )
