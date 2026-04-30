"""
模型配置系统
专用于 DeepSeek 模型配置
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class AuthType(Enum):
    """认证类型"""
    OPENAI = "openai"  # DeepSeek 使用 OpenAI 兼容 API


@dataclass
class SamplingParams:
    """采样参数配置"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 8192
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SamplingParams":
        return cls(
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 0.9),
            max_tokens=data.get("max_tokens", 8192),
            presence_penalty=data.get("presence_penalty", 0.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
        )


@dataclass
class GenerationConfig:
    """生成配置"""
    timeout: int = 60000
    max_retries: int = 3
    enable_cache_control: bool = True
    context_window_size: Optional[int] = None
    enable_stream: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extra_body: Dict[str, Any] = field(default_factory=dict)
    sampling_params: Optional[SamplingParams] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "enable_cache_control": self.enable_cache_control,
            "context_window_size": self.context_window_size,
            "enable_stream": self.enable_stream,
            "custom_headers": self.custom_headers,
            "extra_body": self.extra_body,
        }
        if self.sampling_params:
            result["samplingParams"] = self.sampling_params.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationConfig":
        sampling_data = data.get("samplingParams")
        sampling_params = SamplingParams.from_dict(sampling_data) if sampling_data else None
        return cls(
            timeout=data.get("timeout", 60000),
            max_retries=data.get("max_retries", 3),
            enable_cache_control=data.get("enable_cache_control", True),
            context_window_size=data.get("context_window_size"),
            enable_stream=data.get("enable_stream", False),
            custom_headers=data.get("custom_headers", {}),
            extra_body=data.get("extra_body", {}),
            sampling_params=sampling_params,
        )


@dataclass
class ModelConfig:
    """模型配置"""
    id: str
    env_key: str = "DEEPSEEK_API_KEY"
    auth_type: AuthType = field(default=AuthType.OPENAI)
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    generation_config: Optional[GenerationConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "envKey": self.env_key,
            "authType": self.auth_type.value,
        }
        if self.name:
            result["name"] = self.name
        if self.description:
            result["description"] = self.description
        if self.base_url:
            result["baseUrl"] = self.base_url
        if self.generation_config:
            result["generationConfig"] = self.generation_config.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        gen_config_data = data.get("generationConfig")
        generation_config = GenerationConfig.from_dict(gen_config_data) if gen_config_data else None
        return cls(
            id=data["id"],
            env_key=data.get("envKey", "DEEPSEEK_API_KEY"),
            auth_type=AuthType.OPENAI,
            name=data.get("name"),
            description=data.get("description"),
            base_url=data.get("baseUrl", "https://api.deepseek.com"),
            generation_config=generation_config,
        )


@dataclass
class ModelProvidersConfig:
    """模型提供商配置 - 仅 DeepSeek"""
    openai: List[ModelConfig] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.openai:
            result["openai"] = [m.to_dict() for m in self.openai]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProvidersConfig":
        config = cls()
        if "openai" in data and isinstance(data["openai"], list):
            config.openai = [ModelConfig.from_dict(m) for m in data["openai"]]
        return config

    def get_all_models(self) -> List[ModelConfig]:
        return list(self.openai)

    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        for model in self.openai:
            if model.id == model_id:
                return model
        return None

    def add_model(self, model: ModelConfig) -> None:
        for existing in self.openai:
            if existing.id == model.id:
                raise ValueError(f"模型 ID '{model.id}' 已存在")
        self.openai.append(model)

    def remove_model(self, model_id: str) -> bool:
        for i, model in enumerate(self.openai):
            if model.id == model_id:
                self.openai.pop(i)
                return True
        return False


def get_predefined_models() -> ModelProvidersConfig:
    """获取预定义的 DeepSeek 模型配置"""
    config = ModelProvidersConfig()
    config.openai = [
        ModelConfig(
            id="deepseek-chat",
            env_key="DEEPSEEK_API_KEY",
            auth_type=AuthType.OPENAI,
            name="DeepSeek Chat",
            base_url="https://api.deepseek.com",
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=8192,
                )
            )
        ),
        ModelConfig(
            id="deepseek-reasoner",
            env_key="DEEPSEEK_API_KEY",
            auth_type=AuthType.OPENAI,
            name="DeepSeek Reasoner",
            base_url="https://api.deepseek.com",
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=8192,
                )
            )
        ),
    ]
    return config
