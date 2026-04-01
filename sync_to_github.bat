@echo off
chcp 65001 >nul
echo ========================================
echo   Git 自动同步脚本
echo   GitHub: xuan15x/Translation
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查本地状态...
git status --short
if %errorlevel% neq 0 (
    echo ❌ Git 状态检查失败
    pause
    exit /b 1
)
echo ✅ 本地状态正常
echo.

echo [2/4] Fetch 远程更新...
git fetch origin
if %errorlevel% neq 0 (
    echo ❌ Fetch 失败
    pause
    exit /b 1
)
echo ✅ Fetch 完成
echo.

echo [3/4] Pull 远程变更...
git pull origin main --rebase
if %errorlevel% neq 0 (
    echo ⚠️  Pull 有冲突，请手动解决
    pause
    exit /b 1
)
echo ✅ Pull 完成
echo.

echo [4/4] Push 本地提交...
git push origin main
if %errorlevel% neq 0 (
    echo ❌ Push 失败
    pause
    exit /b 1
)
echo ✅ Push 完成
echo.

echo ========================================
echo   ✅ 同步完成！
echo   仓库：https://github.com/xuan15x/Translation
echo ========================================
pause
