"""
Pytest configuration and fixtures
"""
import os

# Default test environment before framework config loads
os.environ.setdefault("ENV", "test")
os.environ.setdefault("API_BASE_URL", "http://localhost:8080/v1")
os.environ.setdefault("GRAPHQL_ENDPOINT", "http://localhost:8080/graphql")
os.environ.setdefault("WEB_URL", "http://localhost:3000")

import pytest
import allure
import subprocess
import sys
from pathlib import Path

from framework.core.logger import Logger
from framework.core.config_manager import config
from framework.web.browser_manager import BrowserManager

ROOT_DIR = Path(__file__).resolve().parent


Logger.setup()


@pytest.fixture(scope="session", autouse=True)
def mock_servers():
    """Start mock API/web servers when not already running (skip with SKIP_MOCK_SERVERS=true)."""
    if os.getenv("SKIP_MOCK_SERVERS", "").lower() == "true":
        yield
        return

    from scripts.wait_for_mocks import wait_for_url

    def servers_ready() -> bool:
        try:
            wait_for_url("http://localhost:8080/health", timeout_seconds=1.0)
            wait_for_url("http://localhost:3000/health", timeout_seconds=1.0)
            return True
        except TimeoutError:
            return False

    if servers_ready():
        yield
        return

    api = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "tests/mocks/mock_api_server.py")],
        cwd=str(ROOT_DIR),
    )
    web = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "tests/mocks/mock_web_server.py")],
        cwd=str(ROOT_DIR),
    )
    started_by_fixture = True
    try:
        wait_for_url("http://localhost:8080/health")
        wait_for_url("http://localhost:3000/health")
        yield
    finally:
        if started_by_fixture:
            for process in (api, web):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for Allure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def session_browser_manager():
    """Shared browser process for smoke/regression tests — new context per test."""
    manager = BrowserManager()
    manager.launch_browser(
        browser_type=config.web.browser,
        headless=config.web.headless,
    )
    yield manager
    manager.close_browser()


@pytest.fixture(scope="session", autouse=True)
def setup_allure_environment():
    """Setup Allure environment properties."""
    from pathlib import Path

    allure_dir = Path(config.base.allure_results_dir)
    allure_dir.mkdir(parents=True, exist_ok=True)

    env_file = allure_dir / "environment.properties"
    with open(env_file, "w") as file_handle:
        file_handle.write(f"Environment={config.base.env}\n")
        file_handle.write(f"API_URL={config.api.api_base_url}\n")
        file_handle.write(f"Web_URL={config.web.web_url}\n")
        file_handle.write(f"Browser={config.web.browser}\n")

    yield


@pytest.fixture(autouse=True)
def attach_test_info(request):
    """Attach test information to Allure report."""
    test_title = request.node.name
    if request.node.function.__doc__:
        docstring = request.node.function.__doc__.strip()
        if docstring:
            test_title = docstring.split("\n")[0]

    allure.dynamic.title(test_title)

    if request.node.function.__doc__:
        allure.dynamic.description(request.node.function.__doc__)
    else:
        allure.dynamic.description(f"Test: {request.node.name}")

    if hasattr(request.node, "callspec") and request.node.callspec.params:
        params_str = ", ".join(
            f"{key}={value}" for key, value in request.node.callspec.params.items()
        )
        allure.dynamic.description_html(f"<b>Parameters:</b> {params_str}")

    yield
