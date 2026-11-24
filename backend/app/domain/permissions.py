from types import MappingProxyType

PERMISSIONS = (
    "users:read",
    "users:write",
    "users:delete",
    "roles:manage",
    "reports:export",
    "settings:edit",
    "audit:read",
)

PROTECTED_ACTIONS = MappingProxyType({
    "export_report": {"label": "Export Report", "permission": "reports:export"},
    "update_user": {"label": "Update User", "permission": "users:write"},
    "delete_user": {"label": "Delete User", "permission": "users:delete"},
    "edit_settings": {"label": "Edit Settings", "permission": "settings:edit"},
})

ADMIN_ROLE_ID = "admin"