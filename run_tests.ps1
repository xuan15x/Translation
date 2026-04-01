# 运行所有单元测试的 PowerShell 脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始运行单元测试..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 切换到项目目录
Set-Location $PSScriptRoot

# 运行 pytest
python -m pytest tests/ `
    -v `
    --tb=short `
    --cov=. `
    --cov-report=term-missing `
    --cov-report=html:htmlcov `
    --html=test_report.html `
    --self-contained-html

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✅ 所有测试通过！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "❌ $LASTEXITCODE 个测试失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host "`n📊 查看测试报告:" -ForegroundColor Yellow
Write-Host "   - HTML 报告：$PWD\test_report.html"
Write-Host "   - 覆盖率报告：$PWD\htmlcov\index.html"
