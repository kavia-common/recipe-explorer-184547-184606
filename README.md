# Recipe Explorer Backend

Flask REST API for browsing, searching, and managing recipes.

## Quick start

- Install dependencies (handled by CI using requirements.txt)
- Start the server:
  - python recipe_app_backend/run.py
- The service runs on: http://localhost:3001
- API docs (Swagger UI): http://localhost:3001/docs

## Health

GET /health
- 200 -> {"status":"ok"}

## Recipes

Base path: /recipes

- GET /recipes
  - Query params:
    - q: search text across title and ingredients
    - ingredient: filter recipes that include the ingredient
    - page: page number (default 1)
    - page_size: results per page (default 10, max 100)
  - 200 -> {"success": true, "data": [...], "meta": {...}}

- POST /recipes
  - Body:
    {
      "title": "Avocado Toast",
      "description": "Simple breakfast",
      "ingredients": ["bread", "avocado", "salt"],
      "instructions": "Toast bread, mash avocado, season.",
      "tags": ["breakfast","quick"]
    }
  - 201 -> {"success": true, "data": {...}}

- GET /recipes/<id>
  - 200 -> {"success": true, "data": {...}}
  - 404 -> {"success": false, "error": {...}}

- PUT /recipes/<id>
  - Body: any updatable fields from POST
  - 200 -> {"success": true, "data": {...}}
  - 404 -> {"success": false, "error": {...}}

- DELETE /recipes/<id>
  - 204 -> {"success": true}
  - 404 -> {"success": false, "error": {...}}

## Auth (stubs)

Base path: /auth

- POST /auth/login
  - Body: {"username":"alice","password":"secret"}
  - 200 -> {"success": true, "token":"...", "user":{"id":"alice","name":"alice"}}

- POST /auth/logout
  - Header: Authorization: Bearer <token>
  - 200 -> {"success": true}

- GET /auth/me
  - Header: Authorization: Bearer <token>
  - 200 -> {"success": true, "user": {...}}
  - 401 -> {"success": false, "error": {...}}

## Data storage

- Uses a local JSON store at data/recipes.json by default.
- Override with environment variable:
  - RECIPES_STORE_PATH=/path/to/recipes.json

## Error handling

- Errors return JSON:
  {
    "success": false,
    "error": {"code": 404, "status": "Not Found", "message": "Recipe not found"}
  }

## CORS

- Enabled for all routes and origins for development convenience.

## Environment variables

- See .env.example for available configurations.