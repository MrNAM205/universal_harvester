@echo off
title Universal Harvester Installer
echo.
echo ===============================================
echo   UNIVERSAL HARVESTER WINDOWS INSTALLER
echo ===============================================
echo.

set ROOT=%~dp0
cd /d "%ROOT%"

REM ----------------------------------------
REM STEP 1 — Check Python
REM ----------------------------------------
echo [STEP 1] Checking Python installation...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   ✖ Python not found.
    echo   Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON=%%i
echo   ✔ Python found: %PYTHON%

REM ----------------------------------------
REM STEP 2 — Create / repair venv
REM ----------------------------------------
echo.
echo [STEP 2] Creating or repairing virtual environment...

set VENV=%ROOT%.venv
set PYVENV=%VENV%\Scripts\python.exe

if not exist "%VENV%" (
    echo   -> Creating new venv...
    python -m venv "%VENV%"
) else (
    echo   -> venv already exists.
)

if not exist "%PYVENV%" (
    echo   ✖ venv corrupted, recreating...
    rmdir /s /q "%VENV%"
    python -m venv "%VENV%"
)

echo   ✔ venv ready

REM ----------------------------------------
REM STEP 3 — Install dependencies
REM ----------------------------------------
echo.
echo [STEP 3] Installing dependencies...

if not exist "%ROOT%requirements.txt" (
    echo   ✖ requirements.txt missing
    pause
    exit /b 1
)

"%PYVENV%" -m pip install --upgrade pip
"%PYVENV%" -m pip install -r requirements.txt

echo   ✔ Dependencies installed

REM ----------------------------------------
REM STEP 4 — Ensure package structure
REM ----------------------------------------
echo.
echo [STEP 4] Ensuring package structure...

set PKG=%ROOT%universal_harvester
set AGENT=%PKG%\agent
set UTILS=%PKG%\utils

for %%d in ("%PKG%" "%AGENT%" "%UTILS%") do (
    if not exist "%%~d" (
        echo   -> Creating missing directory: %%~d
        mkdir "%%~d"
    ) else (
        echo   ✔ %%~d
    )
)

for %%f in ("%PKG%\__init__.py" "%AGENT%\__init__.py" "%UTILS%\__init__.py") do (
    if not exist "%%~f" (
        echo   -> Creating missing __init__.py: %%~f
        echo # auto-generated> "%%~f"
    ) else (
        echo   ✔ %%~f
    )
)

REM ----------------------------------------
REM STEP 5 — Run validator
REM ----------------------------------------
echo.
echo [STEP 5] Running module validator...

if exist "%ROOT%validate_modules.py" (
    "%PYVENV%" validate_modules.py
) else (
    echo   ✖ validate_modules.py missing
)

REM ----------------------------------------
REM STEP 6 — Run health check
REM ----------------------------------------
echo.
echo [STEP 6] Running health check...

if exist "%ROOT%health_check.py" (
    "%PYVENV%" health_check.py
) else (
    echo   ✖ health_check.py missing
)

echo.
echo ===============================================
echo   INSTALLATION COMPLETE
echo ===============================================
echo.
echo To run the harvester:
echo.
echo   "%PYVENV%" run_pipeline.py
echo.
pause