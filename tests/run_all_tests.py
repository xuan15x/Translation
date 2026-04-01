"""
综合测试运行器
运行所有测试并生成详细报告
"""
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """测试运行器"""
    
    def __init__(self, output_dir: str = "test_reports"):
        """
        初始化测试运行器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("\n" + "=" * 60)
        print("📋 运行单元测试")
        print("=" * 60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/',
            '-v',
            '--tb=short',
            '--ignore=tests/test_integration.py',
            '--ignore=tests/test_performance.py',
            '--ignore=tests/test_gui_automation.py',
            f'--html={self.output_dir}/unit_tests_report.html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results['tests']['unit'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(result.stdout)
        return result.returncode == 0
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("\n" + "=" * 60)
        print("🔗 运行集成测试")
        print("=" * 60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_integration.py',
            '-v',
            '--tb=short',
            f'--html={self.output_dir}/integration_tests_report.html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results['tests']['integration'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(result.stdout)
        return result.returncode == 0
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("\n" + "=" * 60)
        print("⚡ 运行性能测试")
        print("=" * 60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_performance.py',
            '-v',
            '--tb=short',
            f'--html={self.output_dir}/performance_tests_report.html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results['tests']['performance'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(result.stdout)
        return result.returncode == 0
    
    def run_gui_tests(self):
        """运行 GUI 测试"""
        print("\n" + "=" * 60)
        print("🖥️  运行 GUI 测试")
        print("=" * 60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_gui_automation.py',
            '-v',
            '--tb=short',
            f'--html={self.output_dir}/gui_tests_report.html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results['tests']['gui'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(result.stdout)
        return result.returncode == 0
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("🚀 开始运行完整测试套件")
        print("=" * 60)
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'unit': self.run_unit_tests(),
            'integration': self.run_integration_tests(),
            'performance': self.run_performance_tests(),
            'gui': self.run_gui_tests()
        }
        
        # 生成总结报告
        self._generate_summary(results)
        
        return all(results.values())
    
    def _generate_summary(self, results: dict):
        """生成测试总结报告"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r)
        failed_tests = total_tests - passed_tests
        
        summary = f"""
# 测试总结报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体结果

- **总测试类别**: {total_tests}
- **通过**: {passed_tests} ✅
- **失败**: {failed_tests} ❌
- **成功率**: {(passed_tests/total_tests*100):.1f}%

## 详细结果

"""
        
        for test_type, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            summary += f"- **{test_type.title()} Tests**: {status}\n"
        
        summary += f"""
## 测试报告文件

- [单元测试报告]({self.output_dir}/unit_tests_report.html)
- [集成测试报告]({self.output_dir}/integration_tests_report.html)
- [性能测试报告]({self.output_dir}/performance_tests_report.html)
- [GUI 测试报告]({self.output_dir}/gui_tests_report.html)

## 下一步建议

"""
        
        if not results['integration']:
            summary += "1. ⚠️ 优先修复集成测试失败问题\n"
        if not results['performance']:
            summary += "2. ⚠️ 优化性能瓶颈\n"
        if not results['gui']:
            summary += "3. ⚠️ 修复 GUI 测试问题\n"
        
        if all(results.values()):
            summary += "\n🎉 所有测试通过！系统状态良好。\n"
        
        # 保存总结报告
        summary_file = self.output_dir / 'TEST_SUMMARY.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # 保存 JSON 结果
        json_file = self.output_dir / 'test_results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(summary)
        print(f"\n详细报告已保存到：{self.output_dir}")


def main():
    """主函数"""
    runner = TestRunner()
    
    # 运行所有测试
    success = runner.run_all_tests()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
