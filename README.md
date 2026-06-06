# Unified Test Automation Framework

A production-oriented Python test automation framework for **Web UI**, **Mobile UI** (Android & iOS), **API** (REST + GraphQL), and **Database** testing — with self-contained mock servers for local and CI execution.

## Architecture Overview

The framework uses a **layered architecture** with clear separation between tests, domain abstractions, clients, and infrastructure:

```
automation_framework/
├── framework/                  # Reusable framework code
│   ├── core/                   # BaseTest, ConfigManager, Logger
│   ├── api/                    # REST/GraphQL clients, services, validators
│   ├── web/                    # BrowserManager, BasePage, page objects
│   ├── mobile/                 # AppiumManager, BaseScreen, screen objects
│   ├── db/                     # DB clients, repositories, validators
│   ├── integration/            # BaseIntegrationTest (API + Web + DB)
│   ├── utils/                  # Assertions, test data, redaction, UI retry
│   └── reporting/              # TestResultManager, StepContext
├── tests/                      # Scenario tests only — no wrapper base classes
│   ├── api/ web/ mobile/ db/ integration/ core/ utils/ reporting/
│   └── mocks/                  # Self-contained mock API & web servers
├── config/                     # config_{env}.yaml examples
├── scripts/                    # DB init, mock server helpers
├── test_data/                  # YAML/JSON test data (gitignored)
└── reports/                    # Allure results, traces, videos
```

**Key design principle:** Base test classes live in `framework/`. Tests inherit directly from the appropriate base and use **factory methods** for domain objects — not raw clients or locators in test bodies.

| Layer | Base class | Domain abstraction | Factory |
|-------|------------|-------------------|---------|
| API | `BaseAPITest` | `framework/api/services/` | `self.api_service(UsersAPI)` |
| Web | `BaseWebTest` | `framework/web/pages/` | `self.page_object(LoginPage)` |
| Mobile | `BaseMobileTest` | `framework/mobile/screens/` | `self.screen_object(LoginScreen)` |
| DB | `BaseDBTest` | `framework/db/repositories/` | `self.repository(UsersRepository)` |
| E2E | `BaseIntegrationTest` | All of the above | All factories |

## Features

- **Multi-layer testing**: Web, Mobile, API, GraphQL, DB, and integration/E2E
- **Page / Screen / Service / Repository patterns**: Domain logic stays out of tests and base classes
- **Self-contained mocks**: Built-in mock API and web servers — no external URLs required for CI
- **Parallel execution**: pytest-xdist with parallel-safe test data generation
- **Smoke browser pooling**: Session-scoped browser with per-test context for `@pytest.mark.smoke`
- **Allure reporting**: Steps, screenshots, Playwright traces, optional video on failure
- **Sensitive data redaction**: Passwords, tokens, and headers masked in logs and reports
- **JSON Schema validation**: `jsonschema`-backed response validation
- **Retry logic**: Idempotent HTTP retries, UI retry decorator, CI-level reruns
- **CI/CD ready**: GitHub Actions, GitLab CI, Jenkins, Docker Compose
- **Environment management**: `.env` + optional YAML per environment

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Docker (optional, for Postgres + mock services)

### Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps
```

### Configuration

```bash
cp .env.example .env
cp config/config_test.yaml.example config/config_test.yaml   # for ENV=test
# Edit .env for your target environment (dev, staging, etc.)
```

Default `.env.example` points to **local mock servers** (`localhost:8080` API, `localhost:3000` web).

### Run with mock servers (no external dependencies)

```bash
# Start mocks (API on :8080, Web on :3000)
bash scripts/start_mock_servers.sh &

# Run tests
export ENV=test
pytest -m "smoke and not smoke_db and not smoke_e2e and not smoke_mobile" -v
pytest -m "api and not graphql" -n auto
pytest -m web -n auto
```

### Run against real environments

Set URLs and credentials in `.env` or `config/config_{env}.yaml`:

```bash
ENV=dev pytest -m api
ENV=staging pytest -m regression
```

## Running Tests

```bash
# By layer
pytest -m api
pytest -m web
pytest -m mobile
pytest -m db
pytest -m integration

