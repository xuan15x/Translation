"""
数据模型模块（向后兼容）
原有 models.py 拆分为：
  - config.py: Config 配置类
  - config_validators.py: 配置验证器
  - context.py: TaskContext, StageResult, FinalResult
"""
from .config import Config
from .context import TaskContext, StageResult, FinalResult

__all__ = ['Config', 'TaskContext', 'StageResult', 'FinalResult']
