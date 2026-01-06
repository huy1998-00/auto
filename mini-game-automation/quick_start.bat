@echo off
setlocal enabledelayedexpansion
REM Quick Start Script for Windows
REM This script automatically installs all dependencies, environment, and browser

REM Change to script directory (project root)
cd /d "%~dp0"
set PROJECT_ROOT=%CD%

echo ========================================
echo Mini-Game Automation - Auto Setup
echo ========================================
echo.
echo Project directory: %PROJECT_ROOT%
echo.

REM ========================================
REM Step 1: Check/Install Python
REM Based on: https://docs.python.org/dev/using/windows.html
REM ========================================
echo [Step 1/6] Checking Python installation...
echo.

REM Try python command first (recommended by Python docs)
python --version >nul 2>&1
if errorlevel 1 (
    REM Try py command (Python launcher)
    py --version >nul 2>&1
    if errorlevel 1 (
        REM Try pymanager command (Python Install Manager)
        pymanager --version >nul 2>&1
        if errorlevel 1 (
            echo Python not found. Attempting to install Python Install Manager...
            echo.
            echo According to Python documentation:
            echo https://docs.python.org/dev/using/windows.html
            echo.
            echo The recommended way is Python Install Manager from:
            echo - Microsoft Store (recommended)
            echo - python.org/downloads
            echo.
            
            REM Try to install via winget (Windows Package Manager)
            where winget >nul 2>&1
            if not errorlevel 1 (
                echo Installing Python Install Manager via winget...
                winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
                if errorlevel 1 (
                    echo winget installation failed, trying chocolatey...
                    where choco >nul 2>&1
                    if not errorlevel 1 (
                        echo Installing Python via Chocolatey...
                        choco install python3 --yes --silent
                        if errorlevel 1 (
                            goto :manual_python_install
                        )
                    ) else (
                        goto :manual_python_install
                    )
                )
                echo Waiting for Python installation to complete...
                timeout /t 15 /nobreak >nul
                REM Refresh PATH
                call refreshenv >nul 2>&1
            ) else (
                goto :manual_python_install
            )
        )
    )
)

REM Verify Python is available (try all commands)
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
    ) else (
        pymanager --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=pymanager exec
        ) else (
            echo [ERROR] Python installation completed but commands not found
            echo Please restart your terminal/command prompt and run this script again
            echo Or install Python manually from: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)

REM Check Python version (need 3.8+)
for /f "tokens=2" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python found: !PYTHON_CMD! version !PYTHON_VERSION!
echo.

REM Use the detected Python command for rest of script
set PYTHON=!PYTHON_CMD!
goto :python_found

:manual_python_install
echo [ERROR] Automatic Python installation failed
echo.
echo Please install Python manually using one of these methods:
echo.
echo METHOD 1 - Microsoft Store (Recommended):
echo   1. Open Microsoft Store
echo   2. Search for "Python 3.12" or "Python Install Manager"
echo   3. Click "Install"
echo   4. After installation, restart this script
echo.
echo METHOD 2 - Python.org:
echo   1. Visit: https://www.python.org/downloads/
echo   2. Download Python 3.8 or newer
echo   3. Run installer
echo   4. IMPORTANT: Check "Add Python to PATH" during installation
echo   5. After installation, restart this script
echo.
echo METHOD 3 - Python Install Manager:
echo   1. Visit: https://www.python.org/downloads/
echo   2. Download "Python Install Manager"
echo   3. Install it
echo   4. Run: pymanager install 3.12
echo   5. Restart this script
echo.
echo For more information, see:
echo https://docs.python.org/dev/using/windows.html
echo.
pause
exit /b 1

:python_found

REM ========================================
REM Step 2: Check and Upgrade pip
REM ========================================
echo [Step 2/6] Checking pip installation...
!PYTHON! -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    echo Attempting to install pip...
    !PYTHON! -m ensurepip --upgrade
    if errorlevel 1 (
        echo [ERROR] Failed to install pip
        pause
        exit /b 1
    )
) else (
    echo pip is installed
    echo Upgrading pip to latest version...
    !PYTHON! -m pip install --upgrade pip --quiet
)
echo.

REM ========================================
REM Step 3: Create/Check Virtual Environment
REM ========================================
echo [Step 3/6] Setting up virtual environment...

REM Ensure we're in project directory
cd /d "%PROJECT_ROOT%"
echo Working directory: %CD%
echo Expected project root: %PROJECT_ROOT%
echo.

