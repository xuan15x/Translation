"""
统一模型配置系统
参考 Qwen 的 modelProviders 配置结构，支持多模型提供商兼容

认证类型（AuthType）：
- openai: OpenAI 兼容 API（DeepSeek、OpenAI、Azure、vLLM、Ollama 等）
- anthropic: Anthropic Claude API
- gemini: Google Gemini API
- qwen: 阿里云通义千问 API
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class AuthType(Enum):
    """支持的认证类型枚举"""
    OPENAI = "openai"           # OpenAI 兼容 API
    ANTHROPIC = "anthropic"     # Anthropic Claude API
    GEMINI = "gemini"           # Google Gemini API
    QWEN = "qwen"               # 阿里云通义千问 API


@dataclass
class SamplingParams:
    """采样参数配置 - 参考 Qwen samplingParams"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 4096
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    top_k: Optional[int] = None  # Gemini 专用
    stop: Optional[List[str]] = None  # 停止序列
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
        }
        if self.top_k is not None:
            result["top_k"] = self.top_k
        if self.stop is not None:
            result["stop"] = self.stop
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SamplingParams":
        """从字典创建"""
        return cls(
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 0.9),
            max_tokens=data.get("max_tokens", 4096),
            presence_penalty=data.get("presence_penalty", 0.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            top_k=data.get("top_k"),
            stop=data.get("stop"),
        )


@dataclass
class GenerationConfig:
    """生成配置 - 参考 Qwen generationConfig"""
    # 基础参数
    timeout: int = 60000  # 毫秒
    max_retries: int = 3
    
    # 高级功能
    enable_cache_control: bool = True
    context_window_size: Optional[int] = None  # 上下文窗口大小
    enable_stream: bool = False  # 流式输出
    
    # 模态配置（如 vision）
    modalities: Dict[str, bool] = field(default_factory=dict)
    
    # 自定义请求头
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # 额外请求体参数（仅 OpenAI 兼容）
    extra_body: Dict[str, Any] = field(default_factory=dict)
    
    # 采样参数
    sampling_params: Optional[SamplingParams] = None
    
    # 模式合规性（Gemini 专用）
    schema_compliance: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "enable_cache_control": self.enable_cache_control,
            "context_window_size": self.context_window_size,
            "enable_stream": self.enable_stream,
            "modalities": self.modalities,
            "custom_headers": self.custom_headers,
            "extra_body": self.extra_body,
        }
        if self.schema_compliance:
            result["schema_compliance"] = self.schema_compliance
        if self.sampling_params:
            result["samplingParams"] = self.sampling_params.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationConfig":
        """从字典创建"""
        sampling_data = data.get("samplingParams")
        sampling_params = None
        if sampling_data:
            sampling_params = SamplingParams.from_dict(sampling_data)
        
        return cls(
            timeout=data.get("timeout", 60000),
            max_retries=data.get("max_retries", 3),
            enable_cache_control=data.get("enable_cache_control", True),
            context_window_size=data.get("context_window_size"),
            enable_stream=data.get("enable_stream", False),
            modalities=data.get("modalities", {}),
            custom_headers=data.get("custom_headers", {}),
            extra_body=data.get("extra_body", {}),
            schema_compliance=data.get("schema_compliance"),
            sampling_params=sampling_params,
        )


@dataclass
class ModelConfig:
    """单个模型配置 - 参考 Qwen modelProviders 结构"""
    id: str  # 模型标识符（必填）
    env_key: str  # 环境变量名（必填）
    auth_type: AuthType  # 认证类型
    name: Optional[str] = None  # 显示名称
    description: Optional[str] = None  # 描述
    base_url: Optional[str] = None  # API 端点
    generation_config: Optional[GenerationConfig] = None  # 生成配置
    capabilities: Dict[str, bool] = field(default_factory=dict)  # 能力配置
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.id:
            raise ValueError("模型配置必须包含 id")
        if not self.env_key:
            raise ValueError("模型配置必须包含 env_key")
        if not self.auth_type:
            self.auth_type = AuthType.OPENAI  # 默认为 OpenAI 兼容
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
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
        if self.capabilities:
            result["capabilities"] = self.capabilities
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """从字典创建"""
        auth_type_str = data.get("authType", "openai")
        try:
            auth_type = AuthType(auth_type_str)
        except ValueError:
            auth_type = AuthType.OPENAI  # 未知类型默认为 OpenAI 兼容
        
        gen_config_data = data.get("generationConfig")
        generation_config = None
        if gen_config_data:
            generation_config = GenerationConfig.from_dict(gen_config_data)
        
        return cls(
            id=data["id"],
            env_key=data["envKey"],
            auth_type=auth_type,
            name=data.get("name"),
            description=data.get("description"),
            base_url=data.get("baseUrl"),
            generation_config=generation_config,
            capabilities=data.get("capabilities", {}),
        )


