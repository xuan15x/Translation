#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API 连接测试脚本
测试 API Key 是否有效，网络连接是否正常
"""
import json
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config():
    """加载配置文件"""
    config_paths = [
        'config/config.json',
        'config/config.deepseek.example.json',
        'config/config.example.json'
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f), config_path
    
    print("❌ 未找到配置文件")
    print("请先运行 '快速配置.bat' 或手动创建配置文件")
    return None, None


def test_deepseek_connection():
    """测试 DeepSeek API 连接"""
    print("🔍 正在加载配置文件...")
    config, config_path = load_config()
    
    if not config:
        return False
    
    print(f"✓ 配置文件已加载：{config_path}")
    
    # 获取 API 配置
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.deepseek.com')
    model_name = config.get('model_name', 'deepseek-chat')
    
    # 检查 API Key
    if not api_key or api_key == 'sk-your-deepseek-api-key-here':
        print("❌ API Key 未设置或为默认值")
        print("请在配置文件中设置有效的 API Key")
        return False
    
    print(f"✓ API Key 已设置：{api_key[:8]}...{api_key[-4:]}")
    print(f"✓ API 端点：{base_url}")
    print(f"✓ 模型名称：{model_name}")
    print()
    
    # 尝试导入 openai 库
    try:
        from openai import OpenAI
        print("✓ OpenAI 库已安装")
    except ImportError:
        print("❌ OpenAI 库未安装")
        print("请运行：pip install openai")
        return False
    
    # 创建客户端并测试
    print()
    print("🔄 正在测试 API 连接...")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 发送测试请求
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'OK'."}
            ],
            max_tokens=10,
            timeout=10
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"✓ API 响应成功：{content}")
            print()
            print("=" * 50)
            print("🎉 API 连接测试通过！")
            print("=" * 50)
            return True
        else:
            print("❌ API 响应为空")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ API 连接失败：{error_msg}")
        print()
        print("可能的原因:")
        print("  1. API Key 无效或已过期")
        print("  2. 网络连接问题")
        print("  3. 防火墙阻止了 API 访问")
        print("  4. API 服务暂时不可用")
        print()
        print("建议:")
        print("  - 检查 API Key 是否正确")
        print("  - 尝试访问 https://platform.deepseek.com/")
        print("  - 检查防火墙设置")
        return False


def test_translation():
    """测试翻译功能"""
    print()
    print("=" * 50)
    print("📝 测试翻译功能")
    print("=" * 50)
    print()
    
    config, _ = load_config()
    if not config:
        return False
    
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', 'https://api.deepseek.com')
    model_name = config.get('model_name', 'deepseek-chat')
    temperature = config.get('temperature', 0.7)
    top_p = config.get('top_p', 0.9)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试翻译
        print("🔄 正在测试翻译：'你好，世界' -> 英语")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following text to English. Output only the translation."
                },
                {
                    "role": "user",
                    "content": "你好，世界"
                }
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=50,
            timeout=30
        )
        
        if response.choices:
            translation = response.choices[0].message.content
            print(f"✓ 翻译结果：{translation}")
            print()
            print("=" * 50)
            print("🎉 翻译测试通过！")
            print("=" * 50)
            return True
        else:
            print("❌ 翻译结果为空")
            return False
            
    except Exception as e:
        print(f"❌ 翻译测试失败：{e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("  DeepSeek API 连接测试")
    print("=" * 50)
    print()
    
    # 测试连接
    success = test_deepseek_connection()
    
    if success:
        # 询问是否测试翻译
        print()
        choice = input("是否测试翻译功能？(y/n): ").strip().lower()
        if choice == 'y':
            test_translation()
    
    # 退出码
    sys.exit(0 if success else 1)
