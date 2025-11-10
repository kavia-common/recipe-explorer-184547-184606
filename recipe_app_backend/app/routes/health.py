from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health", "health", url_prefix="/", description="Health check routes")


@blp.route("/")
class Root(MethodView):
    def get(self):
        # Simple root response
        return {"message": "Recipe Explorer Backend"}


@blp.route("/health")
class HealthCheck(MethodView):
    def get(self):
        # Acceptance criteria: {status: 'ok'}
        return {"status": "ok"}
