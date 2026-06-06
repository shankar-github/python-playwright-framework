#!/usr/bin/env python3
"""Static mock web server for Playwright tests with data-testid locators."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def dashboard_page(query: dict) -> str:
    first_name = query.get("first_name", ["Test User"])[0]
    return f"""
<!DOCTYPE html><html><body>
  <div data-testid="welcome-message">Welcome back, {first_name}</div>
  <div data-testid="success-message">Welcome to the platform</div>
</body></html>
"""


STATIC_PAGES = {
    "/": """
<!DOCTYPE html><html><body>
  <h1>Home</h1>
  <a data-testid="products-link" href="/products">Products</a>
  <a data-testid="about-link" href="/about">About</a>
</body></html>
""",
    "/login": """
<!DOCTYPE html><html><body>
  <form action="/dashboard" method="GET">
    <input data-testid="email-input" name="email" />
    <input data-testid="password-input" type="password" name="password" />
    <input data-testid="first-name-input" name="first_name" type="hidden" value="" />
    <button data-testid="login-submit" type="submit">Login</button>
  </form>
  <script>
    document.querySelector('form').addEventListener('submit', function () {
      var email = document.querySelector('[data-testid="email-input"]').value || 'user@example.com';
      var hidden = document.querySelector('[data-testid="first-name-input"]');
      hidden.value = email.split('@')[0].replace(/[^a-zA-Z]/g, ' ') || 'Test User';
    });
  </script>
</body></html>
""",
    "/register": """
<!DOCTYPE html><html><body>
  <form action="/dashboard" method="GET">
    <input data-testid="first-name-input" name="first_name" />
    <input data-testid="last-name-input" name="last_name" />
    <input data-testid="email-input" name="email" />
    <input data-testid="password-input" type="password" name="password" />
    <input data-testid="confirm-password-input" type="password" name="confirm_password" />
    <button data-testid="register-submit" type="submit">Register</button>
  </form>
</body></html>
""",
    "/products": """
<!DOCTYPE html><html><body>
  <div data-testid="product-list">
    <div data-testid="product-item">
      <span data-testid="product-name">Sample Product</span>
    </div>
  </div>
  <button data-testid="add-to-cart-button">Add to Cart</button>
  <span data-testid="cart-badge">1</span>
  <input data-testid="search-input" />
  <button data-testid="search-button">Search</button>
</body></html>
""",
    "/contact": """
<!DOCTYPE html><html><body>
  <form><button data-testid="contact-submit" type="submit">Send</button></form>
  <div data-testid="error-message">Name is required</div>
  <div data-testid="error-message">Email is required</div>
</body></html>
""",
    "/upload": """
<!DOCTYPE html><html><body>
  <input data-testid="file-input" type="file" />
  <button data-testid="upload-button">Upload</button>
  <div data-testid="upload-success" style="display:block">Upload successful</div>
</body></html>
""",
    "/about": """
<!DOCTYPE html><html><body><h1>About</h1></body></html>
""",
}


class MockWebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/dashboard":
            content = dashboard_page(query)
            status = 200
        elif path in STATIC_PAGES:
            content = STATIC_PAGES[path]
            status = 200
        else:
            content = "<html><body><h1>404</h1></body></html>"
            status = 404

        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "0.0.0.0", port: int = 3000):
    server = ThreadingHTTPServer((host, port), MockWebHandler)
    print(f"Mock web server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
