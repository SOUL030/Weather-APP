@echo off
title Atmos Weather App
color 0B

echo.
echo  =========================================
echo    ATMOS - Weather App Launcher
echo  =========================================
echo.

REM ── Check if Python is installed ──────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.6+ from:
    echo    https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM ── Show detected Python version ──────────────────────────────────────────
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  Python detected: %PYVER%

REM ── Check if weather_app.py exists ────────────────────────────────────────
if not exist "%~dp0weather_app.py" (
    echo.
    echo  [ERROR] weather_app.py not found in:
    echo    %~dp0
    echo.
    echo  Make sure this .bat file is in the same folder as weather_app.py
    echo.
    pause
    exit /b 1
)

REM ── Check if API key has been configured ──────────────────────────────────
findstr /c:"YOUR_OPENWEATHERMAP_API_KEY" "%~dp0weather_app.py" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  =========================================
    echo   [WARNING] API Key Not Configured!
    echo  =========================================
    echo.
    echo  You have not set your OpenWeatherMap API key yet.
    echo.
    echo  Steps to fix:
    echo    1. Get a free key at https://openweathermap.org/api
    echo    2. Open weather_app.py in a text editor
    echo    3. Replace YOUR_OPENWEATHERMAP_API_KEY with your real key
    echo    4. Run this launcher again
    echo.
    choice /c YN /m "  Launch anyway? [Y/N]"
    if errorlevel 2 (
        echo.
        echo  Exiting. Configure your API key and try again.
        pause
        exit /b 0
    )
)

REM ── Launch the app ────────────────────────────────────────────────────────
echo.
echo  Starting Atmos Weather App...
echo.

python "%~dp0weather_app.py"

REM ── Handle crash ──────────────────────────────────────────────────────────
if %errorlevel% neq 0 (
    echo.
    echo  =========================================
    echo   [ERROR] App exited with an error.
    echo  =========================================
    echo.
    echo  Common fixes:
    echo    - Ensure tkinter is available (python3-tk on Linux)
    echo    - Check your API key in weather_app.py
    echo    - Verify your internet connection
    echo.
    pause
)
