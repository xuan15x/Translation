"""
翻译视图模型
管理翻译状态、进度和预览数据
"""
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProgressInfo:
    """进度信息"""
    current: int = 0
    total: int = 0
    percentage: float = 0.0
    speed: float = 0.0  # 行/秒
    eta_seconds: float = 0.0  # 预计剩余时间（秒）
    status: str = "等待开始"  # 等待开始/运行中/已暂停/已完成/已停止

    @property
    def is_running(self) -> bool:
        return self.status == "运行中"

    @property
    def is_paused(self) -> bool:
        return self.status == "已暂停"

    def update(self, current: int, total: int, speed: float = 0, eta_seconds: float = 0):
        """更新进度"""
        self.current = current
        self.total = total
        self.percentage = (current / total * 100) if total > 0 else 0.0
        self.speed = speed
        self.eta_seconds = eta_seconds

    def format_eta(self) -> str:
        """格式化预计剩余时间"""
        if self.eta_seconds <= 0:
            return "--:--:--"
        hours = int(self.eta_seconds // 3600)
        minutes = int((self.eta_seconds % 3600) // 60)
        seconds = int(self.eta_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class PerformanceMetrics:
    """性能指标"""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    api_calls: int = 0
    success_rate: float = 0.0
    is_monitoring: bool = False


@dataclass 
class PreviewItem:
    """预览数据项"""
    source: str = ""
    target: str = ""
    lang: str = ""
    row_number: int = 0


class TranslationViewModel:
    """翻译视图模型 - 管理翻译状态和进度"""

    def __init__(self):
        # 翻译状态
        self.is_running = False
        self.is_paused = False
        
        # 进度信息
        self.progress = ProgressInfo()
        
        # 性能监控
        self.performance = PerformanceMetrics()
        
        # 预览数据
        self.preview_data: List[PreviewItem] = []
        
        # 进度回调
        self._progress_callback: Optional[Callable] = None
        
        logger.debug("TranslationViewModel 初始化完成")

    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self._progress_callback = callback

    def start_translation(self):
        """开始翻译"""
        self.is_running = True
        self.is_paused = False
        self.progress.status = "运行中"
        self._notify_progress()
        logger.info("🚀 翻译开始")

    def pause_translation(self):
        """暂停翻译"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.progress.status = "已暂停"
            self._notify_progress()
            logger.info("⏸️ 翻译已暂停")

    def resume_translation(self):
        """恢复翻译"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.progress.status = "运行中"
            self._notify_progress()
            logger.info("▶️ 翻译已恢复")

    def stop_translation(self):
        """停止翻译"""
        self.is_running = False
        self.is_paused = False
        self.progress.status = "已停止"
        self._notify_progress()
        logger.info("⏹️ 翻译已停止")

    def complete_translation(self, success_rate: float = 0.0):
        """完成翻译"""
        self.is_running = False
        self.is_paused = False
        self.progress.status = f"已完成 ({success_rate:.1f}%)"
        self.progress.percentage = 100.0
        self._notify_progress()
        logger.info(f"✅ 翻译完成，成功率: {success_rate:.1f}%")

    def update_progress(self, current: int, total: int, speed: float = 0, eta_seconds: float = 0):
        """
        更新进度
        
        Args:
            current: 当前行数
            total: 总行数
            speed: 速度（行/秒）
            eta_seconds: 预计剩余时间（秒）
        """
        if not self.is_running:
            return
            
        self.progress.update(current, total, speed, eta_seconds)
        self._notify_progress()

    def update_performance(self, metrics: Dict[str, Any]):
        """
        更新性能指标
        
        Args:
            metrics: 性能指标字典
        """
        if 'cpu_percent' in metrics:
            self.performance.cpu_percent = metrics['cpu_percent']
        if 'memory_mb' in metrics:
            self.performance.memory_mb = metrics['memory_mb']
        if 'api_calls' in metrics:
            self.performance.api_calls = metrics['api_calls']
        if 'success_rate' in metrics:
            self.performance.success_rate = metrics['success_rate']

    def add_preview_item(self, item: PreviewItem):
        """添加预览数据项"""
        self.preview_data.append(item)

    def clear_preview(self):
        """清空预览数据"""
        self.preview_data.clear()

    def reset(self):
        """重置所有状态"""
        self.is_running = False
        self.is_paused = False
        self.progress = ProgressInfo()
        self.performance = PerformanceMetrics()
        self.preview_data.clear()
        self._notify_progress()
        logger.debug("🔄 视图模型已重置")

    def _notify_progress(self):
        """通知进度更新"""
        if self._progress_callback:
            try:
                self._progress_callback(self.progress)
            except Exception as e:
                logger.error(f"进度回调执行失败: {e}")

    def get_status_text(self) -> str:
        """获取状态文本"""
        if self.is_paused:
            return "⏸ 已暂停"
        elif self.progress.is_running:
            return "▶ 运行中"
        elif "已完成" in self.progress.status:
            return "✅ 已完成"
        elif self.is_running:
            return "▶ 运行中"
        else:
            return "⏸ 等待"

    def get_status_color(self) -> str:
        """获取状态颜色"""
        if self.is_paused:
            return "#cc6600"  # 橙色
        elif self.progress.is_running:
            return "#00aa00"  # 绿色
        elif "已完成" in self.progress.status:
            return "#0066cc"  # 蓝色
        else:
            return "#666666"  # 灰色
