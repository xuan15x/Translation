"""
模型配置管理器
专用于 DeepSeek 模型配置管理
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import logging

from config.model_providers import (
    ModelProvidersConfig,
    ModelConfig,
    AuthType,
    GenerationConfig,
    SamplingParams,
    get_predefined_models,
)

logger = logging.getLogger(__name__)


class ModelConfigManager:
    """DeepSeek 模型配置管理器"""

    def __init__(self):
        self.config: ModelProvidersConfig = ModelProvidersConfig()
        self._predefined: ModelProvidersConfig = get_predefined_models()
        self._current_model_id: Optional[str] = "deepseek-chat"

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        if "modelProviders" in data:
            self.config = ModelProvidersConfig.from_dict(data["modelProviders"])
            logger.info("已加载 modelProviders 配置")
        else:
            self.config = ModelProvidersConfig()
            logger.info("未找到 modelProviders 配置，使用预定义配置")
        if "current_model_id" in data:
            self._current_model_id = data["current_model_id"]

    def load_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.load_from_dict(data)
            logger.info(f"已从文件加载配置：{file_path}")
            return True
        except Exception as e:
            logger.error(f"加载配置文件失败：{e}")
            return False

    def save_to_file(self, file_path: str) -> bool:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            existing_data["modelProviders"] = self.config.to_dict()
            existing_data["current_model_id"] = self._current_model_id
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            logger.info(f"已保存配置到：{file_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败：{e}")
            return False

    def validate_config(self) -> Tuple[bool, List[str]]:
        errors = []
        seen_ids = set()
        for model in self.config.openai:
            if not model.id:
                errors.append("模型缺少 id 字段")
            if not model.env_key:
                errors.append(f"{model.id}: 模型缺少 env_key 字段")
            if model.id in seen_ids:
                errors.append(f"重复的模型 ID '{model.id}'")
            seen_ids.add(model.id)
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("模型配置验证通过")
        else:
            logger.error(f"模型配置验证失败：{len(errors)} 个错误")
        return is_valid, errors

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        return self.config.get_model_by_id(model_id)

    def get_current_model(self) -> Optional[ModelConfig]:
        if not self._current_model_id:
            return None
        return self.get_model(self._current_model_id)

    def set_current_model(self, model_id: str) -> bool:
        model = self.get_model(model_id)
        if not model:
            logger.error(f"模型不存在：{model_id}")
            return False
        self._current_model_id = model_id
        logger.info(f"已设置当前模型：{model_id}")
        return True

    def get_all_models(self) -> List[ModelConfig]:
        return self.config.get_all_models()

    def add_model(self, model: ModelConfig) -> Tuple[bool, str]:
        try:
            self.config.add_model(model)
            logger.info(f"已添加模型：{model.id}")
            return True, ""
        except ValueError as e:
            return False, str(e)

    def remove_model(self, model_id: str) -> bool:
        if self.config.remove_model(model_id):
            logger.info(f"已移除模型：{model_id}")
            if self._current_model_id == model_id:
                self._current_model_id = "deepseek-chat"
            return True
        return False

    def get_api_key(self, model: ModelConfig) -> Optional[str]:
        return os.getenv(model.env_key)

    def get_base_url(self, model: ModelConfig) -> str:
        return model.base_url or "https://api.deepseek.com"

    def get_sampling_params(self, model: ModelConfig) -> SamplingParams:
        if model.generation_config and model.generation_config.sampling_params:
            return model.generation_config.sampling_params
        return SamplingParams()

    def get_generation_config(self, model: ModelConfig) -> GenerationConfig:
        if model.generation_config:
            return model.generation_config
        return GenerationConfig()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modelProviders": self.config.to_dict(),
            "current_model_id": self._current_model_id,
        }


# 全局管理器实例
_manager: Optional[ModelConfigManager] = None


def get_model_manager() -> ModelConfigManager:
    global _manager
    if _manager is None:
        _manager = ModelConfigManager()
    return _manager


def initialize_model_manager(config_file: Optional[str] = None) -> ModelConfigManager:
    global _manager
    _manager = ModelConfigManager()
    if config_file and os.path.exists(config_file):
        _manager.load_from_file(config_file)
    return _manager
