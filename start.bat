@echo off
title Text Replacer
cd /d "%~dp0"

REM Check that Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found.
    echo Install Python 3.10+ from https://www.python.org/
    echo During install, enable the "Add Python to PATH" checkbox.
    echo.
    pause
    exit /b 1
)

REM Install dependencies on first run
if not exist ".installed" (
    echo First run - installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo. > .installed
)

python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] The program exited with an error.
    pause
)
