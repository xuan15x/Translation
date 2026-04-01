"""
高级翻译服务模块
提供上下文感知翻译、机器学习术语推荐、翻译质量自动评估和风格一致性检查
"""
import asyncio
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """翻译质量等级"""
    EXCELLENT = "excellent"      # 优秀 (90-100)
    GOOD = "good"               # 良好 (75-89)
    ACCEPTABLE = "acceptable"   # 可接受 (60-74)
    POOR = "poor"              # 较差 (<60)


class StyleConsistency(Enum):
    """风格一致性级别"""
    PERFECT = "perfect"          # 完全一致
    HIGH = "high"               # 高度一致
    MODERATE = "moderate"       # 中度一致
    LOW = "low"                 # 低度一致
    INCONSISTENT = "inconsistent"  # 不一致


@dataclass
class QualityMetrics:
    """翻译质量评估指标"""
    overall_score: float                    # 总体得分 (0-100)
    accuracy_score: float                   # 准确性得分
    fluency_score: float                    # 流畅性得分
    consistency_score: float                # 一致性得分
    terminology_score: float                # 术语使用得分
    quality_level: QualityLevel             # 质量等级
    issues: List[str] = field(default_factory=list)  # 问题列表
    suggestions: List[str] = field(default_factory=list)  # 改进建议
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'overall_score': self.overall_score,
            'accuracy_score': self.accuracy_score,
            'fluency_score': self.fluency_score,
            'consistency_score': self.consistency_score,
            'terminology_score': self.terminology_score,
            'quality_level': self.quality_level.value,
            'issues': self.issues,
            'suggestions': self.suggestions
        }


@dataclass
class ContextSuggestion:
    """上下文感知翻译建议"""
    source_text: str
    context_type: str  # sentence, paragraph, document
    surrounding_context: List[str]  # 前后文
    translation_suggestion: str
    confidence: float
    reasoning: str
    alternative_translations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'source_text': self.source_text,
            'context_type': self.context_type,
            'surrounding_context': self.surrounding_context,
            'translation_suggestion': self.translation_suggestion,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'alternative_translations': self.alternative_translations
        }


@dataclass
class TermRecommendation:
    """术语推荐结果"""
    source_term: str
    recommended_translation: str
    confidence: float
    source: str  # ml_model, terminology_db, statistical
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    usage_examples: List[str] = field(default_factory=list)
    domain_relevance: float = 0.0  # 领域相关性
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'source_term': self.source_term,
            'recommended_translation': self.recommended_translation,
            'confidence': self.confidence,
            'source': self.source,
            'alternatives': self.alternatives,
            'usage_examples': self.usage_examples,
            'domain_relevance': self.domain_relevance
        }


@dataclass
class StyleConsistencyReport:
    """风格一致性检查报告"""
    consistency_level: StyleConsistency
    consistency_score: float
    inconsistencies: List[Dict] = field(default_factory=list)
    style_violations: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'consistency_level': self.consistency_level.value,
            'consistency_score': self.consistency_score,
            'inconsistencies': self.inconsistencies,
            'style_violations': self.style_violations,
            'recommendations': self.recommendations
        }