@dataclass
class ModelProvidersConfig:
    """模型提供商配置 - 顶层配置"""
    # 按认证类型分组的模型配置列表
    openai: List[ModelConfig] = field(default_factory=list)
    anthropic: List[ModelConfig] = field(default_factory=list)
    gemini: List[ModelConfig] = field(default_factory=list)
    qwen: List[ModelConfig] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for auth_type in AuthType:
            models = getattr(self, auth_type.value, [])
            if models:
                result[auth_type.value] = [m.to_dict() for m in models]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProvidersConfig":
        """从字典创建"""
        config = cls()
        
        for auth_type in AuthType:
            key = auth_type.value
            if key in data:
                models_data = data[key]
                if isinstance(models_data, list):
                    models = []
                    for model_data in models_data:
                        try:
                            model = ModelConfig.from_dict(model_data)
                            models.append(model)
                        except (KeyError, ValueError) as e:
                            print(f"⚠️ 跳过无效的模型配置：{e}")
                    setattr(config, key, models)
        
        return config
    
    def get_all_models(self) -> List[ModelConfig]:
        """获取所有模型配置"""
        all_models = []
        for auth_type in AuthType:
            all_models.extend(getattr(self, auth_type.value, []))
        return all_models
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """根据 ID 获取模型配置"""
        for model in self.get_all_models():
            if model.id == model_id:
                return model
        return None
    
    def add_model(self, model: ModelConfig) -> None:
        """添加模型配置"""
        auth_type = model.auth_type
        models = getattr(self, auth_type.value, [])
        
        # 检查是否已存在相同 ID
        for existing in models:
            if existing.id == model.id:
                raise ValueError(f"模型 ID '{model.id}' 已存在")
        
        models.append(model)
        setattr(self, auth_type.value, models)
    
    def remove_model(self, model_id: str) -> bool:
        """移除模型配置"""
        for auth_type in AuthType:
            models = getattr(self, auth_type.value, [])
            for i, model in enumerate(models):
                if model.id == model_id:
                    models.pop(i)
                    return True
        return False


# 预定义的模型配置（开箱即用）
def get_predefined_models() -> ModelProvidersConfig:
    """获取预定义的模型配置"""
    config = ModelProvidersConfig()
    
    # OpenAI 兼容模型
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
                    max_tokens=4096,
                )
            )
        ),
        ModelConfig(
            id="gpt-4o",
            env_key="OPENAI_API_KEY",
            auth_type=AuthType.OPENAI,
            name="GPT-4o",
            base_url="https://api.openai.com/v1",
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=4096,
                )
            )
        ),
        ModelConfig(
            id="moonshot-v1-8k",
            env_key="MOONSHOT_API_KEY",
            auth_type=AuthType.OPENAI,
            name="Moonshot V1 8K",
            base_url="https://api.moonshot.cn/v1",
        ),
        ModelConfig(
            id="glm-4",
            env_key="ZHIPU_API_KEY",
            auth_type=AuthType.OPENAI,
            name="智谱 GLM-4",
            base_url="https://open.bigmodel.cn/api/paas/v4",
        ),
    ]
    
    # Anthropic 模型
    config.anthropic = [
        ModelConfig(
            id="claude-3-5-sonnet-20240229",
            env_key="ANTHROPIC_API_KEY",
            auth_type=AuthType.ANTHROPIC,
            name="Claude 3.5 Sonnet",
            base_url="https://api.anthropic.com/v1",
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    max_tokens=4096,
                )
            )
        ),
    ]
    
    # Gemini 模型
    config.gemini = [
        ModelConfig(
            id="gemini-1.5-pro",
            env_key="GEMINI_API_KEY",
            auth_type=AuthType.GEMINI,
            name="Gemini 1.5 Pro",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            capabilities={"vision": True},
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=8192,
                    top_k=40,  # Gemini 专用
                )
            )
        ),
    ]
    
    # Qwen 模型
    config.qwen = [
        ModelConfig(
            id="qwen-max",
            env_key="DASHSCOPE_API_KEY",
            auth_type=AuthType.QWEN,
            name="通义千问 Max",
            base_url="https://dashscope.aliyuncs.com/api/v1",
            generation_config=GenerationConfig(
                sampling_params=SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=2048,
                )
            )
        ),
    ]
    
    return config
