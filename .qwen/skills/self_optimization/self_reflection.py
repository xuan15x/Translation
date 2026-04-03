"""
自我反思技能 - 基础设施
提供自动反思生成、保存和回顾功能
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class SelfReflectionSkill:
    """自我反思技能"""
    
    REFLECTION_DIR = Path(".agent_reflections")
    TEMPLATE_FILE = Path(__file__).parent / "reflection_template.md"
    
    @classmethod
    def generate_reflection(
        cls,
        task_id: str,
        task_description: str,
        execution_result: Dict[str, Any],
        agent_type: str = "general"
    ) -> str:
        """
        生成反思报告
        
        Args:
            task_id: 任务ID
            task_description: 任务描述
            execution_result: 执行结果
            agent_type: 智能体类型
            
        Returns:
            反思报告Markdown文本
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_status = execution_result.get('status', 'unknown')
        
        reflection = f"""# 任务反思报告

## 基本信息
- **任务ID**: {task_id}
- **任务描述**: {task_description}
- **执行时间**: {timestamp}
- **执行结果**: {result_status}
- **智能体类型**: {agent_type}

## 任务分析

### 1. 目标达成情况
- **预期目标**: {execution_result.get('expected_goal', 'N/A')}
- **实际结果**: {execution_result.get('actual_result', 'N/A')}
- **达成率**: {execution_result.get('achievement_rate', 'N/A')}
- **差距分析**: {execution_result.get('gap_analysis', 'N/A')}

### 2. 执行过程评估
- **优点**: 
{cls._format_list(execution_result.get('strengths', []))}
- **不足**: 
{cls._format_list(execution_result.get('weaknesses', []))}
- **意外发现**: 
{cls._format_list(execution_result.get('unexpected_findings', []))}

### 3. 技术评估
- **使用的方法**: {execution_result.get('methods_used', 'N/A')}
- **方法有效性**: {execution_result.get('method_effectiveness', 'N/A')}
- **替代方案**: {execution_result.get('alternatives', 'N/A')}
- **性能指标**: {execution_result.get('performance_metrics', 'N/A')}

### 4. 错误和问题
- **遇到的问题**: 
{cls._format_list(execution_result.get('problems', []))}
- **解决方案**: 
{cls._format_list(execution_result.get('solutions', []))}
- **未解决问题**: 
{cls._format_list(execution_result.get('unresolved_issues', []))}

### 5. 经验教训
- **关键学习点**: 
{cls._format_list(execution_result.get('key_learnings', []))}
- **可复用经验**: 
{cls._format_list(execution_result.get('reusable_experience', []))}
- **需要改进**: 
{cls._format_list(execution_result.get('areas_for_improvement', []))}

### 6. 优化建议
- **流程优化**: 
{cls._format_list(execution_result.get('process_optimizations', []))}
- **工具优化**: 
{cls._format_list(execution_result.get('tool_optimizations', []))}
- **技能提升**: 
{cls._format_list(execution_result.get('skill_improvements', []))}

### 7. 后续行动
- **立即执行**: 
{cls._format_list(execution_result.get('immediate_actions', []))}
- **短期计划**: 
{cls._format_list(execution_result.get('short_term_plans', []))}
- **长期改进**: 
{cls._format_list(execution_result.get('long_term_improvements', []))}

## 量化评分

| 维度 | 评分 (1-10) | 说明 |
|------|-------------|------|
| 目标达成 | {execution_result.get('score_goal_achievement', 'N/A')} | {execution_result.get('score_goal_reasoning', 'N/A')} |
| 执行效率 | {execution_result.get('score_efficiency', 'N/A')} | {execution_result.get('score_efficiency_reasoning', 'N/A')} |
| 代码质量 | {execution_result.get('score_code_quality', 'N/A')} | {execution_result.get('score_code_quality_reasoning', 'N/A')} |
| 文档完整 | {execution_result.get('score_documentation', 'N/A')} | {execution_result.get('score_documentation_reasoning', 'N/A')} |
| 用户满意 | {execution_result.get('score_user_satisfaction', 'N/A')} | {execution_result.get('score_user_satisfaction_reasoning', 'N/A')} |
| **综合** | **{cls._calculate_average(execution_result)}** | - |

## 关键洞察

> {execution_result.get('key_insight', '待补充')}

## 承诺

> {execution_result.get('commitment', '待补充')}

---

**反思完成时间**: {timestamp}
**下次审查日期**: {cls._get_next_review_date()}
"""
        return reflection
    
    @classmethod
    def save_reflection(cls, reflection: str, task_id: str = None) -> str:
        """
        保存反思报告
        
        Args:
            reflection: 反思报告文本
            task_id: 任务ID（可选，用于文件名）
            
        Returns:
            保存的文件路径
        """
        cls.REFLECTION_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reflection_{task_id or timestamp}_{timestamp}.md"
        filepath = cls.REFLECTION_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(reflection)
        
        print(f"💾 反思报告已保存: {filepath}")
        return str(filepath)
    
    @classmethod
    def display_reflection(cls, reflection: str) -> None:
        """
        显示反思报告给用户
        
        Args:
            reflection: 反思报告文本
        """
        print("\n" + "="*70)
        print("📝 任务反思报告")
        print("="*70)
        print(reflection)
        print("="*70)
        print()
    
    @classmethod
    def auto_reflect(cls, task_result: Dict[str, Any]) -> str:
        """
        自动反思（从任务结果自动生成）
        
        Args:
            task_result: 任务结果字典
            
        Returns:
            反思报告路径
        """
        reflection = cls.generate_reflection(
            task_id=task_result.get('task_id', 'auto'),
            task_description=task_result.get('description', '自动任务'),
            execution_result=task_result,
            agent_type=task_result.get('agent_type', 'general')
        )
        
        filepath = cls.save_reflection(reflection, task_result.get('task_id'))
        
        # 可选：显示给用户
        if task_result.get('show_reflection', False):
            cls.display_reflection(reflection)
        
        return filepath
    
    @classmethod
    def review_reflections(
        cls,
        days: int = 30,
        output_file: str = None
    ) -> str:
        """
        回顾反思报告，提取经验教训
        
        Args:
            days: 回顾天数
            output_file: 输出文件路径
            
        Returns:
            回顾报告路径
        """
        import json
        
        reflections = cls._load_recent_reflections(days)
        
        if not reflections:
            print("📭 没有找到近期的反思报告")
            return ""
        
        # 分析反思
        summary = cls._analyze_reflections(reflections)
        
        # 保存总结
        if output_file is None:
            output_file = cls.REFLECTION_DIR / f"reflection_summary_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"📊 反思总结报告已保存: {output_file}")
        return str(output_file)
    
    # ========== 私有方法 ==========
    
    @classmethod
    def _format_list(cls, items: list) -> str:
        """格式化列表为Markdown"""
        if not items:
            return "  - 待补充"
        return "\n".join([f"  - {item}" for item in items])
    
    @classmethod
    def _calculate_average(cls, result: Dict) -> str:
        """计算平均分"""
        scores = []
        for key in ['score_goal_achievement', 'score_efficiency', 'score_code_quality', 
                    'score_documentation', 'score_user_satisfaction']:
            val = result.get(key)
            if val and isinstance(val, (int, float)):
                scores.append(float(val))
        
        if scores:
            return f"{sum(scores) / len(scores):.1f}"
        return "N/A"
    
    @classmethod
    def _get_next_review_date(cls) -> str:
        """获取下次审查日期（1个月后）"""
        from datetime import timedelta
        next_date = datetime.now() + timedelta(days=30)
        return next_date.strftime("%Y-%m-%d")
    
    @classmethod
    def _load_recent_reflections(cls, days: int) -> list:
        """加载近期的反思报告"""
        from datetime import timedelta
        
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
                        'date': datetime.fromtimestamp(filepath.stat().st_mtime)
                    })
        
        return sorted(reflections, key=lambda x: x['date'], reverse=True)
    
    @classmethod
    def _analyze_reflections(cls, reflections: list) -> str:
        """分析反思报告，提取洞察"""
        # 简化版分析
        total = len(reflections)
        
        summary = f"""# 反思总结报告

**分析期间**: 过去30天
**反思报告数量**: {total}

## 总体趋势

- 共完成 {total} 个任务
- 平均评分: 待计算
- 主要改进领域: 待分析

## 常见问题

1. 待从反思中提取...

## 成功经验

1. 待从反思中提取...

## 改进建议

1. 待基于反思提出...

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return summary
