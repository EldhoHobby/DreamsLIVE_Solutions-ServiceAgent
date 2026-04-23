@echo off
setlocal

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

echo Setting up virtual environment in .venv...
python -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b %errorlevel%
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    echo Note: PyAudio might require PortAudio headers on some systems.
    pause
    exit /b %errorlevel%
)

echo.
echo Setup complete! To activate the environment in the future, run:
echo .venv\Scripts\activate
pause
