from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

from .routes.health import blp as health_blp
from .routes.recipes import blp as recipes_blp
from .routes.auth import blp as auth_blp


def create_app() -> Flask:
    """
    Flask application factory that configures CORS, OpenAPI docs, blueprints,
    and consistent JSON error handling.
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app, resources={r"/*": {"origins": "*"}})

    # OpenAPI / Swagger configuration
    app.config["API_TITLE"] = "Recipe Explorer API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)

    # Register blueprints
    api.register_blueprint(health_blp)
    api.register_blueprint(recipes_blp)
    api.register_blueprint(auth_blp)

    # JSON error handling
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        response = {
            "success": False,
            "error": {"code": e.code, "status": e.name, "message": e.description},
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        response = {
            "success": False,
            "error": {"code": 500, "status": "Internal Server Error", "message": str(e)},
        }
        return jsonify(response), 500

    return app


# Create default app instance for compatibility with run.py
app = create_app()
