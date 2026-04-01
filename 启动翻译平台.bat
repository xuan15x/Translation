@echo off
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

REM Start application from current directory
python -u presentation\translation.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================
echo   Application closed
echo ========================================
pause
