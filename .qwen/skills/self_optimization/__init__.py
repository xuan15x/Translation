"""
自我优化 Skill 包
为所有子智能体提供任务后自动反思功能

Usage:
    from skills.self_optimization import SelfReflectionSkill
    
    # 任务完成后自动反思
    SelfReflectionSkill.auto_reflect(
        task_id="task_001",
        task_description="重构代码",
        agent_type="code-reviewer",
        execution_result={...}
    )
"""
from .reflector import SelfReflectionSkill

__all__ = ['SelfReflectionSkill']
__version__ = '1.0.0'
