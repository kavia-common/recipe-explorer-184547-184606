from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request

from ..schemas import AuthLoginSchema, AuthTokenSchema
from ..storage import create_session, get_session, delete_session

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/auth",
    description="Basic user session management (stub).",
)


@blp.route("/login")
class Login(MethodView):
    # PUBLIC_INTERFACE
    @blp.arguments(AuthLoginSchema)
    @blp.response(200, AuthTokenSchema)
    def post(self, json_data):
        """
        summary: Login (stub)
        description: Accepts username/password and returns a session token. No real authentication; for demo only.
        """
        username = json_data["username"]
        # password is ignored in stub
        token = create_session(user_id=username, user_name=username)
        return {"success": True, "token": token, "user": {"id": username, "name": username}}


@blp.route("/logout")
class Logout(MethodView):
    # PUBLIC_INTERFACE
    @blp.response(200, example={"success": True})
    def post(self):
        """
        summary: Logout (stub)
        description: Invalidates the provided session token.
        """
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            abort(400, message="Missing Authorization Bearer token")
        delete_session(token)
        return {"success": True}


@blp.route("/me")
class Me(MethodView):
    # PUBLIC_INTERFACE
    @blp.response(200)
    def get(self):
        """
        summary: Current user (stub)
        description: Returns user info for the provided session token, if valid.
        """
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            abort(401, message="Unauthorized")
        sess = get_session(token)
        if not sess:
            abort(401, message="Unauthorized")
        return {"success": True, "user": {"id": sess["user_id"], "name": sess["name"]}}
