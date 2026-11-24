from app.domain.permissions import ADMIN_ROLE_ID, PERMISSIONS, PROTECTED_ACTIONS
from app.domain.store import create_store


def test_every_protected_action_maps_to_a_known_permission():
    for action in PROTECTED_ACTIONS.values():
        assert action["permission"] in PERMISSIONS


def test_admin_role_is_locked_and_has_every_permission():
    store = create_store()
    admin = next(role for role in store["roles"] if role["id"] == ADMIN_ROLE_ID)
    assert admin["is_system"] is True
    assert set(admin["permissions"]) == set(PERMISSIONS)


def test_seed_users_only_reference_roles_that_exist():
    store = create_store()
    known_role_ids = {role["id"] for role in store["roles"]}
    for user in store["users"]:
        assert set(user["role_ids"]) <= known_role_ids


def test_each_store_is_independent():
    first = create_store()
    second = create_store()
    first["users"].clear()
    assert len(second["users"]) == 4