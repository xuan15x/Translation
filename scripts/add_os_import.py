"""
添加 os 导入到 gui_app.py
"""
import sys

# 读取文件
with open('presentation/gui_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 import logging 行并在其后添加 import os
for i, line in enumerate(lines):
    if line.strip() == 'import logging':
        # 在下一行插入 import os
        lines.insert(i + 1, 'import os\n')
        break

# 写回文件
with open('presentation/gui_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ 已成功添加 import os 到 gui_app.py")
