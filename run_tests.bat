@echo off
chcp 65001 >nul
echo ========================================
echo 开始运行单元测试...
echo ========================================

cd /d %~dp0

python -m pytest tests/ ^
    -v ^
    --tb=short ^
    --cov=. ^
    --cov-report=term-missing ^
    --cov-report=html:htmlcov ^
    --html=test_report.html ^
    --self-contained-html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 所有测试通过！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ❌ %ERRORLEVEL% 个测试失败
    echo ========================================
)

echo.
echo 📊 查看测试报告:
echo    - HTML 报告：%cd%\test_report.html
echo    - 覆盖率报告：%cd%\htmlcov\index.html

pause
