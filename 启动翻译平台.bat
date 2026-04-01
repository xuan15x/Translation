@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title AI Translation Platform v3.0

echo ========================================
echo   AI Translation Platform v3.0
echo   Starting...
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set CONFIG_FILE_JSON=%SCRIPT_DIR%config\config.json
set CONFIG_FILE_YAML=%SCRIPT_DIR%config\config.yaml

echo [INFO] Checking config files...
echo [DEBUG] SCRIPT_DIR=%SCRIPT_DIR%
echo [DEBUG] CONFIG_FILE_JSON=%CONFIG_FILE_JSON%

REM Try YAML first (supports comments), then JSON
if exist "%CONFIG_FILE_YAML%" (
    set CONFIG_FILE=%CONFIG_FILE_YAML%
    echo [OK] YAML config found: !CONFIG_FILE!
    echo [INFO] Starting GUI with YAML config...
    python -u presentation\translation.py "!CONFIG_FILE!"
) else if exist "%CONFIG_FILE_JSON%" (
    set CONFIG_FILE=%CONFIG_FILE_JSON%
    echo [OK] JSON config found: !CONFIG_FILE!
    echo [INFO] Starting GUI with JSON config...
    python -u presentation\translation.py "!CONFIG_FILE!"
) else (
    echo [WARNING] No config file found
    echo [INFO] Starting GUI without config file...
    python -u presentation\translation.py
)

echo.
echo ========================================
echo   Application closed
echo ========================================
pause
