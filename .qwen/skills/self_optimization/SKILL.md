# 子智能体自我优化 Skill

**版本**: 1.0.0  
**创建日期**: 2026-04-03  
**适用范围**: 所有子智能体（agents）  
**触发时机**: 每个任务完成后自动执行

---

## 📋 概述

自我优化 Skill 是一个强制性的任务后反思机制。每个子智能体在完成 assigned 任务后，必须自动执行结构化的自我反思，记录经验教训，以便持续改进。

---

## 🎯 核心原则

### 1. 自动化
- 无需用户手动触发
- 任务完成后立即执行
- 无论成功或失败都要反思

### 2. 结构化
- 使用统一的反思模板
- 覆盖所有关键维度
- 量化评估质量

### 3. 可追溯
- 每次反思独立保存
- 时间戳和任务ID标记
- 支持后续回顾分析

### 4. 实用性
- 提取可复用的经验
- 识别需改进的领域
- 制定具体的行动计划

---

## 📝 反思模板

每个任务完成后，子智能体必须填写以下反思报告：

```markdown
# 任务反思报告 #{task_id}

## 📊 基本信息
- **任务ID**: {task_id}
- **任务描述**: {task_description}
- **智能体类型**: {agent_type}
- **开始时间**: {start_time}
- **完成时间**: {end_time}
- **执行时长**: {duration}
- **执行结果**: ✅成功 / ⚠️部分成功 / ❌失败

---

## 1️⃣ 目标达成情况

### 预期目标
{描述任务原本的目标}

### 实际结果
{描述实际达成的结果}

### 达成率评估
- **完成度**: {百分比或定性描述}
- **质量评分**: {1-10分}
- **差距分析**: {如果有差距，详细说明原因}

---

## 2️⃣ 执行过程评估

### ✅ 做得好的地方
1. {具体描述}
2. {具体描述}
3. {具体描述}

### ⚠️ 做得不足的地方
1. {具体描述}
2. {具体描述}
3. {具体描述}

### 💡 意外发现
{执行过程中的意外收获或发现}

---

## 3️⃣ 技术评估

### 使用的方法/工具
- {方法1}: {效果评价}
- {方法2}: {效果评价}

### 方法有效性
{评估所采用方法的有效性}

### 更好的替代方案
{是否有更好的方法，如果有，是什么}

### 性能指标（如适用）
- 处理速度: {量化指标}
- 资源消耗: {量化指标}
- 代码质量: {量化指标}

---

## 4️⃣ 遇到的问题

### 问题清单
1. **问题**: {描述}
   **影响**: {影响程度}
   **解决**: {如何解决}

2. **问题**: {描述}
   **影响**: {影响程度}
   **解决**: {如何解决}

### 未解决的问题
{仍未解决的问题，如有}

---

## 5️⃣ 经验教训

### 关键学习点
1. {学习点1}
2. {学习点2}
3. {学习点3}

### 可复用的经验
{下次可以直接复用的经验}

### 需要改进的领域
{下次需要改进的地方}

---

## 6️⃣ 量化评分

| 评估维度 | 评分 (1-10) | 评分理由 |
|---------|-------------|---------|
| 目标达成 | {分数} | {理由} |
| 执行效率 | {分数} | {理由} |
| 代码质量 | {分数} | {理由} |
| 文档完整 | {分数} | {理由} |
| 用户满意 | {分数} | {理由} |
| **综合评分** | **{平均分}** | - |

---

## 7️⃣ 关键洞察

> {用1-3句话总结这次任务最重要的洞察}

---

## 8️⃣ 改进承诺

基于本次反思，我承诺在未来的任务中：

1. {具体改进承诺1}
2. {具体改进承诺2}
3. {具体改进承诺3}

---

## 9️⃣ 后续行动

### 立即执行（下次任务就做）
- [ ] {行动1}
- [ ] {行动2}

### 短期计划（1-2周内）
- [ ] {行动1}
- [ ] {行动2}

### 长期改进（持续进行）
- [ ] {行动1}
- [ ] {行动2}

---

**反思完成时间**: {timestamp}  
**下次审查日期**: {30天后日期}
```

---

## 🔧 实现机制

### 自动触发器

在每个子智能体的任务执行流程末尾，必须包含：

```python
# 任务完成后的自动反思流程
def _execute_post_task_reflection(self, task_result):
    """执行任务后反思"""
    from skills.self_optimization import SelfReflectionSkill
    
    # 自动生成反思
    reflection = SelfReflectionSkill.generate_reflection(
        task_id=self.task_id,
        task_description=self.task_description,
        agent_type=self.agent_type,
        execution_result=task_result,
        start_time=self.start_time,
        end_time=datetime.now()
    )
    
    # 保存反思报告
    filepath = SelfReflectionSkill.save_reflection(
        reflection=reflection,
        task_id=self.task_id
    )
    
    # 输出提示
    print(f"\n📝 任务反思已完成")
    print(f"💾 反思报告: {filepath}")
    
    return reflection
```

