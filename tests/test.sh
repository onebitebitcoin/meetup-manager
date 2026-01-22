#!/bin/bash

# =============================================================================
# Meetup Manager - Integrated Test Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Print section header
print_header() {
    echo ""
    print_msg "$BLUE" "=============================================="
    print_msg "$BLUE" "$1"
    print_msg "$BLUE" "=============================================="
    echo ""
}

# Print usage
usage() {
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "TEST_TYPE:"
    echo "  all       Run all tests (default)"
    echo "  backend   Run backend tests only"
    echo "  frontend  Run frontend tests only"
    echo ""
    echo "OPTIONS:"
    echo "  -c, --coverage  Generate coverage report"
    echo "  -v, --verbose   Verbose output"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Run all tests"
    echo "  $0 backend          # Run backend tests"
    echo "  $0 frontend         # Run frontend tests"
    echo "  $0 -c all           # Run all tests with coverage"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        all|backend|frontend)
            TEST_TYPE=$1
            shift
            ;;
        *)
            print_msg "$RED" "Unknown option: $1"
            usage
            ;;
    esac
done

# Run backend tests
run_backend_tests() {
    print_header "Running Backend Tests (Django)"

    cd "$PROJECT_ROOT/backend"

    # Activate virtual environment if exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        print_msg "$YELLOW" "Installing test dependencies..."
        pip install -r requirements-test.txt 2>/dev/null || pip install pytest pytest-django pytest-cov factory-boy
    fi

    # Build pytest command
    PYTEST_CMD="python -m pytest tests/"

    if [ "$VERBOSE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -v"
    fi

    if [ "$COVERAGE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov=meetups --cov-report=term-missing --cov-report=html:htmlcov"
    fi

    # Run tests
    print_msg "$YELLOW" "Executing: $PYTEST_CMD"

    if $PYTEST_CMD; then
        print_msg "$GREEN" "Backend tests PASSED"
        BACKEND_RESULT=0
    else
        print_msg "$RED" "Backend tests FAILED"
        BACKEND_RESULT=1
    fi

    cd "$PROJECT_ROOT"
    return $BACKEND_RESULT
}

# Run frontend tests
run_frontend_tests() {
    print_header "Running Frontend Tests (Vue.js + Vitest)"

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_msg "$YELLOW" "Installing dependencies..."
        npm install
    fi

    # Check if test dependencies are installed
    if ! npm list vitest &> /dev/null; then
        print_msg "$YELLOW" "Installing test dependencies..."
        npm install -D vitest @vue/test-utils happy-dom @vitest/coverage-v8
    fi

    # Build test command
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="npm run test:coverage"
    else
        TEST_CMD="npm run test"
    fi

    # Run tests
    print_msg "$YELLOW" "Executing: $TEST_CMD"

    if $TEST_CMD; then
        print_msg "$GREEN" "Frontend tests PASSED"
        FRONTEND_RESULT=0
    else
        print_msg "$RED" "Frontend tests FAILED"
        FRONTEND_RESULT=1
    fi

    cd "$PROJECT_ROOT"
    return $FRONTEND_RESULT
}

# Main execution
main() {
    print_header "Meetup Manager Test Suite"
    print_msg "$BLUE" "Test Type: $TEST_TYPE"
    print_msg "$BLUE" "Coverage: $COVERAGE"
    print_msg "$BLUE" "Verbose: $VERBOSE"

    BACKEND_RESULT=0
    FRONTEND_RESULT=0

    case $TEST_TYPE in
        all)
            run_backend_tests || BACKEND_RESULT=$?
            run_frontend_tests || FRONTEND_RESULT=$?
            ;;
        backend)
            run_backend_tests || BACKEND_RESULT=$?
            ;;
        frontend)
            run_frontend_tests || FRONTEND_RESULT=$?
            ;;
    esac

    # Print summary
    print_header "Test Summary"

    if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "backend" ]; then
        if [ $BACKEND_RESULT -eq 0 ]; then
            print_msg "$GREEN" "Backend:  PASSED"
        else
            print_msg "$RED" "Backend:  FAILED"
        fi
    fi

    if [ "$TEST_TYPE" = "all" ] || [ "$TEST_TYPE" = "frontend" ]; then
        if [ $FRONTEND_RESULT -eq 0 ]; then
            print_msg "$GREEN" "Frontend: PASSED"
        else
            print_msg "$RED" "Frontend: FAILED"
        fi
    fi

    # Exit with appropriate code
    if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
        print_msg "$RED" ""
        print_msg "$RED" "Some tests failed!"
        exit 1
    else
        print_msg "$GREEN" ""
        print_msg "$GREEN" "All tests passed!"
        exit 0
    fi
}

main
