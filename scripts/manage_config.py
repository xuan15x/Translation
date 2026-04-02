"""
配置管理脚本
用于生成、验证和管理配置文件
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)


def create_sample_config(output_path: str = "config.yaml", format: str = "yaml"):
    """创建示例配置文件"""
    from config.config import create_sample_config_file
    
    print(f"📝 创建示例配置文件：{output_path}")
    create_sample_config_file(output_path, format)
    print(f"✅ 配置文件已创建：{output_path}")
    print("\n💡 提示：复制此文件为 config.yaml 并修改配置值")


def validate_config(config_path: str):
    """验证配置文件"""
    from data_access.config_persistence import ConfigPersistence
    from infrastructure.models import Config
    
    print(f"🔍 验证配置文件：{config_path}")
    
    try:
        persistence = ConfigPersistence(config_path)
        config_dict = persistence.load()
        
        # 尝试创建 Config 对象（会触发验证）
        config = Config(**config_dict)
        
        print("✅ 配置文件验证通过！")
        print("\n📊 配置摘要:")
        print(f"  API 提供商：{config.api_provider}")
        print(f"  模型：{config.model_name}")
        print(f"  并发度：{config.initial_concurrency} - {config.max_concurrency}")
        print(f"  超时：{config.timeout}秒")
        print(f"  工作流：{'双阶段' if config.enable_two_pass else '单阶段'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败：{e}")
        return False


def show_config_diff(config_path1: str, config_path2: str):
    """显示两个配置文件的差异"""
    from data_access.config_persistence import ConfigPersistence
    
    print(f"📊 比较配置文件:\n  {config_path1}\n  {config_path2}\n")
    
    try:
        persistence1 = ConfigPersistence(config_path1)
        config1 = persistence1.load()
        
        persistence2 = ConfigPersistence(config_path2)
        config2 = persistence2.load()
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        diffs = []
        for key in sorted(all_keys):
            val1 = config1.get(key)
            val2 = config2.get(key)
            
            if val1 != val2:
                diffs.append((key, val1, val2))
        
        if not diffs:
            print("✅ 两个配置文件完全相同")
            return
        
        print(f"发现 {len(diffs)} 处差异:\n")
        print(f"{'配置项':<30} {'文件 1':<40} {'文件 2':<40}")
        print("-" * 110)
        
        for key, val1, val2 in diffs:
            val1_str = str(val1)[:38] if val1 else "None"
            val2_str = str(val2)[:38] if val2 else "None"
            print(f"{key:<30} {val1_str:<40} {val2_str:<40}")
        
    except Exception as e:
        print(f"❌ 比较失败：{e}")


def export_env_template(config_path: str = "config.yaml", output_path: str = ".env.example"):
    """从配置文件导出环境变量模板"""
    from data_access.config_persistence import ConfigPersistence
    
    print(f"📤 从配置文件导出环境变量：{config_path}")
    
    try:
        persistence = ConfigPersistence(config_path)
        config_dict = persistence.load()
        
        env_mapping = {
            'api_key': 'API_KEY',
            'base_url': 'BASE_URL',
            'model_name': 'MODEL_NAME',
            'api_provider': 'API_PROVIDER',
            'temperature': 'TEMPERATURE',
            'top_p': 'TOP_P',
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# AI 翻译平台 - 环境变量模板\n")
            f.write("# 复制此文件为 .env 并填写实际值\n\n")
            
            for config_key, env_var in env_mapping.items():
                value = config_dict.get(config_key, '')
                if isinstance(value, str) and value:
                    f.write(f'{env_var}="{value}"\n')
                elif value:
                    f.write(f'{env_var}={value}\n')
                else:
                    f.write(f'{env_var}=\n')
        
        print(f"✅ 环境变量模板已导出：{output_path}")
        
    except Exception as e:
        print(f"❌ 导出失败：{e}")


def merge_configs(base_config: str, override_config: str, output: str):
    """合并两个配置文件（override 覆盖 base）"""
    from data_access.config_persistence import ConfigPersistence
    
    print(f"🔀 合并配置文件:")
    print(f"  基础配置：{base_config}")
    print(f"  覆盖配置：{override_config}")
    print(f"  输出：{output}")
    
    try:
        base_persistence = ConfigPersistence(base_config)
        base_dict = base_persistence.load()
        
        override_persistence = ConfigPersistence(override_config)
        override_dict = override_persistence.load()
        
        # 合并配置
        merged = base_dict.copy()
        merged.update(override_dict)
        
        # 保存合并后的配置
        output_persistence = ConfigPersistence(output)
        output_persistence.save(merged)
        
        print(f"✅ 配置合并完成：{output}")
        print(f"   共 {len(merged)} 个配置项")
        
    except Exception as e:
        print(f"❌ 合并失败：{e}")


def list_all_config_options():
    """列出所有可用的配置选项"""
    from config.config import get_default_config, DEFAULT_PROHIBITION_CONFIG
    
    default_config = get_default_config()
    
    print("\n" + "=" * 70)
    print("All Available Configuration Options")
    print("=" * 70)
    
    categories = {
        "API Configuration": ["api_provider", "api_key", "base_url", "model_name"],
        "Model Parameters": ["temperature", "top_p"],
        "Concurrency Control": ["initial_concurrency", "max_concurrency", "concurrency_cooldown_seconds"],
        "Retry Configuration": ["retry_streak_threshold", "base_retry_delay", "max_retries", "timeout"],
        "Workflow Configuration": ["enable_two_pass", "skip_review_if_local_hit", "batch_size", "gc_interval"],
        "Terminology Configuration": ["similarity_low", "exact_match_score", "multiprocess_threshold"],
        "Performance Optimization": ["pool_size", "cache_capacity", "cache_ttl_seconds"],
        "Logging Configuration": ["log_level", "log_granularity", "log_max_lines"],
        "GUI Configuration": ["gui_window_title", "gui_window_width", "gui_window_height"],
        "Prompt Configuration": ["draft_prompt", "review_prompt"],
        "Prohibition Configuration": ["prohibition_config", "prohibition_type_map"],
        "Language Configuration": ["target_languages", "default_source_lang", "supported_source_langs"],
        "Version Control & Backup": ["enable_version_control", "enable_auto_backup", "backup_dir", "backup_strategy"],
        "Performance Monitoring": ["enable_performance_monitor", "perf_sample_interval", "perf_history_size"],
    }
    
    for category, keys in categories.items():
        print(f"\n{category}:")
        print("-" * 50)
        for key in keys:
            if key == 'prohibition_config':
                # 特殊处理禁止事项配置
                print(f"  {key:<30} = Contains {len(DEFAULT_PROHIBITION_CONFIG)} categories of rules")
                for ptype, rules in DEFAULT_PROHIBITION_CONFIG.items():
                    print(f"    - {ptype}: {len(rules)} rules")
            elif key == 'prohibition_type_map':
                print(f"  {key:<30} = Maps translation types to prohibition rules")
            else:
                value = default_config.get(key, "N/A")
                value_str = str(value)[:60]
                if isinstance(value, str) and '\n' in value:
                    value_str = "(multi-line text)"
                print(f"  {key:<30} = {value_str}")


def show_prohibition_details():
    """显示禁止事项配置详情"""
    from config.config import DEFAULT_PROHIBITION_CONFIG, DEFAULT_PROHIBITION_TYPE_MAP
    
    print("\n" + "=" * 70)
    print("Prohibition Configuration Details")
    print("=" * 70)
    
    # 显示禁止事项类别
    print("\nProhibition Categories:")
    print("-" * 70)
    for category, rules in DEFAULT_PROHIBITION_CONFIG.items():
        print(f"\n{category}:")
        print(f"  Rules: {len(rules)}")
        for i, rule in enumerate(rules, 1):
            print(f"  {i}. {rule}")
    
    # 显示类型映射
    print("\n\nTranslation Type Mapping:")
    print("-" * 70)
    for trans_type, categories in DEFAULT_PROHIBITION_TYPE_MAP.items():
        print(f"  {trans_type:<20} -> {', '.join(categories)} ({len(categories)} categories)")
    
    print("\n" + "=" * 70)
    print("Tip: Customize these rules in config/config.json")
    print("Docs: docs/guides/PROHIBITION_CONFIG_GUIDE.md")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 翻译平台配置管理工具")
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建示例配置文件')
    create_parser.add_argument('-o', '--output', default='config.yaml', help='输出文件路径')
    create_parser.add_argument('-f', '--format', choices=['yaml', 'json'], default='yaml', 
                              help='文件格式（默认 YAML）')
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证配置文件')
    validate_parser.add_argument('config', help='配置文件路径')
    
    # diff 命令
    diff_parser = subparsers.add_parser('diff', help='比较两个配置文件')
    diff_parser.add_argument('file1', help='第一个配置文件')
    diff_parser.add_argument('file2', help='第二个配置文件')
    
    # export-env 命令
    env_parser = subparsers.add_parser('export-env', help='导出环境变量模板')
    env_parser.add_argument('-c', '--config', default='config.yaml', help='配置文件路径')
    env_parser.add_argument('-o', '--output', default='.env.example', help='输出文件路径')
    
    # merge 命令
    merge_parser = subparsers.add_parser('merge', help='合并配置文件')
    merge_parser.add_argument('base', help='基础配置文件')
    merge_parser.add_argument('override', help='覆盖配置文件')
    merge_parser.add_argument('-o', '--output', default='config.merged.yaml', help='输出文件路径')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有配置选项')
    
    # prohibitions 命令
    prohibit_parser = subparsers.add_parser('prohibitions', help='显示禁止事项配置详情')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_sample_config(args.output, args.format)
    elif args.command == 'validate':
        success = validate_config(args.config)
        sys.exit(0 if success else 1)
    elif args.command == 'diff':
        show_config_diff(args.file1, args.file2)
    elif args.command == 'export-env':
        export_env_template(args.config, args.output)
    elif args.command == 'merge':
        merge_configs(args.base, args.override, args.output)
    elif args.command == 'list':
        list_all_config_options()
    elif args.command == 'prohibitions':
        show_prohibition_details()
    else:
        parser.print_help()
        print("\n示例用法:")
        print("  python manage_config.py create")
        print("  python manage_config.py validate config.yaml")
        print("  python manage_config.py diff config.example.yaml config.yaml")
        print("  python manage_config.py export-env")
        print("  python manage_config.py merge base.yaml custom.yaml")
        print("  python manage_config.py list")
        print("  python manage_config.py prohibitions  # 查看禁止事项配置详情")


if __name__ == "__main__":
    main()