### Skill 基础设施

```python
# skills/self_optimization/__init__.py
from .reflector import SelfReflectionSkill

__all__ = ['SelfReflectionSkill']
```

```python
# skills/self_optimization/reflector.py
"""
自我反思 Skill - 核心实现
自动在任务完成后生成结构化反思报告
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional


class SelfReflectionSkill:
    """自我反思技能"""
    
    REFLECTION_DIR = Path(".agent_reflections")
    
    @classmethod
    def generate_reflection(
        cls,
        task_id: str,
        task_description: str,
        agent_type: str,
        execution_result: Dict[str, Any],
        start_time: datetime,
        end_time: datetime
    ) -> str:
        """生成反思报告"""
        duration = end_time - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 计算综合评分
        scores = execution_result.get('scores', {})
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        reflection = f"""# 任务反思报告 #{task_id}

## 📊 基本信息
- **任务ID**: {task_id}
- **任务描述**: {task_description}
- **智能体类型**: {agent_type}
- **开始时间**: {start_time.strftime("%Y-%m-%d %H:%M:%S")}
- **完成时间**: {end_time.strftime("%Y-%m-%d %H:%M:%S")}
- **执行时长**: {duration}
- **执行结果**: {execution_result.get('status', 'unknown')}

---

## 1️⃣ 目标达成情况

### 预期目标
{execution_result.get('expected_goal', '待补充')}

### 实际结果
{execution_result.get('actual_result', '待补充')}

### 达成率评估
- **完成度**: {execution_result.get('achievement_rate', '待评估')}
- **质量评分**: {avg_score:.1f}/10
- **差距分析**: {execution_result.get('gap_analysis', '待补充')}

---

## 2️⃣ 执行过程评估

### ✅ 做得好的地方
{cls._format_list(execution_result.get('strengths', ['待补充']))}

### ⚠️ 做得不足的地方
{cls._format_list(execution_result.get('weaknesses', ['待补充']))}

### 💡 意外发现
{execution_result.get('unexpected_findings', '无')}

---

## 3️⃣ 技术评估

### 使用的方法/工具
{cls._format_list(execution_result.get('methods_used', ['待补充']))}

### 方法有效性
{execution_result.get('method_effectiveness', '待评估')}

### 更好的替代方案
{execution_result.get('alternatives', '待分析')}

---

## 4️⃣ 遇到的问题

### 问题清单
{cls._format_problems(execution_result.get('problems', []))}

### 未解决的问题
{cls._format_list(execution_result.get('unresolved_issues', ['无']))}

---

## 5️⃣ 经验教训

### 关键学习点
{cls._format_list(execution_result.get('key_learnings', ['待总结']))}

### 可复用的经验
{execution_result.get('reusable_experience', '待总结')}

### 需要改进的领域
{execution_result.get('areas_for_improvement', '待识别')}

---

## 6️⃣ 量化评分

{cls._format_scores(scores)}

**综合评分**: {avg_score:.1f}/10

---

## 7️⃣ 关键洞察

> {execution_result.get('key_insight', '待补充')}

---

## 8️⃣ 改进承诺

基于本次反思，我承诺在未来的任务中：

{cls._format_list(execution_result.get('commitments', ['持续改进']))}

---

## 9️⃣ 后续行动

### 立即执行（下次任务就做）
{cls._format_checklist(execution_result.get('immediate_actions', []))}

### 短期计划（1-2周内）
{cls._format_checklist(execution_result.get('short_term_plans', []))}

### 长期改进（持续进行）
{cls._format_checklist(execution_result.get('long_term_improvements', []))}

---

**反思完成时间**: {timestamp}
**下次审查日期**: {(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")}
"""
        return reflection
    
    @classmethod
    def save_reflection(cls, reflection: str, task_id: str) -> str:
        """保存反思报告"""
        cls.REFLECTION_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reflection_{task_id}_{timestamp}.md"
        filepath = cls.REFLECTION_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(reflection)
        
        return str(filepath)
    
    @classmethod
    def _format_list(cls, items: list) -> str:
        """格式化列表"""
        if not items:
            return "无"
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
    
    @classmethod
    def _format_checklist(cls, items: list) -> str:
        """格式化检查清单"""
        if not items:
            return "无"
        return "\n".join([f"- [ ] {item}" for item in items])
    
    @classmethod
    def _format_problems(cls, problems: list) -> str:
        """格式化问题清单"""
        if not problems:
            return "无"
        
        formatted = []
        for i, problem in enumerate(problems):
            if isinstance(problem, dict):
                formatted.append(f"{i+1}. **问题**: {problem.get('problem', 'N/A')}")
                formatted.append(f"   **影响**: {problem.get('impact', 'N/A')}")
                formatted.append(f"   **解决**: {problem.get('solution', 'N/A')}")
            else:
                formatted.append(f"{i+1}. {problem}")
        
        return "\n".join(formatted)
    
    @classmethod
    def _format_scores(cls, scores: dict) -> str:
        """格式化评分表"""
        if not scores:
            return "暂无评分"
        
        lines = ["| 评估维度 | 评分 (1-10) | 评分理由 |",
                 "|---------|-------------|---------|"]
        
        for dim, score in scores.items():
            reason = f"{dim}_reasoning"
            lines.append(f"| {dim} | {score}/10 | {scores.get(reason, '待补充')} |")
        
        return "\n".join(lines)
```

