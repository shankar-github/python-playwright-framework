# Framework Architecture & Design Decisions

## High-Level Architecture

The framework follows a **layered, modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Test Layer                            │
│  Scenario tests only — inherit framework bases           │
│  (API, Web, Mobile, DB, Integration)                   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Domain Abstraction Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Services │  │  Pages   │  │ Screens  │  │   Repos  ││
│  │  (API)   │  │  (Web)   │  │ (Mobile) │  │   (DB)   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Client / Infrastructure Layer               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │   REST   │  │ Playwright│ │  Appium  │  │ SQLAlchemy│
│  │ GraphQL  │  │  Browser  │ │  Driver  │  │  MongoDB  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Base Framework Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  Config  │  │  Logger  │  │ BaseTest │  │  Utils   ││
│  │ Manager  │  │ + Redact │  │ + Report │  │ Assertions│
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
```

### Request flow (example: E2E user registration)

```
TestE2EFlow
  └─ self.api_service(UsersAPI)
       └─ RESTClient → POST /users
       └─ APIResponseValidator → status + schema
       └─ DatabaseValidator → assert_record_exists
  └─ self.page_object(LoginPage)
       └─ BasePage → get_by_test_id / get_by_role
       └─ BrowserManager → Playwright context + page
```

## Design Principles

### 1. Separation of Concerns

| Layer | Responsibility | Does NOT contain |
|-------|----------------|------------------|
| Tests | Scenarios, orchestration, high-level assertions | Locators, SQL, HTTP details |
| Domain abstractions | Page/screen actions, API operations, DB queries | Browser/driver lifecycle |
| Clients | Protocol-level I/O | Business validation |
| Base framework | Lifecycle, config, logging, reporting | Test scenarios |

### 2. Single Responsibility

Each module has one well-defined job:

- `RESTClient` — HTTP transport, idempotent retry, request logging
- `UsersAPI` — User resource operations and DB cross-checks
- `LoginPage` — Login screen locators and actions
- `UsersRepository` — User table SQL operations
- `BaseTest` — Setup/teardown, steps, failure artifacts

### 3. Resource Initialization

Resources are created in base test classes, not scattered across tests:

```python
# framework/core/base_test.py — shared lifecycle
@pytest.fixture(autouse=True)
def setup_test(self, request):
    self._init_resources(request)   # layer-specific
    yield
    self._capture_failure_artifacts()
    cleanup_registry.execute_cleanup()
    self._cleanup_resources()

# framework/web/base_web_test.py — web resources
def _init_resources(self, request):
    if request.node.get_closest_marker("smoke"):
        self.browser_manager = request.getfixturevalue("session_browser_manager")
        self.browser_manager.create_context()   # fresh context, shared browser
    else:
        self.browser_manager = BrowserManager()
        self.browser_manager.start_browser()
```

**Factory methods** expose domain objects to tests:

```python
login_page = self.page_object(LoginPage)
users = self.api_service(UsersAPI)
repo = self.repository(UsersRepository)
screen = self.screen_object(LoginScreen)
```

**Pytest session fixtures** (`conftest.py`) provide shared infrastructure:

- `session_browser_manager` — one browser process per session; smoke tests get a new context per test
- `setup_allure_environment` — writes `environment.properties`
- `attach_test_info` — dynamic Allure title/description from docstrings

### 4. Configuration Management

Configuration is loaded once via singleton `ConfigManager`:

```
Priority (highest first):
  1. OS environment variables
  2. .env file
  3. config/config_{ENV}.yaml  (mapped to env vars via YAML_ENV_MAPPINGS)
  4. Pydantic defaults