if not exist "venv" (
    echo Creating new virtual environment in: %PROJECT_ROOT%\venv
    echo Using: !PYTHON! -m venv "%PROJECT_ROOT%\venv"
    !PYTHON! -m venv "%PROJECT_ROOT%\venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Make sure you have write permissions in: %PROJECT_ROOT%
        pause
        exit /b 1
    )
    echo Virtual environment created successfully at: %PROJECT_ROOT%\venv
) else (
    echo Virtual environment already exists at: %PROJECT_ROOT%\venv
    REM Check if it's valid
    if not exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
        echo [WARNING] Virtual environment appears corrupted, recreating...
        rmdir /s /q "%PROJECT_ROOT%\venv"
        !PYTHON! -m venv "%PROJECT_ROOT%\venv"
        if errorlevel 1 (
            echo [ERROR] Failed to recreate virtual environment
            pause
            exit /b 1
        )
    )
)

REM Verify we're still in project directory
cd /d "%PROJECT_ROOT%"
echo.

REM ========================================
REM Step 4: Activate Virtual Environment
REM ========================================
echo [Step 4/6] Activating virtual environment...

REM Ensure we're still in project directory before activation
cd /d "%PROJECT_ROOT%"

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Verify activation and ensure we're in correct directory
if not defined VIRTUAL_ENV (
    echo [WARNING] Virtual environment may not be activated properly
    echo Attempting to activate again...
    cd /d "%PROJECT_ROOT%"
    call venv\Scripts\activate.bat
)

REM Ensure we're in project directory after activation
cd /d "%PROJECT_ROOT%"

REM Upgrade pip in virtual environment
echo Upgrading pip in virtual environment...
python -m pip install --upgrade pip --quiet
REM Note: After venv activation, 'python' refers to venv Python
echo Virtual environment activated: %VIRTUAL_ENV%
echo Current directory: %CD%
echo.

REM ========================================
REM Step 5: Install Python Dependencies
REM ========================================
echo [Step 5/6] Installing Python dependencies...

REM Ensure we're in project directory
cd /d "%PROJECT_ROOT%"
echo Current directory: %CD%

REM Verify we're in the correct directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in: %PROJECT_ROOT%
    echo.
    echo Current directory: %CD%
    echo Script location: %~dp0
    echo.
    echo Attempting to find requirements.txt...
    
    REM Try to find requirements.txt in script directory
    if exist "%~dp0requirements.txt" (
        echo Found requirements.txt in script directory, changing to that location...
        cd /d "%~dp0"
        set PROJECT_ROOT=%CD%
    ) else (
        echo [ERROR] requirements.txt not found!
        echo.
        echo Please ensure:
        echo 1. You're running this script from the project root directory
        echo 2. requirements.txt exists in the project root
        echo.
        echo Expected location: %~dp0requirements.txt
        pause
        exit /b 1
    )
)

echo Found requirements.txt in: %CD%
echo.

REM Check if packages are already installed
echo Checking installed packages...
pip show playwright >nul 2>&1
set INSTALLED=0
if not errorlevel 1 (
    pip show opencv-python >nul 2>&1
    if not errorlevel 1 (
        pip show easyocr >nul 2>&1
        if not errorlevel 1 (
            echo Some packages already installed, checking for updates...
            set INSTALLED=1
        )
    )
)

REM Install or upgrade dependencies
echo Installing/updating dependencies from requirements.txt...
echo This may take a few minutes...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo Retrying with verbose output...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo.
        echo Troubleshooting:
        echo 1. Check your internet connection
        echo 2. Try running: pip install --upgrade pip
        echo 3. Check if antivirus is blocking pip
        pause
        exit /b 1
    )
)

REM Verify critical packages
echo Verifying critical packages...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo [ERROR] playwright package not found after installation
    pause
    exit /b 1
)

pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] opencv-python package not found after installation
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.

REM ========================================
REM Step 6: Install Playwright Browser
REM ========================================
echo [Step 6/6] Installing Playwright browser (Chromium)...
echo This will download ~200MB browser binaries...
echo.

