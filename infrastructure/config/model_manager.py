"""
统一模型配置管理器
参考 Qwen 的 modelProviders 配置系统，实现多模型兼容适配

功能：
1. 加载和解析 modelProviders 配置
2. 验证模型配置有效性
3. 根据 authType 分类管理模型
4. 提供模型切换和查询接口
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import logging

from infrastructure.config.model_providers import (
    ModelProvidersConfig,
    ModelConfig,
    AuthType,
    GenerationConfig,
    SamplingParams,
    get_predefined_models,
)

logger = logging.getLogger(__name__)


class ModelConfigManager:
    """模型配置管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.config: ModelProvidersConfig = ModelProvidersConfig()
        self._predefined: ModelProvidersConfig = get_predefined_models()
        self._current_model_id: Optional[str] = None
    
    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典加载配置
        
        Args:
            data: 配置字典（通常从 JSON 文件加载）
        """
        if "modelProviders" in data:
            self.config = ModelProvidersConfig.from_dict(data["modelProviders"])
            logger.info("✅ 已加载 modelProviders 配置")
        else:
            # 使用预定义配置
            self.config = ModelProvidersConfig()
            logger.info("ℹ️  未找到 modelProviders 配置，使用预定义配置")
        
        # 设置当前模型（如果有）
        if "current_model_id" in data:
            self._current_model_id = data["current_model_id"]
    
    def load_from_file(self, file_path: str) -> bool:
        """
        从文件加载配置
        
        Args:
            file_path: JSON 配置文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.load_from_dict(data)
            logger.info(f"✅ 已从文件加载配置：{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加载配置文件失败：{e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 加载现有配置
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # 更新 modelProviders 配置
            existing_data["modelProviders"] = self.config.to_dict()
            existing_data["current_model_id"] = self._current_model_id
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 已保存配置到：{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存配置文件失败：{e}")
            return False
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        验证配置有效性
        
        Returns:
            (是否有效，错误消息列表)
        """
        errors = []
        
        # 检查每个认证类型下的模型
        for auth_type in AuthType:
            models = getattr(self.config, auth_type.value, [])
            seen_ids = set()
            
            for model in models:
                # 检查必填字段
                if not model.id:
                    errors.append(f"{auth_type.value}: 模型缺少 id 字段")
                
                if not model.env_key:
                    errors.append(f"{auth_type.value}.{model.id}: 模型缺少 env_key 字段")
                
                # 检查重复 ID
                if model.id in seen_ids:
                    errors.append(f"{auth_type.value}: 重复的模型 ID '{model.id}'")
                seen_ids.add(model.id)
                
                # 检查 authType 是否匹配
                if model.auth_type != auth_type:
                    errors.append(
                        f"{auth_type.value}.{model.id}: "
                        f"authType 不匹配（配置为 {model.auth_type.value}）"
                    )
                
                # 检查 extra_body 仅用于 OpenAI 兼容
                if model.generation_config and model.generation_config.extra_body:
                    if auth_type not in [AuthType.OPENAI, AuthType.QWEN]:
                        errors.append(
                            f"{auth_type.value}.{model.id}: "
                            f"extra_body 仅支持 OpenAI 兼容提供商"
                        )
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("✅ 模型配置验证通过")
        else:
            logger.error(f"❌ 模型配置验证失败：{len(errors)} 个错误")
        
        return is_valid, errors
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """
        获取模型配置
        
        Args:
            model_id: 模型 ID
            
        Returns:
            模型配置，如果不存在则返回 None
        """
        return self.config.get_model_by_id(model_id)
    
    def get_current_model(self) -> Optional[ModelConfig]:
        """获取当前选中的模型配置"""
        if not self._current_model_id:
            return None
        return self.get_model(self._current_model_id)
    
    def set_current_model(self, model_id: str) -> bool:
        """
        设置当前使用的模型
        
        Args:
            model_id: 模型 ID
            
        Returns:
            是否设置成功
        """
        model = self.get_model(model_id)
        if not model:
            logger.error(f"❌ 模型不存在：{model_id}")
            return False
        
        self._current_model_id = model_id
        logger.info(f"✅ 已设置当前模型：{model_id}")
        return True
    
    def get_all_models(self) -> List[ModelConfig]:
        """获取所有模型配置"""
        return self.config.get_all_models()
    
    def get_models_by_auth_type(self, auth_type: AuthType) -> List[ModelConfig]:
        """
        根据认证类型获取模型列表
        
        Args:
            auth_type: 认证类型
            
        Returns:
            模型配置列表
        """
        return getattr(self.config, auth_type.value, [])
    
    def add_model(self, model: ModelConfig) -> Tuple[bool, str]:
        """
        添加模型配置
        
        Args:
            model: 模型配置
            
        Returns:
            (是否成功，错误消息)
        """
        try:
            self.config.add_model(model)
            logger.info(f"✅ 已添加模型：{model.id}")
            return True, ""
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"❌ 添加模型失败：{error_msg}")
            return False, error_msg
    
    def remove_model(self, model_id: str) -> bool:
        """
        移除模型配置
        
        Args:
            model_id: 模型 ID
            
        Returns:
            是否移除成功
        """
        if self.config.remove_model(model_id):
            logger.info(f"✅ 已移除模型：{model_id}")
            
            # 如果移除的是当前模型，清空当前模型
            if self._current_model_id == model_id:
                self._current_model_id = None
            
            return True
        return False
    
    def get_api_key(self, model: ModelConfig) -> Optional[str]:
        """
        获取模型的 API Key
        
        Args:
            model: 模型配置
            
        Returns:
            API Key，如果未设置则返回 None
        """
        # 从环境变量读取
        api_key = os.getenv(model.env_key)
        
        if not api_key:
            logger.warning(f"⚠️ 环境变量 {model.env_key} 未设置")
        
        return api_key
    
    def get_base_url(self, model: ModelConfig) -> str:
        """
        获取模型的 API 端点
        
        Args:
            model: 模型配置
            
        Returns:
            API 端点 URL
        """
        if model.base_url:
            return model.base_url
        
        # 根据 authType 返回默认端点
        defaults = {
            AuthType.OPENAI: "https://api.openai.com/v1",
            AuthType.ANTHROPIC: "https://api.anthropic.com/v1",
            AuthType.GEMINI: "https://generativelanguage.googleapis.com/v1beta",
            AuthType.QWEN: "https://dashscope.aliyuncs.com/api/v1",
        }
        
        return defaults.get(model.auth_type, "")
    
    def get_sampling_params(self, model: ModelConfig) -> SamplingParams:
        """
        获取模型的采样参数
        
        Args:
            model: 模型配置
            
        Returns:
            采样参数配置
        """
        if model.generation_config and model.generation_config.sampling_params:
            return model.generation_config.sampling_params
        
        # 返回默认采样参数
        return SamplingParams()
    
    def get_generation_config(self, model: ModelConfig) -> GenerationConfig:
        """
        获取模型的生成配置
        
        Args:
            model: 模型配置
            
        Returns:
            生成配置
        """
        if model.generation_config:
            return model.generation_config
        
        # 返回默认生成配置
        return GenerationConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "modelProviders": self.config.to_dict(),
            "current_model_id": self._current_model_id,
        }


# 全局管理器实例
_manager: Optional[ModelConfigManager] = None


def get_model_manager() -> ModelConfigManager:
    """获取全局模型配置管理器"""
    global _manager
    if _manager is None:
        _manager = ModelConfigManager()
    return _manager


def initialize_model_manager(config_file: Optional[str] = None) -> ModelConfigManager:
    """
    初始化模型配置管理器
    
    Args:
        config_file: 配置文件路径（可选）
        
    Returns:
        模型配置管理器实例
    """
    global _manager
    _manager = ModelConfigManager()
    
    if config_file and os.path.exists(config_file):
        _manager.load_from_file(config_file)
    
    return _manager
