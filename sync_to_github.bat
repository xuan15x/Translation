@echo off
chcp 65001 >nul
echo ========================================
echo   Git Auto Sync Script
echo   GitHub: xuan15x/Translation
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking local status...
git status --short
if %errorlevel% neq 0 (
    echo ERROR: Git status check failed
    pause
    exit /b 1
)
echo OK: Local status checked
echo.

echo [2/4] Fetching remote updates...
git fetch origin
if %errorlevel% neq 0 (
    echo ERROR: Fetch failed
    pause
    exit /b 1
)
echo OK: Fetch completed
echo.

echo [3/4] Pulling remote changes...
git pull origin main --rebase
if %errorlevel% neq 0 (
    echo WARNING: Pull has conflicts, please resolve manually
    pause
    exit /b 1
)
echo OK: Pull completed
echo.

echo [4/4] Pushing local commits...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Push failed
    pause
    exit /b 1
)
echo OK: Push completed
echo.

echo ========================================
echo   SUCCESS: Sync completed!
echo   Repository: https://github.com/xuan15x/Translation
echo ========================================
pause
