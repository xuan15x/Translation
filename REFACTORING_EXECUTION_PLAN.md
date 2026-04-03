# 项目重构执行计划

**日期**: 2026-04-03
**目标**: 优化架构、降低耦合、精简代码、删除冗余

---

## 📋 重构任务清单

### P0级 - 立即修复（架构违规）

#### 1. 修复Domain层依赖Service层
- **文件**: `domain/translation_service_impl.py`
- **问题**: 导入了 `service.api_stages`
- **方案**: 通过依赖注入传入API调用接口

#### 2. 移动仓储接口到Domain层
- **文件**: `infrastructure/repositories.py`
- **问题**: 接口定义在Infrastructure层
- **方案**: 移动到 `domain/repositories.py`

### P1级 - 模块重组

#### 3. Infrastructure层瘦身
- **当前**: 26个文件，职责混乱
- **目标**: 拆分为清晰的子模块
- **方案**:
  - 缓存相关 → `infrastructure/cache/`
  - 日志相关 → `infrastructure/logging/`
  - 数据库相关 → `infrastructure/database/`
  - 工具类 → `infrastructure/utils/`

#### 4. 合并模型文件
- **问题**: `domain/models.py` 和 `infrastructure/models.py` 共存
- **方案**: 合并到 `domain/models.py`

#### 5. Config模块整合
- **当前**: 7个文件游离于六层架构外
- **方案**: 移动到 `infrastructure/config/`

### P2级 - 代码精简

#### 6. 删除冗余文件
- 未使用的测试脚本
- 重复的工具文件
- 过时的备份文件
- 临时文件

#### 7. 消除代码重复
- 提取公共函数
- 合并相似功能
- 删除重复实现

#### 8. 大文件拆分
- `gui_app.py` (1800+行)
- `models.py` (800+行)
- `config.py` (700+行)

---

## 🎯 执行顺序

1. **阶段一** (30分钟): P0级修复
2. **阶段二** (1小时): 删除冗余文件
3. **阶段三** (1.5小时): 代码精简和去重
4. **阶段四** (1小时): 模块重组
5. **阶段五** (30分钟): 文档更新
6. **阶段六** (30分钟): 测试验证
7. **阶段七** (30分钟): Git提交推送

**总计**: 约5.5小时

---

## ✅ 验收标准

- [ ] 所有P0级问题修复
- [ ] 代码量减少20%+
- [ ] 模块耦合度降低
- [ ] 所有测试通过
- [ ] 文档更新完整
- [ ] 代码审查通过
