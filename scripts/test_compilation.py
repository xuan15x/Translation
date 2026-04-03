"""
测试编译 - 验证导入是否正确
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """测试所有关键导入"""
    errors = []
    
    # 测试基础设施层导入
    try:
        from infrastructure import Config, TaskContext, StageResult, FinalResult
        from infrastructure import setup_logger, AdaptiveConcurrencyController
        print("✓ infrastructure 主模块导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure 主模块导入失败: {e}")
    
    # 测试缓存模块
    try:
        from infrastructure.cache import TerminologyCache, UnifiedCacheManager
        print("✓ infrastructure.cache 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.cache 导入失败: {e}")
    
    # 测试日志模块
    try:
        from infrastructure.logging import setup_logger, LogCategory, LoggerSlice
        print("✓ infrastructure.logging 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.logging 导入失败: {e}")
    
    # 测试数据库模块
    try:
        from infrastructure.database import ConnectionPool, DatabaseManager
        print("✓ infrastructure.database 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.database 导入失败: {e}")
    
    # 测试工具模块
    try:
        from infrastructure.utils import AdaptiveConcurrencyController, ValidationError
        print("✓ infrastructure.utils 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.utils 导入失败: {e}")
    
    # 测试模型模块
    try:
        from infrastructure.models import Config, TaskContext
        print("✓ infrastructure.models 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.models 导入失败: {e}")
    
    # 测试DI模块
    try:
        from infrastructure.di import DependencyContainer
        print("✓ infrastructure.di 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.di 导入失败: {e}")
    
    # 测试配置模块
    try:
        from infrastructure.config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT
        print("✓ infrastructure.config 导入成功")
    except Exception as e:
        errors.append(f"✗ infrastructure.config 导入失败: {e}")
    
    # 测试领域模型
    try:
        from domain.models import TranslationTask, TranslationResult, BatchResult
        print("✓ domain.models 导入成功")
    except Exception as e:
        errors.append(f"✗ domain.models 导入失败: {e}")
    
    # 报告结果
    print("\n" + "="*60)
    if errors:
        print(f"发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✓ 所有导入测试通过！")
        return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
