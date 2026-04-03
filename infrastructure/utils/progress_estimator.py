"""
进度估计器
基于历史数据智能预测任务完成时间
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import statistics


@dataclass
class ProgressSample:
    """进度采样点"""
    timestamp: float
    completed: int
    total: int
    elapsed_time: float  # 从开始到现在的秒数
    
    @property
    def progress_percent(self) -> float:
        """进度百分比"""
        return (self.completed / self.total * 100) if self.total > 0 else 0.0


class ProgressEstimator:
    """进度估计器"""
    
    def __init__(self, window_size: int = 20):
        """
        初始化进度估计器
        
        Args:
            window_size: 用于计算平均速度的采样窗口大小
        """
        self.window_size = window_size
        self.samples: deque = deque(maxlen=window_size)
        self.start_time: Optional[float] = None
        self.total_items: int = 0
        self.current_completed: int = 0
        
        # 速度统计（每秒处理项目数）
        self.speeds: deque = deque(maxlen=window_size)
        
        # 估计值缓存
        self._cached_eta_seconds: Optional[float] = None
        self._last_calculation_time: Optional[float] = None
    
    def start(self, total_items: int):
        """
        开始跟踪进度
        
        Args:
            total_items: 总项目数
        """
        self.start_time = time.time()
        self.total_items = total_items
        self.current_completed = 0
        self.samples.clear()
        self.speeds.clear()
        self._cached_eta_seconds = None
        
        # 添加初始采样点
        self.add_sample(0)
    
    def add_sample(self, completed: int):
        """
        添加进度采样点
        
        Args:
            completed: 已完成的项目数
        """
        now = time.time()
        elapsed = now - (self.start_time or now)
        
        sample = ProgressSample(
            timestamp=now,
            completed=completed,
            total=self.total_items,
            elapsed_time=elapsed
        )
        
        self.samples.append(sample)
        self.current_completed = completed
        
        # 计算瞬时速度
        if len(self.samples) >= 2:
            prev_sample = self.samples[-2]
            time_diff = sample.timestamp - prev_sample.timestamp
            items_diff = sample.completed - prev_sample.completed
            
            if time_diff > 0:
                speed = items_diff / time_diff
                self.speeds.append(speed)
        
        # 清除缓存的估计值
        self._cached_eta_seconds = None
    
    def update(self, completed: int):
        """
        更新进度（便捷方法）
        
        Args:
            completed: 已完成的项目数
        """
        self.add_sample(completed)
    
    def get_progress(self) -> Dict:
        """
        获取当前进度信息
        
        Returns:
            包含进度相关信息的字典
        """
        if not self.samples:
            return {
                'completed': 0,
                'total': self.total_items,
                'progress_percent': 0.0,
                'eta_seconds': None,
                'eta_formatted': '--:--:--',
                'speed_per_second': 0.0,
                'elapsed_seconds': 0.0
            }
        
        current_sample = self.samples[-1]
        
        # 计算估计剩余时间
        eta_seconds = self.get_eta_seconds()
        
        # 计算平均速度
        avg_speed = self.get_average_speed()
        
        # 格式化 ETA
        eta_formatted = self._format_eta(eta_seconds)
        
        return {
            'completed': current_sample.completed,
            'total': self.total_items,
            'progress_percent': current_sample.progress_percent,
            'eta_seconds': eta_seconds,
            'eta_formatted': eta_formatted,
            'speed_per_second': round(avg_speed, 2),
            'elapsed_seconds': current_sample.elapsed_time,
            'elapsed_formatted': self._format_eta(current_sample.elapsed_time)
        }
    
    def get_eta_seconds(self) -> Optional[float]:
        """
        获取估计剩余时间（秒）
        
        Returns:
            剩余秒数，如果无法估计则返回 None
        """
        # 使用缓存（1 秒内不重复计算）
        now = time.time()
        if (self._cached_eta_seconds is not None and 
            self._last_calculation_time and 
            now - self._last_calculation_time < 1.0):
            return self._cached_eta_seconds
        
        if not self.speeds or self.current_completed >= self.total_items:
            if self.current_completed >= self.total_items:
                return 0.0
            return None
        
        # 计算平均速度
        avg_speed = self.get_average_speed()
        
        if avg_speed <= 0:
            return None
        
        # 剩余项目数
        remaining = self.total_items - self.current_completed
        
        # 估计剩余时间
        eta_seconds = remaining / avg_speed
        
        # 缓存结果
        self._cached_eta_seconds = eta_seconds
        self._last_calculation_time = now
        
        return eta_seconds
    
    def get_average_speed(self) -> float:
        """
        获取平均处理速度（每秒项目数）
        
        Returns:
            平均速度
        """
        if not self.speeds:
            return 0.0
        
        # 使用中位数避免异常值影响
        try:
            median_speed = statistics.median(self.speeds)
            return max(0.0, median_speed)
        except statistics.StatisticsError:
            return 0.0
    
    def get_completion_rate(self) -> float:
        """获取完成率（百分比）"""
        if not self.samples:
            return 0.0
        
        return self.samples[-1].progress_percent
    
    def _format_eta(self, seconds: Optional[float]) -> str:
        """
        格式化时间为可读字符串
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串 (HH:MM:SS)
        """
        if seconds is None:
            return "--:--:--"
        
        if seconds < 0:
            seconds = 0
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_detailed_stats(self) -> Dict:
        """获取详细的统计信息"""
        progress_info = self.get_progress()
        
        stats = {
            **progress_info,
            'samples_collected': len(self.samples),
            'speed_samples': len(self.speeds),
            'average_speed': self.get_average_speed(),
            'start_time': self.start_time,
            'is_complete': self.current_completed >= self.total_items
        }
        
        # 速度统计
        if self.speeds:
            try:
                stats['min_speed'] = min(self.speeds)
                stats['max_speed'] = max(self.speeds)
                stats['avg_speed'] = statistics.mean(self.speeds)
                stats['median_speed'] = statistics.median(self.speeds)
            except statistics.StatisticsError as e:
                logger.debug(f"统计数据计算失败（可能样本不足）：{e}")
        
        return stats
    
    def reset(self):
        """重置进度跟踪器"""
        self.samples.clear()
        self.speeds.clear()
        self.start_time = None
        self.total_items = 0
        self.current_completed = 0
        self._cached_eta_seconds = None
        self._last_calculation_time = None


# 全局进度估计器实例
_global_estimator: Optional[ProgressEstimator] = None


def get_progress_estimator(window_size: int = 20) -> ProgressEstimator:
    """获取全局进度估计器实例"""
    global _global_estimator
    if _global_estimator is None:
        _global_estimator = ProgressEstimator(window_size=window_size)
    return _global_estimator


def start_progress_tracking(total_items: int):
    """开始进度跟踪"""
    estimator = get_progress_estimator()
    estimator.start(total_items)


def update_progress(completed: int):
    """更新进度"""
    estimator = get_progress_estimator()
    estimator.update(completed)


def get_current_progress() -> Dict:
    """获取当前进度信息"""
    estimator = get_progress_estimator()
    return estimator.get_progress()


def format_progress_summary() -> str:
    """获取格式化的进度摘要"""
    progress = get_current_progress()
    
    summary = (
        f"进度：{progress['completed']}/{progress['total']} "
        f"({progress['progress_percent']:.1f}%) | "
        f"已用：{progress['elapsed_formatted']} | "
        f"预计剩余：{progress['eta_formatted']} | "
        f"速度：{progress['speed_per_second']:.1f} 项/秒"
    )
    
    return summary