```

Key files:

| File | Purpose |
|------|---------|
| `.env.example` | Documents all env vars; defaults to mock server URLs |
| `config/config_dev.yaml.example` | Dev environment template |
| `config/config_test.yaml.example` | CI/local mock environment template |

Layer-specific settings use Pydantic (`APISettings`, `WebSettings`, `MobileSettings`, `DBSettings`).

## Component Design

### API Testing Layer

#### REST Client (`framework/api/rest_client.py`)

- **Idempotent retry only**: GET/HEAD retried on 429/5xx; POST/PUT/DELETE never retried
- **Session reuse**: Connection pooling via `requests.Session`
- **Redacted logging**: Request bodies, response bodies, and headers pass through `redact_payload` / `redact_headers`

#### GraphQL Client (`framework/api/graphql_client.py`)

- Queries retried; mutations single-attempt (no duplicate writes)
- **`GRAPHQL_FETCH_SCHEMA`**: When `false` (default for CI/offline), skips live schema introspection
- Variables and results redacted in debug logs

#### API Services (`framework/api/services/`)

Services encapsulate endpoint paths, expected status codes, and optional DB validation:

```
UsersAPI          → REST /users CRUD + db_validator helpers
ProductsGraphQL   → GraphQL product queries/mutations + cross-layer checks
BaseAPIService    → Shared client access and DB requirement guards
```

Tests call `self.api_service(UsersAPI)` — never `self.api_client.post(...)` directly.

#### API Validators (`framework/api/validators.py`)

- Status code, header, key/value assertions
- **JSON Schema validation** via `jsonschema` library (full schema documents)
- Legacy flat `{key: type}` map still supported for simple checks
- Response time validation

### Database Testing Layer

#### Database Client (`framework/db/db_client.py`)

- PostgreSQL and MySQL via SQLAlchemy 2.0; MongoDB via pymongo
- `NullPool` — no connection reuse between tests
- **`DB_PASSWORD` required** — no silent default credentials
- Connection strings never logged

#### Repositories (`framework/db/repositories/`)

Table-specific data access isolated from tests:

```
BaseRepository    → Generic query/execute helpers
UsersRepository   → users table CRUD
ProductsRepository, CategoriesRepository, OrdersRepository
```

Tests call `self.repository(UsersRepository)`.

#### Transaction Manager (`framework/db/transaction_manager.py`)

- Context manager with automatic rollback for test isolation
- Savepoints use SQLAlchemy `text()` for SQLAlchemy 2.0 compatibility

#### Database Validator (`framework/db/db_validator.py`)

- Pre/post API state checks, field comparison, referential integrity
- Soft assertion collection for multi-field DB validation

### Web UI Testing Layer

#### Locator Strategy

Page objects use **stable, accessible locators** in priority order:

1. `data-testid` via `page.get_by_test_id()` — primary strategy
2. ARIA roles via `page.get_by_role()` — buttons, textboxes, links
3. CSS selectors — avoided in page objects; not used in tests

```python
# framework/web/pages/login_page.py
EMAIL_TEST_ID = "email-input"

def login(self, email, password):
    self.fill_test_id(self.EMAIL_TEST_ID, email)
    self.click_test_id(self.SUBMIT_TEST_ID)
```

#### Base Page (`framework/web/base_page.py`)

- Playwright auto-waiting on all interactions
- `@retry_ui_operation` (tenacity) on click, fill, wait — configurable backoff
- `press_sequentially()` instead of deprecated `page.type()`
- Password field values redacted in debug logs

#### Browser Manager (`framework/web/browser_manager.py`)

Lifecycle split for performance and isolation:

```
launch_browser()   → Start browser process (once per session for smoke)
create_context()   → New context + page + optional trace (per test)
close_context()    → Close context, keep browser (smoke reuse)
close_browser()    → Full teardown
```

Failure diagnostics (`capture_failure_artifacts`):

- Full-page screenshot → Allure
- Playwright trace ZIP → Allure (when `RECORD_TRACE=true`)
- Video WEBM → Allure (when `RECORD_VIDEO=true`)

#### Smoke Browser Pooling

`@pytest.mark.smoke` web/integration tests reuse `session_browser_manager`:

- One browser process per pytest session (per xdist worker)
- Fresh browser context per test — cookies/storage isolated
- ~2–5 s browser startup saved per smoke test

### Mobile UI Testing Layer

#### Screen Object Model

Mirrors web POM:

```
LoginScreen, ProductsScreen, RegistrationScreen, …
BaseScreen    → find_element, swipe, retry, redacted fill logging
AppiumManager → driver lifecycle, platform capabilities
```

Platform selected via `@pytest.mark.android` / `@pytest.mark.ios`.

Set `SKIP_APPIUM=true` to skip when no device/emulator is available (CI collect-only validation).

### Base Framework Layer

#### Config Manager (`framework/core/config_manager.py`)

Singleton with lazy layer settings. YAML keys mapped to env vars:

```python
YAML_ENV_MAPPINGS = [
    (("api", "base_url"), "API_BASE_URL"),
    (("web", "record_trace"), "RECORD_TRACE"),
    (("mobile", "appium_server_url"), "APPIUM_SERVER_URL"),
    ...
]
```

#### Logger (`framework/core/logger.py`)

- loguru with console + rotating file handlers
- **`_redact_log_record` filter**: Applies `redact_log_message()` to every log line
- Lazy import of redact module to avoid circular imports

#### Base Test (`framework/core/base_test.py`)

Shared autouse fixture for all layers:

```
setup_test
  ├─ test_id / correlation_id
  ├─ TestResultManager (title, steps, data)
  ├─ self.soft_assert = SoftAssertions()   ← per-test, not global
  ├─ _init_resources()                     ← overridden per layer
  ├─ yield (test runs)
  ├─ _capture_failure_artifacts()          ← overridden per layer
  ├─ cleanup_registry.execute_cleanup()
  └─ _cleanup_resources()
