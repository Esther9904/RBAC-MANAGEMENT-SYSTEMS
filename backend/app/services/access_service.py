from app.domain.permissions import PROTECTED_ACTIONS
from app.errors import AppError


class AccessService:
    def __init__(self, store, audit):
        self._store = store
        self._audit = audit

    def _find_user(self, user_id):
        if not isinstance(user_id, str):
            return None
        return next((u for u in self._store["users"] if u["id"] == user_id), None)

    def permissions_of(self, user):
        granted = set()
        for role_id in user["role_ids"]:
            role = next((r for r in self._store["roles"] if r["id"] == role_id), None)
            if role is not None:
                granted.update(role["permissions"])
        return granted

    def authorize(self, user_id, permission, action=None, log_allowed=True):
        user = self._find_user(user_id)
        if user is None:
            raise AppError(401, "UNAUTHENTICATED", "Unknown or missing user. Select a user to act as.")

        allowed = permission in self.permissions_of(user)
        if not allowed or log_allowed:
            self._audit.record(
                user_id=user["id"],
                user_name=user["name"],
                action=action or permission,
                permission=permission,
                outcome="Allowed" if allowed else "Denied",
            )
        if not allowed:
            raise AppError(403, "FORBIDDEN", f'Forbidden: this action requires the "{permission}" permission.')
        return user

    def perform_action(self, user_id, action_key):
        if action_key not in PROTECTED_ACTIONS:
            raise AppError(404, "UNKNOWN_ACTION", "Unknown action.")
        definition = PROTECTED_ACTIONS[action_key]
        self.authorize(user_id, definition["permission"], action=definition["label"])
        return {"message": f"{definition['label']} completed successfully (simulated)."}