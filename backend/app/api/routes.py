from flask import Blueprint, current_app, jsonify, request

from app.api.auth import ACTOR_HEADER, require_permission
from app.domain.permissions import PERMISSIONS, PROTECTED_ACTIONS
from app.errors import AppError

api = Blueprint("api", __name__)


def _services():
    return current_app.extensions["rbac"]


def _read_json():
    if not request.get_data():
        return None
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise AppError(400, "INVALID_JSON", "Request body is not valid JSON.")
    return data


@api.get("/meta")
def get_meta():
    return jsonify({"permissions": list(PERMISSIONS), "actions": dict(PROTECTED_ACTIONS)})


@api.get("/demo/users")
def get_demo_users():
    return jsonify(_services()["users"].list_for_switcher())


@api.get("/users")
@require_permission("users:read", action="List users", log_allowed=False)
def list_users():
    return jsonify(_services()["users"].list_users())


@api.put("/users/<user_id>/roles")
@require_permission("roles:manage", action="Assign user roles")
def assign_user_roles(user_id):
    actor_id = request.headers.get(ACTOR_HEADER)
    return jsonify(_services()["users"].assign_roles(user_id, _read_json(), actor_id))


@api.get("/roles")
@require_permission("users:read", action="List roles", log_allowed=False)
def list_roles():
    return jsonify(_services()["roles"].list_roles())


@api.post("/roles")
@require_permission("roles:manage", action="Create role")
def create_role():
    return jsonify(_services()["roles"].create_role(_read_json())), 201


@api.put("/roles/<role_id>")
@require_permission("roles:manage", action="Update role")
def update_role(role_id):
    return jsonify(_services()["roles"].update_role(role_id, _read_json()))


@api.post("/actions/<action_key>")
def perform_action(action_key):
    result = _services()["access"].perform_action(request.headers.get(ACTOR_HEADER), action_key)
    return jsonify(result)


@api.get("/audit-log")
@require_permission("audit:read", action="View audit log", log_allowed=False)
def get_audit_log():
    return jsonify(_services()["audit"].list_entries())