import re

from app.domain.permissions import PERMISSIONS
from app.errors import AppError

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]*$")
NAME_MIN = 2
NAME_MAX = 30


def validate_role_input(data, existing_roles, ignore_role_id=None):
    if not isinstance(data, dict):
        raise AppError(400, "VALIDATION_ERROR", "Request body must be a JSON object.")

    errors = []

    raw_name = data.get("name")
    name = " ".join(raw_name.split()) if isinstance(raw_name, str) else ""
    if not name:
        errors.append({"field": "name", "message": "Role name is required."})
    elif not NAME_MIN <= len(name) <= NAME_MAX:
        errors.append({"field": "name", "message": f"Role name must be {NAME_MIN}-{NAME_MAX} characters."})
    elif not NAME_PATTERN.match(name):
        errors.append({
            "field": "name",
            "message": 'Role name must start with a letter and use only letters, numbers, spaces, "-" or "_".',
        })

    permissions = []
    raw_permissions = data.get("permissions")
    if not isinstance(raw_permissions, list):
        errors.append({"field": "permissions", "message": "Permissions must be a list."})
    elif len(raw_permissions) == 0:
        errors.append({"field": "permissions", "message": "Select at least one permission."})
    elif not all(isinstance(p, str) and p in PERMISSIONS for p in raw_permissions):
        errors.append({"field": "permissions", "message": "One or more permissions are not recognised."})
    else:
        permissions = list(dict.fromkeys(raw_permissions))

    if errors:
        raise AppError(400, "VALIDATION_ERROR", "Please fix the highlighted fields.", errors)

    is_duplicate = any(
        role["id"] != ignore_role_id and role["name"].casefold() == name.casefold()
        for role in existing_roles
    )
    if is_duplicate:
        raise AppError(
            409,
            "DUPLICATE_ROLE_NAME",
            "A role with this name already exists.",
            [{"field": "name", "message": "A role with this name already exists."}],
        )

    return {"name": name, "permissions": permissions}