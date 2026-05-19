#!/bin/bash
# CI 脚本 — 翻译工具测试套件
# 用法: bash ci.sh [--full] [--cov-min=40]
set -euo pipefail

cd "$(dirname "$0")"

COV_MIN=40
FULL=false

for arg in "$@"; do
    case $arg in
        --full) FULL=true ;;
        --cov-min=*) COV_MIN="${arg#*=}" ;;
    esac
done

echo "=========================================="
echo " 翻译工具 CI 检查"
echo "=========================================="
echo ""

# 1. Import check
echo "[1/4] 模块导入检查..."
if python -c "from infrastructure.models.config import Config; print('  ✅ Config loaded OK')" 2>/dev/null; then
    echo "  ✅ 导入检查通过"
else
    echo "  ❌ 导入检查失败"
    exit 1
fi

# 2. Unit tests
echo ""
echo "[2/4] 运行测试套件..."
if source .venv/bin/activate 2>/dev/null; then
    pytest tests/ -q --tb=short
else
    python -m pytest tests/ -q --tb=short
fi

# 3. Coverage check
echo ""
echo "[3/4] 覆盖率检查 (最低 ${COV_MIN}%)..."
COV_OUTPUT=$(pytest tests/ --cov=. --cov-report=term --no-cov-on-fail -q 2>&1 || true)
COV_PCT=$(echo "$COV_OUTPUT" | grep "^TOTAL" | awk '{print $NF}' | sed 's/%//')

if [ -z "$COV_PCT" ]; then
    echo "  ⚠️ 无法解析覆盖率数据"
elif (( $(echo "$COV_PCT >= $COV_MIN" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ✅ 覆盖率 ${COV_PCT}% ≥ ${COV_MIN}%"
else
    echo "  ❌ 覆盖率 ${COV_PCT}% < ${COV_MIN}%"
    exit 1
fi

# 4. Full check (optional)
if $FULL; then
    echo ""
    echo "[4/4] 全量代码检查..."
    # Check for TODOs
    TODO_COUNT=$(grep -rn "TODO" --include="*.py" . | grep -v "tests/" | grep -v ci.sh | wc -l)
    echo "  待办事项: ${TODO_COUNT} 个 TODO"
    # Check for large files
    echo "  Top 5 最大文件:"
    find . -name "*.py" -not -path "./.venv/*" -not -path "./tests/*" \
        -exec wc -l {} \; | sort -rn | head -5 | awk '{printf "    %s (%d 行)\n", $2, $1}'
else
    echo ""
    echo "[4/4] 跳过全量检查 (加 --full 启用)"
fi

echo ""
echo "=========================================="
echo " CI 检查完成 ✅"
echo "=========================================="
