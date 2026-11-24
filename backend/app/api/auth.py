from functools import wraps

from flask import current_app, request

ACTOR_HEADER = "X-User-Id"


def require_permission(permission, action=None, log_allowed=True):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            access = current_app.extensions["rbac"]["access"]
            access.authorize(
                request.headers.get(ACTOR_HEADER),
                permission,
                action=action,
                log_allowed=log_allowed,
            )
            return view(*args, **kwargs)

        return wrapper

    return decorator