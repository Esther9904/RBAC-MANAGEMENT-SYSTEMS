import pytest

from app.errors import AppError


def _roles_of(user_service, user_id):
    return next(u for u in user_service.list_users() if u["id"] == user_id)["role_ids"]


def test_assigning_a_non_existent_role_is_rejected_and_leaves_the_user_unchanged(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-carol", {"role_ids": ["viewer", "ghost-role"]}, "u-alice")

    assert exc_info.value.status == 400
    assert exc_info.value.code == "ROLE_NOT_FOUND"
    assert _roles_of(user_service, "u-carol") == ["viewer"]


def test_the_last_admin_cannot_lose_the_admin_role(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-alice", {"role_ids": ["viewer"]}, "u-alice")

    assert exc_info.value.status == 409
    assert exc_info.value.code == "LAST_ADMIN"
    assert _roles_of(user_service, "u-alice") == ["admin"]


def test_an_admin_can_step_down_once_another_admin_exists(user_service):
    user_service.assign_roles("u-bob", {"role_ids": ["admin"]}, "u-alice")

    result = user_service.assign_roles("u-alice", {"role_ids": ["viewer"]}, "u-alice")

    assert result["role_ids"] == ["viewer"]


def test_a_user_can_hold_multiple_roles_and_duplicates_are_collapsed(user_service):
    result = user_service.assign_roles("u-carol", {"role_ids": ["viewer", "auditor", "viewer"]}, "u-alice")

    assert result["role_ids"] == ["viewer", "auditor"]


def test_assigning_roles_to_an_unknown_user_returns_404(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("nobody", {"role_ids": ["viewer"]}, "u-alice")

    assert exc_info.value.status == 404


@pytest.mark.parametrize("bad_body", [None, {}, {"role_ids": "viewer"}, {"role_ids": [1, 2]}, ["viewer"]])
def test_malformed_assignment_bodies_are_rejected_with_400(user_service, bad_body):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-carol", bad_body, "u-alice")

    assert exc_info.value.status == 400


@pytest.mark.parametrize("bad_actor", [None, "nobody", 123])
def test_an_unknown_actor_gets_401_and_nothing_changes(user_service, bad_actor):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-carol", {"role_ids": ["editor"]}, bad_actor)

    assert exc_info.value.status == 401
    assert _roles_of(user_service, "u-carol") == ["viewer"]


def test_a_non_admin_cannot_grant_the_admin_role_and_the_denial_is_logged(user_service, audit):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-bob", {"role_ids": ["admin"]}, "u-bob")

    assert exc_info.value.status == 403
    assert exc_info.value.code == "ADMIN_ROLE_RESTRICTED"
    assert _roles_of(user_service, "u-bob") == ["editor"]
    latest = audit.list_entries()[0]
    assert (latest["user_id"], latest["outcome"]) == ("u-bob", "Denied")


def test_a_non_admin_cannot_remove_the_admin_role_from_an_admin(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-alice", {"role_ids": ["viewer"]}, "u-bob")

    assert exc_info.value.code == "ADMIN_ROLE_RESTRICTED"
    assert _roles_of(user_service, "u-alice") == ["admin"]


def test_a_non_admin_can_still_assign_ordinary_roles(user_service):
    result = user_service.assign_roles("u-carol", {"role_ids": ["editor"]}, "u-bob")

    assert result["role_ids"] == ["editor"]


def test_an_admin_can_grant_the_admin_role(user_service):
    result = user_service.assign_roles("u-bob", {"role_ids": ["editor", "admin"]}, "u-alice")

    assert "admin" in result["role_ids"]