# By scope
pytest -m "smoke and not smoke_db and not smoke_e2e and not smoke_mobile"
pytest -m smoke_db          # requires Postgres + MOCK_DB_SYNC=true
pytest -m smoke_e2e         # full-stack integration smoke
pytest -m regression

# Parallel + reruns
pytest -n auto --reruns 2

# Coverage
pytest -m api --cov=framework --cov-report=html

# Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Test markers

| Marker | Description |
|--------|-------------|
| `api`, `rest`, `graphql` | API test categories |
| `web`, `mobile` | UI test categories |
| `db`, `integration`, `e2e` | Data and cross-layer tests |
| `smoke` | Fast API/web checks against mocks only (no DB/Appium) |
| `smoke_db` | Smoke tests requiring Postgres + `MOCK_DB_SYNC=true` |
| `smoke_e2e` | Full-stack smoke (API + DB + web) |
| `smoke_mobile` | Mobile smoke (requires Appium) |
| `regression` | Full regression suite |
| `android`, `ios` | Mobile platform filters |

## Writing Tests

Inherit from the framework base for your layer. Use **page objects, services, and repositories** — not raw selectors or HTTP calls in tests.

### Web UI (Page Object Model)

```python
from framework.web.base_web_test import BaseWebTest
from framework.web.pages import LoginPage
from framework.utils.assertions import hard_assert

@pytest.mark.web
@pytest.mark.smoke
class TestLogin(BaseWebTest):
    def test_user_login(self):
        login_page = self.page_object(LoginPage)

        with self.step("Log in with valid credentials"):
            login_page.open()
            login_page.login("user@example.com", "SecurePass123!")

        with self.step("Verify dashboard"):
            login_page.wait_for_dashboard()
            welcome = login_page.get_welcome_message()
            hard_assert.assert_string_contains(welcome, "Welcome", "Should reach dashboard")
```

Locators live in page objects using **`data-testid`** and Playwright role APIs — not CSS/XPath in tests.

### API (Service layer)

```python
from framework.api.base_api_test import BaseAPITestWithDB
from framework.api.services import UsersAPI
from framework.utils.test_data import test_data

@pytest.mark.api
class TestUsers(BaseAPITestWithDB):
    def test_create_user(self):
        users = self.api_service(UsersAPI)
        user_data = test_data.generate_user_data()

        with self.step("Create user via API"):
            created = users.create(user_data)

        with self.step("Validate in database"):
            users.validate_user_exists_in_db(created["id"])

        with self.step("Cleanup"):
            users.delete(created["id"])
```

Use `BaseAPITest` for pure API tests without DB. Use `BaseAPITestWithDB` only when DB validation is required.

### Integration / E2E

```python
from framework.integration.base_integration_test import BaseIntegrationTest
from framework.api.services import UsersAPI
from framework.web.pages import LoginPage

@pytest.mark.integration
@pytest.mark.e2e
class TestRegistrationFlow(BaseIntegrationTest):
    def test_api_to_ui_login(self):
        users = self.api_service(UsersAPI)
        login_page = self.page_object(LoginPage)
        user_data = test_data.generate_user_data()

        with self.step("Create user via API"):
            users.create(user_data)

        with self.step("Log in via UI"):
            login_page.open()
            login_page.login(user_data["email"], user_data["password"])
```

## Framework Components

### Core
- **`BaseTest`**: Shared lifecycle, `self.step()`, failure artifacts, cleanup registry
- **`ConfigManager`**: Singleton — `.env` + `config_{env}.yaml` with env precedence
- **`Logger`**: loguru with automatic sensitive-data redaction in log output

### API
- **`RESTClient`**: Session-based HTTP client; retries **GET/HEAD only** (idempotent)
- **`GraphQLClient`**: Query/mutation execution; optional schema fetch (`GRAPHQL_FETCH_SCHEMA`)
- **`APIResponseValidator`**: Status codes, headers, JSON Schema (`jsonschema`), response time
- **Services** (`UsersAPI`, `ProductsGraphQL`): Endpoint logic and cross-layer validation