REM Check if browser is already installed
playwright install --dry-run chromium >nul 2>&1
if errorlevel 1 (
    echo Browser not installed, installing now...
    echo This will download ~200MB browser binaries...
    playwright install chromium --with-deps
    if errorlevel 1 (
        echo [ERROR] Failed to install Playwright browser
        echo Retrying without system dependencies...
        playwright install chromium
        if errorlevel 1 (
            echo [ERROR] Failed to install Playwright browser
            echo.
            echo Troubleshooting:
            echo 1. Check your internet connection
            echo 2. Try running: playwright install-deps chromium
            echo 3. Check if antivirus is blocking the download
            pause
            exit /b 1
        )
    )
    echo Browser installed successfully!
) else (
    echo Browser already installed
    echo Updating browser...
    playwright install chromium --with-deps >nul 2>&1
)

REM Verify browser installation
playwright install --dry-run chromium >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Browser installation verification failed
    echo You may need to run: playwright install chromium
) else (
    echo Browser installation verified!
)
echo.

REM ========================================
REM Setup Complete
REM ========================================
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Installed components:
echo   [X] Python environment
echo   [X] Virtual environment
echo   [X] Python dependencies
echo   [X] Playwright browser
echo.

REM Auto-create configuration files if missing
set CONFIG_OK=1
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating .env file from .env.example...
        copy .env.example .env >nul
    ) else (
        echo [INFO] Creating default .env file...
        (
            echo GAME_URL=https://your-game-url.com
            echo HEADLESS=false
        ) > .env
    )
)

if not exist "config" (
    echo [INFO] Creating config directory...
    mkdir config
)

if not exist "config\table_regions.yaml" (
    echo [INFO] Creating default table_regions.yaml...
    (
        echo tables:
        echo   1:
        echo     x: 100
        echo     y: 200
        echo     width: 300
        echo     height: 250
        echo     buttons:
        echo       blue: {x: 10, y: 20}
        echo       red: {x: 30, y: 40}
        echo       confirm: {x: 50, y: 60}
        echo       cancel: {x: 70, y: 80}
        echo     timer: {x: 5, y: 5, width: 50, height: 30}
        echo     blue_score: {x: 10, y: 10, width: 30, height: 20}
        echo     red_score: {x: 40, y: 10, width: 30, height: 20}
    ) > config\table_regions.yaml
)

if not exist "config\default_patterns.yaml" (
    echo [INFO] Creating default_patterns.yaml...
    (
        echo default_patterns: "BBP-P;BPB-B;BBB-P"
    ) > config\default_patterns.yaml
)

echo Configuration files ready!
echo.
echo Next steps:
echo 1. Edit .env file and set GAME_URL=https://your-game-url.com
echo 2. Update config\table_regions.yaml with your table coordinates
echo 3. Update config\default_patterns.yaml with your betting patterns
echo 4. Run: python -m automation.main
echo.
echo Or run tests: run_tests.bat
echo.

REM Run application if --run flag provided
if "%1"=="--run" (
    echo ========================================
    echo Starting application...
    echo ========================================
    echo.
    
    REM Ensure we're in project directory
    cd /d "%PROJECT_ROOT%"
    
    REM Set PYTHONPATH to include project root for module imports
    set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%
    
    REM Run as module to support relative imports
    python -m src.automation.main
    goto :end
)

REM Run tests if --test flag provided
if "%1"=="--test" (
    echo ========================================
    echo Running tests...
    echo ========================================
    echo.
    python -m pytest tests/ -v
    goto :end
)

REM If no flags, offer interactive options
echo Setup complete! Ready to use.
echo.
echo ========================================
echo What would you like to do next?
echo ========================================
echo.
echo [1] Run unit tests
echo [2] Start the application (UI mode)
echo [3] Exit
echo.
set /p CHOICE="Enter your choice (1-3): "

if "!CHOICE!"=="1" (
    echo.
    echo ========================================
    echo Running tests...
    echo ========================================
    echo.
    python -m pytest tests/ -v
    echo.
    echo Tests completed!
    goto :end
)

if "!CHOICE!"=="2" (
    echo.
    echo ========================================
    echo Starting application...
    echo ========================================
    echo.
    echo Note: Make sure you have configured:
    echo   - .env file with GAME_URL
    echo   - config\table_regions.yaml with table coordinates
    echo.
    
    REM Ensure we're in project directory
    cd /d "%PROJECT_ROOT%"
    
    REM Set PYTHONPATH to include project root for module imports
    set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%
    
    REM Run as module to support relative imports
    python -m src.automation.main
    goto :end
)

if "!CHOICE!"=="3" (
    echo.
    echo Exiting. Run 'quick_start.bat --test' or 'quick_start.bat --run' next time.
    goto :end
)

echo.
echo Invalid choice. Exiting.
echo.

:end
if "%1"=="" (
    pause
)
