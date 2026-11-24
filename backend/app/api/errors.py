from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.errors import AppError

HTTP_ERROR_CODES = {
    404: ("NOT_FOUND", "Route not found."),
    405: ("METHOD_NOT_ALLOWED", "Method not allowed."),
    413: ("PAYLOAD_TOO_LARGE", "Request body is too large."),
}


def _error_response(status, code, message, details=None):
    body = {"code": code, "message": message}
    if details is not None:
        body["details"] = details
    return jsonify({"error": body}), status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return _error_response(err.status, err.code, err.message, err.details)

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        code, message = HTTP_ERROR_CODES.get(err.code, ("HTTP_ERROR", "Request could not be processed."))
        return _error_response(err.code or 500, code, message)

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Unhandled error")
        return _error_response(500, "INTERNAL_ERROR", "Something went wrong.")