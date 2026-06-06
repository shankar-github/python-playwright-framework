# Test Execution Guide

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run Tests

#### Using pytest directly:

```bash
# Run all tests
pytest

# Run specific test types
pytest -m api          # API tests
pytest -m web          # Web UI tests
pytest -m mobile       # Mobile UI tests
pytest -m db           # Database tests
pytest -m integration  # Integration tests
pytest -m smoke        # Smoke tests

# Run in parallel
pytest -n auto         # Auto-detect CPU count
pytest -n 4            # Use 4 workers

# Run with specific environment
ENV=staging pytest

# Run with Allure reporting
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

#### Using the execution script:

```bash
# Run all tests
./run_tests.sh

# Run specific test type
./run_tests.sh --type api
./run_tests.sh --type web
./run_tests.sh --type smoke

# Run with custom marker
./run_tests.sh --marker "api and rest"

# Run with specific environment
./run_tests.sh --env staging

# Run with custom parallel workers
./run_tests.sh --parallel 4
```

## Test Execution Strategies

### 1. Standalone Layer Execution

Each layer can be executed independently:

```bash
# API tests only
pytest -m api

# Web UI tests only
pytest -m web

# Database tests only
pytest -m db

# Mobile tests only
pytest -m mobile
```

### 2. Parallel Execution

```bash
# Auto-detect optimal workers
pytest -n auto

# Specify number of workers
pytest -n 4

# Run specific tests in parallel
pytest -m api -n auto
```

### 3. Selective Execution

```bash
# Run smoke tests
pytest -m smoke

# Run regression tests
pytest -m regression

# Run specific test file
pytest tests/api/test_rest_api_with_db.py

# Run specific test
pytest tests/api/test_rest_api_with_db.py::TestRESTAPIWithDB::test_create_user_and_validate_in_db
```

### 4. Environment-Based Execution

```bash
# Development environment
ENV=dev pytest

# Staging environment
ENV=staging pytest

# Production environment (use with caution)
ENV=prod pytest
```

## CI/CD Execution

### GitHub Actions

The framework includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

- Runs linting
- Executes API tests in parallel
- Executes Web UI tests
- Executes Database tests
- Executes Smoke tests
- Generates Allure reports
- Uploads artifacts

### Jenkins

The `Jenkinsfile` includes:

- Multi-stage pipeline
- Parallel test execution
- Allure report generation
- Artifact archiving

### GitLab CI

The `.gitlab-ci.yml` includes:

- Lint stage
- Test stages (API, Web, DB)
- Report generation
- Artifact storage

## Reporting

### Allure Reports

```bash
# Generate report
allure generate reports/allure-results -o reports/allure-report --clean

# Serve report locally
allure serve reports/allure-results

# Open report
open reports/allure-report/index.html
```

### HTML Reports

```bash
# Generate HTML report
pytest --html=reports/report.html --self-contained-html
```

## Debugging

### Verbose Output

```bash
# Verbose output
pytest -v

# Very verbose
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

### Run Failed Tests Only

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Debug with PDB

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on error
pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb
```

## Best Practices

1. **Run tests in parallel** for faster execution
2. **Use markers** to organize and selectively run tests
3. **Clean up test data** after each test
4. **Use environment variables** for configuration
5. **Generate reports** for test results analysis
6. **Run smoke tests** before full regression suite
7. **Isolate tests** - each test should be independent

## Troubleshooting

### Common Issues

1. **Import errors**
   - Ensure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

2. **Playwright browser not found**
   - Run: `playwright install`

3. **Database connection errors**
   - Verify database is running
   - Check connection credentials in `.env`

4. **Allure report not generating**
   - Ensure `allure-pytest` is installed
   - Check `reports/allure-results` directory exists

5. **Parallel execution issues**
   - Reduce number of workers: `pytest -n 2`
   - Check for thread-safety issues in tests

## Performance Tips

1. **Use parallel execution** (`-n auto`)
2. **Run only necessary tests** (use markers)
3. **Use test data caching** (already implemented)
4. **Optimize database queries** in tests
5. **Use headless browsers** for Web UI tests
6. **Clean up resources** promptly
