"""
配置检查模块
提供完整的配置验证功能，确保外部配置的正确性和安全性
"""
import re
import os
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CheckLevel(Enum):
    """检查级别"""
    ERROR = "error"      # 致命错误，必须修复
    WARNING = "warning"  # 警告，建议修复
    INFO = "info"        # 提示信息


class CheckCategory(Enum):
    """检查类别"""
    SYNTAX = "syntax"          # 语法检查
    RANGE = "range"            # 取值范围
    DEPENDENCY = "dependency"  # 依赖关系
    SECURITY = "security"      # 安全性
    PERFORMANCE = "performance" # 性能建议
    BEST_PRACTICE = "best_practice"  # 最佳实践


@dataclass
class CheckResult:
    """检查结果"""
    level: CheckLevel
    category: CheckCategory
    key: str
    message: str
    suggestion: Optional[str] = None
    value: Any = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'level': self.level.value,
            'category': self.category.value,
            'key': self.key,
            'message': self.message,
            'suggestion': self.suggestion,
            'value': self.value
        }


class ConfigChecker:
    """配置检查器"""
    
    # API 提供商映射
    PROVIDER_ENV_MAPPING = {
        'deepseek': 'DEEPSEEK_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'moonshot': 'MOONSHOT_API_KEY',
        'zhipu': 'ZHIPU_API_KEY',
        'baidu': 'BAIDU_API_KEY',
        'alibaba': 'ALIBABA_API_KEY',
    }
    
    # URL 正则表达式
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def __init__(self):
        """初始化配置检查器"""
        self.results: List[CheckResult] = []
    
    def check(self, config: Dict[str, Any]) -> List[CheckResult]:
        """
        执行完整配置检查
        
        Args:
            config: 配置字典
            
        Returns:
            检查结果列表
        """
        self.results = []
        
        # 1. 必填字段检查
        self._check_required_fields(config)
        
        # 2. API 配置检查
        self._check_api_config(config)
        
        # 3. 模型参数检查
        self._check_model_params(config)
        
        # 4. 并发控制检查
        self._check_concurrency_config(config)
        
        # 5. 重试配置检查
        self._check_retry_config(config)
        
        # 6. 工作流配置检查
        self._check_workflow_config(config)
        
        # 7. 术语库配置检查
        self._check_terminology_config(config)
        
        # 8. 性能配置检查
        self._check_performance_config(config)
        
        # 9. 日志配置检查
        self._check_log_config(config)
        
        # 10. GUI 配置检查
        self._check_gui_config(config)
        
        # 11. 语言配置检查
        self._check_language_config(config)
        
        # 12. 备份配置检查
        self._check_backup_config(config)
        
        # 13. 监控配置检查
        self._check_monitor_config(config)
        
        # 14. 提示词检查
        self._check_prompts(config)
        
        # 按级别排序：ERROR > WARNING > INFO
        self.results.sort(key=lambda x: {'error': 0, 'warning': 1, 'info': 2}[x.level.value])
        
        return self.results
    
    def _add_result(self, level: CheckLevel, category: CheckCategory, 
                   key: str, message: str, suggestion: Optional[str] = None,
                   value: Any = None):
        """添加检查结果"""
        self.results.append(CheckResult(
            level=level,
            category=category,
            key=key,
            message=message,
            suggestion=suggestion,
            value=value
        ))
    
    def _check_required_fields(self, config: Dict[str, Any]):
        """检查必填字段"""
        required_fields = ['api_key']
        
        for field in required_fields:
            value = config.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                self._add_result(
                    CheckLevel.ERROR,
                    CheckCategory.SYNTAX,
                    field,
                    f"必填字段 '{field}' 不能为空",
                    f"请设置有效的 {field} 值"
                )
    
    def _check_api_config(self, config: Dict[str, Any]):
        """检查 API 配置"""
        # api_provider
        provider = config.get('api_provider', 'deepseek')
        valid_providers = list(self.PROVIDER_ENV_MAPPING.keys())
        if provider not in valid_providers:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'api_provider',
                f"未知的 API 提供商：'{provider}'",
                f"支持的提供商：{', '.join(valid_providers)}",
                provider
            )
        
        # base_url
        base_url = config.get('base_url', '')
        if base_url and not self.URL_PATTERN.match(base_url):
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'base_url',
                f"base_url 格式可能不正确：'{base_url}'",
                "URL 应以 http:// 或 https:// 开头",
                base_url
            )
        
        # api_key 和 provider 的匹配性
        if provider in self.PROVIDER_ENV_MAPPING:
            env_var = self.PROVIDER_ENV_MAPPING[provider]
            if not config.get('api_key'):
                # 检查环境变量
                if not os.getenv(env_var):
                    self._add_result(
                        CheckLevel.ERROR,
                        CheckCategory.SECURITY,
                        'api_key',
                        f"API 密钥未设置（提供商：{provider}）",
                        f"请设置 api_key 或环境变量 {env_var}"
                    )
    
    def _check_model_params(self, config: Dict[str, Any]):
        """检查模型参数"""
        # temperature
        temperature = config.get('temperature', 0.3)
        if not isinstance(temperature, (int, float)):
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'temperature',
                f"temperature 必须是数字，当前类型：{type(temperature).__name__}",
                "设置 0-2 之间的数值"
            )
        elif not (0 <= temperature <= 2):
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.RANGE,
                'temperature',
                f"temperature 值为 {temperature}，超出推荐范围 [0, 2]",
                "推荐值：0.3（平衡），0.7（创造性），0.1（保守）",
                temperature
            )
        
        # top_p
        top_p = config.get('top_p', 0.8)
        if not isinstance(top_p, (int, float)):
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'top_p',
                f"top_p 必须是数字，当前类型：{type(top_p).__name__}",
                "设置 0-1 之间的数值"
            )
        elif not (0 <= top_p <= 1):
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.RANGE,
                'top_p',
                f"top_p 值为 {top_p}，超出推荐范围 [0, 1]",
                "推荐值：0.8-0.9",
                top_p
            )
    
    def _check_concurrency_config(self, config: Dict[str, Any]):
        """检查并发控制配置"""
        initial = config.get('initial_concurrency', 8)
        maximum = config.get('max_concurrency', 10)
        cooldown = config.get('concurrency_cooldown_seconds', 5.0)
        
        # 初始并发
        if not isinstance(initial, int) or initial < 1:
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'initial_concurrency',
                f"initial_concurrency 必须是正整数，当前值：{initial}",
                "设置 >= 1 的整数"
            )
        
        # 最大并发
        if not isinstance(maximum, int) or maximum < 1:
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'max_concurrency',
                f"max_concurrency 必须是正整数，当前值：{maximum}",
                "设置 >= 1 的整数"
            )
        
        # max >= initial
        if isinstance(initial, int) and isinstance(maximum, int):
            if maximum < initial:
                self._add_result(
                    CheckLevel.ERROR,
                    CheckCategory.DEPENDENCY,
                    'max_concurrency',
                    f"max_concurrency ({maximum}) 不能小于 initial_concurrency ({initial})",
                    f"调整 max_concurrency >= {initial}"
                )
        
        # cooldown
        if not isinstance(cooldown, (int, float)) or cooldown < 0:
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'concurrency_cooldown_seconds',
                f"concurrency_cooldown_seconds 必须是非负数，当前值：{cooldown}",
                "设置 >= 0 的数值"
            )
    
    def _check_retry_config(self, config: Dict[str, Any]):
        """检查重试配置"""
        retry_streak = config.get('retry_streak_threshold', 3)
        base_delay = config.get('base_retry_delay', 3.0)
        max_retries = config.get('max_retries', 3)
        timeout = config.get('timeout', 60)
        
        checks = [
            ('retry_streak_threshold', retry_streak, 1, None),
            ('base_retry_delay', base_delay, 0, None),
            ('max_retries', max_retries, 0, 10),
            ('timeout', timeout, 1, 300),
        ]
        
        for name, value, min_val, max_val in checks:
            if not isinstance(value, (int, float)):
                self._add_result(
                    CheckLevel.ERROR,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 必须是数字，当前值：{value}",
                    f"设置 >= {min_val} 的数值"
                )
            elif value < min_val:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 值为 {value}，小于最小值 {min_val}",
                    f"设置 >= {min_val}",
                    value
                )
            elif max_val and value > max_val:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 值为 {value}，大于最大值 {max_val}",
                    f"设置 <= {max_val}",
                    value
                )
    
    def _check_workflow_config(self, config: Dict[str, Any]):
        """检查工作流配置"""
        enable_two_pass = config.get('enable_two_pass', True)
        skip_review = config.get('skip_review_if_local_hit', True)
        batch_size = config.get('batch_size', 1000)
        gc_interval = config.get('gc_interval', 2)
        
        # 布尔值检查
        for name, value in [('enable_two_pass', enable_two_pass), 
                           ('skip_review_if_local_hit', skip_review)]:
            if not isinstance(value, bool):
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.SYNTAX,
                    name,
                    f"{name} 应该是布尔值，当前类型：{type(value).__name__}",
                    "设置为 true 或 false",
                    value
                )
        
        # batch_size
        if not isinstance(batch_size, int) or batch_size < 1:
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.RANGE,
                'batch_size',
                f"batch_size 必须是正整数，当前值：{batch_size}",
                "设置 >= 1 的整数"
            )
        
        # gc_interval
        if not isinstance(gc_interval, int) or gc_interval < 1:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.RANGE,
                'gc_interval',
                f"gc_interval 值为 {gc_interval}，推荐 >= 1",
                "设置 >= 1 的整数"
            )
    
    def _check_terminology_config(self, config: Dict[str, Any]):
        """检查术语库配置"""
        similarity_low = config.get('similarity_low', 60)
        exact_match_score = config.get('exact_match_score', 100)
        threshold = config.get('multiprocess_threshold', 1000)
        
        checks = [
            ('similarity_low', similarity_low, 0, 100, "相似度阈值（0-100）"),
            ('exact_match_score', exact_match_score, 0, 100, "精确匹配置信度（0-100）"),
            ('multiprocess_threshold', threshold, 0, None, "多进程阈值"),
        ]
        
        for name, value, min_val, max_val, desc in checks:
            if not isinstance(value, (int, float)):
                self._add_result(
                    CheckLevel.ERROR,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 必须是数字，当前值：{value}",
                    desc
                )
            elif value < min_val:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 值为 {value}，小于最小值 {min_val}",
                    f"设置 >= {min_val}",
                    value
                )
            elif max_val and value > max_val:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 值为 {value}，大于最大值 {max_val}",
                    f"设置 <= {max_val}",
                    value
                )
    
    def _check_performance_config(self, config: Dict[str, Any]):
        """检查性能配置"""
        pool_size = config.get('pool_size', 5)
        cache_capacity = config.get('cache_capacity', 2000)
        cache_ttl = config.get('cache_ttl_seconds', 3600)
        
        checks = [
            ('pool_size', pool_size, 1, 20, "连接池大小（1-20）"),
            ('cache_capacity', cache_capacity, 100, None, "缓存容量"),
            ('cache_ttl_seconds', cache_ttl, 0, None, "缓存 TTL"),
        ]
        
        for name, value, min_val, max_val, desc in checks:
            if not isinstance(value, (int, float)):
                self._add_result(
                    CheckLevel.ERROR,
                    CheckCategory.RANGE,
                    name,
                    f"{name} 必须是数字，当前值：{value}",
                    desc
                )
            elif value < min_val:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.PERFORMANCE,
                    name,
                    f"{name} 值为 {value}，可能影响性能",
                    f"建议设置 >= {min_val}",
                    value
                )
    
    def _check_log_config(self, config: Dict[str, Any]):
        """检查日志配置"""
        log_level = config.get('log_level', 'INFO')
        log_granularity = config.get('log_granularity', 'normal')
        log_max_lines = config.get('log_max_lines', 1000)
        
        # log_level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if isinstance(log_level, str) and log_level.upper() not in valid_levels:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'log_level',
                f"无效的日志级别：'{log_level}'",
                f"有效值：{', '.join(valid_levels)}",
                log_level
            )
        
        # log_granularity
        valid_granularities = ['minimal', 'basic', 'normal', 'detailed', 'verbose']
        if isinstance(log_granularity, str) and log_granularity.lower() not in valid_granularities:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'log_granularity',
                f"无效的日志粒度：'{log_granularity}'",
                f"有效值：{', '.join(valid_granularities)}",
                log_granularity
            )
        
        # log_max_lines
        if not isinstance(log_max_lines, int) or log_max_lines < 100:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.PERFORMANCE,
                'log_max_lines',
                f"log_max_lines 值为 {log_max_lines}，可能影响性能",
                "建议设置 >= 100",
                log_max_lines
            )
    
    def _check_gui_config(self, config: Dict[str, Any]):
        """检查 GUI 配置"""
        window_width = config.get('gui_window_width', 950)
        window_height = config.get('gui_window_height', 800)
        
        for name, value, min_val in [
            ('gui_window_width', window_width, 640),
            ('gui_window_height', window_height, 480)
        ]:
            if not isinstance(value, int):
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.SYNTAX,
                    name,
                    f"{name} 应该是整数，当前类型：{type(value).__name__}",
                    f"设置 >= {min_val} 的整数"
                )
            elif value < min_val:
                self._add_result(
                    CheckLevel.INFO,
                    CheckCategory.BEST_PRACTICE,
                    name,
                    f"{name} 值为 {value}，可能太小",
                    f"建议设置 >= {min_val}",
                    value
                )
    
    def _check_language_config(self, config: Dict[str, Any]):
        """检查语言配置"""
        target_langs = config.get('target_languages', [])
        source_lang = config.get('default_source_lang', '中文')
        supported_langs = config.get('supported_source_langs', [])
        
        # target_languages
        if not isinstance(target_langs, list):
            self._add_result(
                CheckLevel.ERROR,
                CheckCategory.SYNTAX,
                'target_languages',
                f"target_languages 应该是列表，当前类型：{type(target_langs).__name__}",
                "使用 YAML/JSON 列表格式"
            )
        elif len(target_langs) == 0:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.BEST_PRACTICE,
                'target_languages',
                "target_languages 为空，翻译时将无法选择目标语言",
                "至少添加一个目标语言"
            )
        
        # default_source_lang
        if not isinstance(source_lang, str) or not source_lang.strip():
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'default_source_lang',
                f"default_source_lang 应该是非空字符串，当前值：{source_lang}",
                "设置有效的语言名称"
            )
        
        # supported_source_langs
        if not isinstance(supported_langs, list):
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'supported_source_langs',
                f"supported_source_langs 应该是列表，当前类型：{type(supported_langs).__name__}",
                "使用 YAML/JSON 列表格式"
            )
    
    def _check_backup_config(self, config: Dict[str, Any]):
        """检查备份配置"""
        enable_vc = config.get('enable_version_control', False)
        enable_backup = config.get('enable_auto_backup', False)
        backup_dir = config.get('backup_dir', '.terminology_backups')
        backup_strategy = config.get('backup_strategy', 'daily')
        
        # 布尔值检查
        for name, value in [('enable_version_control', enable_vc),
                           ('enable_auto_backup', enable_backup)]:
            if not isinstance(value, bool):
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.SYNTAX,
                    name,
                    f"{name} 应该是布尔值，当前类型：{type(value).__name__}",
                    "设置为 true 或 false"
                )
        
        # backup_dir
        if not isinstance(backup_dir, str) or not backup_dir.strip():
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'backup_dir',
                f"backup_dir 应该是非空字符串，当前值：{backup_dir}",
                "设置有效的目录路径"
            )
        
        # backup_strategy
        valid_strategies = ['hourly', 'daily', 'weekly', 'per_batch']
        if isinstance(backup_strategy, str) and backup_strategy.lower() not in valid_strategies:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'backup_strategy',
                f"无效的备份策略：'{backup_strategy}'",
                f"有效值：{', '.join(valid_strategies)}",
                backup_strategy
            )
    
    def _check_monitor_config(self, config: Dict[str, Any]):
        """检查监控配置"""
        enable_monitor = config.get('enable_performance_monitor', False)
        sample_interval = config.get('perf_sample_interval', 1.0)
        history_size = config.get('perf_history_size', 300)
        
        # enable_performance_monitor
        if not isinstance(enable_monitor, bool):
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'enable_performance_monitor',
                f"enable_performance_monitor 应该是布尔值，当前类型：{type(enable_monitor).__name__}",
                "设置为 true 或 false"
            )
        
        # sample_interval
        if not isinstance(sample_interval, (int, float)) or sample_interval <= 0:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.RANGE,
                'perf_sample_interval',
                f"perf_sample_interval 必须是正数，当前值：{sample_interval}",
                "设置 > 0 的数值"
            )
        
        # history_size
        if not isinstance(history_size, int) or history_size < 10:
            self._add_result(
                CheckLevel.INFO,
                CheckCategory.PERFORMANCE,
                'perf_history_size',
                f"perf_history_size 值为 {history_size}，可能不足以分析趋势",
                "建议设置 >= 100",
                history_size
            )
    
    def _check_prompts(self, config: Dict[str, Any]):
        """检查提示词配置"""
        draft_prompt = config.get('draft_prompt', '')
        review_prompt = config.get('review_prompt', '')
        
        # draft_prompt
        if not isinstance(draft_prompt, str) or not draft_prompt.strip():
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.BEST_PRACTICE,
                'draft_prompt',
                "draft_prompt 为空，将使用默认提示词",
                "建议自定义提示词以获得更好的翻译效果"
            )
        else:
            # 检查占位符
            if '{target_lang}' not in draft_prompt:
                self._add_result(
                    CheckLevel.WARNING,
                    CheckCategory.SYNTAX,
                    'draft_prompt',
                    "draft_prompt 缺少 {target_lang} 占位符",
                    "在提示词中添加 {target_lang} 以指定目标语言"
                )
        
        # review_prompt
        if not isinstance(review_prompt, str) or not review_prompt.strip():
            self._add_result(
                CheckLevel.INFO,
                CheckCategory.BEST_PRACTICE,
                'review_prompt',
                "review_prompt 为空，将使用默认提示词",
                "如果启用双阶段模式，建议自定义校对提示词"
            )
        elif '{target_lang}' not in review_prompt:
            self._add_result(
                CheckLevel.WARNING,
                CheckCategory.SYNTAX,
                'review_prompt',
                "review_prompt 缺少 {target_lang} 占位符",
                "在提示词中添加 {target_lang} 以指定目标语言"
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取检查摘要
        
        Returns:
            包含统计信息的字典
        """
        errors = sum(1 for r in self.results if r.level == CheckLevel.ERROR)
        warnings = sum(1 for r in self.results if r.level == CheckLevel.WARNING)
        infos = sum(1 for r in self.results if r.level == CheckLevel.INFO)
        
        return {
            'total_issues': len(self.results),
            'errors': errors,
            'warnings': warnings,
            'infos': infos,
            'passed': errors == 0,
            'categories': {
                cat.value: sum(1 for r in self.results if r.category == cat)
                for cat in CheckCategory
            }
        }
    
    def print_report(self, show_all: bool = True):
        """
        打印检查报告
        
        Args:
            show_all: 是否显示所有结果（包括 INFO）
        """
        print("\n" + "="*70)
        print("📋 配置检查报告")
        print("="*70)
        
        summary = self.get_summary()
        print(f"\n总体状态：{'✅ 通过' if summary['passed'] else '❌ 未通过'}")
        print(f"发现问题：{summary['total_issues']} 个 "
              f"(错误：{summary['errors']}, 警告：{summary['warnings']}, 提示：{summary['infos']})")
        
        if not summary['passed']:
            print("\n⚠️  存在致命错误，请务必修复！")
        
        # 按类别分组显示
        for category in CheckCategory:
            category_results = [r for r in self.results if r.category == category]
            if not category_results:
                continue
            
            print(f"\n【{category.value.upper()}】")
            print("-"*70)
            
            for result in category_results:
                if result.level == CheckLevel.INFO and not show_all:
                    continue
                
                icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[result.level.value]
                print(f"\n{icon} [{result.key}]")
                print(f"   问题：{result.message}")
                if result.suggestion:
                    print(f"   建议：{result.suggestion}")
                if result.value is not None:
                    print(f"   当前值：{result.value}")
        
        print("\n" + "="*70)


def check_config(config: Dict[str, Any], verbose: bool = True) -> Tuple[bool, List[CheckResult]]:
    """
    便捷函数：检查配置并返回结果
    
    Args:
        config: 配置字典
        verbose: 是否打印详细报告
        
    Returns:
        (是否通过，检查结果列表)
    """
    checker = ConfigChecker()
    results = checker.check(config)
    
    if verbose:
        checker.print_report()
    
    return checker.get_summary()['passed'], results


def validate_config(config: Dict[str, Any], raise_on_error: bool = True) -> bool:
    """
    便捷函数：验证配置，如有错误则抛出异常
    
    Args:
        config: 配置字典
        raise_on_error: 发现错误时是否抛出异常
        
    Returns:
        配置是否有效
        
    Raises:
        ValueError: 当配置无效且 raise_on_error=True 时
    """
    passed, results = check_config(config, verbose=False)
    
    if not passed and raise_on_error:
        errors = [r for r in results if r.level == CheckLevel.ERROR]
        error_messages = [f"- {r.key}: {r.message}" for r in errors]
        raise ValueError(f"配置验证失败:\n" + "\n".join(error_messages))
    
    return passed


# 测试代码
if __name__ == "__main__":
    # 示例：测试配置检查
    test_config = {
        'api_key': '',  # 错误：空值
        'api_provider': 'invalid_provider',  # 警告：未知提供商
        'temperature': 3.0,  # 警告：超出范围
        'initial_concurrency': 0,  # 错误：无效值
        'max_concurrency': 5,  # 错误：小于 initial_concurrency
        'batch_size': -1,  # 错误：负值
        'log_level': 'INVALID',  # 警告：无效级别
        'target_languages': [],  # 警告：空列表
    }
    
    print("🧪 测试配置检查功能...\n")
    passed, results = check_config(test_config)
    
    print(f"\n测试结果：{'通过 ✅' if passed else '未通过 ❌'}")
    print(f"发现问题：{len(results)} 个")
    
    # 显示前 5 个问题
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. {result.level.value.upper()} - {result.key}")
        print(f"   {result.message}")
