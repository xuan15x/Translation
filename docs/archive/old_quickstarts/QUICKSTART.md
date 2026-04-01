# AI 智能翻译工作台 - 启动指南

##  快速开始

### 方法一：使用批处理文件（推荐）

**Windows CMD 用户：**
```bash
双击运行：启动翻译平台.bat
```

或命令行：
```bash
.\启动翻译平台.bat
```

### 方法二：使用 PowerShell 脚本

**PowerShell 用户：**
```powershell
.\启动翻译平台.ps1
```

如果 PowerShell 提示脚本执行策略错误，请先运行：
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 方法三：直接命令行启动

```bash
python presentation/translation.py
```

带配置文件启动：
```bash
python presentation/translation.py config/config.json
```

---

## 🔧 环境检查

在首次启动前，建议先运行环境检查：

**CMD 用户：**
```bash
scripts\check_env.bat
```

**Python 用户（跨平台）：**
```bash
python scripts/check_environment.py
```

---

## 📋 启动脚本功能

### 启动翻译平台.bat / .ps1

**功能：**
- ✅ 自动检测 Python 是否安装
- ✅ 检查配置文件是否存在
- ✅ 启动现代化 GUI 应用
- ✅ 错误处理和友好提示
- ✅ 退出状态检测

**启动流程：**
1. 检查 Python 环境
2. 检查配置文件
3. 启动现代化 GUI
4. 显示退出状态

### check_env.bat / check_environment.py

**功能：**
- ✅ 检查 Python 版本（需要 3.8+）
- ✅ 检查必需依赖（tkinter, openpyxl）
- ✅ 检查可选依赖（PyYAML）
- ✅ 检查配置文件
- ✅ 检查项目结构完整性

**检查项：**
1. Python 版本
2. 依赖包
3. 配置文件
4. 项目结构

---

##  使用示例

### 1. 首次使用

```bash
# 1. 检查环境
python scripts/check_environment.py

# 2. 复制配置示例
cp config/config.example.json config/config.json

# 3. 编辑配置文件
# 在文本编辑器中打开 config/config.json
# 填入你的 API 密钥和其他配置

# 4. 启动应用
.\启动翻译平台.bat
```

### 2. 日常使用

```bash
# 直接双击启动
.\启动翻译平台.bat
```

### 3. 带参数启动

```bash
# 使用自定义配置文件
python presentation/translation.py path/to/your/config.json
```

---

## ⚠️ 常见问题

### Q1: 提示 "未检测到 Python"

**解决方案：**
1. 安装 Python 3.8 或更高版本
2. 确保 Python 已添加到系统 PATH
3. 重启终端或命令行

### Q2: 提示 "tkinter 缺失"

**解决方案：**
```bash
# Windows 用户
# tkinter 通常随 Python 一起安装
# 如果没有，重新安装 Python 并勾选 tcl/tk 支持

# Linux 用户
sudo apt-get install python3-tk
```

### Q3: 提示 "openpyxl 缺失"

**解决方案：**
```bash
pip install openpyxl
```

### Q4: 提示 "PyYAML 缺失"

**解决方案：**
```bash
pip install pyyaml
```

这是可选依赖，不影响基本功能。

### Q5: PowerShell 无法运行脚本

**解决方案：**
```powershell
# 更改执行策略
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 或者使用批处理版本
.\启动翻译平台.bat
```

---

## 📁 项目结构

```
translation/
├── 启动翻译平台.bat          # CMD 启动脚本
├── 启动翻译平台.ps1          # PowerShell 启动脚本
├── presentation/
│   ├── translation.py        # 主入口文件
│   └── modern_gui_app.py     # 现代化 GUI
├── config/
│   ├── config.json           # 主配置文件
│   └── config.example.json   # 配置示例
└── scripts/
    ├── check_env.bat         # CMD 环境检查
    └── check_environment.py  # Python 环境检查
```

---

## 🎯 现代化 GUI 特性

全新重构的现代化 GUI 包含：

- ✅ 统一美观的样式
- ✅ 清晰合理的布局
- ✅ 完整的功能按钮
- ✅ 支持鼠标滚轮滚动
- ✅ 自适应窗口大小（1200x900）
- ✅ 响应式设计
- ✅ 8 大功能区域：
  - 📂 文件配置
  - 🔌 API 配置
  - ⚙️ 双阶段参数
  - 🎮 翻译方向
  - 🌍 目标语言（T1/T2/T3）
  - 📝 提示词配置
  - 🚀 执行控制
  - 📋 运行日志

---

## 📞 技术支持

如遇到其他问题，请：

1. 检查环境：`python scripts/check_environment.py`
2. 查看日志输出
3. 确认配置文件正确
4. 检查 Python 和依赖版本

---

**祝使用愉快！** 🎉
