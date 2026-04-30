"""
版本历史记录模块
记录程序版本变更和使用历史
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class VersionRecord:
    """版本记录"""
    version: str  # 版本号
    release_date: str  # 发布日期
    changes: List[str]  # 变更列表
    used_at: str = ""  # 使用时间
    session_id: str = ""  # 会话 ID
    notes: str = ""  # 备注
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VersionRecord':
        """从字典创建"""
        return cls(**data)


class VersionHistoryManager:
    """版本历史管理器"""
    
    VERSION_FILE = "VERSION.md"
    HISTORY_DB = "version_history.json"
    
    # 当前版本号
    CURRENT_VERSION = "3.0.0"
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化版本历史管理器
        
        Args:
            db_path: 历史数据库路径
        """
        self.db_path = db_path or self.HISTORY_DB
        self.current_version = self.CURRENT_VERSION
        self._init_history()
    
    def _init_history(self):
        """初始化历史数据库"""
        if not os.path.exists(self.db_path):
            self._create_default_history()
    
    def _create_default_history(self):
        """创建默认历史记录"""
        history = {
            'current_version': self.current_version,
            'first_used': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'usage_count': 1,
            'version_records': []
        }
        
        self._save_history(history)
        logger.info(f"✅ 版本历史初始化完成：{self.current_version}")
    
    def _load_history(self) -> Dict[str, Any]:
        """加载历史记录"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载版本历史失败：{e}")
            return {
                'current_version': self.current_version,
                'first_used': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'usage_count': 0,
                'version_records': []
            }
    
    def _save_history(self, history: Dict[str, Any]):
        """保存历史记录"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def record_usage(self, session_id: str = ""):
        """
        记录版本使用
        
        Args:
            session_id: 会话 ID
        """
        history = self._load_history()
        
        # 更新使用信息
        history['last_used'] = datetime.now().isoformat()
        history['usage_count'] = history.get('usage_count', 0) + 1
        history['current_version'] = self.current_version
        
        # 添加版本记录
        record = VersionRecord(
            version=self.current_version,
            release_date=self._get_release_date(),
            changes=self._get_version_changes(),
            used_at=datetime.now().isoformat(),
            session_id=session_id
        )
        
        history['version_records'].append(record.to_dict())
        
        # 限制记录数量（保留最近 100 次）
        if len(history['version_records']) > 100:
            history['version_records'] = history['version_records'][-100:]
        
        self._save_history(history)
        logger.info(f"📊 版本使用已记录：{self.current_version} (第{history['usage_count']}次)")
    
    def _get_release_date(self) -> str:
        """获取版本发布日期"""
        # 从 VERSION.md 文件读取
        try:
            if os.path.exists(self.VERSION_FILE):
                with open(self.VERSION_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('## '):
                            # 提取日期
                            parts = line.split('[')
                            if len(parts) > 1:
                                return parts[1].split(']')[0]
        except Exception:
            pass
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_version_changes(self) -> List[str]:
        """获取版本变更列表"""
        changes = [
            "双阶段翻译参数 GUI 控制",
            "语言配置扩展（33 种目标语言）",
            "翻译方向可配置化",
            "错误处理手册（776 行）",
            "GUI 布局优化",
            "日志粒度控制增强"
        ]
        return changes
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        history = self._load_history()
        
        return {
            'version': self.current_version,
            'first_used': history.get('first_used', ''),
            'last_used': history.get('last_used', ''),
            'usage_count': history.get('usage_count', 0),
            'total_records': len(history.get('version_records', []))
        }
    
    def get_usage_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取使用历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            使用历史记录列表
        """
        history = self._load_history()
        records = history.get('version_records', [])
        
        # 按时间倒序返回
        return records[-limit:][::-1]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        history = self._load_history()
        records = history.get('version_records', [])
        
        # 按版本分组统计
        version_stats = {}
        for record in records:
            version = record.get('version', 'unknown')
            if version not in version_stats:
                version_stats[version] = {
                    'version': version,
                    'count': 0,
                    'first_used': '',
                    'last_used': ''
                }
            
            version_stats[version]['count'] += 1
            timestamp = record.get('used_at', '')
            
            if not version_stats[version]['first_used']:
                version_stats[version]['first_used'] = timestamp
            version_stats[version]['last_used'] = timestamp
        
        return {
            'total_usage': history.get('usage_count', 0),
            'versions_used': len(version_stats),
            'version_details': list(version_stats.values())
        }
    
    def export_to_json(self, output_file: Optional[str] = None) -> str:
        """
        导出版本历史到 JSON 文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            输出文件路径
        """
        output_file = output_file or "version_history_export.json"
        
        history = self._load_history()
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'current_version': self.current_version,
            'history': history
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📤 版本历史已导出：{output_file}")
        return output_file


# 全局单例
_version_manager: Optional[VersionHistoryManager] = None


def get_version_manager(db_path: Optional[str] = None) -> VersionHistoryManager:
    """
    获取全局版本历史管理器实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        版本历史管理器实例
    """
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionHistoryManager(db_path)
    return _version_manager
