# P0和P1级问题修复计划

**日期**: 2026-04-03  
**状态**: 执行中

---

## 🔴 P0级修复（已完成）

### 1. 导入路径设计问题 ✅

**问题**: 相对导入导致无法正常使用

**修复方案**:
- ✅ 创建`.qwen/__init__.py`
- ✅ 创建`.qwen/skills/__init__.py`
- ✅ 更新文档示例添加sys.path说明

**修复文件**:
- `.qwen/__init__.py` - 新建
- `.qwen/skills/__init__.py` - 新建
- `code_dedup_scanner/__init__.py` - 更新文档示例
- `arch_dependency_checker/__init__.py` - 更新文档示例

---

## 🟡 P1级修复（执行中）

### 2. 标准化算法优化

**问题**: `_normalize_line`方法过于激进，可能误判

**修复方案**:
```python
@classmethod
def _normalize_line(cls, line: str) -> str:
    """标准化代码行，保留结构特征"""
    import re
    
    # 移除行尾注释
    if '#' in line:
        line = line[:line.index('#')].strip()
    
    # 替换字符串字面量
    line = re.sub(r'""".*?"""', '"""STR"""', line, flags=re.DOTALL)
    line = re.sub(r"'''.*?'''", "'''STR'''", line, flags=re.DOTALL)
    line = re.sub(r'"[^"]*"', '"STR"', line)
    line = re.sub(r"'[^']*'", "'STR'", line)
    
    # 替换数字
    line = re.sub(r'\b\d+\b', 'NUM', line)
    
    # 提取关键字
    keywords = [
        'class', 'def', 'if', 'elif', 'else', 'for', 'while', 'try',
        'except', 'finally', 'with', 'as', 'import', 'from', 'return',
        'yield', 'raise', 'pass', 'break', 'continue', 'and', 'or',
        'not', 'is', 'in', 'True', 'False', 'None', 'self', 'async',
        'await'
    ]
    
    # 保留关键字序列
    parts = [kw for kw in keywords if f' {kw} ' in f' {line} ' or line.startswith(kw + ' ')]
    
    # 如果有关键字，返回关键字序列；否则返回标准化后的行
    if parts:
        return ' '.join(parts)
    
    # 对赋值语句特殊处理
    if '=' in line and '==' not in line and '!=' not in line:
        parts = line.split('=')
        if len(parts) == 2:
            return 'VAR = VAR'  # 统一赋值语句
    
    return line.strip() if line.strip() else ''
```

**状态**: 待应用到代码

---

### 3. 相对导入解析完善

**问题**: `dots > 1`时计算层级不正确

**修复方案**:
```python
# 当前代码（错误）
for _ in range(dots - 1):  # ❌ dots=2时只移动1层
    base_dir = base_dir.parent

# 修复后
for _ in range(dots):  # ✅ dots=2时移动2层
    base_dir = base_dir.parent
```

**状态**: 待应用到代码

---

### 4. 添加基础单元测试

**问题**: 缺少测试文件

**修复方案**:
创建测试目录结构：
```
.qwen/skills/code_dedup_scanner/tests/
  ├── __init__.py
  ├── test_scanner.py
  └── test_data/
      ├── sample_duplicates.py
      └── expected_results.json

.qwen/skills/arch_dependency_checker/tests/
  ├── __init__.py
  ├── test_checker.py
  └── test_data/
      ├── sample_project/
      └── expected_violations.json
```

**测试用例**:
1. 测试重复类检测
2. 测试文件相似度计算
3. 测试架构违规检测
4. 测试报告生成

**状态**: 待创建

---

## 📝 执行计划

### 阶段一：P0修复（已完成）
- [x] 创建`.qwen/__init__.py`
- [x] 创建`.qwen/skills/__init__.py`
- [x] 更新文档示例

### 阶段二：P1-1修复（下一步）
- [ ] 优化`_normalize_line`方法
- [ ] 测试优化后的算法

### 阶段三：P1-2修复
- [ ] 修复相对导入解析逻辑
- [ ] 测试修复后的检测

### 阶段四：P1-3修复
- [ ] 创建测试目录结构
- [ ] 编写测试用例
- [ ] 运行测试验证

### 阶段五：文档更新
- [ ] 更新SKILL.md文档
- [ ] 更新使用示例
- [ ] 添加常见问题

### 阶段六：验证和提交
- [ ] 运行完整验证
- [ ] Git提交
- [ ] 推送远程

---

**预计完成时间**: 2-3小时
