from datetime import datetime

from app.services.audit_log import MAX_ENTRIES


def test_entries_are_newest_first_with_a_parseable_timestamp(audit):
    audit.record("u-bob", "Bob Editor", "First", "users:read", "Allowed")
    audit.record("u-bob", "Bob Editor", "Second", "users:read", "Allowed")

    entries = audit.list_entries()

    assert [e["action"] for e in entries] == ["Second", "First"]
    datetime.fromisoformat(entries[0]["timestamp"])


def test_log_never_grows_beyond_the_cap_and_drops_oldest_first(audit):
    for i in range(MAX_ENTRIES + 5):
        audit.record("u-bob", "Bob Editor", f"Action {i}", "users:read", "Allowed")

    entries = audit.list_entries()

    assert len(entries) == MAX_ENTRIES
    assert entries[-1]["action"] == "Action 5"