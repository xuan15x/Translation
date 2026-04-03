"""
测试禁止事项配置功能 - 验证禁止事项可以从配置文件加载并正确注入
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from config.config import (
    get_prohibition_config, 
    get_prohibition_type_map,
    DEFAULT_PROHIBITION_CONFIG,
    DEFAULT_PROHIBITION_TYPE_MAP
)
from infrastructure.prompt_injector import get_prompt_injector


def test_config_loading():
    """测试配置加载"""
    print("=" * 60)
    print("🧪 测试 1: 配置加载功能")
    print("=" * 60)
    
    # 测试获取禁止事项配置
    config = get_prohibition_config()
    print(f"\n✅ 成功加载禁止事项配置")
    print(f"   配置项数：{len(config)}")
    print(f"   包含的类别：{list(config.keys())}")
    
    # 测试获取类型映射
    type_map = get_prohibition_type_map()
    print(f"\n✅ 成功加载类型映射")
    print(f"   映射项数：{len(type_map)}")
    print(f"   支持的翻译类型：{list(type_map.keys())[:5]}...")
    
    # 验证配置内容
    assert 'global_prohibitions' in config, "缺少 global_prohibitions"
    assert 'match3_prohibitions' in config, "缺少 match3_prohibitions"
    assert len(config['global_prohibitions']) > 0, "global_prohibitions 为空"
    
    print("\n✅ 配置内容验证通过")


def test_injector():
    """测试注入器功能"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: 注入器功能")
    print("=" * 60)
    
    injector = get_prompt_injector()
    print(f"\n✅ 注入器初始化成功")
    
    # 测试不同翻译类型的禁止事项
    test_types = ['match3_item', 'dialogue', 'ui', 'custom']
    
    for trans_type in test_types:
        prohibitions = injector.get_prohibitions(trans_type)
        print(f"\n📋 {trans_type}:")
        print(f"   禁止事项数量：{len(prohibitions)}")
        print(f"   前 3 条：{prohibitions[:3]}")
        
        # 验证至少包含通用禁止事项
        assert len(prohibitions) >= len(DEFAULT_PROHIBITION_CONFIG['global_prohibitions']), \
            f"{trans_type} 的禁止事项数量不足"
    
    print("\n✅ 所有翻译类型的禁止事项加载正确")


def test_prompt_injection():
    """测试提示词注入"""
    print("\n" + "=" * 60)
    print("🧪 测试 3: 提示词注入功能")
    print("=" * 60)
    
    injector = get_prompt_injector()
    
    # 测试示例提示词
    draft_prompt = "Role: Translator.\nTask: Translate to {target_lang}.\nConstraints:\n1. Output JSON."
    
    injected = injector.inject_draft_prompt(draft_prompt, 'match3_item')
    
    print(f"\n原始提示词长度：{len(draft_prompt)}")
    print(f"注入后提示词长度：{len(injected)}")
    print(f"增加的长度：{len(injected) - len(draft_prompt)}")
    
    # 验证禁止事项被注入
    assert "⚠️ STRICT PROHIBITIONS" in injected, "未找到禁止事项标题"
    assert "禁止输出原文" in injected, "未找到通用禁止事项"
    assert "禁止使用超过 4 个字" in injected, "未找到三消专项禁止事项"
    
    print("\n✅ 禁止事项成功注入到提示词中")
    print("\n注入后的提示词片段:")
    print("-" * 60)
    # 显示禁止事项部分
    start = injected.find("⚠️ STRICT PROHIBITIONS")
    if start >= 0:
        end = injected.find("\n\n", start)
        if end < 0:
            end = len(injected)
        print(injected[start:end])
    print("-" * 60)


def test_custom_config():
    """测试自定义配置"""
    print("\n" + "=" * 60)
    print("🧪 测试 4: 自定义配置能力")
    print("=" * 60)
    
    # 从配置文件加载的配置应该与默认配置不同（如果用户修改了）
    current_config = get_prohibition_config()
    
    print("\n📊 当前配置 vs 默认配置")
    print(f"   当前 global_prohibitions 数量：{len(current_config['global_prohibitions'])}")
    print(f"   默认 global_prohibitions 数量：{len(DEFAULT_PROHIBITION_CONFIG['global_prohibitions'])}")
    
    # 验证配置是从文件加载的还是使用默认的
    if current_config == DEFAULT_PROHIBITION_CONFIG:
        print("\nℹ️  使用默认禁止事项配置（配置文件中未自定义）")
    else:
        print("\n✅ 已加载自定义禁止事项配置")
    
    print("\n💡 提示：可以在 config/config.json 中修改 prohibition_config 来自定义禁止事项")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 开始测试禁止事项配置功能")
    print("=" * 60)
    
    try:
        test_config_loading()
        test_injector()
        test_prompt_injection()
        test_custom_config()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
        print("\n📝 功能总结:")
        print("  1. ✅ 禁止事项配置可从 config.json/config.yaml 加载")
        print("  2. ✅ 支持按翻译类型配置不同的禁止事项")
        print("  3. ✅ 自动将禁止事项注入到提示词中")
        print("  4. ✅ 提供默认配置作为后备")
        print("  5. ✅ 用户可在配置文件中自定义禁止规则")
        
        print("\n📖 使用指南:")
        print("  在 config/config.json 或 config/config.yaml 中修改:")
        print("  - prohibition_config.global_prohibitions: 通用禁止事项")
        print("  - prohibition_config.match3_prohibitions: 三消游戏禁止事项")
        print("  - prohibition_config.rpg_prohibitions: RPG 游戏禁止事项")
        print("  - prohibition_config.ui_prohibitions: UI 界面禁止事项")
        print("  - prohibition_config.dialogue_prohibitions: 对话剧情禁止事项")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