### Web
- **`BrowserManager`**: Browser launch, per-test context, trace/video on failure
- **`BasePage`**: Playwright wrapper with `fill_test_id`, `click_role`, UI retry
- **Page objects** (`LoginPage`, `ProductsPage`, …): Locators and user actions
- **`session_browser_manager`**: Session fixture — smoke tests reuse browser, get fresh context

### DB
- **`DatabaseClient`**: PostgreSQL, MySQL via SQLAlchemy; MongoDB via pymongo
- **Repositories**: Table-specific queries (`UsersRepository`, `ProductsRepository`, …)
- **`DatabaseValidator`**: Pre/post API checks, field comparison, referential integrity
- **`TransactionManager`**: Test-level rollback and savepoints

### Mobile
- **`AppiumManager`**: Android/iOS driver lifecycle
- **Screen objects**: Platform-specific locators and gestures
- Set `SKIP_APPIUM=true` to skip mobile tests when no device is available

### Utilities
- **`assertions`**: Hard/soft assertions; per-test `self.soft_assert` on `BaseTest`
- **`redact`**: Masks passwords, tokens, Authorization headers in logs/reports
- **`test_data`**: Faker + YAML/JSON; xdist-safe unique IDs
- **`ui_retry`**: Tenacity-backed retry for flaky UI operations

## Mock Servers

Located in `tests/mocks/` for **zero-dependency** local and CI runs:

| Server | Port | Purpose |
|--------|------|---------|
| `mock_api_server.py` | 8080 | REST `/v1/users` CRUD + GraphQL `/graphql` |
| `mock_web_server.py` | 3000 | Static HTML with `data-testid` elements |

Mock servers start automatically via `conftest.py` (set `SKIP_MOCK_SERVERS=true` to disable). Postgres sync in mocks is opt-in via `MOCK_DB_SYNC=true` (used in `smoke_db` / integration CI jobs).

Docker Compose also runs these as `mock-api` and `mock-web` services alongside Postgres.

## CI/CD Integration

| Platform | File | Highlights |
|----------|------|------------|
| GitHub Actions | `.github/workflows/ci.yml` | Lint, unit tests, API matrix, web (chromium/firefox/webkit), DB, curated smoke, smoke_db, integration, mobile collect-only |
| Azure Pipelines | `azure-pipelines.yml` | Lint + smoke |
| GitLab CI | `.gitlab-ci.yml` | DB schema init, mock servers, integration job |
| Jenkins | `Jenkinsfile` | Blocking lint, mock servers, parallel stages |
| Dependabot | `.github/dependabot.yml` | Weekly pip + GitHub Actions updates |

CI uses mock servers by default — **no secrets required** for API/web/smoke/integration jobs.

## Docker

```bash
docker-compose up --build
# Runs: postgres-test, mock-api, mock-web, test-runner
```

## Best Practices

1. **Keep tests thin** — scenarios and assertions only; logic in pages/services/repositories
2. **Use `with self.step(...)`** — readable reports and clear AAA structure
3. **Use `data-testid` locators** — stable, accessible, maintainable
4. **Never hardcode credentials** — use `.env`, CI secrets, or generated test data
5. **Mark suite tier** — `@pytest.mark.smoke` for fast checks, `@pytest.mark.regression` for full coverage
6. **Register cleanup** — use `cleanup_registry` for data created outside service helpers

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Playwright browser not found | `playwright install --with-deps` |
| API/web tests fail locally | Start mock servers: `bash scripts/start_mock_servers.sh &` |
| DB connection errors | Check Postgres is running; verify `DB_*` in `.env` |
| Mobile tests skip/fail in CI | Expected without Appium — set `SKIP_APPIUM=true` or run on device farm |
| GraphQL schema errors offline | Set `GRAPHQL_FETCH_SCHEMA=false` in `.env` |
| Allure report empty | Ensure `reports/allure-results` exists; run `allure serve reports/allure-results` |

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — Design decisions and component deep-dive
- [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) — Execution patterns and CI usage
- [TEST_RESULT_CUSTOMIZATION.md](TEST_RESULT_CUSTOMIZATION.md) — Steps, titles, and Allure customization
- [STEP_CONTEXT_GUIDE.md](STEP_CONTEXT_GUIDE.md) — Step context manager usage

## License

[Your License Here]
