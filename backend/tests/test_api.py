def call(client, method, path, user=None, body=None, raw=None):
    headers = {"X-User-Id": user} if user else {}
    if raw is not None:
        return client.open(path, method=method, data=raw, content_type="application/json", headers=headers)
    return client.open(path, method=method, json=body, headers=headers)


def test_admin_can_create_a_role_and_gets_201(client):
    response = call(client, "POST", "/api/roles", user="u-alice", body={"name": "Support", "permissions": ["users:read"]})

    assert response.status_code == 201
    assert response.get_json()["name"] == "Support"


def test_viewer_calling_create_role_directly_gets_403(client):
    response = call(client, "POST", "/api/roles", user="u-carol", body={"name": "Sneaky", "permissions": ["users:read"]})

    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "FORBIDDEN"


def test_viewer_cannot_escalate_by_assigning_themselves_admin(client):
    response = call(client, "PUT", "/api/users/u-carol/roles", user="u-carol", body={"role_ids": ["admin"]})
    assert response.status_code == 403

    users = call(client, "GET", "/api/users", user="u-alice").get_json()
    assert next(u for u in users if u["id"] == "u-carol")["role_ids"] == ["viewer"]


def test_authorization_runs_before_validation(client):
    response = call(client, "POST", "/api/roles", user="u-carol", raw="{not json")

    assert response.status_code == 403


def test_duplicate_role_name_returns_409_with_a_field_message(client):
    response = call(client, "POST", "/api/roles", user="u-alice", body={"name": "editor", "permissions": ["users:read"]})

    assert response.status_code == 409
    assert response.get_json()["error"]["details"][0]["field"] == "name"


def test_malformed_json_returns_400_not_a_crash(client):
    response = call(client, "POST", "/api/roles", user="u-alice", raw="{not json")

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_JSON"


def test_removing_the_last_admin_over_http_returns_409(client):
    response = call(client, "PUT", "/api/users/u-alice/roles", user="u-alice", body={"role_ids": ["viewer"]})

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "LAST_ADMIN"


def test_missing_user_header_returns_401(client):
    assert call(client, "GET", "/api/users").status_code == 401


def test_viewer_can_list_users_but_not_read_the_audit_log(client):
    assert call(client, "GET", "/api/users", user="u-carol").status_code == 200
    assert call(client, "GET", "/api/audit-log", user="u-carol").status_code == 403


def test_simulator_allowed_and_denied_attempts_appear_in_the_audit_log(client):
    assert call(client, "POST", "/api/actions/export_report", user="u-bob").status_code == 200
    assert call(client, "POST", "/api/actions/delete_user", user="u-carol").status_code == 403

    log = call(client, "GET", "/api/audit-log", user="u-dave").get_json()

    outcomes = {(e["user_id"], e["action"], e["outcome"]) for e in log}
    assert ("u-bob", "Export Report", "Allowed") in outcomes
    assert ("u-carol", "Delete User", "Denied") in outcomes


def test_demo_user_list_is_public_and_exposes_only_id_and_name(client):
    response = call(client, "GET", "/api/demo/users")

    assert response.status_code == 200
    assert all(set(u) == {"id", "name"} for u in response.get_json())


def test_unknown_route_is_404_and_wrong_method_is_405_in_the_same_error_shape(client):
    not_found = call(client, "GET", "/api/nope", user="u-alice")
    wrong_method = call(client, "DELETE", "/api/roles", user="u-alice")

    assert not_found.status_code == 404
    assert not_found.get_json()["error"]["code"] == "NOT_FOUND"
    assert wrong_method.status_code == 405


def test_oversized_body_is_rejected_with_413(client):
    response = call(client, "POST", "/api/roles", user="u-alice", raw="x" * (200 * 1024))

    assert response.status_code == 413


def test_unexpected_errors_return_a_generic_500_without_leaking_details(app):
    @app.get("/boom")
    def boom():
        raise RuntimeError("secret database password")

    response = app.test_client().get("/boom")

    assert response.status_code == 500
    assert response.get_json()["error"]["code"] == "INTERNAL_ERROR"
    assert "secret" not in response.get_data(as_text=True)



def test_a_role_manager_who_is_not_admin_cannot_promote_themselves_to_admin(client):
    created = call(
        client, "POST", "/api/roles", user="u-alice",
        body={"name": "RoleManager", "permissions": ["roles:manage", "users:read"]},
    ).get_json()
    call(client, "PUT", "/api/users/u-bob/roles", user="u-alice", body={"role_ids": [created["id"]]})

    response = call(client, "PUT", "/api/users/u-bob/roles", user="u-bob", body={"role_ids": ["admin"]})

    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "ADMIN_ROLE_RESTRICTED"
    users = call(client, "GET", "/api/users", user="u-alice").get_json()
    assert next(u for u in users if u["id"] == "u-bob")["role_ids"] == [created["id"]]


def test_me_returns_the_acting_users_permissions_and_requires_a_known_user(client):
    response = call(client, "GET", "/api/me", user="u-bob")

    assert response.status_code == 200
    assert "reports:export" in response.get_json()["permissions"]
    assert "users:delete" not in response.get_json()["permissions"]
    assert call(client, "GET", "/api/me").status_code == 401