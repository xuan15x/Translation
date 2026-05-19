"""
配置验证器模块
从 Config 类中拆分的验证逻辑，包含所有 _validate_* 方法
"""
from typing import Any, Dict, List
import os
import logging

from ..exceptions import ValidationError, AuthenticationError

logger = logging.getLogger(__name__)


def validate_config_post_init(config):
    """Config __post_init__ 入口"""
    from infrastructure.logging import LoggerSlice, LogCategory
    if not hasattr(config, '_logger_slice'):
        from infrastructure.logging import LoggerSlice, LogCategory
        config._logger_slice = LoggerSlice(config.LOG_CATEGORY)

    config.log_info("Config 初始化", api_key_set=bool(config.api_key), provider=config.api_provider)

    # 从 api_keys 旧结构兼容读取（向下兼容）
    if not config.api_key and hasattr(config, 'api_keys') and config.api_keys:
        api_keys_dict = config.api_keys
        provider = config.api_provider or 'deepseek'
        if provider in api_keys_dict:
            provider_config = api_keys_dict[provider]
            if isinstance(provider_config, dict):
                config.api_key = provider_config.get('api_key', '')
                if not config.base_url or config.base_url == "https://api.deepseek.com":
                    new_base_url = provider_config.get('base_url', '')
                    if new_base_url:
                        config.base_url = new_base_url
                config.log_info(f"从 api_keys.{provider}.api_key 读取 API Key")

    test_mode = os.getenv('TEST_MODE', '').lower()
    skip_all_checks = test_mode == 'skip_all'

    if skip_all_checks:
        config.log_warning("测试模式：跳过所有配置验证（仅限测试环境）")
    else:
        if not config.api_key or not config.api_key.strip():
            config.log_error("API 密钥不能为空")
            raise AuthenticationError("API 密钥不能为空，请在 config.json 中设置 api_key。")

        _track_config_usage(config)
        _run_full_validation(config)

    config.log_debug(f"Config 参数：base_url={config.base_url}, model={config.model_name}, provider={config.api_provider}")
    config.log_debug(f"Draft 模型：{config.get_draft_model_name()}, temperature={config.get_draft_temperature()}")
    config.log_debug(f"Review 模型：{config.get_review_model_name()}, temperature={config.get_review_temperature()}")


def _track_config_usage(config):
    """跟踪配置使用情况"""
    config.log_debug(
        "配置使用跟踪",
        provider=config.api_provider,
        model=config.model_name,
        concurrency=config.initial_concurrency,
        batch_size=config.batch_size
    )


def _run_full_validation(config):
    """运行全部验证"""
    errors = []
    errors.extend(_validate_api_config(config))
    errors.extend(_validate_model_params(config))
    errors.extend(_validate_dual_stage_params(config))
    errors.extend(_validate_concurrency(config))
    errors.extend(_validate_workflow(config))
    errors.extend(_validate_terminology(config))
    errors.extend(_validate_performance(config))
    errors.extend(_validate_log(config))
    errors.extend(_validate_language(config))
    errors.extend(_validate_backup(config))
    errors.extend(_validate_monitor(config))
    errors.extend(_validate_prompts(config))
    errors.extend(_validate_thinking(config))

    if errors:
        error_message = _format_validation_errors(errors)
        raise ValidationError(
            message=f"配置验证失败：共发现 {len(errors)} 个错误",
            field_name='config_validation',
            details={
                'total_errors': len(errors),
                'errors': errors,
                'error_summary': error_message
            }
        )


def _format_validation_errors(errors: list) -> str:
    """格式化验证错误"""
    return "\n".join(
        f"[{e['check_point']}] {e['field']}: {e['error']}\n  -> 当前值: {e['current_value']}\n  -> 要求: {e['requirement']}\n  -> 解决方案: {e['solution']}"
        for e in errors
    )


