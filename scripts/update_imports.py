"""
重构辅助脚本 - 批量更新导入语句
"""
import os
import re

# 定义导入映射
IMPORT_MAPPINGS = {
    # infrastructure 层的导入
    'from infrastructure.logging import': 'from infrastructure.logging import',
    'from infrastructure.logging import': 'from infrastructure.logging import',
    'from infrastructure.logging import': 'from infrastructure.logging import',
    'from infrastructure.logging import': 'from infrastructure.logging import',
    'from infrastructure.cache import': 'from infrastructure.cache import',
    'from infrastructure.cache import': 'from infrastructure.cache import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.database import': 'from infrastructure.database import',
    'from infrastructure.database import': 'from infrastructure.database import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.di import': 'from infrastructure.di import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    'from infrastructure.utils import': 'from infrastructure.utils import',
    
    # config 模块的导入（移动到 infrastructure.config）
    'from config.config import': 'from config.config import',
    'from config.loader import': 'from config.loader import',
    'from config.checker import': 'from config.checker import',
    'from config.constants import': 'from config.constants import',
    'from config.model_manager import': 'from config.model_manager import',
    'from config.model_providers import': 'from config.model_providers import',
}

def update_imports_in_file(filepath):
    """更新单个文件中的导入语句"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换导入语句
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # 只有当内容有变化时才写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"已更新: {filepath}"
        return False, f"无需更新: {filepath}"
    except Exception as e:
        return False, f"错误 {filepath}: {str(e)}"

def scan_and_update_python_files(base_dir):
    """扫描并更新所有Python文件"""
    updated_count = 0
    error_count = 0
    messages = []
    
    for root, dirs, files in os.walk(base_dir):
        # 跳过 __pycache__ 目录
        if '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                updated, message = update_imports_in_file(filepath)
                messages.append(message)
                if updated:
                    updated_count += 1
                if '错误' in message:
                    error_count += 1
    
    return updated_count, error_count, messages

if __name__ == '__main__':
    base_dir = r'C:\Users\13457\PycharmProjects\translation'
    print("开始批量更新导入语句...")
    print("=" * 60)
    
    updated_count, error_count, messages = scan_and_update_python_files(base_dir)
    
    for message in messages:
        print(message)
    
    print("=" * 60)
    print(f"\n重构完成:")
    print(f"  - 更新文件数: {updated_count}")
    print(f"  - 错误数: {error_count}")
