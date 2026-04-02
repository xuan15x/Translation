"""
健康检查服务模块
提供系统健康状态检查功能
为未来 API 化做准备
"""
import asyncio
import time
import psutil
import os
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from infrastructure.models import Config
from infrastructure.exceptions import ErrorHandler


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    status: HealthStatus
    version: str
    timestamp: float
    checks: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'status': self.status.value,
            'version': self.version,
            'timestamp': self.timestamp,
            'checks': self.checks,
            'details': self.details
        }


class HealthCheckService:
    """
    健康检查服务
    检查系统各个组件的健康状态
    """
    
    VERSION = "3.0.0"
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化健康检查服务

        Args:
            config: 系统配置对象
        """
        self.config = config
        self._start_time = time.time()
    
    async def check(self) -> HealthCheckResult:
        """
        执行全面健康检查

        Returns:
            健康检查结果
        """
        checks = {}
        overall_status = HealthStatus.HEALTHY
        
        # 执行各项检查
        api_check = await self._check_api_connection()
        checks['api_connection'] = api_check
        
        db_check = await self._check_database()
        checks['database'] = db_check
        
        memory_check = self._check_memory()
        checks['memory'] = memory_check
        
        disk_check = self._check_disk()
        checks['disk'] = disk_check
        
        config_check = self._check_config()
        checks['config'] = config_check
        
        # 确定整体状态
        statuses = [check.get('status', 'unknown') for check in checks.values()]
        
        if any(s == 'unhealthy' for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        elif any(s == 'degraded' for s in statuses):
            overall_status = HealthStatus.DEGRADED
        
        return HealthCheckResult(
            status=overall_status,
            version=self.VERSION,
            timestamp=time.time(),
            checks=checks,
            details=self._generate_details(checks)
        )
    
    async def _check_api_connection(self) -> Dict[str, Any]:
        """
        检查 API 连接状态

        Returns:
            检查结果
        """
        result = {
            'status': 'unknown',
            'message': '',
            'latency_ms': 0
        }
        
        if not self.config:
            result['status'] = 'degraded'
            result['message'] = '配置未加载'
            return result
        
        if not self.config.api_key or not self.config.api_key.strip():
            result['status'] = 'degraded'
            result['message'] = 'API 密钥未配置'
            return result
        
        # 尝试简单的 API 调用
        try:
            start = time.time()
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            
            # 简单的模型列表请求
            await client.models.list()
            latency = (time.time() - start) * 1000
            
            result['status'] = 'healthy'
            result['message'] = 'API 连接正常'
            result['latency_ms'] = round(latency, 2)
            
        except Exception as e:
            result['status'] = 'unhealthy'
            result['message'] = f'API 连接失败：{str(e)}'
        
        return result
    
    async def _check_database(self) -> Dict[str, Any]:
        """
        检查数据库状态

        Returns:
            检查结果
        """
        result = {
            'status': 'unknown',
            'message': ''
        }
        
        try:
            import sqlite3
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..', 'data', 'terminology.db'
            )
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                conn.close()
                
                result['status'] = 'healthy'
                result['message'] = '数据库连接正常'
            else:
                result['status'] = 'degraded'
                result['message'] = '数据库文件不存在（首次启动时正常）'
                
        except Exception as e:
            result['status'] = 'unhealthy'
            result['message'] = f'数据库检查失败：{str(e)}'
        
        return result
    
    def _check_memory(self) -> Dict[str, Any]:
        """
        检查内存使用状态

        Returns:
            检查结果
        """
        result = {
            'status': 'healthy',
            'message': '',
            'usage': {}
        }
        
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # 获取系统内存信息
            system_memory = psutil.virtual_memory()
            
            result['usage'] = {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'system_percent': round(system_memory.percent, 2),
                'available_mb': round(system_memory.available / 1024 / 1024, 2)
            }
            
            # 如果系统内存使用超过 90%，标记为降级
            if system_memory.percent > 90:
                result['status'] = 'degraded'
                result['message'] = f'系统内存使用率高：{system_memory.percent}%'
            else:
                result['message'] = '内存使用正常'
                
        except Exception as e:
            result['status'] = 'unknown'
            result['message'] = f'内存检查失败：{str(e)}'
        
        return result
    
    def _check_disk(self) -> Dict[str, Any]:
        """
        检查磁盘状态

        Returns:
            检查结果
        """
        result = {
            'status': 'healthy',
            'message': '',
            'usage': {}
        }
        
        try:
            # 检查项目目录所在磁盘
            project_dir = os.path.dirname(os.path.dirname(__file__))
            disk_usage = psutil.disk_usage(project_dir)
            
            result['usage'] = {
                'total_gb': round(disk_usage.total / 1024 / 1024 / 1024, 2),
                'used_gb': round(disk_usage.used / 1024 / 1024 / 1024, 2),
                'free_gb': round(disk_usage.free / 1024 / 1024 / 1024, 2),
                'percent': round(disk_usage.percent, 2)
            }
            
            # 如果磁盘使用超过 90%，标记为降级
            if disk_usage.percent > 90:
                result['status'] = 'degraded'
                result['message'] = f'磁盘使用率高：{disk_usage.percent}%'
            else:
                result['message'] = '磁盘空间充足'
                
        except Exception as e:
            result['status'] = 'unknown'
            result['message'] = f'磁盘检查失败：{str(e)}'
        
        return result
    
    def _check_config(self) -> Dict[str, Any]:
        """
        检查配置状态

        Returns:
            检查结果
        """
        result = {
            'status': 'unknown',
            'message': '',
            'items': {}
        }
        
        if not self.config:
            result['status'] = 'degraded'
            result['message'] = '配置未加载'
            return result
        
        # 检查关键配置项
        checks = {
            'api_key': bool(self.config.api_key and self.config.api_key.strip()),
            'base_url': bool(self.config.base_url and self.config.base_url.strip()),
            'model_name': bool(self.config.model_name and self.config.model_name.strip()),
        }
        
        result['items'] = checks
        
        # 如果所有关键配置都存在，标记为健康
        if all(checks.values()):
            result['status'] = 'healthy'
            result['message'] = '配置完整'
        else:
            missing = [k for k, v in checks.items() if not v]
            result['status'] = 'degraded'
            result['message'] = f'缺少配置项：{", ".join(missing)}'
        
        return result
    
    def _generate_details(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成详细信息

        Args:
            checks: 各项检查结果

        Returns:
            详细信息字典
        """
        return {
            'uptime_seconds': round(time.time() - self._start_time, 2),
            'python_version': os.sys.version,
            'platform': os.sys.platform,
            'working_directory': os.getcwd()
        }
    
    def get_uptime(self) -> float:
        """
        获取运行时长（秒）

        Returns:
            运行时长
        """
        return time.time() - self._start_time


# 便捷函数
async def run_health_check(config: Optional[Config] = None) -> HealthCheckResult:
    """
    运行健康检查

    Args:
        config: 系统配置对象

    Returns:
        健康检查结果
    """
    service = HealthCheckService(config)
    return await service.check()


def get_health_status_simple(config: Optional[Config] = None) -> str:
    """
    获取简化的健康状态

    Args:
        config: 系统配置对象

    Returns:
        健康状态字符串
    """
    service = HealthCheckService(config)
    # 同步检查基本项目
    memory = service._check_memory()
    disk = service._check_disk()
    
    if memory['status'] == 'unhealthy' or disk['status'] == 'unhealthy':
        return 'unhealthy'
    elif memory['status'] == 'degraded' or disk['status'] == 'degraded':
        return 'degraded'
    else:
        return 'healthy'


__all__ = [
    'HealthStatus',
    'HealthCheckResult',
    'HealthCheckService',
    'run_health_check',
    'get_health_status_simple'
]