def _validate_api_config(config) -> list:
    errors = []
    if not config.api_key or not config.api_key.strip():
        errors.append({
            'field': 'api_key', 'error': 'API 密钥不能为空',
            'check_point': 'API 认证配置', 'current_value': '(空)',
            'requirement': '必须设置有效的 API 密钥',
            'solution': '请检查 api_key 格式，确保为有效的 DeepSeek API 密钥（sk- 开头）'
        })
    valid_providers = ['deepseek']
    if config.api_provider not in valid_providers:
        errors.append({
            'field': 'api_provider', 'error': f'api_provider "{config.api_provider}" 无效',
            'check_point': 'API 提供商选择', 'current_value': config.api_provider,
            'requirement': '只支持 deepseek',
            'solution': '请将 api_provider 设置为 "deepseek"'
        })
    if not config.base_url or not config.base_url.strip():
        errors.append({
            'field': 'base_url', 'error': 'API Base URL 不能为空',
            'check_point': 'API 端点配置', 'current_value': repr(config.base_url),
            'requirement': '必须设置有效的 API 端点 URL',
            'solution': '"base_url": "https://api.deepseek.com"'
        })
    elif not config.base_url.startswith(('http://', 'https://')):
        errors.append({
            'field': 'base_url', 'error': 'URL 格式错误',
            'check_point': 'URL 格式验证', 'current_value': config.base_url,
            'requirement': 'URL 必须以 http:// 或 https:// 开头',
            'solution': '修正为："https://api.deepseek.com"'
        })
    return errors


def _validate_model_params(config) -> list:
    errors = []
    if not isinstance(config.model_name, str) or not config.model_name.strip():
        errors.append({
            'field': 'model_name', 'error': '模型名称不能为空',
            'check_point': '模型标识配置', 'current_value': repr(config.model_name),
            'requirement': '必须指定有效的模型名称',
            'solution': '"model_name": "deepseek-chat"'
        })
    if not (0 <= config.temperature <= 2):
        errors.append({
            'field': 'temperature', 'error': f'temperature {config.temperature} 超出范围',
            'check_point': '模型温度参数', 'current_value': config.temperature,
            'requirement': '必须在 0 到 2 之间（推荐：0.3-0.5）',
            'solution': '建议设置为 0.3'
        })
    if not (0 <= config.top_p <= 1):
        errors.append({
            'field': 'top_p', 'error': f'top_p {config.top_p} 超出范围',
            'check_point': '核采样参数', 'current_value': config.top_p,
            'requirement': '必须在 0 到 1 之间（推荐：0.8-0.9）',
            'solution': '建议设置为 0.8'
        })
    if config.timeout < 1:
        errors.append({
            'field': 'timeout', 'error': f'timeout {config.timeout}秒 太短',
            'check_point': '超时时间配置', 'current_value': f'{config.timeout}秒',
            'requirement': '必须 >= 1 秒（推荐：30-120 秒）',
            'solution': '建议设置为 60 秒'
        })
    if config.max_retries < 0:
        errors.append({
            'field': 'max_retries', 'error': f'max_retries {config.max_retries} 无效',
            'check_point': '重试次数配置', 'current_value': config.max_retries,
            'requirement': '必须 >= 0（推荐：2-5 次）',
            'solution': '建议设置为 3 次'
        })
    return errors


