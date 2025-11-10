"""
In-memory and JSON file-backed storage utilities for recipes and simple user session store.
This module abstracts storage operations so the rest of the app can remain agnostic of storage implementation.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

_STORAGE_FILE = os.environ.get("RECIPES_STORE_PATH", "data/recipes.json")
os.makedirs(os.path.dirname(_storage_file) if (_storage_file := _STORAGE_FILE) and "/" in _STORAGE_FILE else "data", exist_ok=True)

_lock = threading.RLock()


def _read_file() -> Dict:
    """Read JSON content from storage file, returning a default structure if not present or invalid."""
    if not os.path.exists(_STORAGE_FILE):
        return {"recipes": [], "next_id": 1}
    try:
        with open(_STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "recipes" not in data or "next_id" not in data:
                return {"recipes": [], "next_id": 1}
            return data
    except Exception:
        return {"recipes": [], "next_id": 1}


def _write_file(data: Dict) -> None:
    """Persist JSON content to storage file safely."""
    tmp_path = f"{_STORAGE_FILE}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, _STORAGE_FILE)


def _normalize_recipe(recipe: Dict) -> Dict:
    """Ensure recipe contains expected fields and types."""
    recipe.setdefault("id", None)
    recipe.setdefault("title", "")
    recipe.setdefault("description", "")
    recipe.setdefault("ingredients", [])
    recipe.setdefault("instructions", "")
    recipe.setdefault("tags", [])
    recipe.setdefault("created_at", int(time.time()))
    recipe.setdefault("updated_at", int(time.time()))
    return recipe


# PUBLIC_INTERFACE
def list_recipes(q: Optional[str] = None, ingredient: Optional[str] = None, page: int = 1, page_size: int = 10) -> Tuple[List[Dict], Dict]:
    """List recipes with optional search and pagination."""
    with _lock:
        data = _read_file()
        recipes = data["recipes"]

        # Filter by q across title and ingredients
        if q:
            ql = q.lower()
            recipes = [
                r for r in recipes
                if ql in (r.get("title") or "").lower()
                or any(ql in (ing or "").lower() for ing in r.get("ingredients", []))
            ]
        # Filter by ingredient
        if ingredient:
            il = ingredient.lower()
            recipes = [
                r for r in recipes
                if any(il in (ing or "").lower() for ing in r.get("ingredients", []))
            ]

        total = len(recipes)
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        start = (page - 1) * page_size
        end = start + page_size
        items = recipes[start:end]

        total_pages = (total + page_size - 1) // page_size if page_size else 1
        meta = {
            "total": total,
            "total_pages": total_pages,
            "first_page": 1,
            "last_page": total_pages if total_pages > 0 else 1,
            "page": page,
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if end < total else None,
            "page_size": page_size,
        }
        return items, meta


# PUBLIC_INTERFACE
def get_recipe(recipe_id: int) -> Optional[Dict]:
    """Get a single recipe by ID."""
    with _lock:
        data = _read_file()
        for r in data["recipes"]:
            if r.get("id") == recipe_id:
                return r
        return None


# PUBLIC_INTERFACE
def create_recipe(recipe: Dict) -> Dict:
    """Create a new recipe and return it."""
    with _lock:
        data = _read_file()
        recipe = _normalize_recipe(recipe)
        recipe["id"] = int(data.get("next_id", 1))
        now = int(time.time())
        recipe["created_at"] = now
        recipe["updated_at"] = now
        data["recipes"].append(recipe)
        data["next_id"] = recipe["id"] + 1
        _write_file(data)
        return recipe


# PUBLIC_INTERFACE
def update_recipe(recipe_id: int, updates: Dict) -> Optional[Dict]:
    """Update an existing recipe by ID; returns updated recipe or None if not found."""
    with _lock:
        data = _read_file()
        for i, r in enumerate(data["recipes"]):
            if r.get("id") == recipe_id:
                r.update({k: v for k, v in updates.items() if k in {"title", "description", "ingredients", "instructions", "tags"}})
                r["updated_at"] = int(time.time())
                data["recipes"][i] = _normalize_recipe(r)
                _write_file(data)
                return data["recipes"][i]
        return None


# PUBLIC_INTERFACE
def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe by ID; returns True if deleted."""
    with _lock:
        data = _read_file()
        before = len(data["recipes"])
        data["recipes"] = [r for r in data["recipes"] if r.get("id") != recipe_id]
        if len(data["recipes"]) < before:
            _write_file(data)
            return True
        return False


# Simple in-memory session store for auth stubs
_sessions: Dict[str, Dict] = {}
_session_lock = threading.RLock()


# PUBLIC_INTERFACE
def create_session(user_id: str, user_name: str) -> str:
    """Create a new session token for a user and return the token."""
    token = f"token_{user_id}_{int(time.time())}"
    with _session_lock:
        _sessions[token] = {"user_id": user_id, "name": user_name, "created_at": int(time.time())}
    return token


# PUBLIC_INTERFACE
def get_session(token: str) -> Optional[Dict]:
    """Get session data by token."""
    with _session_lock:
        return _sessions.get(token)


# PUBLIC_INTERFACE
def delete_session(token: str) -> None:
    """Invalidate a session token."""
    with _session_lock:
        _sessions.pop(token, None)