```

Step API:

```python
with self.step("Create user") as step_ctx:
    result = users.create(user_data)
    step_ctx.set_result(result)
```

### Utilities Layer

#### Assertions (`framework/utils/assertions.py`)

- `HardAssertions` — fail immediately (static methods)
- `SoftAssertions` — collect failures; call `assert_all()` at end
- `self.soft_assert` on `BaseTest` — isolated per test
- Custom `AssertionError` with actual/expected/context for reporting

#### Redaction (`framework/utils/redact.py`)

Applied across logging, REST/GraphQL clients, and `TestResultManager`:

| Trigger | Redacted in |
|---------|-------------|
| Key names: password, token, authorization, api_key, … | Dicts, test data, payloads |
| Selector names containing "password" | UI fill logs |
| Bearer token patterns | Log messages |
| JSON `"password": "..."` patterns | Log message filter |

#### Test Data (`framework/utils/test_data.py`)

- YAML/JSON file loading with dot-notation access
- Faker-generated data with **xdist-safe unique IDs**: `{uuid}_{timestamp}_{worker_id}`
- `cleanup_registry` for post-test data teardown

#### UI Retry (`framework/utils/ui_retry.py`)

Tenacity decorator shared by web (`BasePage`) and mobile (`BaseScreen`):

- Catches `PlaywrightTimeoutError` / Appium timeout exceptions
- Exponential backoff with Allure retry step attachments

## Mock Infrastructure

Self-contained test targets in `tests/mocks/`:

```
tests/mocks/
├── mock_api_server.py    # In-memory REST API (port 8080)
│   └── /v1/users CRUD with UUID generation
└── mock_web_server.py    # Static HTML (port 3000)
    └── Pages with data-testid elements matching page objects
```

Used by:

- Local development (`scripts/start_mock_servers.sh`)
- GitHub Actions / GitLab CI (background process before pytest)
- Docker Compose (`mock-api`, `mock-web` services)

This removes the need for external `example.com` URLs or CI secrets for API/web/smoke jobs.

## Test Organization

```
tests/
├── api/              # REST + GraphQL (smoke + comprehensive tiers)
├── web/              # Playwright POM tests
├── mobile/           # Appium screen object tests
├── db/               # Standalone DB + repository tests
├── integration/      # API → DB → UI cross-layer flows
├── core/             # ConfigManager, Logger unit tests
├── utils/            # Assertions, redact, test_data unit tests
├── reporting/        # TestResultManager unit tests
└── mocks/            # Mock servers (not pytest tests)
```

### Test markers

| Marker | Usage |
|--------|-------|
| `smoke` | Fast critical-path; triggers shared browser pooling |
| `regression` | Full comprehensive suites |
| `api`, `rest`, `graphql` | API sub-layers |
| `web`, `mobile`, `db` | Layer filters |
| `integration`, `e2e` | Cross-layer flows |
| `android`, `ios` | Mobile platform |

## Reporting Strategy

### Allure Integration

| Artifact | Source | When |
|----------|--------|------|
| Screenshots | `BrowserManager.capture_failure_artifacts` | Test failure |
| Playwright trace ZIP | `BrowserManager` | Test failure (`RECORD_TRACE=true`) |
| Video WEBM | `BrowserManager` | Test failure (`RECORD_VIDEO=true`) |
| Step results | `StepContext` / `TestResultManager` | Every step |
| Environment | `conftest.setup_allure_environment` | Session start |
| API retry info | `RESTClient._log_response` | HTTP retry occurred |

`TestResultManager` redacts sensitive values in `add_test_data`, step data, and `get_summary()`.

### Logging Strategy

- **Correlation ID**: `{ClassName}_{test_id}` on every test
- **Levels**: DEBUG (assertions, locators), INFO (steps, API calls), WARNING (retries), ERROR (failures)
- **Redaction filter**: All log output passes through `redact_log_message`
- **File rotation**: 10 MB rotation, 7-day retention, zip compression

## CI/CD Architecture

```
┌──────────── GitHub Actions ────────────┐
│ lint → api (py 3.9–3.11) → web (browser│
│ matrix) → db (Postgres + init.sql) →  │
│ smoke → integration → mobile (collect)│
└────────────────────────────────────────┘
         Mock servers started in-job
         No secrets required for API/web
