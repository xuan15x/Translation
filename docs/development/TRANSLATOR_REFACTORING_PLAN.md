# 翻译器深度重构实施计划

**创建日期**: 2026-04-03  
**版本**: v1.0  
**状态**: 实施中

---

## 📋 重构概述

### 目标
深度重构翻译器，实现以下核心功能：
1. ✅ 行级断点续传
2. ✅ 实时进度显示
3. ✅ 翻译预览
4. ✅ 暂停/恢复功能
5. ✅ 状态持久化

### 当前进度
- ✅ 新翻译器核心代码已完成 (`application/enhanced_translator.py`)
- ✅ Facade层已添加支持方法
- ⏸️ GUI适配待完成
- ⏸️ 完整测试待执行
- ⏸️ 旧代码解耦待执行

---

## 🏗️ 架构设计

### 新旧架构对比

#### 旧架构
```
GUI → Facade → BatchTaskProcessor → WorkflowCoordinator → API调用
```

**问题**:
- 无法暂停/恢复
- 无断点续传
- 进度回调简单
- 无状态持久化

#### 新架构
```
GUI → Facade → EnhancedTranslator → Facade.translate_text() → API调用
                ↓
          TranslationState (断点续传)
                ↓
          TranslationProgress (实时进度)
```

**优势**:
- ✅ 支持暂停/恢复
- ✅ 行级断点续传
- ✅ 实时进度回调
- ✅ 翻译预览
- ✅ 状态持久化

---

## 🔧 实施步骤

### 阶段一：核心代码实现 ✅

#### 1.1 增强型翻译器 ✅
**文件**: `application/enhanced_translator.py`

**已实现功能**:
- [x] TranslationState 数据类
- [x] TranslationProgress 数据类  
- [x] EnhancedTranslator 核心类
- [x] pause() / resume() / stop() 方法
- [x] 状态持久化（JSON文件）
- [x] 进度回调机制
- [x] 预览回调机制

#### 1.2 Facade层更新 ✅
**文件**: `application/translation_facade.py`

**已添加**:
- [x] enable_enhanced_translator() 方法
- [x] pause_translation() 方法
- [x] resume_translation() 方法
- [x] stop_translation() 方法
- [x] set_progress_callback_enhanced() 方法
- [x] set_preview_callback() 方法

---

### 阶段二：GUI适配 ⏸️ 待实施

#### 2.1 添加暂停/恢复按钮

**文件**: `presentation/gui_app.py`

**需要添加的代码**:

```python
# 在 __init__ 中添加
self.is_paused = False

# 在 _setup_ui 的按钮区域添加
def _create_pause_button(self, parent):
    """创建暂停/恢复按钮"""
    self.pause_btn = ttk.Button(
        parent,
        text="⏸️ 暂停",
        command=self._toggle_pause,
        state='disabled'
    )
    self.pause_btn.pack(side=tk.LEFT, padx=5)

# 暂停/恢复切换
def _toggle_pause(self):
    """切换暂停/恢复状态"""
    if self.is_paused:
        # 恢复
        self.translation_facade.resume_translation()
        self.pause_btn.config(text="⏸️ 暂停")
        self.is_paused = False
        logger.info("▶️ 已恢复翻译")
    else:
        # 暂停
        self.translation_facade.pause_translation()
        self.pause_btn.config(text="▶️ 恢复")
        self.is_paused = True
        logger.info("⏸️ 已暂停翻译")
```

#### 2.2 更新进度显示

```python
def _setup_enhanced_progress_callback(self):
    """设置增强型进度回调"""
    def on_progress(progress: TranslationProgress):
        # 更新进度条
        self.progress_var.set(progress.percentage)
        
        # 更新进度标签
        speed = f"{progress.speed:.1f} 行/秒"
        eta = f"预计剩余: {progress.eta_seconds:.0f} 秒"
        self.progress_label.config(
            text=f"{progress.completed_lines}/{progress.total_lines} | {speed} | {eta}"
        )
        
        # 记录日志
        logger.info(
            f"📊 进度: {progress.percentage:.1f}% | "
            f"{progress.completed_lines}/{progress.total_lines} | "
            f"{speed}"
        )
    
    self.translation_facade.set_progress_callback_enhanced(on_progress)
```

#### 2.3 添加预览窗口

```python
def _create_preview_panel(self, parent):
    """创建翻译预览面板"""
    preview_frame = ttk.LabelFrame(parent, text="👁️ 翻译预览 (前10行)", padding="10")
    preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 创建表格
    columns = ('源文本', '翻译结果')
    self.preview_tree = ttk.Treeview(
        preview_frame,
        columns=columns,
        show='headings',
        height=10
    )
    
    self.preview_tree.heading('源文本', text='源文本')
    self.preview_tree.heading('翻译结果', text='翻译结果')
    self.preview_tree.column('源文本', width=300)
    self.preview_tree.column('翻译结果', width=300)
    
    # 添加滚动条
    scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
    self.preview_tree.configure(yscrollcommand=scrollbar.set)
    
    self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 设置预览回调
    def on_preview(rows):
        # 清空现有数据
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 添加新数据
        for row in rows:
            source = row.get('source_text', '')
            # 获取第一个目标语言的翻译
            translation = row.get(self.selected_langs[0], '') if self.selected_langs else ''
            self.preview_tree.insert('', tk.END, values=(source[:50], translation[:50]))
    
    self.translation_facade.set_preview_callback(on_preview)
```

#### 2.4 启用增强型翻译器

```python
# 在 _initialize_services 方法中添加
def _initialize_services(self):
    """初始化服务"""
    # ... 现有代码 ...
    
    # 启用增强型翻译器
    self.translation_facade.enable_enhanced_translator(True)
    self._setup_enhanced_progress_callback()
```

