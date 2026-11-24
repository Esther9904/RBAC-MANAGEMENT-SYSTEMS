from app.domain.permissions import ADMIN_ROLE_ID
from app.errors import AppError


def _to_view(user):
    return {"id": user["id"], "name": user["name"], "role_ids": list(user["role_ids"])}


class UserService:
    def __init__(self, store):
        self._store = store

    def list_users(self):
        return [_to_view(user) for user in self._store["users"]]

    def list_for_switcher(self):
        return [{"id": user["id"], "name": user["name"]} for user in self._store["users"]]

    def assign_roles(self, user_id, data):
        user = next((u for u in self._store["users"] if u["id"] == user_id), None)
        if user is None:
            raise AppError(404, "USER_NOT_FOUND", "User not found.")

        if (
            not isinstance(data, dict)
            or not isinstance(data.get("role_ids"), list)
            or not all(isinstance(role_id, str) for role_id in data["role_ids"])
        ):
            raise AppError(
                400,
                "VALIDATION_ERROR",
                "role_ids must be a list of role ids.",
                [{"field": "role_ids", "message": "role_ids must be a list of role ids."}],
            )
        role_ids = list(dict.fromkeys(data["role_ids"]))

        known_role_ids = {role["id"] for role in self._store["roles"]}
        if not set(role_ids) <= known_role_ids:
            raise AppError(400, "ROLE_NOT_FOUND", "One or more selected roles do not exist.")

        is_losing_admin = ADMIN_ROLE_ID in user["role_ids"] and ADMIN_ROLE_ID not in role_ids
        if is_losing_admin:
            other_admins = [
                u for u in self._store["users"]
                if u["id"] != user["id"] and ADMIN_ROLE_ID in u["role_ids"]
            ]
            if not other_admins:
                raise AppError(409, "LAST_ADMIN", "Cannot remove the Admin role from the last Admin.")

        user["role_ids"] = role_ids
        return _to_view(user)