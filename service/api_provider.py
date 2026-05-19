"""
DeepSeek API 客户端管理
"""
from typing import Optional
from openai import AsyncOpenAI


def create_api_client(api_key: Optional[str] = None,
                      base_url: str = "https://api.deepseek.com") -> AsyncOpenAI:
    """创建 DeepSeek API 客户端（OpenAI 兼容协议）"""
    return AsyncOpenAI(api_key=api_key, base_url=base_url)
