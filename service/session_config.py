"""
会话配置管理器
记录每次翻译会话的完整配置，支持自动保存和还原
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """会话配置数据类"""
    # 文件路径
    term_file_path: str = ""
    source_file_path: str = ""
    
    # 翻译模式
    translation_mode: int = 1  # 1=新文档，2=旧文档校对
    
    # API 配置
    api_provider: str = "deepseek"
    
    # 双阶段参数
    draft_model: str = ""
    draft_temperature: float = 0.3
    draft_top_p: float = 0.8
    draft_timeout: int = 60
    draft_max_tokens: int = 512
    
    review_model: str = ""
    review_temperature: float = 0.5
    review_top_p: float = 0.9
    review_timeout: int = 60
    review_max_tokens: int = 512
    
    # 游戏翻译方向
    translation_type: str = "match3_item"
    
    # 提示词
    draft_prompt: str = ""
    review_prompt: str = ""
    
    # 目标语言（逗号分隔的字符串）
    target_languages: str = ""
    
    # 源语言
    source_language: str = "中文"
    
    # 日志配置
    log_level: str = "INFO"
    log_granularity: str = "normal"
    
    # 性能监控
    enable_performance_monitor: bool = False
    
    # 元数据
    session_id: str = ""
    last_updated: str = ""
    version: str = "3.0"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SessionConfig':
        """从字典创建"""
        # 过滤掉不存在的字段（向后兼容）
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class SessionConfigManager:
    """会话配置管理器"""
    
    DEFAULT_CONFIG_FILE = "session_config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化管理器
        
        Args:
            config_file: 配置文件路径，默认当前目录
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.current_session: Optional[SessionConfig] = None
        logger.info(f"📋 会话配置管理器初始化完成：{self.config_file}")
    
    def create_session(self) -> SessionConfig:
        """创建新的会话配置"""
        self.current_session = SessionConfig(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            last_updated=datetime.now().isoformat()
        )
        logger.info(f"🆕 创建新会话：{self.current_session.session_id}")
        return self.current_session
    
    def update_session(self, **kwargs):
        """
        更新当前会话配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        if not self.current_session:
            self.create_session()
        
        for key, value in kwargs.items():
            if hasattr(self.current_session, key):
                setattr(self.current_session, key, value)
        
        self.current_session.last_updated = datetime.now().isoformat()
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        保存会话配置到文件
        
        Args:
            file_path: 文件路径，默认使用初始化时的路径
            
        Returns:
            是否保存成功
        """
        if not self.current_session:
            logger.warning("⚠️ 没有可保存的会话配置")
            return False
        
        save_path = file_path or self.config_file
        
        try:
            data = {
                'session': self.current_session.to_dict(),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 会话配置已保存：{save_path}")
            logger.debug(f"会话 ID: {self.current_session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存会话配置失败：{e}")
            return False
    
    def load_from_file(self, file_path: Optional[str] = None) -> Optional[SessionConfig]:
        """
        从文件加载会话配置
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的会话配置，失败返回 None
        """
        load_path = file_path or self.config_file
        
        if not os.path.exists(load_path):
            logger.info(f"📭 会话配置文件不存在：{load_path}")
            return None
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_data = data.get('session', {})
            self.current_session = SessionConfig.from_dict(session_data)
            
            logger.info(f"📥 会话配置已加载：{load_path}")
            logger.debug(f"会话 ID: {self.current_session.session_id}")
            logger.debug(f"最后更新：{self.current_session.last_updated}")
            return self.current_session
            
        except Exception as e:
            logger.error(f"❌ 加载会话配置失败：{e}")
            return None
    
    def get_current_session(self) -> Optional[SessionConfig]:
        """获取当前会话配置"""
        return self.current_session
    
    def clear_session(self):
        """清除当前会话"""
        self.current_session = None
        logger.info("🗑️ 已清除当前会话")
    
    def get_history_file(self) -> str:
        """获取历史配置文件路径"""
        return str(Path(self.config_file).parent / "session_history.json")
    
    def export_session_history(self, sessions: list) -> str:
        """
        导出会话历史到文件
        
        Args:
            sessions: 会话配置列表
            
        Returns:
            输出文件路径
        """
        output_file = self.get_history_file()
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_sessions': len(sessions),
            'sessions': sessions
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📤 会话历史已导出：{output_file} ({len(sessions)} 个会话)")
        return output_file


# 全局单例
_session_manager: Optional[SessionConfigManager] = None


def get_session_manager(config_file: Optional[str] = None) -> SessionConfigManager:
    """
    获取全局会话管理器实例
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        会话管理器实例
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionConfigManager(config_file)
    return _session_manager
