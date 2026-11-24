import pytest

from app.errors import AppError


def _roles_of(user_service, user_id):
    return next(u for u in user_service.list_users() if u["id"] == user_id)["role_ids"]


def test_assigning_a_non_existent_role_is_rejected_and_leaves_the_user_unchanged(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-carol", {"role_ids": ["viewer", "ghost-role"]})

    assert exc_info.value.status == 400
    assert exc_info.value.code == "ROLE_NOT_FOUND"
    assert _roles_of(user_service, "u-carol") == ["viewer"]


def test_the_last_admin_cannot_lose_the_admin_role(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-alice", {"role_ids": ["viewer"]})

    assert exc_info.value.status == 409
    assert exc_info.value.code == "LAST_ADMIN"
    assert _roles_of(user_service, "u-alice") == ["admin"]


def test_an_admin_can_step_down_once_another_admin_exists(user_service):
    user_service.assign_roles("u-bob", {"role_ids": ["admin"]})

    result = user_service.assign_roles("u-alice", {"role_ids": ["viewer"]})

    assert result["role_ids"] == ["viewer"]


def test_a_user_can_hold_multiple_roles_and_duplicates_are_collapsed(user_service):
    result = user_service.assign_roles("u-carol", {"role_ids": ["viewer", "auditor", "viewer"]})

    assert result["role_ids"] == ["viewer", "auditor"]


def test_assigning_roles_to_an_unknown_user_returns_404(user_service):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("nobody", {"role_ids": ["viewer"]})

    assert exc_info.value.status == 404


@pytest.mark.parametrize("bad_body", [None, {}, {"role_ids": "viewer"}, {"role_ids": [1, 2]}, ["viewer"]])
def test_malformed_assignment_bodies_are_rejected_with_400(user_service, bad_body):
    with pytest.raises(AppError) as exc_info:
        user_service.assign_roles("u-carol", bad_body)

    assert exc_info.value.status == 400