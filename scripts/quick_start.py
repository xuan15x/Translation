#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速配置脚本 - 5 分钟完成翻译平台配置
自动检查配置并引导用户完成设置
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)


def print_banner():
    """打印欢迎横幅"""
    print("=" * 70)
    print("  AI 智能翻译平台 - 快速配置向导")
    print("  5 分钟完成配置，开始翻译！")
    print("=" * 70)
    print()


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 版本过低，需要 3.8+")
        print(f"   当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python 版本：{version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """检查依赖项"""
    required_packages = ['openpyxl', 'pandas', 'aiohttp']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ 已安装：{package}")
        except ImportError:
            missing.append(package)
            print(f"❌ 缺失：{package}")
    
    if missing:
        print("\n💡 请运行以下命令安装缺失的依赖:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True


def check_config_file():
    """检查配置文件是否存在"""
    config_paths = [
        "config/config.json",
        "config/config.yaml",
        "config.json",
        "config.yaml"
    ]
    
    for path in config_paths:
        if Path(path).exists():
            print(f"✅ 找到配置文件：{path}")
            return path
    
    print("❌ 未找到配置文件")
    return None


def create_config_from_example():
    """从示例文件创建配置文件"""
    example_paths = [
        "config/config.example.json",
        "config/config.example.yaml"
    ]
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    for example_path in example_paths:
        if Path(example_path).exists():
            if example_path.endswith('.json'):
                target_path = config_dir / "config.json"
            else:
                target_path = config_dir / "config.yaml"
            
            print(f"📝 从 {example_path} 创建配置文件...")
            
            # 读取示例配置
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 保存为新配置文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 配置文件已创建：{target_path}")
            return str(target_path)
    
    print("❌ 未找到示例配置文件")
    return None


def get_api_key_interactive():
    """交互式获取 API Key"""
    print("\n" + "=" * 70)
    print("  配置 API 密钥")
    print("=" * 70)
    print()
    print("请选择 API 提供商:")
    print("  1. DeepSeek (推荐，性价比高)")
    print("  2. OpenAI")
    print("  3. Azure OpenAI")
    print("  4. 自定义 API")
    print()
    
    choice = input("请输入选择 (1-4): ").strip()
    
    providers = {
        '1': 'deepseek',
        '2': 'openai',
        '3': 'azure_openai',
        '4': 'custom'
    }
    
    provider = providers.get(choice, 'deepseek')
    
    print(f"\n已选择：{provider}")
    print()
    print("请输入 API Key:")
    print("💡 提示：如果是 DeepSeek，访问 https://platform.deepseek.com/ 获取")
    print("💡 提示：如果是 OpenAI，访问 https://platform.openai.com/ 获取")
    print()
    
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return None, None
    
    # 隐藏显示 API Key（只显示前后缀）
    masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
    print(f"✅ API Key 已设置：{masked}")
    
    return provider, api_key


def update_config_api_key(config_path: str, provider: str, api_key: str):
    """更新配置文件中的 API Key"""
    print(f"\n📝 更新配置文件：{config_path}")
    
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            # 移除 JSON 注释（// 开头的行）
            lines = []
            for line in f:
                if '//' in line:
                    # 保留 // 前面的内容
                    before_comment = line.split('//')[0]
                    if before_comment.strip():
                        lines.append(before_comment + '\n')
                else:
                    lines.append(line)
            
            config = json.loads(''.join(lines))
        
        # 更新 API Key
        if 'api_keys' in config and provider in config['api_keys']:
            config['api_keys'][provider]['api_key'] = api_key
            print(f"✅ 已更新 {provider} 的 API Key")
        else:
            # 如果没有 api_keys 结构，使用旧的 api_key 字段
            config['api_key'] = api_key
            config['api_provider'] = provider
            print(f"✅ 已设置 API Key 和提供商")
        
        # 保存更新后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件已更新")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败：{e}")
        return False


def validate_config(config_path: str):
    """验证配置文件"""
    print(f"\n🔍 验证配置文件...")
    
    try:
        from data_access.config_persistence import ConfigPersistence
        from infrastructure.models.models import Config
        
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
        print(f"⚠️ 配置验证警告：{e}")
        print("   配置可能仍可工作，但建议检查")
        return True  # 即使有警告也继续


def show_next_steps():
    """显示下一步操作"""
    print("\n" + "=" * 70)
    print("  🎉 配置完成！")
    print("=" * 70)
    print()
    print("下一步:")
    print()
    print("1. 启动翻译平台:")
    print("   Windows: 双击 启动翻译平台.bat")
    print("   或运行：python presentation/translation.py")
    print()
    print("2. 准备翻译文件:")
    print("   - 术语库：Excel 格式，包含中文原文和目标语言翻译")
    print("   - 待翻译文件：Excel 格式，包含 key 和 source_text 列")
    print()
    print("3. 开始翻译:")
    print("   - 选择术语库和待翻译文件")
    print("   - 选择目标语言")
    print("   - 点击'开始翻译任务'")
    print()
    print("📖 更多帮助:")
    print("   - 完整使用手册：COMPLETE_MANUAL.md")
    print("   - 配置填入手册：docs/guides/CONFIG_SETUP_HANDBOOK.md")
    print("   - 快速开始指南：docs/guides/QUICKSTART.md")
    print()


def main():
    """主函数"""
    print_banner()
    
    # 1. 检查环境
    print("=" * 70)
    print("  步骤 1/3: 检查环境")
    print("=" * 70)
    print()
    
    env_ok = check_python_version()
    if not env_ok:
        print("\n❌ 环境检查失败，请先升级 Python")
        return 1
    
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️ 缺少依赖项，但可继续配置")
    
    print()
    
    # 2. 检查/创建配置文件
    print("=" * 70)
    print("  步骤 2/3: 配置文件设置")
    print("=" * 70)
    print()
    
    config_path = check_config_file()
    
    if not config_path:
        print("\n📝 创建配置文件...")
        config_path = create_config_from_example()
        
        if not config_path:
            print("\n❌ 无法创建配置文件")
            return 1
    
    # 3. 配置 API Key
    print("=" * 70)
    print("  步骤 3/3: 配置 API Key")
    print("=" * 70)
    print()
    
    # 检查是否已有 API Key
    need_api_key = True
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"aa"' not in content and 'your-' not in content.lower():
                print("✅ 检测到已配置的 API Key")
                need_api_key = False
    except:
        pass
    
    if need_api_key:
        provider, api_key = get_api_key_interactive()
        
        if not api_key:
            print("\n❌ 未设置 API Key")
            return 1
        
        if not update_config_api_key(config_path, provider, api_key):
            print("\n❌ 更新配置文件失败")
            return 1
    
    # 4. 验证配置
    if not validate_config(config_path):
        print("\n⚠️ 配置验证有问题，但可能仍可工作")
    
    # 5. 显示下一步
    show_next_steps()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ 配置已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
