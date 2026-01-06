# Python Installation Guide for Windows

Based on [Official Python Windows Documentation](https://docs.python.org/dev/using/windows.html)

## Recommended: Python Install Manager

The **Python Install Manager** is the recommended way to install Python on Windows according to the official documentation.

### Installation Methods

#### Method 1: Microsoft Store (Easiest)
1. Open **Microsoft Store** app
2. Search for **"Python 3.12"** or **"Python Install Manager"**
3. Click **"Install"**
4. After installation, open a terminal and type `python` to verify

#### Method 2: Download from python.org
1. Visit: https://www.python.org/downloads/
2. Download **"Python Install Manager"** (MSIX package)
3. Double-click the downloaded file and select **"Install"**
4. Or run in PowerShell: `Add-AppxPackage <path to MSIX>`

### Available Commands

After installation, these commands are available:

- **`python`** - Recommended command (launches default/latest version)
- **`py`** - Python launcher (supports version selection)
- **`pymanager`** - Unambiguous command (for scripts)

### Using Python Commands

```batch
REM Check Python version
python --version

REM Launch Python
python

REM Use py launcher for specific version
py -3.12 script.py

REM Use pymanager (for scripts)
pymanager exec script.py
```

### Virtual Environments (Recommended)

According to Python documentation, **always use virtual environments** for projects:

```batch
REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate

REM Deactivate
deactivate
```

### Automatic Installation

Our `quick_start.bat` script automatically:
1. Detects Python using `python`, `py`, or `pymanager` commands
2. Creates a virtual environment
3. Installs all dependencies
4. Sets up Playwright browser

### Troubleshooting

#### Python command not found

If `python` command doesn't work:

1. **Check if Python Install Manager is installed:**
   ```batch
   pymanager --version
   ```

2. **Check if py launcher works:**
   ```batch
   py --version
   ```

3. **Check PATH environment variable:**
   - Open "Edit environment variables for your account"
   - Look for: `%LocalAppData%\Python\bin`
   - Add it if missing

4. **Restart terminal** after installation

#### Multiple Python installations

If you have multiple Python installations:

- Use `py` command to select specific version: `py -3.12`
- Use `pymanager list` to see installed versions
- Use `pymanager install 3.12` to install specific version

### Installing Specific Python Version

```batch
REM Using Python Install Manager
pymanager install 3.12

REM Or using py launcher (if Install Manager installed)
py -3.12 --version
```

### References

- **Official Documentation**: https://docs.python.org/dev/using/windows.html
- **Python Downloads**: https://www.python.org/downloads/
- **Python Install Manager**: Available in Microsoft Store or python.org

### Quick Start Script

Our `quick_start.bat` script follows Python's recommendations:

1. ✅ Detects Python using official commands (`python`, `py`, `pymanager`)
2. ✅ Creates virtual environment (recommended practice)
3. ✅ Uses `python -m venv` (official method)
4. ✅ Activates virtual environment before installing packages
5. ✅ Installs dependencies in isolated environment

### Best Practices

According to Python documentation:

1. **Use virtual environments** for each project
2. **Use `python` command** for launching (it's smart about versions)
3. **Use `py` command** when you need version selection
4. **Keep Python Install Manager updated** (auto-updates)

### Example Workflow

```batch
REM 1. Install Python Install Manager (one-time)
REM    - Via Microsoft Store or python.org

REM 2. Run our setup script
quick_start.bat

REM 3. Script automatically:
REM    - Detects Python
REM    - Creates venv
REM    - Installs dependencies
REM    - Sets up browser

REM 4. Use the project
python -m automation.main
```
