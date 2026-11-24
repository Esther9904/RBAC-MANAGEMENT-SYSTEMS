import copy
import uuid

from app.errors import AppError
from app.validation.role_validation import validate_role_input


class RoleService:
    def __init__(self, store):
        self._store = store

    def _find_or_404(self, role_id):
        role = next((r for r in self._store["roles"] if r["id"] == role_id), None)
        if role is None:
            raise AppError(404, "ROLE_NOT_FOUND", "Role not found.")
        return role

    def list_roles(self):
        return copy.deepcopy(self._store["roles"])

    def create_role(self, data):
        cleaned = validate_role_input(data, self._store["roles"])
        role = {
            "id": str(uuid.uuid4()),
            "name": cleaned["name"],
            "permissions": cleaned["permissions"],
            "is_system": False,
        }
        self._store["roles"].append(role)
        return copy.deepcopy(role)

    def update_role(self, role_id, data):
        role = self._find_or_404(role_id)
        if role["is_system"]:
            raise AppError(409, "SYSTEM_ROLE_LOCKED", "The built-in Admin role cannot be modified.")
        cleaned = validate_role_input(data, self._store["roles"], ignore_role_id=role_id)
        role["name"] = cleaned["name"]
        role["permissions"] = cleaned["permissions"]
        return copy.deepcopy(role)