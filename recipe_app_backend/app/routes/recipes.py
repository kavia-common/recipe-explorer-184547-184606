from flask_smorest import Blueprint, abort
from flask.views import MethodView
from typing import Any, Dict

from ..schemas import (
    PaginationQuerySchema,
    RecipeCreateSchema,
    RecipeUpdateSchema,
    RecipeSchema,
)
from ..storage import list_recipes, get_recipe, create_recipe, update_recipe, delete_recipe

blp = Blueprint(
    "Recipes",
    "recipes",
    url_prefix="/recipes",
    description="Recipe browsing, searching, and management endpoints",
)


@blp.route("")
class RecipesCollection(MethodView):
    """Collection routes for listing and creating recipes."""

    # PUBLIC_INTERFACE
    @blp.arguments(PaginationQuerySchema, location="query")
    @blp.response(200, RecipeSchema(many=True), description="List of recipes")
    @blp.alt_response(200, example={"data": [], "meta": {}}, description="Wrapped response")
    def get(self, args: Dict[str, Any]):
        """
        summary: List recipes
        description: Returns a paginated list of recipes with optional search and ingredient filtering.
        """
        q = args.get("q")
        ingredient = args.get("ingredient")
        page = args.get("page", 1)
        page_size = args.get("page_size", 10)
        items, meta = list_recipes(q=q, ingredient=ingredient, page=page, page_size=page_size)
        return {"success": True, "data": items, "meta": meta}

    # PUBLIC_INTERFACE
    @blp.arguments(RecipeCreateSchema)
    @blp.response(201, RecipeSchema, description="Created recipe")
    def post(self, json_data: Dict[str, Any]):
        """
        summary: Create a recipe
        description: Creates a new recipe.
        """
        created = create_recipe(json_data)
        return {"success": True, "data": created}


@blp.route("/<int:recipe_id>")
class RecipeItem(MethodView):
    """Item routes for retrieving, updating, and deleting a recipe."""

    # PUBLIC_INTERFACE
    @blp.response(200, RecipeSchema, description="Recipe detail")
    def get(self, recipe_id: int):
        """
        summary: Get recipe
        description: Retrieve a recipe by ID.
        """
        recipe = get_recipe(recipe_id)
        if not recipe:
            abort(404, message="Recipe not found")
        return {"success": True, "data": recipe}

    # PUBLIC_INTERFACE
    @blp.arguments(RecipeUpdateSchema)
    @blp.response(200, RecipeSchema, description="Updated recipe")
    def put(self, json_data: Dict[str, Any], recipe_id: int):
        """
        summary: Update recipe
        description: Update an existing recipe by ID.
        """
        updated = update_recipe(recipe_id, json_data)
        if not updated:
            abort(404, message="Recipe not found")
        return {"success": True, "data": updated}

    # PUBLIC_INTERFACE
    @blp.response(204)
    def delete(self, recipe_id: int):
        """
        summary: Delete recipe
        description: Delete a recipe by ID.
        """
        ok = delete_recipe(recipe_id)
        if not ok:
            abort(404, message="Recipe not found")
        # No content, but keep consistent envelope if needed by clients:
        return {"success": True}
