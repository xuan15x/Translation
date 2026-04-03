"""
自我反思 Skill - 核心实现
自动在任务完成后生成结构化反思报告

Usage:
    from skills.self_optimization.reflector import SelfReflectionSkill
    
    # 任务完成后自动反思
    result = SelfReflectionSkill.auto_reflect(
        task_id="task_001",
        task_description="重构Config验证方法",
        agent_type="code-architecture-manager",
        execution_result={...}
    )
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List


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
        """
        生成反思报告
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            agent_type: 智能体类型
            execution_result: 执行结果
            start_time: 开始时间
            end_time: 完成时间
            
        Returns:
            反思报告Markdown文本
        """
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
        """
        保存反思报告到文件
        
        Args:
            reflection: 反思报告文本
            task_id: 任务ID
            
        Returns:
            保存的文件路径
        """
        cls.REFLECTION_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reflection_{task_id}_{timestamp}.md"
        filepath = cls.REFLECTION_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(reflection)
        
        print(f"\n📝 任务反思已完成")
        print(f"💾 反思报告: {filepath}")
        
        return str(filepath)
    
    @classmethod
    def auto_reflect(
        cls,
        task_id: str,
        task_description: str,
        agent_type: str,
        execution_result: Dict[str, Any],
        start_time: Optional[datetime] = None
    ) -> str:
        """
        自动反思（从任务结果自动生成）
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            agent_type: 智能体类型
            execution_result: 执行结果
            start_time: 开始时间（可选）
            
        Returns:
            保存的文件路径
        """
        if start_time is None:
            start_time = datetime.now()
        
        end_time = datetime.now()
        
        reflection = cls.generate_reflection(
            task_id=task_id,
            task_description=task_description,
            agent_type=agent_type,
            execution_result=execution_result,
            start_time=start_time,
            end_time=end_time
        )
        
        filepath = cls.save_reflection(reflection, task_id)
        
        return filepath
    
    @classmethod
    def load_reflections(cls, days: int = 30) -> List[Dict[str, Any]]:
        """
        加载近期的反思报告
        
        Args:
            days: 加载天数
            
        Returns:
            反思报告列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        reflections = []
        
        if not cls.REFLECTION_DIR.exists():
            return reflections
        
        for filepath in cls.REFLECTION_DIR.glob("reflection_*.md"):
            if filepath.stat().st_mtime >= cutoff_date.timestamp():
                with open(filepath, 'r', encoding='utf-8') as f:
                    reflections.append({
                        'file': str(filepath),
                        'content': f.read(),
                        'date': datetime.fromtimestamp(filepath.stat().st_mtime),
                        'task_id': filepath.stem
                    })
        
        return sorted(reflections, key=lambda x: x['date'], reverse=True)
    
    @classmethod
    def review_reflections(cls, days: int = 30) -> str:
        """
        回顾反思报告，提取经验教训
        
        Args:
            days: 回顾天数
            
        Returns:
            回顾报告路径
        """
        reflections = cls.load_reflections(days)
        
        if not reflections:
            print("📭 没有找到近期的反思报告")
            return ""
        
        # 生成总结
        summary = cls._generate_summary(reflections, days)
        
        # 保存总结
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = cls.REFLECTION_DIR / f"review_summary_{timestamp}.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"📊 反思总结报告已保存: {summary_file}")
        return str(summary_file)
    
    # ========== 私有方法 ==========
    
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
            if dim.endswith('_reasoning'):
                continue
            reason = f"{dim}_reasoning"
            lines.append(f"| {dim} | {score}/10 | {scores.get(reason, '待补充')} |")
        
        return "\n".join(lines)
    
    @classmethod
    def _generate_summary(cls, reflections: List[Dict], days: int) -> str:
        """生成反思总结"""
        total = len(reflections)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"""# 反思总结报告

**分析期间**: 过去{days}天
**反思报告数量**: {total}
**报告生成时间**: {timestamp}

---

## 总体趋势

- 共完成 {total} 个任务
- 任务类型分布: 待分析
- 平均评分: 待计算

## 常见问题

{total} 个任务中发现的共性问题：
1. 待从反思中提取...

## 成功经验

{total} 个任务中的成功经验：
1. 待从反思中提取...

## 改进建议

基于反思分析的改进建议：
1. 待基于反思提出...

---

**报告生成时间**: {timestamp}
"""
        return summary
