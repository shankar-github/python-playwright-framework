#!/usr/bin/env python3
"""REST + GraphQL mock API with optional Postgres sync for CI and local testing."""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from tests.mocks import db_sync

USERS: Dict[int, Dict[str, Any]] = {}
PRODUCTS: Dict[int, Dict[str, Any]] = {}
_NEXT_USER_ID = 1
_NEXT_PRODUCT_ID = 1


def _next_user_id() -> int:
    global _NEXT_USER_ID
    value = _NEXT_USER_ID
    _NEXT_USER_ID += 1
    return value


def _next_product_id() -> int:
    global _NEXT_PRODUCT_ID
    value = _NEXT_PRODUCT_ID
    _NEXT_PRODUCT_ID += 1
    return value


class MockAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_json(self, status: int, payload: Any):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._send_json(200, {"status": "ok"})

        if parsed.path == "/v1/users":
            query = parse_qs(parsed.query)
            page = int(query.get("page", ["1"])[0])
            limit = int(query.get("limit", ["10"])[0])
            users = list(USERS.values())
            return self._send_json(200, {
                "data": users[(page - 1) * limit: page * limit],
                "total": len(users),
                "page": page,
                "limit": limit,
            })

        match = re.match(r"^/v1/users/(\d+)$", parsed.path)
        if match:
            user_id = int(match.group(1))
            user = USERS.get(user_id)
            if user is None:
                return self._send_json(404, {"error": "User not found"})
            return self._send_json(200, user)

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/graphql":
            return self._handle_graphql()

        if self.path == "/v1/users":
            payload = self._read_json()
            if not payload.get("email"):
                return self._send_json(422, {"error": "Validation failed", "fields": ["email"]})

            db_id = db_sync.insert_user(payload)
            user_id = db_id if db_id is not None else _next_user_id()
            user = {"id": user_id, **payload}
            USERS[user_id] = user
            return self._send_json(201, user)

        self._send_json(404, {"error": "Not found"})

    def do_PUT(self):
        match = re.match(r"^/v1/users/(\d+)$", self.path)
        if not match:
            return self._send_json(404, {"error": "Not found"})
        user_id = int(match.group(1))
        if user_id not in USERS:
            return self._send_json(404, {"error": "User not found"})
        payload = self._read_json()
        USERS[user_id].update(payload)
        USERS[user_id]["id"] = user_id
        return self._send_json(200, USERS[user_id])

    def do_PATCH(self):
        return self.do_PUT()

    def do_DELETE(self):
        match = re.match(r"^/v1/users/(\d+)$", self.path)
        if not match:
            return self._send_json(404, {"error": "Not found"})
        user_id = int(match.group(1))
        if user_id not in USERS:
            return self._send_json(404, {"error": "User not found"})
        del USERS[user_id]
        db_sync.delete_user(user_id)
        self.send_response(204)
        self.end_headers()

    def _handle_graphql(self):
        payload = self._read_json()
        query = payload.get("query", "")
        variables = payload.get("variables") or {}

        if "createProduct" in query:
            product_input = variables.get("input", {})
            db_id = db_sync.insert_product(product_input)
            product_id = db_id if db_id is not None else _next_product_id()
            product = {
                "id": str(product_id),
                "name": product_input.get("name"),
                "description": product_input.get("description"),
                "price": product_input.get("price"),
                "sku": product_input.get("sku"),
                "category": product_input.get("category"),
                "stock": product_input.get("stock", 0),
                "createdAt": "2024-01-01T00:00:00Z",
            }
            PRODUCTS[product_id] = product
            return self._send_json(200, {"data": {"createProduct": product}})

        if "GetProduct" in query or "product(id" in query:
            product_id = int(variables.get("id"))
            product = PRODUCTS.get(product_id) or db_sync.get_product(product_id)
            if product and product_id not in PRODUCTS:
                PRODUCTS[product_id] = product
            return self._send_json(200, {"data": {"product": product}})

        if "GetProducts" in query or "products(" in query:
            items: List[Dict[str, Any]] = list(PRODUCTS.values())
            return self._send_json(200, {"data": {"products": items}})

        if "updateProduct" in query:
            product_id = int(variables.get("id"))
            update_input = variables.get("input", {})
            product = PRODUCTS.get(product_id, {"id": str(product_id)})
            product.update(update_input)
            product["id"] = str(product_id)
            PRODUCTS[product_id] = product
            return self._send_json(200, {"data": {"updateProduct": product}})

        if "deleteProduct" in query:
            product_id = int(variables.get("id"))
            PRODUCTS.pop(product_id, None)
            db_sync.delete_product(product_id)
            return self._send_json(200, {"data": {"deleteProduct": {"success": True, "message": "Deleted"}}})

        if "nonExistentField" in query or "invalidField" in query:
            return self._send_json(200, {"errors": [{"message": "Cannot query field"}]})

        return self._send_json(200, {"data": {}})


def run(host: str = "0.0.0.0", port: int = 8080):
    server = ThreadingHTTPServer((host, port), MockAPIHandler)
    print(f"Mock API server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
