"""
一键启动脚本 - 简化启动流程

提供交互式配置、自动检测、智能推荐等功能。
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 70)
    print(" " * 20 + "AI 智能翻译工作台")
    print(" " * 25 + "v3.0 简化版")
    print("=" * 70 + "\n")


def check_config_exists() -> bool:
    """检查配置文件是否存在"""
    config_paths = [
        Path("config/config.json"),
        Path("config/config.yaml"),
        Path("config.json"),
        Path("config.yaml"),
    ]
    
    for path in config_paths:
        if path.exists():
            return True
    
    return False


def quick_setup_wizard():
    """快速配置向导"""
    print("\n")
    print("🎉 欢迎使用 AI 智能翻译工作台！")
    print("看起来这是第一次运行，让我们花 1 分钟完成初始配置吧~\n")
    
    # 步骤 1: 选择模式
    print("=" * 70)
    print("步骤 1/3: 选择使用模式")
    print("-" * 70)
    print("1. 🐣 新手模式     - 最简单配置，只需设置 API Key（推荐）")
    print("2. ⚖️  平衡模式     - 性能与质量的平衡（推荐）")
    print("3. 🏆 高质量模式   - 翻译质量优先，适合重要文档")
    print("4. ⚡ 快速模式     - 翻译速度优先，适合大批量")
    print()
    
    mode_choice = input("请选择模式 (1-4，默认 1): ").strip() or "1"
    
    modes = {
        '1': 'beginner',
        '2': 'balanced',
        '3': 'quality',
        '4': 'speed',
    }
    
    selected_mode = modes.get(mode_choice, 'beginner')
    print(f"✅ 已选择：{modes[selected_mode]}\n")
    
    # 步骤 2: 输入 API Key
    print("=" * 70)
    print("步骤 2/3: 配置 API Key")
    print("-" * 70)
    print("💡 提示：API Key 可以从 DeepSeek 官网获取：https://platform.deepseek.com/")
    print()
    
    api_key = input("请输入您的 DeepSeek API Key: ").strip()
    
    while not api_key:
        print("❌ API Key 不能为空！")
        api_key = input("请重新输入 API Key: ").strip()
    
    print(f"✅ API Key 已设置（{'*' * 10}{api_key[-4:]})\n")
    
    # 步骤 3: 确认配置
    print("=" * 70)
    print("步骤 3/3: 确认配置")
    print("-" * 70)
    
    from infrastructure.smart_config import SmartConfigurator
    
    configurator = SmartConfigurator()
    config = configurator.quick_setup(api_key, selected_mode)
    
    print("\n📋 配置摘要:")
    print(f"   使用模式：{configurator.PRESETS[selected_mode]['name']}")
    print(f"   模型名称：{config['model_name']}")
    print(f"   并发范围：{config['initial_concurrency']}-{config['max_concurrency']}")
    print(f"   超时时间：{config['timeout']}秒")
    print()
    
    confirm = input("是否保存配置？(Y/n): ").strip().lower() or "y"
    
    if confirm == 'y':
        # 确保 config 目录存在
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # 保存配置
        config_path = config_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 配置已保存到：{config_path}")
        print("💡 稍后可以在 config/config.json 文件中修改配置\n")
    else:
        print("\n⚠️  配置未保存，下次启动时需要重新配置\n")
    
    return True


def start_gui():
    """启动 GUI 应用"""
    print("\n")
    print("=" * 70)
    print("正在启动翻译平台...")
    print("=" * 70 + "\n")
    
    try:
        from presentation.gui_app import TranslationApp
        import tkinter as tk
        
        root = tk.Tk()
        app = TranslationApp(root)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("\n💡 建议:")
        print("   1. 检查是否正确安装依赖：pip install -r requirements.txt")
        print("   2. 查看日志文件获取详细错误信息")
        return False


def main():
    """主函数"""
    print_banner()
    
    # 检查配置文件
    if not check_config_exists():
        print("⚠️  未检测到配置文件\n")
        
        setup = input("是否需要快速配置向导？(Y/n): ").strip().lower() or "y"
        
        if setup == 'y':
            quick_setup_wizard()
        else:
            print("\n❌ 没有配置文件无法启动")
            print("\n💡 您可以:")
            print("   1. 运行配置向导：python scripts/quick_start.py --setup")
            print("   2. 手动创建配置文件：复制 config/config.example.json 为 config/config.json")
            return 1
    
    # 启动 GUI
    success = start_gui()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