```

| Job | Mock servers | Database | Notes |
|-----|-------------|----------|-------|
| api-tests | mock_api :8080 | — | Excludes live GraphQL |
| web-tests | mock_web :3000 | — | chromium + firefox matrix |
| db-tests | — | Postgres + init.sql | |
| smoke | both mocks | — | Uses shared browser fixture |
| integration | both mocks | Postgres + init.sql | Full E2E against mocks |
| mobile | — | — | `--collect-only` validation |

GitLab CI and Jenkins follow the same pattern: mock servers, DB schema init, blocking lint.

Dependabot (`.github/dependabot.yml`) monitors pip and GitHub Actions weekly.

## Security Design

1. **No default DB passwords** — `DB_PASSWORD` must be set explicitly
2. **`.env` and `test_data/*.yaml` gitignored** — secrets stay local/CI
3. **Redaction at every output boundary** — logs, Allure attachments, test data summaries
4. **Idempotent HTTP retry** — prevents duplicate writes on POST retry
5. **SQLAlchemy parameterized queries** — no string-interpolated SQL in repositories

## Scalability Considerations

| Scale | Status | Notes |
|-------|--------|-------|
| ~100 tests | ✅ Ready | Current architecture handles easily |
| ~500 tests | ✅ Ready | Parallel xdist; smoke browser pooling helps |
| 1000+ tests | ⚠️ Plan needed | Consider session browser for regression; test sharding in CI |

Design enablers:

- Modular layer addition (new service/page/repo without touching bases)
- xdist-safe test data generation
- Per-test browser context (isolation) with optional shared browser process
- Cleanup registry for parallel-safe teardown

## Best Practices Implemented

1. **Thin tests, fat abstractions** — POM, services, repositories
2. **Test isolation** — unique test IDs, cleanup registry, DB rollback
3. **Parallel-safe** — xdist worker IDs in test data; no global mutable soft assert state
4. **Configuration externalization** — zero hardcoded URLs in framework code
5. **Failure diagnostics** — screenshot + trace + video on failure
6. **Accessible locators** — data-testid and ARIA roles
7. **Type hints and docstrings** throughout framework modules
8. **Self-contained CI** — mock servers eliminate external dependencies

## Future Enhancements

| Enhancement | Status |
|-------------|--------|
| Mock API/web for CI | ✅ Implemented (`tests/mocks/`) |
| JSON Schema validation | ✅ Implemented (`jsonschema`) |
| Sensitive data redaction | ✅ Implemented (`framework/utils/redact.py`) |
| Smoke browser pooling | ✅ Implemented (`session_browser_manager`) |
| WireMock Docker service | Optional — Python mocks used instead |
| Visual regression (Percy/Applitools) | Planned |
| Accessibility testing (axe) | Planned |
| Mobile device farm (BrowserStack/Sauce) | Planned |
| Secrets manager (Vault/AWS SM) | Planned |
| TestContainers for ephemeral DB | Planned |
