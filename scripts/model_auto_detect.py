"""
模型名称自动识别提供商工具

演示如何根据模型名称自动识别 API 提供商，简化配置复杂度。
用户只需设置 model_name，无需手动选择 api_provider。
"""

import re
from typing import Optional, Tuple


# 模型名称到提供商的映射规则
MODEL_PATTERNS = {
    'deepseek': [
        r'^deepseek[-_]',      # deepseek-chat, deepseek-coder
        r'^deepseek$',         # deepseek
    ],
    'openai': [
        r'^gpt[-_]',           # gpt-4, gpt-3.5-turbo
        r'^chatgpt[-_]',       # chatgpt-4
        r'^o\d[-_]',           # o1-preview, o1-mini
    ],
    'anthropic': [
        r'^claude[-_]',        # claude-3-opus, claude-2
        r'^claude$',           # claude
    ],
    'moonshot': [
        r'^moonshot[-_]',      # moonshot-v1
        r'^kimi[-_]',          # kimi-chat
    ],
    'zhipu': [
        r'^glm[-_]',           # glm-4, glm-edge
        r'^zhipu[-_]',         # zhipu-ai
    ],
    'baidu': [
        r'^ernie[-_]',         # ernie-bot
        r'^wenxin[-_]',        # wenxin-yiyan
    ],
    'alibaba': [
        r'^qwen[-_]',          # qwen-72b
        r'^tongyi[-_]',        # tongyi-qianwen
    ],
    'custom': [
        r'^custom[-_]',        # custom-model
    ],
}


def detect_provider_from_model(model_name: str) -> Optional[str]:
    """
    根据模型名称检测 API 提供商
    
    Args:
        model_name: 模型名称
        
    Returns:
        提供商名称，如果无法识别则返回 None
    """
    model_name_lower = model_name.lower().strip()
    
    for provider, patterns in MODEL_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, model_name_lower):
                return provider
    
    return None


def get_api_config_for_model(model_name: str, api_keys_config: dict) -> Tuple[Optional[str], Optional[dict]]:
    """
    根据模型名称获取对应的 API 配置
    
    Args:
        model_name: 模型名称
        api_keys_config: API 密钥配置字典
        
    Returns:
        (provider_name, api_config) 元组
    """
    provider = detect_provider_from_model(model_name)
    
    if not provider:
        return None, None
    
    api_config = api_keys_config.get(provider)
    return provider, api_config


def validate_model_name(model_name: str) -> bool:
    """
    验证模型名称格式
    
    Args:
        model_name: 模型名称
        
    Returns:
        是否有效
    """
    if not model_name or not model_name.strip():
        return False
    
    # 检查是否包含非法字符
    if not re.match(r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$', model_name):
        return False
    
    return True


def suggest_models_for_provider(provider: str) -> list:
    """
    根据提供商推荐常用模型列表
    
    Args:
        provider: 提供商名称
        
    Returns:
        推荐模型列表
    """
    recommendations = {
        'deepseek': ['deepseek-chat', 'deepseek-coder'],
        'openai': ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo', 'o1-preview'],
        'anthropic': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
        'moonshot': ['moonshot-v1-8k', 'moonshot-v1-32k'],
        'zhipu': ['glm-4', 'glm-3-turbo'],
        'baidu': ['ernie-bot-4', 'ernie-bot-turbo'],
        'alibaba': ['qwen-72b', 'qwen-14b'],
        'custom': ['your-custom-model'],
    }
    
    return recommendations.get(provider, [])


def main():
    """主函数 - 演示使用"""
    print("=" * 70)
    print("模型名称自动识别提供商工具")
    print("=" * 70)
    print()
    
    # 示例模型名称
    test_models = [
        'deepseek-chat',
        'deepseek-coder',
        'gpt-4-turbo',
        'gpt-3.5-turbo',
        'claude-3-opus',
        'claude-3-sonnet',
        'moonshot-v1-8k',
        'glm-4',
        'ernie-bot-4',
        'qwen-72b',
        'unknown-model',
    ]
    
    print("1️⃣  模型名称自动识别演示:")
    print("-" * 70)
    for model in test_models:
        provider = detect_provider_from_model(model)
        status = f"✅ {provider}" if provider else "❌ 未知"
        print(f"  {model:20s} → {status}")
    
    print()
    print("2️⃣  根据模型获取 API 配置:")
    print("-" * 70)
    
    # 模拟 API 密钥配置
    api_keys_config = {
        'deepseek': {
            'api_key': 'sk-deepseek-key',
            'base_url': 'https://api.deepseek.com'
        },
        'openai': {
            'api_key': 'sk-openai-key',
            'base_url': 'https://api.openai.com/v1'
        },
        'anthropic': {
            'api_key': 'sk-anthropic-key',
            'base_url': 'https://api.anthropic.com'
        },
    }
    
    demo_models = ['deepseek-chat', 'gpt-4-turbo', 'claude-3-opus']
    
    for model in demo_models:
        provider, config = get_api_config_for_model(model, api_keys_config)
        if provider and config:
            print(f"  {model:20s} → {provider}")
            print(f"    Base URL: {config['base_url']}")
            print(f"    API Key: {'*' * 20}")
        else:
            print(f"  {model:20s} → ❌ 未找到配置")
        print()
    
    print("3️⃣  推荐模型列表:")
    print("-" * 70)
    for provider in ['deepseek', 'openai', 'anthropic']:
        models = suggest_models_for_provider(provider)
        print(f"  {provider:15s}: {', '.join(models)}")
    
    print()
    print("4️⃣  配置文件简化对比:")
    print("-" * 70)
    print()
    print("❌ 旧方式（复杂）:")
    print("""
    {
      "api_provider": "deepseek",
      "api_providers": {
        "deepseek": {
          "api_key": "...",
          "base_url": "...",
          "model_name": "deepseek-chat",
          "models": ["deepseek-chat", "deepseek-coder"]
        }
      },
      "model_name": "deepseek-chat"
    }
    """)
    
    print("✅ 新方式（简化）:")
    print("""
    {
      "model_name": "deepseek-chat",
      "api_keys": {
        "deepseek": {
          "api_key": "...",
          "base_url": "..."
        },
        "openai": {
          "api_key": "...",
          "base_url": "..."
        }
      }
    }
    """)
    
    print("=" * 70)
    print("✅ 优势:")
    print("   1. 用户只需设置 model_name，无需关心 api_provider")
    print("   2. 自动识别提供商，减少配置步骤")
    print("   3. 支持多提供商配置，灵活切换")
    print("   4. 配置文件更简洁，易于维护")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())
