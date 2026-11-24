import pytest

from app.errors import AppError


def test_a_valid_role_can_be_created_and_then_listed(role_service):
    created = role_service.create_role({"name": "Support", "permissions": ["users:read"]})

    assert created["is_system"] is False
    assert any(role["id"] == created["id"] for role in role_service.list_roles())


def test_duplicate_name_fails_with_409_and_stores_nothing(role_service):
    count_before = len(role_service.list_roles())

    with pytest.raises(AppError) as exc_info:
        role_service.create_role({"name": "Viewer", "permissions": ["users:read"]})

    assert exc_info.value.status == 409
    assert exc_info.value.code == "DUPLICATE_ROLE_NAME"
    assert len(role_service.list_roles()) == count_before


def test_invalid_permission_fails_with_400_and_stores_nothing(role_service):
    count_before = len(role_service.list_roles())

    with pytest.raises(AppError) as exc_info:
        role_service.create_role({"name": "Rogue", "permissions": ["everything:all"]})

    assert exc_info.value.status == 400
    assert len(role_service.list_roles()) == count_before


def test_a_role_can_be_updated(role_service):
    created = role_service.create_role({"name": "Support", "permissions": ["users:read"]})

    updated = role_service.update_role(created["id"], {"name": "Support", "permissions": ["users:read", "users:write"]})

    assert updated["permissions"] == ["users:read", "users:write"]


def test_the_built_in_admin_role_cannot_be_edited(role_service):
    with pytest.raises(AppError) as exc_info:
        role_service.update_role("admin", {"name": "Admin", "permissions": ["users:read"]})

    assert exc_info.value.status == 409
    assert exc_info.value.code == "SYSTEM_ROLE_LOCKED"


def test_updating_an_unknown_role_returns_404(role_service):
    with pytest.raises(AppError) as exc_info:
        role_service.update_role("missing", {"name": "Anything", "permissions": ["users:read"]})

    assert exc_info.value.status == 404


def test_returned_roles_are_copies_so_callers_cannot_corrupt_the_store(role_service):
    role_service.list_roles()[0]["permissions"].clear()

    assert role_service.list_roles()[0]["permissions"] != []