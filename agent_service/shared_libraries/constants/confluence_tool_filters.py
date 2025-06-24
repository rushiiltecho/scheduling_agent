
# Content Access & Retrieval
content_access_tools = [
    "search_content_by_cql",
    "get_content_descendants", 
    "get_descendants_of_type",
    "get_macro_body_by_macro_id",
    "get_and_convert_macro_body_by_macro_id"
]

# Content Analysis & Conversion
content_conversion_tools = [
    "async_convert_content_body_request",
    "async_convert_content_body_response", 
    "bulk_async_convert_content_body_request",
    "bulk_async_convert_content_body_response"
]

# Attachments & Files
attachment_tools = [
    "download_attatchment",
    # "create_attachment",
    # "update_attachment_data"
]

# Labels & Categorization
label_tools = [
    "get_all_label_content",
    "add_labels_to_content", 
    "get_labels_for_space"
]

# User & Permission Context
user_tools = [
    "get_current_user",
    "get_user_properties",
    "get_user_property",
    "create_user_property", 
    "update_user_property",
    "check_content_permission"
]

# Space-Level Analysis
space_tools = [
    "get_space_settings",
    "get_space_content_states",
    "get_contents_with_state"
]

# Templates (for Documentation)
template_tools = [
    "get_content_templates",
    "create_content_template"
]

# Search & Discovery
search_tools = [
    "search_by_cql",
    "search_user"
]

# Audit & History (for Change Analysis)
audit_tools = [
    "get_audit_records",
    "get_audit_records_for_time_period"
]

# Combined list of all recommended tools
knowledge_extraction_tools = [
    # Content Access & Retrieval
    "search_content_by_cql",
    "get_content_descendants", 
    "get_descendants_of_type",
    "get_macro_body_by_macro_id",
    "get_and_convert_macro_body_by_macro_id",
    
    # Content Analysis & Conversion
    "async_convert_content_body_request",
    "async_convert_content_body_response", 
    "bulk_async_convert_content_body_request",
    "bulk_async_convert_content_body_response",
    
    # Attachments & Files
    "download_attatchment",
    # "create_attachment",
    # "update_attachment_data",
    
    # Labels & Categorization
    "get_all_label_content",
    "add_labels_to_content", 
    "get_labels_for_space",
    
    # User & Permission Context
    "get_current_user",
    "get_user_properties",
    "get_user_property",
    "create_user_property", 
    "update_user_property",
    "check_content_permission",
    
    # Space-Level Analysis
    "get_space_settings",
    "get_space_content_states",
    "get_contents_with_state",
    
    # Templates (for Documentation)
    "get_content_templates",
    "create_content_template",
    
    # Search & Discovery
    "search_by_cql",
    "search_user",
    
    # Audit & History (for Change Analysis)
    "get_audit_records",
    "get_audit_records_for_time_period"
]

# Core workflow tools (most essential)
core_workflow_tools = [
    "search_content_by_cql",        # Discovery
    "get_content_descendants",      # Content retrieval
    "download_attatchment",         # File access
    "async_convert_content_body_request",  # Format conversion
    "create_user_property",         # Analysis storage
    "add_labels_to_content",        # Organization
    "check_content_permission",     # Permission checks
    "get_current_user"              # User context
]