def _validate_dual_stage_params(config) -> list:
    errors = []
    if config.draft_temperature is not None and not (0 <= config.draft_temperature <= 2):
        errors.append({
            'field': 'draft_temperature', 'error': f'draft_temperature {config.draft_temperature} 超出范围',
            'check_point': '初译阶段温度参数', 'current_value': config.draft_temperature,
            'requirement': '0-2 之间（推荐 0.3-0.4）',
            'solution': '初译建议使用较低温度（如 0.3）'
        })
    if config.draft_top_p is not None and not (0 <= config.draft_top_p <= 1):
        errors.append({
            'field': 'draft_top_p', 'error': f'draft_top_p {config.draft_top_p} 超出范围',
            'check_point': '初译核采样参数', 'current_value': config.draft_top_p,
            'requirement': '0-1 之间（推荐 0.8）',
            'solution': '初译建议使用 0.8'
        })
    if config.draft_max_tokens < 100:
        errors.append({
            'field': 'draft_max_tokens', 'error': f'draft_max_tokens {config.draft_max_tokens} 过小',
            'check_point': '初译输出长度限制', 'current_value': config.draft_max_tokens,
            'requirement': '>= 100（推荐 512-1024）',
            'solution': '建议设置为 512'
        })
    if config.review_temperature is not None and not (0 <= config.review_temperature <= 2):
        errors.append({
            'field': 'review_temperature', 'error': f'review_temperature {config.review_temperature} 超出范围',
            'check_point': '校对阶段温度参数', 'current_value': config.review_temperature,
            'requirement': '0-2 之间（推荐 0.5-0.7）',
            'solution': '校对建议使用 0.5-0.7'
        })
    if config.review_top_p is not None and not (0 <= config.review_top_p <= 1):
        errors.append({
            'field': 'review_top_p', 'error': f'review_top_p {config.review_top_p} 超出范围',
            'check_point': '校对核采样参数', 'current_value': config.review_top_p,
            'requirement': '0-1 之间（推荐 0.9）',
            'solution': '校对建议使用 0.9'
        })
    if config.review_max_tokens < 100:
        errors.append({
            'field': 'review_max_tokens', 'error': f'review_max_tokens {config.review_max_tokens} 过小',
            'check_point': '校对输出长度限制', 'current_value': config.review_max_tokens,
            'requirement': '>= 100（推荐 512-1024）',
            'solution': '建议设置为 512'
        })
    return errors


def _validate_concurrency(config) -> list:
    errors = []
    if config.initial_concurrency < 1:
        errors.append({
            'field': 'initial_concurrency', 'error': f'initial_concurrency {config.initial_concurrency} 无效',
            'check_point': '初始并发数', 'current_value': config.initial_concurrency,
            'requirement': '>= 1（推荐 2-10）',
            'solution': '新手从 2 开始'
        })
    if config.max_concurrency < config.initial_concurrency:
        errors.append({
            'field': 'max_concurrency', 'error': f'max({config.max_concurrency}) < initial({config.initial_concurrency})',
            'check_point': '并发上限逻辑校验', 'current_value': f'max={config.max_concurrency}, initial={config.initial_concurrency}',
            'requirement': 'max_concurrency >= initial_concurrency',
            'solution': f'请将 max_concurrency 设置为 >= {config.initial_concurrency}'
        })
    if config.concurrency_cooldown_seconds < 0:
        errors.append({
            'field': 'concurrency_cooldown_seconds', 'error': f'cooldown {config.concurrency_cooldown_seconds}秒 无效',
            'check_point': '并发冷却时间', 'current_value': f'{config.concurrency_cooldown_seconds}秒',
            'requirement': '>= 0（推荐 3.0-10.0 秒）',
            'solution': '建议设置为 5.0 秒'
        })
    return errors


def _validate_workflow(config) -> list:
    errors = []
    if config.batch_size < 1:
        errors.append({
            'field': 'batch_size', 'error': f'batch_size {config.batch_size} 无效',
            'check_point': '批处理大小', 'current_value': config.batch_size,
            'requirement': '>= 1（推荐 500-2000）',
            'solution': '建议设置为 1000'
        })
    if config.gc_interval < 0:
        errors.append({
            'field': 'gc_interval', 'error': f'gc_interval {config.gc_interval} 无效',
            'check_point': '垃圾回收间隔', 'current_value': config.gc_interval,
            'requirement': '>= 0（推荐 2-5）',
            'solution': '建议每 2 个任务执行一次 GC'
        })
    return errors


