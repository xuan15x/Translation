"""
重构脚本：修复P1级问题
1. 删除重复的_validate_config方法
2. 重构剩余的一个_validate_config为子验证器
"""
import re

# 读取文件
with open('infrastructure/models.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# 找到两个_validate_config的位置
first_validate = None
second_validate = None
track_config = None

for i, line in enumerate(lines):
    if '    def _validate_config(self):' in line:
        if first_validate is None:
            first_validate = i
        else:
            second_validate = i
    if '    def _track_config_usage(self):' in line and first_validate is not None and second_validate is None:
        track_config = i

print(f"第一个 _validate_config: 行 {first_validate + 1 if first_validate is not None else None}")
print(f"_track_config_usage: 行 {track_config + 1 if track_config is not None else None}")
print(f"第二个 _validate_config: 行 {second_validate + 1 if second_validate is not None else None}")

# 删除第一个_validate_config (从first_validate到track_config之前)
if first_validate is not None and track_config is not None:
    # 找到第一个_validate_config前面的空行
    start = first_validate
    while start > 0 and lines[start - 1].strip() == '':
        start -= 1
    
    # 删除从start到track_config-1的所有行
    del lines[start:track_config]
    
    print(f"\n已删除第一个_validate_config方法 (行 {start+1} 到 {track_config})")

# 保存修改后的内容
with open('infrastructure/models.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("\n✅ 重复的_validate_config方法已删除")
print("下一步：手动重构剩余的_validate_config方法")
