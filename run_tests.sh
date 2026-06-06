#!/bin/bash

# Test Execution Script
# Usage: ./run_tests.sh [test_type] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
PARALLEL="auto"
ENV="dev"
MARKER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --marker)
            MARKER="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL="$2"
            shift 2
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --type TYPE       Test type: all, api, web, mobile, db, integration, smoke"
            echo "  --marker MARKER   Pytest marker (e.g., 'api and rest')"
            echo "  --parallel N      Number of parallel workers (default: auto)"
            echo "  --env ENV         Environment: dev, staging, prod (default: dev)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Set marker based on test type if not specified
if [ -z "$MARKER" ]; then
    case $TEST_TYPE in
        api)
            MARKER="api"
            ;;
        web)
            MARKER="web"
            ;;
        mobile)
            MARKER="mobile"
            ;;
        db)
            MARKER="db"
            ;;
        integration)
            MARKER="integration"
            ;;
        smoke)
            MARKER="smoke"
            ;;
        all)
            MARKER=""
            ;;
        *)
            echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
            exit 1
            ;;
    esac
fi

# Build pytest command
PYTEST_CMD="pytest"

if [ -n "$MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKER\""
fi

PYTEST_CMD="$PYTEST_CMD -n $PARALLEL"
PYTEST_CMD="$PYTEST_CMD --alluredir=reports/allure-results"
PYTEST_CMD="$PYTEST_CMD --clean-alluredir"

# Export environment
export ENV=$ENV

echo -e "${GREEN}Running tests...${NC}"
echo -e "Type: ${YELLOW}$TEST_TYPE${NC}"
echo -e "Marker: ${YELLOW}${MARKER:-none}${NC}"
echo -e "Parallel: ${YELLOW}$PARALLEL${NC}"
echo -e "Environment: ${YELLOW}$ENV${NC}"
echo ""

# Run tests
eval $PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Tests passed!${NC}"
    
    # Generate Allure report if available
    if command -v allure &> /dev/null; then
        echo -e "\n${GREEN}Generating Allure report...${NC}"
        allure generate reports/allure-results -o reports/allure-report --clean
        echo -e "${GREEN}Report generated at: reports/allure-report/index.html${NC}"
    else
        echo -e "\n${YELLOW}Allure not installed. Install with: pip install allure-pytest${NC}"
    fi
else
    echo -e "\n${RED}Tests failed!${NC}"
    exit 1
fi
