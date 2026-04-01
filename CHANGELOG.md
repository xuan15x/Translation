# 📋 更新日志

所有重要的项目变更都将记录在此文件中。

---

## [3.0.0] - 2026-04-01

### ✨ 新增功能

#### 1. 双阶段翻译参数 GUI 控制 ⭐ NEW
- **完整的参数控制面板**
  - 📝 初译参数页签：模型、温度、Top P、超时、Max Tokens
  - ✏️ 校对参数页签：独立配置校对阶段参数
  - 🔄 一键重置为默认值
  - 💾 配置自动加载和保存

- **灵活的模型选择**
  - 空值 = 使用全局模型
  - 支持初译和校对使用不同模型
  - 支持混合模型配置（如：初译 deepseek-chat，校对 gpt-4）

- **可视化控制**
  - Notebook 分页设计，清晰分离
  - Spinbox 精确控制数值参数
  - 实时生效，无需重启

#### 2. 语言配置扩展 ⭐ NEW
- **目标语言扩展**：从 12 种扩展到 33 种
  - T1 核心市场（9 种）：英语、德语、法语、日语、韩语、瑞典语、挪威语、丹麦语、芬兰语
  - T2 潜力市场（11 种）：意大利语、西班牙语、葡萄牙语、泰语、越南语、印尼语、马来语、俄语、波兰语、土耳其语、阿拉伯语
  - T3 新兴市场（13 种）：印地语、乌尔都语、孟加拉语、菲律宾语、缅甸语、柬埔寨语、老挝语、波斯语、希伯来语、斯瓦希里语、豪萨语、哈萨克语、乌兹别克语

- **源语言扩展**：从 6 种扩展到 10 种
  - 中文、英语、日语、韩语、法语、德语、西班牙语、意大利语、葡萄牙语、俄语

#### 3. 翻译方向可配置化 ⭐ NEW
- **enabled_translation_types 配置项**
  - 支持在配置文件中启用特定翻译方向
  - 未启用的方向不会在 GUI 中显示
  - 支持 13 种预设方向 + 自定义

#### 4. 错误处理手册 ⭐ NEW
- **完整的错误处理文档**（776 行）
  - 8 大错误分类
  - 25 个常见错误处理指南
  - 30+ 个代码示例
  - 详细的问题定位和修复方法

---

### 🐛 Bug 修复

#### 1. Provider 名称格式错误
- **问题**：`'APIProvider.DEEPSEEK' is not a valid APIProvider`
- **原因**：provider_name 格式不正确
- **修复**：添加字符串解析逻辑，支持 `'APIProvider.DEEPSEEK'` → `'deepseek'` 转换

#### 2. 初始化顺序错误
- **问题**：`AttributeError: 'TranslationApp' object has no attribute 'draft_model_combo'`
- **原因**：`_update_model_list()` 在双阶段控件创建前调用
- **修复**：调整初始化顺序，在双阶段控件创建后调用

#### 3. 日志粒度选择缺失
- **问题**：GUI 中看不到日志粒度选择器
- **原因**：log_controller 未初始化就创建控制面板
- **修复**：修正初始化顺序，先初始化 log_controller

#### 4. GUI 右侧空白
- **问题**：双阶段参数控件太窄（width=25/28）
- **修复**：所有控件宽度增加到 30，充分利用空间

---

### 🔧 技术优化

#### 1. GUI 布局优化
- 双阶段参数控件宽度：25/28 → 30
- 语言区 5 列布局，独立滚动
- 主界面支持鼠标滚轮滚动

#### 2. 初始化顺序优化
```python
# 正确的顺序
1. 初始化 log_controller
2. 创建日志控制面板
3. 初始化模型列表（需要双阶段控件）
```

#### 3. 配置管理增强
- 双阶段参数配置化
- 语言列表可配置
- 翻译方向可配置
- 性能监控开关可配置

---

### 📝 文档更新

#### 新增文档
- `docs/DOCUMENTATION_UPDATE_SUMMARY.md` - 文档更新总结
- `docs/guides/ERROR_HANDLING_MANUAL.md` - 错误处理手册（776 行）

#### 更新文档
- `README.md` - 更新核心特性和使用指南
- `config/config.example.json` - 更新配置示例和注释

---

### 📊 代码统计

#### 新增代码
- `presentation/gui_app.py`: +146 行（双阶段参数 GUI）
- `config/config.example.json`: +45 行（语言扩展和配置）
- `docs/guides/ERROR_HANDLING_MANUAL.md`: +776 行（错误手册）
- **总计**: +967 行

#### 删除代码
- `presentation/gui_app.py`: -6 行（初始化顺序调整）
- `config/config.example.json`: -8 行（旧配置清理）
- **总计**: -14 行

---

### 🎯 使用示例

#### 质量优先配置
```json
{
  "draft_model_name": "deepseek-chat",
  "draft_temperature": 0.3,
  "review_model_name": "gpt-4",
  "review_temperature": 0.7
}
```

#### 经济模式配置
```json
{
  "draft_model_name": null,  // 使用全局模型
  "draft_temperature": 0.3,
  "review_model_name": null,  // 使用全局模型
  "review_temperature": 0.5
}
```

#### 创意文学翻译配置
```json
{
  "draft_model_name": "claude-3",
  "draft_temperature": 0.8,
  "draft_top_p": 0.95,
  "review_model_name": "claude-3",
  "review_temperature": 0.9,
  "review_top_p": 0.98
}
```

---

### 🔗 相关链接

- [架构设计文档](docs/architecture/ARCHITECTURE.md)
- [快速入门指南](docs/guides/QUICKSTART.md)
- [错误处理手册](docs/guides/ERROR_HANDLING_MANUAL.md)
- [最佳实践](docs/guides/BEST_PRACTICES.md)

---

## [2.5.0] - 2026-03-28

### 新增功能
- 性能监控系统
- 日志粒度控制（5 级）
- 撤销/重做功能

### Bug 修复
- 修复缓存命中率计算错误
- 修复日志切片显示异常

---

## [2.0.0] - 2026-03-20

### 重大更新
- 六层架构重构
- 依赖注入容器实现
- 外观模式简化调用

---

## [1.0.0] - 2026-03-01

### 初始版本
- 基础翻译功能
- 术语库管理
- GUI 界面

---

## 版本说明

### 版本号规则
- **主版本号**：重大架构变更
- **次版本号**：新功能添加
- **修订号**：Bug 修复和优化

### 符号说明
- ⭐ NEW: 全新功能
- ✨ IMPROVED: 改进功能
- 🐛 FIXED: Bug 修复
- 🔧 OPTIMIZED: 性能优化
- 📝 UPDATED: 文档更新

---

**更新日期**: 2026-04-01  
**维护者**: Translation Team  
**许可证**: MIT
