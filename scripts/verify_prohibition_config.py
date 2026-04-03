"""快速验证禁止事项配置功能"""
import sys
from pathlib import Path

# 添加项目根目录到路径
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from infrastructure.config.loader import get_config_loader

loader = get_config_loader()
config = loader.get('prohibition_config')

print('✅ 配置文件中的 prohibition_config:')
print(f'   类别数：{len(config) if config else 0}')
if config:
    print(f'   类别列表：{list(config.keys())}')
    print(f'\n📋 global_prohibitions 数量：{len(config.get("global_prohibitions", []))}')
    print(f'📋 match3_prohibitions 数量：{len(config.get("match3_prohibitions", []))}')
    print(f'📋 ui_prohibitions 数量：{len(config.get("ui_prohibitions", []))}')
else:
    print('   ❌ 未找到配置，将使用默认值')
