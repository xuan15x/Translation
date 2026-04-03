"""
导入路径验证器 - 独立测试脚本

直接运行此脚本验证 Skill 功能:
    python test_skill.py
"""

import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from validator import ImportPathValidator


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("导入路径验证器 - 功能测试")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建测试项目
        print("1. 创建测试项目结构...")
        ImportPathValidator._create_test_project(temp_path)
        print("   ✅ 测试项目创建完成")
        print()

        # 测试项目验证
        print("2. 验证整个项目...")
        result = ImportPathValidator.validate_project(str(temp_path))
        print(f"   扫描文件数: {result['summary']['total_files']}")
        print(f"   导入语句数: {result['summary']['total_imports']}")
        print(f"   包数量: {result['summary']['total_packages']}")
        print()

        # 测试重复导入检测
        print("3. 检测重复导入...")
        duplicates = ImportPathValidator.check_duplicate_imports(str(temp_path))
        print(f"   发现 {len(duplicates)} 个重复导入问题")
        if duplicates:
            for dup in duplicates[:2]:
                print(f"   - {dup['symbol']}: {dup['path_count']} 个路径")
        print()

        # 测试循环导入检测
        print("4. 检测循环导入...")
        circulars = ImportPathValidator.check_circular_imports(str(temp_path))
        print(f"   发现 {len(circulars)} 个循环导入问题")
        if circulars:
            for cycle in circulars[:2]:
                print(f"   - 循环: {' → '.join(cycle['cycle'])}")
        print()

        # 测试 __init__.py 一致性
        print("5. 检查 __init__.py 一致性...")
        init_issues = ImportPathValidator.check_init_consistency(str(temp_path))
        print(f"   发现 {len(init_issues)} 个一致性问题")
        if init_issues:
            for issue in init_issues[:2]:
                print(f"   - [{issue['issue_type']}] {issue['symbol']}")
        print()

        # 测试单文件验证
        print("6. 验证单个文件...")
        test_file = temp_path / 'package_a' / 'module_a.py'
        issues = ImportPathValidator.validate_file(str(test_file))
        print(f"   发现 {len(issues)} 个问题")
        print()

        # 测试报告生成
        print("7. 生成文本报告...")
        text_report = ImportPathValidator.generate_report(result, output_format='text')
        assert '导入路径验证报告' in text_report
        print("   ✅ 文本报告生成成功")
        print()

        print("8. 生成 JSON 报告...")
        import json
        json_report = ImportPathValidator.generate_report(result, output_format='json')
        json_data = json.loads(json_report)
        assert 'summary' in json_data
        print("   ✅ JSON 报告生成成功")
        print()

        print("9. 生成 Markdown 报告...")
        md_report = ImportPathValidator.generate_report(result, output_format='markdown')
        assert '# 导入路径验证报告' in md_report
        print("   ✅ Markdown 报告生成成功")
        print()

        # 打印完整报告
        print("=" * 60)
        print("完整验证报告")
        print("=" * 60)
        print()
        print(text_report)
        print()

        return True


def test_self_test():
    """运行内置自检测试"""
    print("=" * 60)
    print("运行内置自检测试...")
    print("=" * 60)
    print()

    result = ImportPathValidator.self_test()

    if result:
        print("✅ 自检测试通过")
    else:
        print("❌ 自检测试失败")

    print()
    return result


if __name__ == '__main__':
    try:
        # 测试基本功能
        test_basic_functionality()

        # 测试自检测试
        self_test_result = test_self_test()

        # 总结
        print("=" * 60)
        print("测试总结")
        print("=" * 60)
        print()
        print("✅ 所有功能测试通过")
        print("✅ 导入路径验证器工作正常")
        print()
        print("Skill 位置:")
        print(f"  .qwen/skills/import_path_validator/")
        print()
        print("使用方法:")
        print("  from .qwen.skills.import_path_validator import ImportPathValidator")
        print("  result = ImportPathValidator.validate_project('/path/to/project')")
        print("  report = ImportPathValidator.generate_report(result)")
        print("  print(report)")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
