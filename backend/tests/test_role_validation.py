import pytest

from app.domain.store import create_store
from app.errors import AppError
from app.validation.role_validation import validate_role_input


@pytest.fixture
def roles():
    return create_store()["roles"]


def test_valid_input_is_trimmed_deduplicated_and_returned_clean(roles):
    result = validate_role_input({"name": "  Support   Agent ", "permissions": ["users:read", "users:read"]}, roles)
    assert result == {"name": "Support Agent", "permissions": ["users:read"]}


def test_duplicate_role_name_is_rejected_case_insensitively_with_409(roles):
    with pytest.raises(AppError) as exc_info:
        validate_role_input({"name": "editor", "permissions": ["users:read"]}, roles)
    assert exc_info.value.status == 409
    assert exc_info.value.code == "DUPLICATE_ROLE_NAME"


def test_a_role_may_keep_its_own_name_when_updating(roles):
    result = validate_role_input({"name": "Editor", "permissions": ["users:read"]}, roles, ignore_role_id="editor")
    assert result["name"] == "Editor"


def test_empty_permissions_list_is_rejected_with_a_field_message(roles):
    with pytest.raises(AppError) as exc_info:
        validate_role_input({"name": "Ghost", "permissions": []}, roles)
    assert exc_info.value.status == 400
    assert {"field": "permissions", "message": "Select at least one permission."} in exc_info.value.details


def test_unknown_permission_is_rejected(roles):
    with pytest.raises(AppError) as exc_info:
        validate_role_input({"name": "Rogue", "permissions": ["users:raed"]}, roles)
    assert exc_info.value.status == 400
    assert exc_info.value.code == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    "bad_body",
    [None, [], "text", 42, {"name": 123, "permissions": "users:read"}],
)
def test_malformed_bodies_are_rejected_not_crashed_on(roles, bad_body):
    with pytest.raises(AppError) as exc_info:
        validate_role_input(bad_body, roles)
    assert exc_info.value.status == 400


@pytest.mark.parametrize("bad_name", ["<script>", "9lives", "A", "x" * 31])
def test_invalid_names_are_rejected(roles, bad_name):
    with pytest.raises(AppError) as exc_info:
        validate_role_input({"name": bad_name, "permissions": ["users:read"]}, roles)
    assert exc_info.value.details[0]["field"] == "name"


def test_all_field_errors_are_reported_together(roles):
    with pytest.raises(AppError) as exc_info:
        validate_role_input({}, roles)
    assert {d["field"] for d in exc_info.value.details} == {"name", "permissions"}