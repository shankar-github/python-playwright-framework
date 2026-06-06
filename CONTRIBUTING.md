# Contributing

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
cp .env.example .env
cp config/config_test.yaml.example config/config_test.yaml
pre-commit install
```

## Conventions

- Tests stay thin; put logic in page objects, services, or repositories.
- Use `data-testid` and ARIA roles for web locators.
- Use `with self.step(...)` for readable Allure reports.
- Use framework `AssertionError` via `hard_assert` / `self.soft_assert`.
- Mark tests with the correct tier: `smoke`, `smoke_db`, `smoke_e2e`, `regression`.

## Running checks

```bash
flake8 framework tests
black --check framework tests
isort --check-only framework tests
pytest tests/core tests/utils tests/reporting -q
bash scripts/start_mock_servers.sh &
pytest -m smoke -q
```

## Pull requests

- Keep changes focused and include updated docs when behavior changes.
- Ensure CI jobs pass for affected layers.
- Do not commit secrets, `.env`, or generated reports.
