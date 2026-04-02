# 目录链接自动检查工具

## 📋 概述

本项目包含两个工具，用于自动检查 Markdown 文件中的目录索引链接是否匹配标题。

---

## 🔧 工具说明

### 1. check_toc_links.py - 目录链接检查器

**功能**: 扫描所有 Markdown 文件，检查目录中的锚点链接是否与实际标题匹配。

**使用方法**:

```bash
# 检查所有 Markdown 文件
python scripts/check_toc_links.py

# 检查指定文件
python scripts/check_toc_links.py README.md docs/guides/CONFIG_SETUP_HANDBOOK.md
```

**输出示例**:
```
✅ 所有文件的目录链接都正确！

# 或发现错误时：
❌ docs/guides/CONFIG_SETUP_HANDBOOK.md
============================================================
  第 8 行：[3 分钟快速配置](#3 分钟快速配置)
    ❌ 锚点 '#3 分钟快速配置' 不存在
    💡 可用的锚点:
       - #-3 分钟快速配置
       - #配置文件详解
       - #常用场景配置
```

---

### 2. pre-commit-toc-check.py - Git Pre-commit Hook

**功能**: 在 Git 提交前自动检查暂存区中的 Markdown 文件。

**安装方法**:

#### Windows (PowerShell):
```powershell
# 1. 创建 hook 脚本
Copy-Item .git/hooks/pre-commit-toc-check.py .git/hooks/pre-commit

# 2. 设置执行权限（可选）
Set-ExecutionPolicy RemoteSigned -Scope Process
```

#### Linux/Mac:
```bash
# 1. 创建符号链接
ln -s ../../.git/hooks/pre-commit-toc-check.py .git/hooks/pre-commit

# 2. 添加执行权限
chmod +x .git/hooks/pre-commit
```

**使用方法**:

安装后，每次执行 `git commit` 时会自动检查：

```bash
git add docs/guides/CONFIG_SETUP_HANDBOOK.md
git commit -m "docs: 更新配置手册"

# 自动触发检查：
# ================================================================
# 🔧 Git Pre-commit: 检查目录链接
# ================================================================
# 🔍 检查 1 个 Markdown 文件的目录链接...
# ✅ 所有文件的目录链接都正确！
# 
# ✅ Pre-commit 检查通过！
```

如果发现问题，会阻止提交并显示详细错误信息。

---

## 🎯 常见问题

### Q1: 为什么我的目录链接不可用？

**原因**: GitHub 的锚点生成规则会：
1. 转换为小写
2. 移除特殊字符（如 emoji）
3. 空格转横杠 `-`
4. 连续横杠简化为单个

**示例**:
```markdown
## ⚡ 3 分钟快速配置

# 生成的锚点是：#-3 分钟快速配置（不是 #3 分钟快速配置）
```

**修复**:
```markdown
<!-- 错误 -->
[3 分钟快速配置](#3 分钟快速配置)

<!-- 正确 -->
[3 分钟快速配置](#-3 分钟快速配置)
```

---

### Q2: 如何快速生成正确的锚点？

使用 Python 脚本：

```python
import re

def generate_anchor(title):
    anchor = title.lower()
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    return f"#{anchor}"

# 示例
print(generate_anchor("⚡ 3 分钟快速配置"))  
# 输出：#-3-分钟快速配置
```

---

### Q3: 如何禁用 pre-commit hook？

临时禁用：
```bash
git commit --no-verify -m "临时提交"
```

永久删除：
```bash
rm .git/hooks/pre-commit  # Linux/Mac
del .git\hooks\pre-commit  # Windows
```

---

## 📊 检查规则

工具会检查以下内容：

1. **目录位置**: 只检查文件前 1/3 部分（假设是目录区域）
2. **链接格式**: `[文本](#锚点)` 格式的內部链接
3. **标题匹配**: 验证锚点是否存在于文件的标题中
4. **GitHub 规则**: 按照 GitHub 的锚点生成算法计算正确 ID

---

## 🔍 技术实现

### 锚点生成算法

```python
def generate_anchor(title):
    # 1. 转小写
    anchor = title.lower()
    
    # 2. 移除特殊字符（保留中文、字母、数字、横杠）
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 3. 空格转横杠
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 4. 简化连续横杠
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    
    return anchor
```

### 标题识别

支持 `##` 到 `######` 级别的标题：
```python
pattern = r'^(#{2,6})\s+(.+)$'
```

---

## ✅ 最佳实践

1. **编写目录时立即检查**: 写完目录后立即运行检查工具
2. **使用预提交钩子**: 自动防止错误链接被提交
3. **手动验证**: 在 GitHub 上查看渲染效果
4. **保持一致性**: 目录文本与标题文本完全一致

---

## 📝 示例

### 错误的目录格式

```markdown
## 📋 目录

- [3 分钟快速配置](#3 分钟快速配置)  ❌ 错误

## ⚡ 3 分钟快速配置  # 实际标题
```

### 正确的目录格式

```markdown
## 📋 目录

- [3 分钟快速配置](#-3 分钟快速配置)  ✅ 正确

## ⚡ 3 分钟快速配置  # 实际标题
```

---

## 🚀 CI/CD 集成

可以在 GitHub Actions 中使用：

```yaml
name: Check TOC Links

on: [push, pull_request]

jobs:
  check-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Check TOC links
        run: python scripts/check_toc_links.py
```

---

## 📞 故障排查

### 问题：检查脚本无法运行

**解决**:
```bash
# 确保安装了依赖
pip install -r requirements.txt

# 或直接运行（不需要额外依赖）
python scripts/check_toc_links.py
```

### 问题：误报链接错误

某些情况下链接可能指向其他文件，这是正常的。工具只检查当前文件内的锚点链接。

---

## 📚 相关文档

- [Markdown 语法指南](https://guides.github.com/features/mastering-markdown/)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [项目文档规范](README 目录索引有效性规范)