class ContextAwareTranslator:
    """上下文感知翻译器（针对 UI 文案优化）"""
    
    def __init__(self, client=None, config=None):
        """
        初始化上下文感知翻译器
        
        Args:
            client: API 客户端
            config: 配置对象
        """
        self.client = client
        self.config = config
        self.context_mode = "isolated"  # isolated(独立) 或 contextual(上下文)
        self.terminology_expansion = True  # 启用术语扩展
    
    def set_context_mode(self, mode: str):
        """
        设置上下文模式
        
        Args:
            mode: 'isolated' (独立模式，适合 UI 文案) 或 'contextual' (上下文模式，适合文档)
        """
        self.context_mode = mode
        logger.info(f"上下文模式已设置为：{mode}")
    
    async def analyze_context(
        self,
        source_text: str,
        full_document: List[str],
        current_index: int,
        target_lang: str,
        terminology_db: Optional[Dict] = None,
        source_lang: Optional[str] = None  # 新增：源语言
    ) -> ContextSuggestion:
        """
        分析上下文并提供翻译建议
        
        Args:
            source_text: 当前待翻译文本
            full_document: 完整文档（句子列表）
            current_index: 当前索引位置
            target_lang: 目标语言
            terminology_db: 术语库数据库（可选）
            source_lang: 源语言（可选）
            
        Returns:
            上下文翻译建议
        """
        # 根据模式决定是否使用上下文
        if self.context_mode == "isolated":
            # 独立模式：忽略上下文，专注当前行和术语扩展
            return await self._analyze_isolated(
                source_text, target_lang, terminology_db, source_lang
            )
        else:
            # 上下文模式：使用传统的窗口分析
            return await self._analyze_with_context(
                source_text, full_document, current_index, target_lang, terminology_db, source_lang
            )
    
    async def _analyze_isolated(
        self,
        source_text: str,
        target_lang: str,
        terminology_db: Optional[Dict] = None,
        source_lang: Optional[str] = None
    ) -> ContextSuggestion:
        """
        独立模式分析（适合 UI 文案）
        
        Args:
            source_text: 源文本
            target_lang: 目标语言
            terminology_db: 术语库
            source_lang: 源语言
            
        Returns:
            翻译建议
        """
        # 提取并扩展术语
        expanded_terms = []
        if terminology_db and self.terminology_expansion:
            expanded_terms = self._expand_terminology(source_text, terminology_db, target_lang, source_lang)
        
        # 构建提示词（强调独立性和术语使用）
        prompt = self._build_isolated_prompt(
            source_text, target_lang, expanded_terms, source_lang
        )
        
        # 调用 API 获取建议
        suggestion = await self._get_ai_suggestion(prompt, source_text, target_lang)
        
        return ContextSuggestion(
            source_text=source_text,
            context_type="isolated",
            surrounding_context=[],
            translation_suggestion=suggestion['translation'],
            confidence=suggestion['confidence'],
            reasoning=suggestion['reasoning'],
            alternative_translations=suggestion.get('alternatives', [])
        )
    
    def _expand_terminology(
        self,
        source_text: str,
        terminology_db: Dict,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> List[Dict]:
        """
        从术语库中扩展相关术语
        
        Args:
            source_text: 源文本
            terminology_db: 术语库
            target_lang: 目标语言
            source_lang: 源语言（用于过滤）
            
        Returns:
            相关术语列表
        """
        related_terms = []
        
        # 检查源文本是否包含术语库中的术语
        for term, translations in terminology_db.items():
            if term in source_text:
                trans = translations.get(target_lang, '')
                if trans:
                    related_terms.append({
                        'source': term,
                        'translation': trans,
                        'exact_match': True,
                        'source_lang': source_lang
                    })
            else:
                # 模糊匹配：检查术语是否是源文本的子串
                # 或者源文本包含术语的关键词
                term_keywords = set(term.split())
                text_words = set(source_text.split())
                
                # 如果有重叠的关键词
                if term_keywords & text_words:
                    trans = translations.get(target_lang, '')
                    if trans:
                        related_terms.append({
                            'source': term,
                            'translation': trans,
                            'exact_match': False,
                            'match_keywords': list(term_keywords & text_words),
                            'source_lang': source_lang
                        })
        
        return related_terms
    
    def _build_isolated_prompt(
        self,
        source_text: str,
        target_lang: str,
        expanded_terms: List[Dict],
        source_lang: Optional[str] = None
    ) -> str:
        """构建独立模式的提示词（强调术语使用）"""
        # 构建术语参考信息
        term_info = ""
        if expanded_terms:
            term_lines = ["【相关术语参考】"]
            for term_data in expanded_terms:
                match_type = "精确匹配" if term_data['exact_match'] else f"相关匹配 ({', '.join(term_data.get('match_keywords', []))})"
                source_lang_info = f" (源语言：{term_data.get('source_lang', '未知')})" if term_data.get('source_lang') else ""
                term_lines.append(f"• {term_data['source']} → {term_data['translation']} [{match_type}]{source_lang_info}")
            term_info = "\n".join(term_lines) + "\n\n"
        
        # 添加源语言信息到提示词
        source_lang_info = f"\n源语言：{source_lang}" if source_lang else ""
        
        prompt = f"""你是一个专业的 UI 文案翻译，擅长将界面文本翻译成{target_lang}。

【待翻译文本】
{source_text}
{source_lang_info}
{term_info}【要求】
1. 这是独立的 UI 元素文案（如按钮、标签等），不需要考虑上下文
2. 简洁明了，符合 UI 文案规范
3. **必须使用上述提供的术语翻译**（如果有）
4. 保持专业性和一致性
5. 长度适中，适合界面显示
6. 注意源语言的语义特点（如果有提供）

请提供：
1. 最佳翻译建议
2. 置信度（0-100）
3. 推理过程说明
4. 2-3 个备选翻译（如果有）

请以 JSON 格式返回：
{{
    "translation": "翻译结果",
    "confidence": 95,
    "reasoning": "推理说明，特别是术语使用情况",
    "alternatives": ["备选 1", "备选 2"]
}}"""
        
        return prompt
    
    async def _analyze_with_context(
        self,
        source_text: str,
        full_document: List[str],
        current_index: int,
        target_lang: str,
        terminology_db: Optional[Dict] = None
    ) -> ContextSuggestion:
        """带上下文的分析（传统模式）"""
        # 提取上下文窗口
        start = max(0, current_index - self.context_window_size)
        end = min(len(full_document), current_index + self.context_window_size + 1)
        
        preceding_context = full_document[start:current_index]
        following_context = full_document[current_index + 1:end]
        
        surrounding = []
        if preceding_context:
            surrounding.append(f"前文：{' | '.join(preceding_context[-2:])}")
        if following_context:
            surrounding.append(f"后文：{' | '.join(following_context[:2])}")
        
        # 确定上下文类型
        context_type = "sentence"
        if len(preceding_context) + len(following_context) > 4:
            context_type = "paragraph"
        
        # 构建提示词
        prompt = self._build_context_prompt(
            source_text, surrounding, target_lang, context_type
        )
        
        # 调用 API 获取建议
        suggestion = await self._get_ai_suggestion(prompt, source_text, target_lang)
        
        return ContextSuggestion(
            source_text=source_text,
            context_type=context_type,
            surrounding_context=surrounding,
            translation_suggestion=suggestion['translation'],
            confidence=suggestion['confidence'],
            reasoning=suggestion['reasoning'],
            alternative_translations=suggestion.get('alternatives', [])
        )
    
    def _build_context_prompt(
        self,
        source_text: str,
        surrounding: List[str],
        target_lang: str,
        context_type: str
    ) -> str:
        """构建上下文感知的提示词"""
        context_info = "\n".join(surrounding) if surrounding else "无上下文信息"
        
        prompt = f"""你是一个专业的翻译，擅长根据上下文进行翻译。请根据提供的上下文信息，将下面的文本翻译成{target_lang}。

【上下文信息】
{context_info}

【待翻译文本】
{source_text}

【要求】
1. 结合上下文理解语义，确保翻译连贯
2. 保持与前后文的逻辑关系
3. 注意代词指代和时态一致性
4. 如果是段落的一部分，确保风格统一

请提供：
1. 最佳翻译建议
2. 置信度（0-100）
3. 推理过程说明
4. 2-3 个备选翻译（如果有）

请以 JSON 格式返回：
{{
    "translation": "翻译结果",
    "confidence": 95,
    "reasoning": "推理说明",
    "alternatives": ["备选 1", "备选 2"]
}}"""
        
        return prompt
    
    async def _get_ai_suggestion(
        self,
        prompt: str,
        source_text: str,
        target_lang: str
    ) -> Dict:
        """获取 AI 建议"""
        if not self.client:
            # 没有客户端时返回默认值
            return {
                'translation': source_text,  # 占位
                'confidence': 50,
                'reasoning': '未配置 AI 客户端',
                'alternatives': []
            }
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.model_name if self.config else "deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是专业的翻译助手"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            
            # 解析 JSON 响应
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # 如果不是 JSON，尝试提取第一行作为翻译
                lines = content.split('\n')
                return {
                    'translation': lines[0] if lines else source_text,
                    'confidence': 70,
                    'reasoning': content[:100],
                    'alternatives': []
                }
                
        except Exception as e:
            logger.error(f"获取上下文建议失败：{e}")
            return {
                'translation': source_text,
                'confidence': 50,
                'reasoning': f'API 调用失败：{str(e)}',
                'alternatives': []
            }


class TranslationQualityEvaluator:
    """翻译质量自动评估器"""
    
    def __init__(self, terminology_db: Optional[Dict] = None):
        """
        初始化质量评估器
        
        Args:
            terminology_db: 术语库数据库
        """
        self.terminology_db = terminology_db or {}
    
    async def evaluate_quality(
        self,
        source_text: str,
        translation: str,
        target_lang: str,
        context: Optional[Dict] = None
    ) -> QualityMetrics:
        """
        评估翻译质量
        
        Args:
            source_text: 源文本
            translation: 翻译结果
            target_lang: 目标语言
            context: 上下文信息（可选）
            
        Returns:
            质量评估指标
        """
        issues = []
        suggestions = []
        
        # 1. 准确性评估
        accuracy_score = await self._evaluate_accuracy(source_text, translation)
        
        # 2. 流畅性评估
        fluency_score = await self._evaluate_fluency(translation, target_lang)
        
        # 3. 一致性评估
        consistency_score = await self._evaluate_consistency(source_text, translation)
        
        # 4. 术语使用评估
        terminology_score, term_issues = await self._evaluate_terminology(
            source_text, translation, target_lang
        )
        issues.extend(term_issues)
        
        # 计算总体得分
        weights = {
            'accuracy': 0.4,
            'fluency': 0.3,
            'consistency': 0.2,
            'terminology': 0.1
        }
        
        overall_score = (
            accuracy_score * weights['accuracy'] +
            fluency_score * weights['fluency'] +
            consistency_score * weights['consistency'] +
            terminology_score * weights['terminology']
        )
        
        # 确定质量等级
        quality_level = self._determine_quality_level(overall_score)
        
        # 生成改进建议
        suggestions = self._generate_suggestions(
            overall_score, accuracy_score, fluency_score,
            consistency_score, terminology_score
        )
        
        return QualityMetrics(
            overall_score=round(overall_score, 2),
            accuracy_score=round(accuracy_score, 2),
            fluency_score=round(fluency_score, 2),
            consistency_score=round(consistency_score, 2),
            terminology_score=round(terminology_score, 2),
            quality_level=quality_level,
            issues=issues,
            suggestions=suggestions
        )
    
    async def _evaluate_accuracy(
        self,
        source_text: str,
        translation: str
    ) -> float:
        """评估准确性（语义完整性）"""
        # 简单实现：基于长度比例和关键词匹配
        src_len = len(source_text)
        trans_len = len(translation)
        
        # 长度比例（理想比例因语言而异，这里简化处理）
        length_ratio = min(trans_len / (src_len * 1.5), src_len * 1.5 / trans_len) if trans_len > 0 else 0
        
        # 基础分数
        score = min(length_ratio * 100, 100)
        
        # 检查是否有明显的遗漏（如数字、专有名词）
        src_numbers = re.findall(r'\d+', source_text)
        trans_numbers = re.findall(r'\d+', translation)
        
        if src_numbers and set(src_numbers) != set(trans_numbers):
            score -= 20
        
        return max(0, min(100, score))
    
    async def _evaluate_fluency(
        self,
        translation: str,
        target_lang: str
    ) -> float:
        """评估流畅性"""
        # 简单实现：基于语法和可读性
        score = 80  # 基础分
        
        # 检查明显的语法问题
        if translation.count(' ') < len(translation) // 10:  # 缺少空格
            score -= 20
        
        # 检查重复词汇
        words = translation.split()
        if len(words) > 3:
            from collections import Counter
            word_counts = Counter(words)
            most_common = word_counts.most_common(1)[0][1]
            if most_common > len(words) * 0.3:  # 某个词占比超过 30%
                score -= 15
        
        return max(0, min(100, score))
    
    async def _evaluate_consistency(
        self,
        source_text: str,
        translation: str
    ) -> float:
        """评估一致性（术语、风格）"""
        # 简单实现
        return 85.0
    
    async def _evaluate_terminology(
        self,
        source_text: str,
        translation: str,
        target_lang: str
    ) -> Tuple[float, List[str]]:
        """评估术语使用"""
        issues = []
        score = 100.0
        
        if not self.terminology_db:
            return score, issues
        
        # 检查术语库中的术语是否被正确使用
        for term, translations in self.terminology_db.items():
            if term in source_text:
                correct_trans = translations.get(target_lang, '')
                if correct_trans and correct_trans not in translation:
                    issues.append(f"术语 '{term}' 应翻译为 '{correct_trans}'")
                    score -= 15
        
        return max(0, score), issues
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        else:
            return QualityLevel.POOR
    
    def _generate_suggestions(
        self,
        overall: float,
        accuracy: float,
        fluency: float,
        consistency: float,
        terminology: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if accuracy < 80:
            suggestions.append("提高翻译准确性，确保完整传达原文含义")
        
        if fluency < 75:
            suggestions.append("改善译文流畅度，使其更符合目标语言表达习惯")
        
        if consistency < 70:
            suggestions.append("保持术语和风格的一致性")
        
        if terminology < 80:
            suggestions.append("使用标准术语库中的译法")
        
        if overall >= 90:
            suggestions.append("翻译质量优秀，无需特别改进")
        
        return suggestions


class StyleConsistencyChecker:
    """风格一致性检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.style_patterns = {}
        self.translation_history = []
    
    async def check_consistency(
        self,
        translations: List[Dict[str, str]],
        style_guide: Optional[Dict] = None
    ) -> StyleConsistencyReport:
        """
        检查翻译风格一致性
        
        Args:
            translations: 翻译列表，每项包含 {'source': ..., 'translation': ...}
            style_guide: 风格指南（可选）
            
        Returns:
            一致性检查报告
        """
        inconsistencies = []
        style_violations = []
        recommendations = []
        
        # 1. 检查相同源词的不同翻译
        term_translations = {}
        for item in translations:
            src = item['source']
            trans = item['translation']
            
            # 提取关键术语
            terms = self._extract_key_terms(src)
            for term in terms:
                if term not in term_translations:
                    term_translations[term] = []
                term_translations[term].append(trans)
        
        # 找出不一致的翻译
        for term, trans_list in term_translations.items():
            unique_trans = set(trans_list)
            if len(unique_trans) > 1:
                inconsistencies.append({
                    'term': term,
                    'translations': list(unique_trans),
                    'occurrences': len(trans_list)
                })
        
        # 2. 检查风格指南违规
        if style_guide:
            violations = await self._check_style_violations(translations, style_guide)
            style_violations.extend(violations)
        
        # 3. 计算一致性得分
        total_items = len(translations)
        inconsistent_count = len(inconsistencies)
        violation_count = len(style_violations)
        
        consistency_score = max(
            0,
            100 - (inconsistent_count * 10) - (violation_count * 5)
        )
        
        # 4. 确定一致性级别
        consistency_level = self._determine_consistency_level(consistency_score)
        
        # 5. 生成建议
        recommendations = self._generate_style_recommendations(
            inconsistencies, style_violations
        )
        
        return StyleConsistencyReport(
            consistency_level=consistency_level,
            consistency_score=round(consistency_score, 2),
            inconsistencies=inconsistencies,
            style_violations=style_violations,
            recommendations=recommendations
        )
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """提取关键术语"""
        # 简单实现：提取名词短语
        # 实际应用中可以使用 NLP 工具
        words = text.split()
        # 过滤掉常见虚词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人'}
        key_terms = [w for w in words if w not in stop_words and len(w) > 1]
        return key_terms[:5]  # 限制数量
    
    async def _check_style_violations(
        self,
        translations: List[Dict],
        style_guide: Dict
    ) -> List[Dict]:
        """检查风格指南违规"""
        violations = []
        
        # 示例：检查是否使用指定的称谓
        if 'pronouns' in style_guide:
            preferred = style_guide['pronouns']
            for item in translations:
                trans = item['translation']
                # 检查是否使用了不推荐的代词
                # 这里简化处理
                pass
        
        return violations
    
    def _determine_consistency_level(self, score: float) -> StyleConsistency:
        """确定一致性级别"""
        if score >= 95:
            return StyleConsistency.PERFECT
        elif score >= 85:
            return StyleConsistency.HIGH
        elif score >= 70:
            return StyleConsistency.MODERATE
        elif score >= 50:
            return StyleConsistency.LOW
        else:
            return StyleConsistency.INCONSISTENT
    
    def _generate_style_recommendations(
        self,
        inconsistencies: List[Dict],
        violations: List[Dict]
    ) -> List[str]:
        """生成风格建议"""
        recommendations = []
        
        if inconsistencies:
            terms = [inc['term'] for inc in inconsistencies[:3]]
            recommendations.append(
                f"统一以下术语的翻译：{', '.join(terms)}"
            )
        
        if violations:
            recommendations.append("遵守风格指南规范")
        
        if not recommendations:
            recommendations.append("风格一致性良好，继续保持")
        
        return recommendations


class MLTermRecommender:
    """机器学习术语推荐器（简化版，基于统计）"""
    
    def __init__(self, training_data: Optional[List[Dict]] = None):
        """
        初始化推荐器
        
        Args:
            training_data: 训练数据（平行语料）
        """
        self.training_data = training_data or []
        self.term_database = {}
        self.statistics = {}
        
        if self.training_data:
            self._build_term_database()
    
    def _build_term_database(self):
        """构建术语数据库"""
        # 从训练数据中提取术语对
        term_freq = {}
        
        for item in self.training_data:
            src = item.get('source', '')
            trans = item.get('translation', '')
            
            # 提取术语（简化：按词分割）
            src_terms = src.split()
            trans_terms = trans.split()
            
            # 统计共现频率
            for i, src_term in enumerate(src_terms):
                if len(src_term) > 1:  # 忽略单字词
                    corresponding = trans_terms[i] if i < len(trans_terms) else ''
                    
                    if src_term not in term_freq:
                        term_freq[src_term] = {}
                    
                    if corresponding not in term_freq[src_term]:
                        term_freq[src_term][corresponding] = 0
                    
                    term_freq[src_term][corresponding] += 1
        
        # 选择最佳翻译
        for src_term, trans_dict in term_freq.items():
            if trans_dict:
                best_trans = max(trans_dict.items(), key=lambda x: x[1])
                total_freq = sum(trans_dict.values())
                
                self.term_database[src_term] = {
                    'best_translation': best_trans[0],
                    'confidence': best_trans[1] / total_freq if total_freq > 0 else 0,
                    'alternatives': sorted(
                        [(k, v/total_freq) for k, v in trans_dict.items()],
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'frequency': total_freq
                }
    
    async def recommend_translation(
        self,
        source_term: str,
        target_lang: str,
        context: Optional[str] = None
    ) -> Optional[TermRecommendation]:
        """
        推荐术语翻译
        
        Args:
            source_term: 源术语
            target_lang: 目标语言
            context: 上下文（可选）
            
        Returns:
            术语推荐结果
        """
        if source_term not in self.term_database:
            return None
        
        term_info = self.term_database[source_term]
        
        # 计算领域相关性（如果有上下文）
        domain_relevance = 0.8  # 默认值
        
        return TermRecommendation(
            source_term=source_term,
            recommended_translation=term_info['best_translation'],
            confidence=term_info['confidence'],
            source='statistical',
            alternatives=term_info.get('alternatives', []),
            usage_examples=[],
            domain_relevance=domain_relevance
        )
    
    async def batch_recommend(
        self,
        terms: List[str],
        target_lang: str
    ) -> Dict[str, TermRecommendation]:
        """批量推荐"""
        results = {}
        
        for term in terms:
            rec = await self.recommend_translation(term, target_lang)
            if rec:
                results[term] = rec
        
        return results


# 全局服务实例
_context_translator: Optional[ContextAwareTranslator] = None
_quality_evaluator: Optional[TranslationQualityEvaluator] = None
_style_checker: Optional[StyleConsistencyChecker] = None
_term_recommender: Optional[MLTermRecommender] = None


def get_context_translator(client=None, config=None) -> ContextAwareTranslator:
    """获取上下文翻译器实例"""
    global _context_translator
    if _context_translator is None:
        _context_translator = ContextAwareTranslator(client, config)
    return _context_translator


def get_quality_evaluator(terminology_db=None) -> TranslationQualityEvaluator:
    """获取质量评估器实例"""
    global _quality_evaluator
    if _quality_evaluator is None:
        _quality_evaluator = TranslationQualityEvaluator(terminology_db)
    return _quality_evaluator


def get_style_checker() -> StyleConsistencyChecker:
    """获取风格检查器实例"""
    global _style_checker
    if _style_checker is None:
        _style_checker = StyleConsistencyChecker()
    return _style_checker


def get_term_recommender(training_data=None) -> MLTermRecommender:
    """获取术语推荐器实例"""
    global _term_recommender
    if _term_recommender is None:
        _term_recommender = MLTermRecommender(training_data)
    return _term_recommender
