@echo off
title Universal Harvester Setup
echo.
echo ===============================================
echo   UNIVERSAL HARVESTER SETUP
echo ===============================================
echo.

set ROOT=%~dp0
cd /d "%ROOT%"

REM ----------------------------------------
REM STEP 1 - Check Python
REM ----------------------------------------
echo [STEP 1] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
for /f "delims=" %%i in ('where python') do set PYTHON=%%i
echo   [OK] Python found: %PYTHON%

REM ----------------------------------------
REM STEP 2 - Create or Repair venv
REM ----------------------------------------
echo.
echo [STEP 2] Creating or repairing virtual environment...
set VENV=%ROOT%.venv
set PYVENV=%VENV%\Scripts\python.exe

if not exist "%VENV%" (
    python -m venv "%VENV%"
)
if not exist "%PYVENV%" (
    rmdir /s /q "%VENV%"
    python -m venv "%VENV%"
)
echo   [OK] Virtual environment ready.

REM ----------------------------------------
REM STEP 3 - Install dependencies
REM ----------------------------------------
echo.
echo [STEP 3] Installing dependencies...
"%PYVENV%" -m pip install --upgrade pip
"%PYVENV%" -m pip install -r requirements.txt
echo   [OK] Dependencies installed.

REM ----------------------------------------
REM STEP 4 - Install Playwright Browsers
REM ----------------------------------------
echo.
echo [STEP 4] Installing Playwright browsers (for UI Fallback)...
"%PYVENV%" -m playwright install chromium
echo   [OK] Playwright ready.

echo.
echo ===============================================
echo   SETUP COMPLETE
echo ===============================================
echo To run the pipeline:
echo   .venv\Scripts\python run_pipeline.py
echo.
pause
