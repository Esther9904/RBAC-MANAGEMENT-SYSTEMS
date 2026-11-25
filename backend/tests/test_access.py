import pytest

from app.errors import AppError


def test_user_with_permission_can_perform_action_and_it_is_logged_as_allowed(access, audit):
    result = access.perform_action("u-bob", "export_report")

    assert "Export Report completed" in result["message"]
    latest = audit.list_entries()[0]
    assert latest["user_id"] == "u-bob"
    assert latest["action"] == "Export Report"
    assert latest["outcome"] == "Allowed"


def test_user_without_permission_is_blocked_with_403_and_logged_as_denied(access, audit):
    with pytest.raises(AppError) as exc_info:
        access.perform_action("u-carol", "delete_user")

    assert exc_info.value.status == 403
    assert exc_info.value.code == "FORBIDDEN"
    latest = audit.list_entries()[0]
    assert latest["user_id"] == "u-carol"
    assert latest["outcome"] == "Denied"


@pytest.mark.parametrize("bad_user_id", ["nobody", "", None, 123])
def test_unknown_or_missing_user_gets_401(access, bad_user_id):
    with pytest.raises(AppError) as exc_info:
        access.perform_action(bad_user_id, "export_report")
    assert exc_info.value.status == 401


def test_unknown_action_gets_404(access):
    with pytest.raises(AppError) as exc_info:
        access.perform_action("u-alice", "launch_rocket")
    assert exc_info.value.status == 404
    assert exc_info.value.code == "UNKNOWN_ACTION"


def test_permissions_are_read_live_from_roles(access, store):
    with pytest.raises(AppError):
        access.perform_action("u-carol", "export_report")

    viewer = next(r for r in store["roles"] if r["id"] == "viewer")
    viewer["permissions"].append("reports:export")

    assert "completed" in access.perform_action("u-carol", "export_report")["message"]


def test_permissions_from_multiple_roles_are_combined(access, store):
    carol = next(u for u in store["users"] if u["id"] == "u-carol")
    carol["role_ids"] = ["viewer", "auditor"]

    assert access.authorize("u-carol", "audit:read")["id"] == "u-carol"


def test_allowed_reads_can_skip_logging_but_denials_are_always_logged(access, audit):
    access.authorize("u-carol", "users:read", log_allowed=False)
    assert audit.list_entries() == []

    with pytest.raises(AppError):
        access.authorize("u-carol", "audit:read", log_allowed=False)
    assert len(audit.list_entries()) == 1



def test_describe_returns_effective_permissions_without_writing_to_the_audit_log(access, audit):
    me = access.describe("u-carol")

    assert me == {"id": "u-carol", "name": "Carol Viewer", "role_ids": ["viewer"], "permissions": ["users:read"]}
    assert audit.list_entries() == []


@pytest.mark.parametrize("bad_user_id", ["nobody", None])
def test_describe_for_an_unknown_user_gets_401(access, bad_user_id):
    with pytest.raises(AppError) as exc_info:
        access.describe(bad_user_id)
    assert exc_info.value.status == 401