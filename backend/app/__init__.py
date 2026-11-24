from flask import Flask

from app.api.errors import register_error_handlers
from app.api.routes import api
from app.domain.store import create_store
from app.services.access_service import AccessService
from app.services.audit_log import AuditLog
from app.services.role_service import RoleService
from app.services.user_service import UserService

MAX_BODY_BYTES = 100 * 1024


def create_app(store=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES

    store = create_store() if store is None else store
    audit = AuditLog(store)
    app.extensions["rbac"] = {
        "audit": audit,
        "access": AccessService(store, audit),
        "roles": RoleService(store),
        "users": UserService(store),
    }

    app.register_blueprint(api, url_prefix="/api")
    register_error_handlers(app)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app