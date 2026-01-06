#!/bin/bash
# Test Runner Script for Mini-Game Automation
# This script runs pytest tests for the project

set -e

echo "========================================"
echo "Running Unit Tests"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo ""
    echo "Please run quick_start.sh first to set up the environment."
    echo ""
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo "[ERROR] pytest is not installed"
    echo "Installing pytest..."
    pip install pytest pytest-cov
fi

echo ""
echo "Running tests..."
echo ""

# Run tests with verbose output
python -m pytest tests/ -v

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] All tests passed!"
    echo ""
else
    echo ""
    echo "[WARNING] Some tests failed!"
    echo ""
fi

# Option to run with coverage
echo ""
read -p "Run tests with coverage report? (y/n): " RUN_COVERAGE
if [ "$RUN_COVERAGE" = "y" ] || [ "$RUN_COVERAGE" = "Y" ]; then
    echo ""
    echo "Running tests with coverage..."
    python -m pytest tests/ --cov=src/automation --cov-report=html --cov-report=term
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
    echo ""
fi
