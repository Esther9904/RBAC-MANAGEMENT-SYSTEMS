"""Acceptance tests for the three scenarios the brief requires under "Code Quality & Testing".

Each test drives the real Flask app over HTTP, exactly as the React UI does.
Finer-grained unit tests for the same rules live in the other test files (see README).
"""

ALICE, BOB, CAROL, DAVE = "u-alice", "u-bob", "u-carol", "u-dave"


def as_user(user_id):
    return {"X-User-Id": user_id}


def list_roles(client):
    return client.get("/api/roles", headers=as_user(ALICE)).get_json()


def latest_audit_entry(client):
    return client.get("/api/audit-log", headers=as_user(DAVE)).get_json()[0]


# --- Scenario 1 -------------------------------------------------------------------------------
# Brief: "A user with the required permission successfully performing a protected action."


def test_scenario_1_user_with_the_required_permission_succeeds(client):
    # Bob is an Editor, and Editors hold reports:export.
    response = client.post("/api/actions/export_report", headers=as_user(BOB))

    assert response.status_code == 200
    assert "Export Report completed" in response.get_json()["message"]

    entry = latest_audit_entry(client)
    assert (entry["user_id"], entry["action"], entry["outcome"]) == (BOB, "Export Report", "Allowed")


# --- Scenario 2 -------------------------------------------------------------------------------
# Brief: "An unauthorized user being blocked (403 / denied) when attempting a restricted action."


def test_scenario_2_unauthorized_user_is_blocked_with_403_and_logged(client):
    # Carol is a Viewer, and Viewers do not hold users:delete.
    response = client.post("/api/actions/delete_user", headers=as_user(CAROL))

    assert response.status_code == 403
    error = response.get_json()["error"]
    assert error["code"] == "FORBIDDEN"
    assert "users:delete" in error["message"]

    entry = latest_audit_entry(client)
    assert (entry["user_id"], entry["action"], entry["outcome"]) == (CAROL, "Delete User", "Denied")


def test_scenario_2_restriction_is_enforced_by_the_server_not_just_the_ui(client):
    # Skip the UI completely: call a protected endpoint directly as a Viewer.
    roles_before = list_roles(client)

    response = client.post(
        "/api/roles",
        json={"name": "Sneaky", "permissions": ["users:read"]},
        headers=as_user(CAROL),
    )

    assert response.status_code == 403
    assert list_roles(client) == roles_before  # and nothing was created


# --- Scenario 3 -------------------------------------------------------------------------------
# Brief: "An invalid/malformed input (e.g., duplicate role name or invalid permission)
# handled gracefully."


def test_scenario_3_duplicate_role_name_is_handled_gracefully(client):
    roles_before = list_roles(client)

    response = client.post(
        "/api/roles",
        json={"name": "editor", "permissions": ["users:read"]},  # "Editor" already exists
        headers=as_user(ALICE),
    )

    assert response.status_code == 409
    error = response.get_json()["error"]
    assert error["code"] == "DUPLICATE_ROLE_NAME"
    assert error["details"] == [{"field": "name", "message": "A role with this name already exists."}]
    assert list_roles(client) == roles_before


def test_scenario_3_invalid_permission_is_handled_gracefully(client):
    roles_before = list_roles(client)

    response = client.post(
        "/api/roles",
        json={"name": "Typo", "permissions": ["users:raed"]},  # not in the permission catalogue
        headers=as_user(ALICE),
    )

    assert response.status_code == 400
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "permissions"
    assert list_roles(client) == roles_before


def test_scenario_3_malformed_json_is_handled_gracefully(client):
    response = client.post(
        "/api/roles",
        data="{this is not json",
        content_type="application/json",
        headers=as_user(ALICE),
    )

    assert response.status_code == 400  # a clear client error, not a 500 crash
    assert response.get_json()["error"]["code"] == "INVALID_JSON"