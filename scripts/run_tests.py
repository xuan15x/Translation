"""
运行所有单元测试的脚本
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """运行 pytest 测试套件"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 构建 pytest 命令
    cmd = [
        sys.executable, '-m', 'pytest',
        str(project_root / 'tests'),
        '-v',  # 详细输出
        '--tb=short',  # 简短的错误追踪
        '--cov=.',  # 覆盖率报告
        '--cov-report=term-missing',  # 终端显示缺失行
        '--cov-report=html:htmlcov',  # HTML 报告
        '--html=test_report.html',  # HTML 测试报告
        '--self-contained-html'  # 独立 HTML 文件
    ]
    
    print("=" * 60)
    print("开始运行单元测试...")
    print("=" * 60)
    
    # 执行测试
    result = subprocess.run(cmd, cwd=str(project_root))
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"❌ {result.returncode} 个测试失败")
    print("=" * 60)
    
    print("\n📊 查看测试报告:")
    print(f"   - HTML 报告：{project_root / 'test_report.html'}")
    print(f"   - 覆盖率报告：{project_root / 'htmlcov' / 'index.html'}")
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())