---

## 📊 使用示例

### 示例1：代码重构任务

```python
# 任务完成后
task_result = {
    'status': '✅成功',
    'expected_goal': '将400行方法拆分为多个子验证器',
    'actual_result': '成功拆分为13个子方法，每个20-40行',
    'achievement_rate': '100%',
    'gap_analysis': '无差距，完全达成目标',
    'strengths': [
        '拆分逻辑清晰，每个子方法职责单一',
        '保持了向后兼容性',
        '添加了完整的文档字符串'
    ],
    'weaknesses': [
        '拆分过程耗时较长（约45分钟）',
        '部分边界情况处理可以更优雅'
    ],
    'unexpected_findings': '发现并修复了2个隐藏的Bug',
    'methods_used': ['提取方法重构模式', '依赖注入'],
    'method_effectiveness': '非常有效，代码可读性大幅提升',
    'alternatives': '可以使用策略模式，但会增加复杂度',
    'problems': [
        {
            'problem': '某些验证逻辑有交叉依赖',
            'impact': '中等',
            'solution': '重新组织验证顺序，消除交叉依赖'
        }
    ],
    'key_learnings': [
        '重构前先画依赖关系图很重要',
        '小步重构比大步重构更安全'
    ],
    'reusable_experience': '验证器拆分模式可复用到其他验证场景',
    'areas_for_improvement': '重构前应该先写单元测试',
    'scores': {
        '目标达成': 10,
        '执行效率': 7,
        '代码质量': 9,
        '文档完整': 9,
        '用户满意': 9
    },
    'key_insight': '重构大型方法时，先识别依赖关系，再制定拆分策略，最后逐步执行，这样既安全又高效。',
    'commitments': [
        '在未来的重构任务中，先写单元测试再进行重构',
        '确保重构过程中不会引入Bug'
    ],
    'immediate_actions': [
        '为新的子验证器添加单元测试'
    ],
    'short_term_plans': [
        '应用相同模式重构其他大方法'
    ],
    'long_term_improvements': [
        '建立项目重构指南文档'
    ]
}

# 自动生成反思
reflection = SelfReflectionSkill.generate_reflection(
    task_id="refactor_001",
    task_description="重构Config._validate_config方法",
    agent_type="code-architecture-manager",
    execution_result=task_result,
    start_time=datetime(2026, 4, 3, 14, 30),
    end_time=datetime(2026, 4, 3, 15, 15)
)

# 保存反思
filepath = SelfReflectionSkill.save_reflection(reflection, "refactor_001")
```

---

## 📈 质量评估

### 反思质量指标

| 指标 | 权重 | 评估标准 |
|------|------|---------|
| 完整性 | 30% | 是否填写所有必填字段 |
| 深度 | 25% | 分析的深入程度 |
| 具体性 | 20% | 是否具体而非泛泛而谈 |
| 可操作性 | 15% | 是否有明确的后续行动 |
| 诚实度 | 10% | 是否诚实面对不足 |

### 质量等级

- **优秀 (9-10)**: 深刻、全面、有洞察力
- **良好 (7-8)**: 较完整，有少量不足
- **合格 (5-6)**: 基本完整，但缺乏深度
- **待改进 (<5)**: 不完整或流于形式

---

## 🔄 定期回顾

### 月度回顾流程

```python
def monthly_reflection_review():
    """月度反思回顾"""
    from skills.self_optimization import SelfReflectionSkill
    
    # 加载本月所有反思
    reflections = SelfReflectionSkill.load_reflections(days=30)
    
    # 分析趋势
    trends = analyze_trends(reflections)
    
    # 提取最佳实践
    best_practices = extract_best_practices(reflections)
    
    # 识别共性问题
    common_issues = identify_common_issues(reflections)
    
    # 生成改进建议
    recommendations = generate_recommendations(trends, best_practices, common_issues)
    
    return {
        'trends': trends,
        'best_practices': best_practices,
        'common_issues': common_issues,
        'recommendations': recommendations
    }
```

---

## ⚠️ 注意事项

### 好的反思 ✅
- 具体、详细、诚实
- 承认不足和错误
- 提出具体改进行动
- 有量化评估

### 差的反思 ❌
- 泛泛而谈、空洞无物
- 只说优点，回避缺点
- 没有具体行动
- 流于形式，缺乏深度

---

**Skill版本**: 1.0.0  
**生效日期**: 2026-04-03  
**适用范围**: 所有子智能体  
**下次审查**: 2026-05-03
