"""
性能监控模块
实时监控系统性能指标，提供性能分析和告警
"""
import asyncio
import time
import psutil
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    active_threads: int = 0
    open_files: int = 0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, sample_interval: float = 1.0, 
                 history_size: int = 300):
        """
        初始化性能监控器
        
        Args:
            sample_interval: 采样间隔（秒）
            history_size: 历史记录数量（5 分钟默认）
        """
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.history: deque = deque(maxlen=history_size)
        
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # 进程信息
        self.process = psutil.Process(os.getpid())
        
        # 告警阈值
        self.thresholds = {
            'cpu_high': 80.0,
            'memory_high': 80.0,
            'memory_critical': 90.0
        }
        
        # 统计信息
        self.stats = {
            'samples_collected': 0,
            'alerts_triggered': 0,
            'peak_cpu': 0.0,
            'peak_memory_mb': 0.0
        }
    
    async def start(self):
        """启动性能监控"""
        if self._monitoring:
            logger.warning("性能监控已在运行中")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"性能监控已启动 (间隔:{self.sample_interval}s, 历史:{self.history_size})")
    
    async def stop(self):
        """停止性能监控"""
        self._monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                logger.debug("监控任务已取消")
        
        logger.info("性能监控已停止")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                self.history.append(metrics)
                self.stats['samples_collected'] += 1
                
                # 更新峰值
                self.stats['peak_cpu'] = max(self.stats['peak_cpu'], metrics.cpu_percent)
                self.stats['peak_memory_mb'] = max(self.stats['peak_memory_mb'], metrics.memory_mb)
                
                # 检查告警
                self._check_alerts(metrics)
                
            except Exception as e:
                logger.error(f"性能监控异常：{e}")
            
            await asyncio.sleep(self.sample_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集当前性能指标"""
        # CPU 使用率
        cpu_percent = self.process.cpu_percent(interval=None)
        
        # 内存使用
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        memory_percent = self.process.memory_percent()
        
        # 磁盘 IO
        try:
            io_counters = self.process.io_counters()
            disk_io_read_mb = io_counters.read_bytes / (1024 * 1024)
            disk_io_write_mb = io_counters.write_bytes / (1024 * 1024)
        except (AttributeError, psutil.AccessDenied):
            disk_io_read_mb = 0.0
            disk_io_write_mb = 0.0
        
        # 网络 IO（需要管理员权限）
        try:
            net_io = psutil.net_io_counters()
            network_sent_mb = net_io.bytes_sent / (1024 * 1024)
            network_recv_mb = net_io.bytes_recv / (1024 * 1024)
        except (AttributeError, psutil.AccessDenied):
            network_sent_mb = 0.0
            network_recv_mb = 0.0
        
        # 线程和文件
        active_threads = self.process.num_threads()
        open_files = len(self.process.open_files())
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_threads=active_threads,
            open_files=open_files
        )
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查并触发告警"""
        alerts = []
        
        # CPU 告警
        if metrics.cpu_percent > self.thresholds['cpu_high']:
            alerts.append(f"CPU 使用率过高：{metrics.cpu_percent:.1f}%")
        
        # 内存告警
        if metrics.memory_percent > self.thresholds['memory_critical']:
            alerts.append(f"内存使用严重过高：{metrics.memory_percent:.1f}%")
            self.stats['alerts_triggered'] += 1
        elif metrics.memory_percent > self.thresholds['memory_high']:
            alerts.append(f"内存使用过高：{metrics.memory_percent:.1f}%")
        
        # 记录告警
        for alert in alerts:
            logger.warning(f"⚠️ 性能告警：{alert}")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """获取当前性能指标"""
        return self._collect_metrics()
    
    def get_average_metrics(self, window_seconds: int = 60) -> Dict[str, float]:
        """
        获取指定时间窗口的平均指标
        
        Args:
            window_seconds: 时间窗口（秒）
            
        Returns:
            平均指标字典
        """
        samples_needed = int(window_seconds / self.sample_interval)
        
        if len(self.history) < samples_needed:
            samples = list(self.history)
        else:
            samples = list(self.history)[-samples_needed:]
        
        if not samples:
            return {}
        
        avg_cpu = sum(s.cpu_percent for s in samples) / len(samples)
        avg_memory = sum(s.memory_mb for s in samples) / len(samples)
        avg_threads = sum(s.active_threads for s in samples) / len(samples)
        
        return {
            'avg_cpu_percent': round(avg_cpu, 2),
            'avg_memory_mb': round(avg_memory, 2),
            'avg_threads': round(avg_threads, 1),
            'sample_count': len(samples)
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        current = self.get_current_metrics()
        averages = self.get_average_metrics()
        
        return {
            **self.stats,
            'current': {
                'cpu_percent': current.cpu_percent,
                'memory_mb': current.memory_mb,
                'threads': current.active_threads
            },
            'averages': averages,
            'thresholds': self.thresholds
        }
    
    def set_threshold(self, name: str, value: float):
        """
        设置告警阈值
        
        Args:
            name: 阈值名称
            value: 阈值
        """
        if name in self.thresholds:
            self.thresholds[name] = value
            logger.info(f"阈值已更新：{name}={value}")
        else:
            logger.warning(f"未知阈值：{name}")


# 全局性能监控实例
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


async def start_performance_monitoring(sample_interval: float = 1.0):
    """启动全局性能监控"""
    monitor = get_performance_monitor()
    monitor.sample_interval = sample_interval
    await monitor.start()


async def stop_performance_monitoring():
    """停止全局性能监控"""
    monitor = get_performance_monitor()
    await monitor.stop()


def get_performance_stats() -> Dict:
    """获取性能统计信息"""
    monitor = get_performance_monitor()
    return monitor.get_stats()
