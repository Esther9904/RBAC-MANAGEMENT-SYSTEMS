from datetime import datetime, timezone

MAX_ENTRIES = 500


class AuditLog:
    def __init__(self, store):
        self._entries = store["audit_log"]

    def record(self, user_id, user_name, action, permission, outcome):
        self._entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "user_name": user_name,
            "action": action,
            "permission": permission,
            "outcome": outcome,
        })
        if len(self._entries) > MAX_ENTRIES:
            del self._entries[: len(self._entries) - MAX_ENTRIES]

    def list_entries(self):
        return [dict(entry) for entry in reversed(self._entries)]