def _validate_terminology(config) -> list:
    errors = []
    if not (0 <= config.similarity_low <= 100):
        errors.append({
            'field': 'similarity_low', 'error': f'similarity_low {config.similarity_low} 超出范围',
            'check_point': '模糊匹配阈值', 'current_value': config.similarity_low,
            'requirement': '0-100（推荐 60-70）',
            'solution': '建议设置为 60'
        })
    if config.exact_match_score != 100:
        errors.append({
            'field': 'exact_match_score', 'error': f'exact_match_score {config.exact_match_score} 不推荐',
            'check_point': '精确匹配置信度', 'current_value': config.exact_match_score,
            'requirement': '强烈建议 100',
            'solution': '精确匹配使用满分 100'
        })
    if config.multiprocess_threshold < 100:
        errors.append({
            'field': 'multiprocess_threshold', 'error': f'multiprocess_threshold {config.multiprocess_threshold} 过小',
            'check_point': '多进程阈值', 'current_value': config.multiprocess_threshold,
            'requirement': '>= 100（推荐 1000-2000）',
            'solution': '建议设置为 1000'
        })
    return errors


def _validate_performance(config) -> list:
    errors = []
    if config.pool_size < 1:
        errors.append({
            'field': 'pool_size', 'error': f'pool_size {config.pool_size} 无效',
            'check_point': '数据库连接池大小', 'current_value': config.pool_size,
            'requirement': '>= 1（推荐 5-10）',
            'solution': '建议设置为 5'
        })
    if config.cache_capacity < 100:
        errors.append({
            'field': 'cache_capacity', 'error': f'cache_capacity {config.cache_capacity} 过小',
            'check_point': '缓存容量', 'current_value': config.cache_capacity,
            'requirement': '>= 100（推荐 2000-5000）',
            'solution': '建议设置为 2000'
        })
    if config.cache_ttl_seconds < 0:
        errors.append({
            'field': 'cache_ttl_seconds', 'error': f'cache_ttl {config.cache_ttl_seconds}秒 无效',
            'check_point': '缓存过期时间', 'current_value': f'{config.cache_ttl_seconds}秒',
            'requirement': '>= 0（0=永不过期，推荐 3600）',
            'solution': '建议 3600 秒'
        })
    return errors


def _validate_log(config) -> list:
    errors = []
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config.log_level not in valid_levels:
        errors.append({
            'field': 'log_level', 'error': f'log_level "{config.log_level}" 无效',
            'check_point': '日志级别', 'current_value': config.log_level,
            'requirement': f'须为：{valid_levels}',
            'solution': '建议 "INFO"'
        })
    valid_granularities = ['minimal', 'basic', 'normal', 'detailed', 'verbose']
    if config.log_granularity not in valid_granularities:
        errors.append({
            'field': 'log_granularity', 'error': f'log_granularity "{config.log_granularity}" 无效',
            'check_point': '日志粒度', 'current_value': config.log_granularity,
            'requirement': f'须为：{valid_granularities}',
            'solution': '建议 "normal"'
        })
    if config.log_max_lines < 100:
        errors.append({
            'field': 'log_max_lines', 'error': f'log_max_lines {config.log_max_lines} 过小',
            'check_point': '日志行数', 'current_value': config.log_max_lines,
            'requirement': '>= 100（推荐 1000-5000）',
            'solution': '建议 1000 行'
        })
    return errors


def _validate_language(config) -> list:
    errors = []
    if not config.default_source_lang or not config.default_source_lang.strip():
        errors.append({
            'field': 'default_source_lang', 'error': '默认源语言不能为空',
            'check_point': '默认源语言', 'current_value': repr(config.default_source_lang),
            'requirement': '必须设置有效语言名称',
            'solution': '示例："中文"'
        })
    if not isinstance(config.supported_source_langs, list) or len(config.supported_source_langs) == 0:
        errors.append({
            'field': 'supported_source_langs', 'error': '支持语言列表不能为空',
            'check_point': '支持语言列表', 'current_value': config.supported_source_langs,
            'requirement': '须包含至少一种语言',
            'solution': '示例：["中文"]'
        })
    return errors


