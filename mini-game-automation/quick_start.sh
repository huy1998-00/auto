#!/bin/bash
# Quick Start Script for macOS/Linux
# This script checks and installs dependencies, environment, and browser

set -e  # Exit on error

echo "========================================"
echo "Mini-Game Automation - Quick Start"
echo "========================================"
echo ""

# ========================================
# Step 1: Check Python Installation
# ========================================
echo "[Step 1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python version: $PYTHON_VERSION"
echo ""

# ========================================
# Step 2: Check and Upgrade pip
# ========================================
echo "[Step 2/6] Checking pip installation..."
if ! python3 -m pip --version &> /dev/null; then
    echo "[ERROR] pip is not installed"
    echo "Attempting to install pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install pip"
        exit 1
    fi
else
    echo "pip is installed"
    echo "Upgrading pip to latest version..."
    python3 -m pip install --upgrade pip --quiet
fi
echo ""

# ========================================
# Step 3: Create/Check Virtual Environment
# ========================================
echo "[Step 3/6] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        echo "Make sure you have write permissions in this directory"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
    # Check if it's valid
    if [ ! -f "venv/bin/python" ]; then
        echo "[WARNING] Virtual environment appears corrupted, recreating..."
        rm -rf venv
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to recreate virtual environment"
            exit 1
        fi
    fi
fi
echo ""

# ========================================
# Step 4: Activate Virtual Environment
# ========================================
echo "[Step 4/6] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip in virtual environment
echo "Upgrading pip in virtual environment..."
python -m pip install --upgrade pip --quiet
echo "Virtual environment activated: $VIRTUAL_ENV"
echo ""

# ========================================
# Step 5: Install Python Dependencies
# ========================================
echo "[Step 5/6] Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "[ERROR] requirements.txt not found!"
    echo "Make sure you're running this script from the project root directory"
    exit 1
fi

# Check if packages are already installed
echo "Checking installed packages..."
INSTALLED=0
if pip show playwright &> /dev/null && \
   pip show opencv-python &> /dev/null && \
   pip show easyocr &> /dev/null; then
    echo "Some packages already installed, checking for updates..."
    INSTALLED=1
fi

# Install or upgrade dependencies
echo "Installing/updating dependencies from requirements.txt..."
echo "This may take a few minutes..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check your internet connection"
    echo "2. Try running: pip install --upgrade pip"
    echo "3. Check if firewall is blocking pip"
    exit 1
fi

# Verify critical packages
echo "Verifying critical packages..."
if ! pip show playwright &> /dev/null; then
    echo "[ERROR] playwright package not found after installation"
    exit 1
fi

if ! pip show opencv-python &> /dev/null; then
    echo "[ERROR] opencv-python package not found after installation"
    exit 1
fi

echo "Dependencies installed successfully!"
echo ""

# ========================================
# Step 6: Install Playwright Browser
# ========================================
echo "[Step 6/6] Installing Playwright browser (Chromium)..."
echo "This will download ~200MB browser binaries..."
echo ""

# Check if browser is already installed
if playwright install --dry-run chromium &> /dev/null; then
    echo "Browser already installed"
    echo "Checking for updates..."
    playwright install chromium
else
    echo "Browser not installed, installing now..."
    playwright install chromium
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install Playwright browser"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check your internet connection"
        echo "2. Try running: playwright install-deps chromium"
        echo "3. Check if firewall is blocking the download"
        exit 1
    fi
    echo "Browser installed successfully!"
fi

# Verify browser installation
if ! playwright install --dry-run chromium &> /dev/null; then
    echo "[WARNING] Browser installation verification failed"
    echo "You may need to run: playwright install chromium"
else
    echo "Browser installation verified!"
fi
echo ""

# ========================================
# Setup Complete
# ========================================
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Installed components:"
echo "  [X] Python environment"
echo "  [X] Virtual environment"
echo "  [X] Python dependencies"
echo "  [X] Playwright browser"
echo ""

# Check configuration files
CONFIG_OK=1
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[INFO] .env file not found, copying from .env.example..."
        cp .env.example .env
        echo "Please edit .env file and set GAME_URL"
    else
        echo "[WARNING] .env.example not found"
        CONFIG_OK=0
    fi
fi

if [ ! -f "config/table_regions.yaml" ]; then
    echo "[WARNING] config/table_regions.yaml not found"
    CONFIG_OK=0
fi

if [ ! -f "config/default_patterns.yaml" ]; then
    echo "[WARNING] config/default_patterns.yaml not found"
    CONFIG_OK=0
fi

if [ $CONFIG_OK -eq 0 ]; then
    echo ""
    echo "[WARNING] Some configuration files are missing"
    echo "Please check your project structure"
    echo ""
fi

echo "Next steps:"
echo "1. Edit .env file and set GAME_URL=https://your-game-url.com"
echo "2. Update config/table_regions.yaml with your table coordinates"
echo "3. Update config/default_patterns.yaml with your betting patterns"
echo "4. Run: python -m automation.main --url YOUR_GAME_URL"
echo ""

# Run application if --run flag provided
if [ "$1" == "--run" ]; then
    echo "========================================"
    echo "Starting application..."
    echo "========================================"
    echo ""
    python -m automation.main
else
    echo "To run the application now, execute:"
    echo "  python -m automation.main --url YOUR_GAME_URL"
    echo ""
    echo "Or run: ./quick_start.sh --run"
    echo ""
    echo "For detailed help, see INSTALLATION_GUIDE.md"
fi

echo ""