---

### 阶段三：完整测试 ⏸️ 待实施

#### 3.1 单元测试

创建测试文件 `tests/test_enhanced_translator.py`:

```python
import pytest
import asyncio
from application.enhanced_translator import EnhancedTranslator, TranslationState, TranslationProgress

@pytest.fixture
def translator(mock_facade):
    """创建翻译器实例"""
    return EnhancedTranslator(
        translation_facade=mock_facade,
        state_dir=".test_state",
        preview_lines=5
    )

async def test_pause_resume(translator):
    """测试暂停/恢复功能"""
    # 启动翻译
    task = asyncio.create_task(translator.translate_with_resume(...))
    
    # 暂停
    translator.pause()
    assert translator.state.is_paused == True
    
    # 恢复
    translator.resume()
    assert translator.state.is_paused == False
    
    await task

async def test_state_persistence(translator):
    """测试状态持久化"""
    # 执行部分翻译
    await translator.translate_with_resume(...)
    
    # 验证状态文件存在
    state_file = translator.state_dir / f"{translator.state.batch_id}.json"
    assert state_file.exists()
    
    # 加载状态
    loaded_state = TranslationState.load(str(state_file))
    assert loaded_state.current_line > 0

async def test_resume_from_checkpoint(translator):
    """测试断点续传"""
    # 第一次翻译（部分）
    translator.pause()
    await asyncio.sleep(0.1)  # 等待暂停生效
    
    # 第二次翻译（恢复）
    translator.resume()
    result = await translator.translate_with_resume(...)
    
    # 验证从断点继续
    assert result.current_line == result.total_lines
```

#### 3.2 集成测试

```python
async def test_full_translation_with_pause():
    """完整翻译流程测试（含暂停/恢复）"""
    # 1. 准备测试数据
    # 2. 启动翻译
    # 3. 中途暂停
    # 4. 恢复翻译
    # 5. 验证结果
    pass
```

---

### 阶段四：旧代码解耦 ⏸️ 待实施

#### 4.1 标记旧代码为废弃

在旧代码中添加废弃警告：

```python
# application/batch_processor.py
import warnings

warnings.warn(
    "BatchTaskProcessor 将在 v4.0 中移除，请使用 EnhancedTranslator",
    DeprecationWarning,
    stacklevel=2
)
```

#### 4.2 逐步替换调用

1. 更新GUI默认使用新翻译器
2. 更新所有测试用例
3. 更新文档

#### 4.3 删除旧代码

确认无调用后删除：
- `application/batch_processor.py` (部分功能已集成到EnhancedTranslator)
- 旧的进度回调机制

---

## 📊 迁移检查清单

### 代码迁移
- [x] 创建EnhancedTranslator类
- [x] 更新Facade添加支持方法
- [ ] 更新GUI添加暂停/恢复按钮
- [ ] 更新GUI添加预览面板
- [ ] 更新进度显示逻辑
- [ ] 启用增强型翻译器

### 测试
- [ ] 单元测试 - 暂停/恢复
- [ ] 单元测试 - 状态持久化
- [ ] 单元测试 - 断点续传
- [ ] 集成测试 - 完整流程
- [ ] GUI测试 - 按钮功能
- [ ] GUI测试 - 进度显示
- [ ] GUI测试 - 预览功能

### 文档
- [ ] 更新README
- [ ] 更新API文档
- [ ] 创建使用指南
- [ ] 更新CHANGELOG

### 清理
- [ ] 标记旧代码为废弃
- [ ] 更新所有调用点
- [ ] 删除旧代码
- [ ] 运行完整测试套件

---

## 🎯 快速开始指南

### 启用增强型翻译器

```python
# 1. 初始化Facade
facade = TranslationServiceFacade(terminology_service, translation_service)

# 2. 启用增强型翻译器
facade.enable_enhanced_translator(True)

# 3. 设置回调
facade.set_progress_callback_enhanced(on_progress)
facade.set_preview_callback(on_preview)

# 4. 执行翻译（自动使用增强型翻译器）
result = await facade.translate_file(
    source_excel_path="input.xlsx",
    target_langs=["英语", "日语"],
    output_excel_path="output.xlsx"
)

# 5. 暂停/恢复
facade.pause_translation()  # 暂停
facade.resume_translation()  # 恢复
facade.stop_translation()    # 停止
```

### GUI使用

```python
# 用户操作流程
1. 选择源文件
2. 选择目标语言
3. 点击"开始翻译"
4. 翻译过程中可点击"暂停"暂停
5. 点击"恢复"继续翻译
6. 查看预览面板了解翻译质量
```

---

## ⚠️ 注意事项

### 兼容性
- 新旧翻译器可共存
- 默认使用旧翻译器（向后兼容）
- 需显式启用增强型翻译器

### 性能
- 增强型翻译器有轻微性能开销（状态保存）
- 建议批量翻译>100行时使用

### 状态文件
- 状态文件存储在 `.translation_state/` 目录
- 完成后自动清理（保留7天）
- 可手动调用 `cleanup_old_states()` 清理

---

## 📝 后续计划

### v3.1 (2周后)
- [ ] 完成GUI适配
- [ ] 添加完整测试
- [ ] 修复发现的Bug

### v3.2 (1个月后)
- [ ] 标记旧代码为废弃
- [ ] 更新所有文档
- [ ] 用户反馈收集

### v4.0 (2个月后)
- [ ] 删除旧代码
- [ ] 增强型翻译器成为默认
- [ ] 发布正式版

---

**文档版本**: v1.0  
**最后更新**: 2026-04-03  
**下次更新**: 完成GUI适配后
