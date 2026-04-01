> ⚠️ **重要提示**: 本文档内容已整合到 [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)  
> 建议优先阅读新手册获取更全面、更准确的信息
> 
> **整合日期**: 2026-04-01  
> **替代文档**: [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) 使用教程

---

# 全局退出机制和统一 Excel 保存功能

## 📋 功能概述

本次更新实现了完整的全局退出机制，在程序退出时（通过退出按钮或关闭窗口）自动将所有使用 SQLite 内存数据库存储的数据转换为 Excel 文件保存，提高数据的可读性和可修改性，降低使用难度。

## ✨ 主要特性

### 1. **统一的退出按钮**
- 在 GUI 界面添加了"🚪 退出程序"按钮
- 点击后显示确认对话框
- 自动保存所有数据库到 Excel
- 显示保存结果统计

### 2. **窗口关闭自动保存**
- 拦截窗口关闭事件（WM_DELETE_WINDOW）
- 自动触发数据保存流程
- 确保数据不会丢失

### 3. **全面的数据覆盖**
支持保存以下数据类型：
- ✅ **术语库** (`terminology.xlsx`) - 使用 `TerminologyPersistence`
- ✅ **翻译历史** (`translation_history.xlsx`) - 使用 `TranslationHistoryManager.export_to_excel()`
- ✅ **术语历史** (`terminology_history.xlsx`) - 使用 `TerminologyHistoryManager.export_to_excel()`

### 4. **智能数据管理**
- 使用全局单例模式管理所有持久化实例
- 支持动态注册新的数据源
- 统一的保存和关闭接口

## 🔧 技术实现

### 核心组件

#### 1. **GlobalPersistenceManager** (`data_access/global_persistence_manager.py`)
```python
class GlobalPersistenceManager:
    """全局持久化管理器 - 单例模式"""
    
    def register_terminology(persistence)      # 注册术语库
    def register_history(persistence)           # 注册历史库
    def register_translation_history(manager)   # 注册翻译历史管理器
    def register_terminology_history(manager)   # 注册术语历史管理器
    
    def save_all()          # 保存所有到 Excel
    def close_all()         # 关闭所有连接
    def shutdown_all()      # 完整流程：先保存，再关闭
```

#### 2. **退出流程** (`presentation/gui_app.py`)
```python
def _exit_application(self):
    """退出程序并保存所有数据库到 Excel"""
    1. 显示确认对话框
    2. 调用 shutdown_all_databases()
    3. 显示保存结果
    4. 关闭窗口

def _on_closing(self):
    """窗口关闭事件处理"""
    self._exit_application()
```

#### 3. **数据导出方法**

**术语库和历史库** (`data_access/excel_sqlite_persistence.py`):
```python
class TerminologyPersistence:
    def save_to_excel(output_path) -> str

class HistoryPersistence:
    def save_to_excel(output_path) -> str
```

**翻译历史和术语历史** (`service/translation_history.py`, `service/terminology_history.py`):
```python
def export_to_excel(output_path) -> str
```

## 📁 生成的 Excel 文件

### 1. 术语库 (`terminology.xlsx`)
| 列名 | 说明 |
|------|------|
| 中文原文 | 源文本 |
| English | 英文翻译 |
| 日本語 | 日文翻译 |
| ... | 其他语言 |

### 2. 翻译历史 (`translation_history.xlsx`)
| 列名 | 说明 |
|------|------|
| id | 记录 ID |
| key | 原文键 |
| source_text | 原文 |
| target_lang | 目标语言 |
| draft_trans | 初译 |
| final_trans | 最终译文 |
| status | 状态 (SUCCESS/FAILED) |
| api_provider | API 提供商 |
| created_at | 创建时间 |

### 3. 术语历史 (`terminology_history.xlsx`)
| 列名 | 说明 |
|------|------|
| id | 记录 ID |
| timestamp | 时间戳 |
| change_type | 变更类型 (added/updated/deleted) |
| source_text | 源文本 |
| language | 目标语言 |
| old_value | 旧值 |
| new_value | 新值 |

## 🎯 使用方法

### 方式一：点击退出按钮
1. 点击 GUI 界面上的"🚪 退出程序"按钮
2. 确认退出
3. 等待保存完成提示
4. 程序自动关闭

### 方式二：关闭窗口
1. 点击窗口右上角的关闭按钮 (X)
2. 自动触发保存流程
3. 程序自动关闭

### 方式三：编程调用
```python
from data_access.global_persistence_manager import shutdown_all_databases

# 保存并关闭所有数据库
results = shutdown_all_databases()
print(f"保存成功：{results['total_saved']} 个数据库")
```

## 🧪 测试验证

运行测试脚本验证功能：
```bash
python scripts/test_exit_and_save.py
```

测试内容包括：
- ✅ 全局管理器实例化
- ✅ 保存所有数据库
- ✅ 关闭所有数据库
- ✅ 验证 Excel 文件生成

## 📊 数据统计

每次退出时会显示详细的统计信息：

```
💾 开始保存所有数据库到 Excel...
✅ terminology 已保存：terminology.xlsx
✅ translation_history 已导出：translation_history.xlsx
✅ terminology_history 已导出：terminology_history.xlsx
💾 保存完成：成功 3/3, 失败 0/3

🔒 关闭完成：成功 3, 失败 0
✅ 全局持久化管理器已正常关闭
```

## ⚠️ 注意事项

1. **首次运行**：如果是首次运行且没有数据，Excel 文件可能不会生成（正常现象）
2. **数据为空**：如果数据库为空，会跳过保存并在日志中提示
3. **文件覆盖**：Excel 文件会被覆盖保存，请注意备份重要数据
4. **异常处理**：如果保存失败，会显示错误信息并建议检查日志

## 🔍 故障排查

### 问题：退出时没有生成 Excel 文件
**原因**：数据库中没有数据
**解决**：先执行一些翻译任务，产生数据后再退出

### 问题：保存失败提示权限错误
**原因**：Excel 文件被其他程序占用
**解决**：关闭正在查看 Excel 的程序，重新退出

### 问题：部分数据保存失败
**原因**：可能是数据格式错误或磁盘空间不足
**解决**：检查日志获取详细错误信息

## 📝 更新日志

### v2.2.0 (2026-04-01)
- ✅ 添加 `_exit_application` 方法，支持退出按钮保存
- ✅ 添加 `_on_closing` 方法，拦截窗口关闭事件
- ✅ 注册翻译历史管理器和术语历史管理器
- ✅ 增强 `GlobalPersistenceManager` 支持历史管理器
- ✅ 为 `TranslationHistoryManager` 添加 `export_to_excel` 方法
- ✅ 修复 `shutdown_all` 方法字典键访问错误
- ✅ 添加测试脚本 `test_exit_and_save.py`

## 🎉 优势总结

1. **提高可读性**：Excel 文件可直接用 Excel 打开查看和编辑
2. **便于备份**：Excel 文件易于版本管理和云同步
3. **降低门槛**：用户无需了解数据库结构，直接操作 Excel
4. **数据安全**：程序退出时自动保存，防止数据丢失
5. **统一管理**：所有数据源统一保存，避免遗漏
