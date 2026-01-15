@echo off
REM League of Legends Role Quest Calculator - Windows Launcher

echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Checking for required packages...
python -c "import matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install packages
        echo Try running: pip install matplotlib numpy
        pause
        exit /b 1
    )
)

echo.
echo Launching LoL Role Quest Calculator...
echo.
python launcher.py

pause
