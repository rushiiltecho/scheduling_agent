import os
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
# from .tools_instructions import JIRA_TOOLS_INSTRUCTIONS
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, HttpAuth, HttpCredentials
import json

jira_tool = ApplicationIntegrationToolset(
    project="proposal-auto-ai-internal",  #Replace with GCP project
    location="us-central1",  #Replace with location of the connection
    connection="jira-cloud-poc-conn",  #Replace with connection name
    entity_operations = {
        "Projects": ["LIST", "GET", "CREATE", "UPDATE"],
        "Issues": ["LIST", "GET", "CREATE", "UPDATE"],
        "IssueTransition": ["LIST", "GET", "CREATE", "UPDATE"],
        "Comments": ["LIST", "GET", "CREATE", "UPDATE"]
    },
    # auth_credential=AuthCredential(
    #     auth_type=AuthCredentialTypes.HTTP,
    #     http=HttpAuth(
    #         scheme="bearer",
    #         credentials=HttpCredentials(token="TOKEN"),
    #     ),
    # )
    triggers=["api_trigger/jira_vertex_ai_poc_API_1"],
    service_account_json=os.getenv("SERVICE_ACCOUNT") or "",
)