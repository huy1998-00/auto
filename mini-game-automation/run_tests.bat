@echo off
REM Test Runner Script for Mini-Game Automation
REM This script runs pytest tests for the project

echo ========================================
echo Running Unit Tests
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run quick_start.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest is not installed
    echo Installing pytest...
    pip install pytest pytest-cov
)

echo.
echo Running tests...
echo.

REM Run tests with verbose output
python -m pytest tests/ -v

REM Check exit code
if errorlevel 1 (
    echo.
    echo [WARNING] Some tests failed!
    echo.
) else (
    echo.
    echo [SUCCESS] All tests passed!
    echo.
)

REM Option to run with coverage
echo.
set /p RUN_COVERAGE="Run tests with coverage report? (y/n): "
if /i "%RUN_COVERAGE%"=="y" (
    echo.
    echo Running tests with coverage...
    python -m pytest tests/ --cov=src/automation --cov-report=html --cov-report=term
    echo.
    echo Coverage report generated in htmlcov/index.html
    echo.
)

pause
