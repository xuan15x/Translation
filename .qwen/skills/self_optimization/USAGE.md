# 自我优化 Skill 使用指南

**版本**: 1.0.0  
**最后更新**: 2026-04-03

---

## 📋 概述

自我优化 Skill 为所有子智能体提供自动反思功能。每个任务完成后，智能体会自动填写结构化的反思报告，记录经验教训，持续改进。

---

## 🚀 快速开始

### 1. 基本使用

```python
from datetime import datetime
from skills.self_optimization import SelfReflectionSkill

# 任务完成后，自动记录反思
result = {
    'status': '✅成功',
    'expected_goal': '重构验证方法',
    'actual_result': '成功拆分为13个子方法',
    'achievement_rate': '100%',
    'strengths': ['逻辑清晰', '职责单一'],
    'weaknesses': ['耗时较长'],
    'key_learnings': ['先画依赖图很重要'],
    'scores': {
        '目标达成': 10,
        '执行效率': 7,
        '代码质量': 9
    }
}

SelfReflectionSkill.auto_reflect(
    task_id="refactor_001",
    task_description="重构Config验证方法",
    agent_type="code-architecture-manager",
    execution_result=result,
    start_time=datetime(2026, 4, 3, 14, 30)
)
```

### 2. 查看反思报告

```bash
# 查看所有反思报告
ls .agent_reflections/

# 查看最新反思
cat .agent_reflections/reflection_*.md | tail -50
```

### 3. 月度回顾

```python
from skills.self_optimization import SelfReflectionSkill

# 回顾过去30天的反思
summary_file = SelfReflectionSkill.review_reflections(days=30)
print(f"总结报告: {summary_file}")
```

---

## 📝 反思模板说明

每个反思报告包含9个部分：

1. **基本信息** - 任务ID、描述、时间、结果
2. **目标达成** - 预期vs实际，达成率
3. **执行评估** - 优点、不足、意外发现
4. **技术评估** - 方法、效果、替代方案
5. **问题清单** - 遇到的问题及解决
6. **经验教训** - 学习点、可复用经验
7. **量化评分** - 5个维度评分
8. **关键洞察** - 1-3句总结
9. **改进承诺** - 具体行动计划

---

## 🎯 最佳实践

### 填写反思

#### ✅ 好的反思
- **具体**: "重构耗时45分钟，比预期长"
- **诚实**: "边界情况处理不够优雅"
- **可操作**: "下次先写单元测试再重构"
- **量化**: "质量评分9/10，效率7/10"

#### ❌ 差的反思
- **模糊**: "做得还可以"
- **逃避**: "没什么不足"
- **空泛**: "需要改进"
- **无评分**: 所有字段"待补充"

### 回顾反思

**每周**:
- 查看本周反思
- 识别常见问题
- 提取成功经验

**每月**:
- 运行月度回顾
- 生成总结报告
- 制定改进计划

---

## 📊 使用场景

### 场景1: 代码重构任务

```python
result = {
    'status': '✅成功',
    'expected_goal': '将400行方法拆分',
    'actual_result': '拆分为13个子方法',
    'achievement_rate': '100%',
    'strengths': [
        '逻辑清晰',
        '职责单一',
        '文档完善'
    ],
    'weaknesses': [
        '耗时较长(45分钟)',
        '边界处理可优化'
    ],
    'unexpected_findings': '发现2个隐藏Bug',
    'key_learnings': [
        '先画依赖图很重要',
        '小步重构更安全'
    ],
    'scores': {
        '目标达成': 10,
        '执行效率': 7,
        '代码质量': 9,
        '文档完整': 9,
        '用户满意': 9
    },
    'key_insight': '先识别依赖，再制定策略，逐步执行。',
    'commitments': [
        '先写单元测试再重构'
    ]
}

SelfReflectionSkill.auto_reflect(
    task_id="refactor_001",
    task_description="重构验证方法",
    agent_type="code-architecture-manager",
    execution_result=result
)
```

### 场景2: Bug修复任务

