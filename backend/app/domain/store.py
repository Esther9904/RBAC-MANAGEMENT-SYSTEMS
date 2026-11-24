from app.domain.permissions import ADMIN_ROLE_ID, PERMISSIONS


def create_store():
    return {
        "roles": [
            {"id": ADMIN_ROLE_ID, "name": "Admin", "permissions": list(PERMISSIONS), "is_system": True},
            {"id": "editor", "name": "Editor", "permissions": ["users:read", "users:write", "reports:export"], "is_system": False},
            {"id": "viewer", "name": "Viewer", "permissions": ["users:read"], "is_system": False},
            {"id": "auditor", "name": "Auditor", "permissions": ["users:read", "audit:read", "reports:export"], "is_system": False},
        ],
        "users": [
            {"id": "u-alice", "name": "Alice Admin", "role_ids": [ADMIN_ROLE_ID]},
            {"id": "u-bob", "name": "Bob Editor", "role_ids": ["editor"]},
            {"id": "u-carol", "name": "Carol Viewer", "role_ids": ["viewer"]},
            {"id": "u-dave", "name": "Dave Auditor", "role_ids": ["auditor"]},
        ],
        "audit_log": [],
    }