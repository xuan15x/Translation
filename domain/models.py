"""
领域模型层
定义核心业务实体和业务规则
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class MatchType(Enum):
    """匹配类型"""
    EXACT = "exact"          # 精确匹配（100 分）
    FUZZY = "fuzzy"          # 模糊匹配（60-99 分）
    NO_MATCH = "no_match"    # 无匹配


class TranslationStatus(Enum):
    """翻译状态"""
    PENDING = "pending"      # 待翻译
    TRANSLATING = "translating"  # 翻译中
    SUCCESS = "success"      # 翻译成功
    FAILED = "failed"        # 翻译失败
    LOCAL_HIT = "local_hit"  # 本地命中


@dataclass
class TermMatch:
    """术语匹配结果 - 领域模型"""
    original: str                    # 原文
    translation: str                 # 译文
    score: int                       # 匹配置信度 (0-100)
    match_type: MatchType            # 匹配类型
    target_lang: str                 # 目标语言
    
    @property
    def is_exact(self) -> bool:
        """是否精确匹配"""
        return self.match_type == MatchType.EXACT
    
    @property
    def should_use_ai(self) -> bool:
        """是否需要 AI 翻译"""
        return not self.is_exact
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TermMatch':
        """从字典创建"""
        score = data.get('score', 0)
        match_type = MatchType.EXACT if score == 100 else (
            MatchType.FUZZY if score >= 60 else MatchType.NO_MATCH
        )
        
        return cls(
            original=data.get('original', ''),
            translation=data.get('translation', ''),
            score=score,
            match_type=match_type,
            target_lang=data.get('target_lang', '')
        )


@dataclass
class TranslationTask:
    """翻译任务 - 领域模型"""
    idx: int                         # 行索引
    key: str                         # 唯一标识
    source_text: str                 # 源文本
    original_trans: Optional[str]    # 原译文（校对模式）
    target_lang: str                 # 目标语言
    source_lang: Optional[str] = None  # 源语言
    
    def to_context(self) -> Dict[str, Any]:
        """转换为上下文对象"""
        return {
            'idx': self.idx,
            'key': self.key,
            'source_text': self.source_text,
            'original_trans': self.original_trans,
            'target_lang': self.target_lang,
            'source_lang': self.source_lang
        }


@dataclass
class TranslationResult:
    """翻译结果 - 领域模型"""
    task: TranslationTask            # 关联的任务
    final_trans: str                 # 最终译文
    initial_trans: str               # 初译结果
    reason: str                      # 修改原因
    diagnosis: str                   # 诊断信息
    status: TranslationStatus        # 状态
    tm_match: Optional[TermMatch] = None  # 术语库匹配结果
    
    @property
    def success(self) -> bool:
        """是否成功"""
        return self.status in [
            TranslationStatus.SUCCESS,
            TranslationStatus.LOCAL_HIT
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'idx': self.task.idx,
            'key': self.task.key,
            'source_text': self.task.source_text,
            'final_trans': self.final_trans,
            'initial_trans': self.initial_trans,
            'reason': self.reason,
            'diagnosis': self.diagnosis,
            'status': self.status.value,
            'tm_match': {
                'original': self.tm_match.original,
                'translation': self.tm_match.translation,
                'score': self.tm_match.score,
                'match_type': self.tm_match.match_type.value
            } if self.tm_match else None
        }


@dataclass
class BatchResult:
    """批量翻译结果 - 领域模型"""
    total: int                       # 总任务数
    success_count: int               # 成功数
    failed_count: int                # 失败数
    local_hit_count: int             # 本地命中数
    results: List[TranslationResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """成功率"""
        return (self.success_count / self.total * 100) if self.total > 0 else 0.0

    def add_result(self, result: TranslationResult):
        """添加结果"""
        self.results.append(result)
        if result.success:
            self.success_count += 1
            if result.status == TranslationStatus.LOCAL_HIT:
                self.local_hit_count += 1
        else:
            self.failed_count += 1


@dataclass
class MultiLanguageTask:
    """多语言翻译任务 - 一次请求翻译多种语言"""
    idx: int                         # 行索引
    key: str                         # 唯一标识
    source_text: str                 # 源文本
    target_langs: List[str]          # 目标语言列表
    source_lang: Optional[str] = None  # 源语言
    tm_matches: Dict[str, Optional['TermMatch']] = field(default_factory=dict)  # 各语言术语匹配

    def to_prompt_context(self) -> Dict[str, Any]:
        """转换为提示词上下文"""
        return {
            'idx': self.idx,
            'key': self.key,
            'source_text': self.source_text,
            'target_langs': self.target_langs,
            'source_lang': self.source_lang,
            'tm_matches': self.tm_matches
        }


@dataclass
class MultiLanguageResult:
    """多语言翻译结果 - 一次请求的多种语言结果"""
    task: MultiLanguageTask          # 关联的任务
    translations: Dict[str, str]     # 各语言翻译结果 {lang: translation}
    success_langs: List[str]         # 成功的语言列表
    failed_langs: List[str]          # 失败的语言列表
    diagnosis: str                   # 诊断信息
    status: TranslationStatus        # 整体状态

    @property
    def success(self) -> bool:
        """是否全部成功"""
        return len(self.failed_langs) == 0 and len(self.success_langs) > 0

    @property
    def partial_success(self) -> bool:
        """是否部分成功"""
        return len(self.success_langs) > 0 and len(self.failed_langs) > 0

    def to_single_results(self) -> List[TranslationResult]:
        """转换为单语言结果列表"""
        results = []
        for lang in self.task.target_langs:
            task = TranslationTask(
                idx=self.task.idx,
                key=self.task.key,
                source_text=self.task.source_text,
                original_trans=None,
                target_lang=lang,
                source_lang=self.task.source_lang
            )
            
            if lang in self.success_langs:
                status = TranslationStatus.SUCCESS
                final_trans = self.translations.get(lang, '')
                reason = ''
            else:
                status = TranslationStatus.FAILED
                final_trans = '(Failed)'
                reason = f"语言 {lang} 翻译失败"
            
            result = TranslationResult(
                task=task,
                final_trans=final_trans,
                initial_trans=final_trans,
                reason=reason,
                diagnosis=self.diagnosis,
                status=status
            )
            results.append(result)
        return results