```python
result = {
    'status': '✅成功',
    'expected_goal': '修复导入错误',
    'actual_result': '修复并添加测试',
    'achievement_rate': '100%',
    'strengths': ['快速定位问题'],
    'weaknesses': ['未及时发现'],
    'key_learnings': ['添加导入测试'],
    'scores': {
        '目标达成': 10,
        '执行效率': 9,
        '代码质量': 8
    }
}

SelfReflectionSkill.auto_reflect(
    task_id="bugfix_001",
    task_description="修复导入错误",
    agent_type="code-reviewer",
    execution_result=result
)
```

### 场景3: 新功能开发

```python
result = {
    'status': '✅成功',
    'expected_goal': '实现配置向导',
    'actual_result': '7步图形化向导',
    'achievement_rate': '100%',
    'strengths': ['用户体验好'],
    'weaknesses': ['代码量大(600行)'],
    'key_learnings': ['分步实现测试'],
    'scores': {
        '目标达成': 10,
        '执行效率': 8,
        '代码质量': 9
    }
}

SelfReflectionSkill.auto_reflect(
    task_id="feature_001",
    task_description="实现配置向导",
    agent_type="python-feature-developer",
    execution_result=result
)
```

---

## 🔧 高级功能

### 自定义反思模板

```python
from skills.self_optimization.reflector import SelfReflectionSkill

# 生成自定义反思
reflection = SelfReflectionSkill.generate_reflection(
    task_id="custom_001",
    task_description="自定义任务",
    agent_type="general",
    execution_result={
        'strengths': ['自定义优点'],
        'weaknesses': ['自定义不足'],
        'scores': {'质量': 9}
    },
    start_time=datetime.now(),
    end_time=datetime.now()
)

# 保存
filepath = SelfReflectionSkill.save_reflection(reflection, "custom_001")
```

### 批量回顾分析

```python
from skills.self_optimization import SelfReflectionSkill

# 加载所有反思
reflections = SelfReflectionSkill.load_reflections(days=90)

# 分析趋势
for r in reflections:
    print(f"任务: {r['task_id']}")
    print(f"日期: {r['date']}")
    # 提取评分、经验等
```

---

## 📁 文件组织

```
.qwen/skills/self_optimization/
├── __init__.py              # 包初始化
├── reflector.py             # 核心实现
└── SKILL.md                 # Skill文档

.agent_reflections/           # 反思存储
├── reflection_task1_20260403_143022.md
├── reflection_task2_20260403_150145.md
└── review_summary_20260503.md
```

---

## ⚠️ 注意事项

### 反思质量

**高质量反思的特征**:
- ✅ 填写所有必填字段
- ✅ 具体而非泛泛而谈
- ✅ 诚实面对不足
- ✅ 提出具体改进行动
- ✅ 有量化评分

**低质量反思的特征**:
- ❌ 大量"待补充"
- ❌ 只说优点
- ❌ 没有具体行动
- ❌ 评分全部10分

### 隐私和安全

- 反思报告仅用于改进
- 不包含敏感信息（API密钥等）
- 定期清理旧报告（建议保留90天）

---

## 📞 故障排查

### 问题1: 反思未生成

**症状**: 任务完成后没有反思文件

**解决**:
```python
# 检查导入
from skills.self_optimization import SelfReflectionSkill

# 手动生成
result = {...}
SelfReflectionSkill.auto_reflect(
    task_id="test",
    task_description="测试",
    agent_type="test",
    execution_result=result
)
```

### 问题2: 反思质量低

**症状**: 大量字段为"待补充"

**解决**:
- 填写execution_result时提供完整信息
- 至少包含: strengths, weaknesses, key_learnings, scores

### 问题3: 回顾报告为空

**症状**: review_reflections返回空

**解决**:
```python
# 检查是否有反思文件
import os
print(os.path.exists('.agent_reflections'))

# 查看反思文件数量
from pathlib import Path
files = list(Path('.agent_reflections').glob('reflection_*.md'))
print(f"反思文件数: {len(files)}")
```

---

## 🎓 学习资源

- **Skill文档**: `.qwen/skills/self_optimization/SKILL.md`
- **实现代码**: `.qwen/skills/self_optimization/reflector.py`
- **示例反思**: `.agent_reflections/` 目录

---

**文档版本**: 1.0.0  
**创建日期**: 2026-04-03  
**下次更新**: 功能增强时