def _validate_backup(config) -> list:
    errors = []
    if config.enable_auto_backup and not config.backup_dir:
        errors.append({
            'field': 'backup_dir', 'error': '启用自动备份时必须指定 backup_dir',
            'check_point': '备份目录', 'current_value': repr(config.backup_dir),
            'requirement': 'enable_auto_backup=true 时需有效的 backup_dir',
            'solution': '示例：".terminology_backups"'
        })
    valid_strategies = ['hourly', 'daily', 'weekly', 'per_batch']
    if config.enable_auto_backup and config.backup_strategy not in valid_strategies:
        errors.append({
            'field': 'backup_strategy', 'error': f'backup_strategy "{config.backup_strategy}" 无效',
            'check_point': '备份策略', 'current_value': config.backup_strategy,
            'requirement': f'须为：{valid_strategies}',
            'solution': '建议 "daily"'
        })
    return errors


def _validate_monitor(config) -> list:
    errors = []
    if config.enable_performance_monitor:
        if config.perf_sample_interval <= 0:
            errors.append({
                'field': 'perf_sample_interval', 'error': f'sample_interval {config.perf_sample_interval} 无效',
                'check_point': '性能采样间隔', 'current_value': f'{config.perf_sample_interval}秒',
                'requirement': '> 0（推荐 1.0-5.0 秒）',
                'solution': '建议 1.0 秒'
            })
        if config.perf_history_size < 10:
            errors.append({
                'field': 'perf_history_size', 'error': f'history_size {config.perf_history_size} 过小',
                'check_point': '历史记录大小', 'current_value': config.perf_history_size,
                'requirement': '>= 10（推荐 300-500）',
                'solution': '建议 300'
            })
    return errors


def _validate_prompts(config) -> list:
    errors = []
    if not config.draft_prompt or not config.draft_prompt.strip():
        errors.append({
            'field': 'draft_prompt', 'error': '初译提示词不能为空',
            'check_point': 'Draft Prompt', 'current_value': '(空)',
            'requirement': '须含有效提示词模板',
            'solution': '须含 {target_lang} 和 JSON 输出格式要求'
        })
    elif '{target_lang}' not in config.draft_prompt:
        errors.append({
            'field': 'draft_prompt', 'error': '缺少 {target_lang} 占位符',
            'check_point': 'Prompt 变量占位符', 'current_value': config.draft_prompt[:100] + '...',
            'requirement': '须含 {target_lang}',
            'solution': '添加 "Translate to {target_lang}"'
        })
    if not config.review_prompt or not config.review_prompt.strip():
        errors.append({
            'field': 'review_prompt', 'error': '校对提示词不能为空',
            'check_point': 'Review Prompt', 'current_value': '(空)',
            'requirement': '须含有效提示词模板',
            'solution': '须含 {target_lang} 和 Reason 字段要求'
        })
    elif '{target_lang}' not in config.review_prompt:
        errors.append({
            'field': 'review_prompt', 'error': '缺少 {target_lang} 占位符',
            'check_point': 'Prompt 变量占位符', 'current_value': config.review_prompt[:100] + '...',
            'requirement': '须含 {target_lang}',
            'solution': '添加 "Polish into {target_lang}"'
        })
    return errors


def _validate_thinking(config) -> list:
    """验证思考模式配置"""
    errors = []
    valid_efforts = ["low", "high", "max"]
    if config.enable_thinking_mode and config.thinking_effort not in valid_efforts:
        errors.append({
            'field': 'thinking_effort', 'error': f'思考强度 "{config.thinking_effort}" 无效',
            'check_point': '思考模式强度', 'current_value': config.thinking_effort,
            'requirement': f'须为：{valid_efforts}',
            'solution': '建议 "high" 或 "max"'
        })
    if config.enable_thinking_mode and hasattr(config, 'model_name') and config.model_name and 'deepseek-v4' not in config.model_name:
        # 默认值 deepseek-chat 视为可接受（可通过配置文件更改）
        if config.model_name not in ('deepseek-chat',):
            errors.append({
                'field': 'model_name', 'error': '思考模式仅支持 deepseek-v4 系列模型，当前模型不兼容',
                'check_point': '模型兼容性', 'current_value': config.model_name,
                'requirement': '启用思考模式时须使用 deepseek-v4 模型',
                'solution': '请将 model_name 改为 "deepseek-v4-pro"'
            })
    return errors
