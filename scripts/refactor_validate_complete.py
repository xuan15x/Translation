"""
完整重构_validate_config方法
将其拆分为13个子验证器方法
"""

# 新的_validate_config方法和所有子验证器
new_methods = '''
    def _validate_config(self):
        """验证配置参数的有效性 - 重构版，拆分为多个子验证器"""
        errors = []
        
        # 调用各个子验证器
        errors.extend(self._validate_api_config())
        errors.extend(self._validate_model_params())
        errors.extend(self._validate_dual_stage_params())
        errors.extend(self._validate_concurrency())
        errors.extend(self._validate_workflow())
        errors.extend(self._validate_terminology())
        errors.extend(self._validate_performance())
        errors.extend(self._validate_log())
        errors.extend(self._validate_gui())
        errors.extend(self._validate_language())
        errors.extend(self._validate_backup())
        errors.extend(self._validate_monitor())
        errors.extend(self._validate_prompts())

        # ========== 抛出所有验证错误 ==========
        if errors:
            error_message = self._format_validation_errors(errors)
            raise ValidationError(
                message=f"配置验证失败：共发现 {len(errors)} 个错误",
                field_name='config_validation',
                details={
                    'total_errors': len(errors),
                    'errors': errors,
                    'error_summary': error_message
                }
            )

    def _validate_api_config(self) -> list:
        """验证API基础配置"""
        errors = []

        if not self.api_key or not self.api_key.strip():
            errors.append({
                'field': 'api_key',
                'error': 'API 密钥不能为空',
                'check_point': 'API 认证配置',
                'current_value': '(空)' if not self.api_key else '***',
                'requirement': '必须设置有效的 API 密钥',
                'solution': '请通过以下方式设置：\\n'
                           '1. 配置文件：config.json 中设置 "api_key": "your-key"\\n'
                           '2. GUI 界面：在翻译平台界面中配置 API 密钥'
            })

        valid_providers = ['deepseek', 'openai', 'anthropic', 'moonshot', 'zhipu', 'baidu', 'alibaba', 'custom']
        if self.api_provider not in valid_providers:
            errors.append({
                'field': 'api_provider',
                'error': f'api_provider 值 "{self.api_provider}" 无效',
                'check_point': 'API 提供商选择',
                'current_value': self.api_provider,
                'requirement': f'必须是以下之一：{valid_providers}',
                'solution': f'建议使用 "deepseek" 或 "openai"，当前值：" {self.api_provider}"'
            })

        if not self.base_url or not self.base_url.strip():
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 不能为空',
                'check_point': 'API 端点配置',
                'current_value': repr(self.base_url),
                'requirement': '必须设置有效的 API 端点 URL',
                'solution': '示例："base_url": "https://api.deepseek.com"'
            })
        elif not self.base_url.startswith(('http://', 'https://')):
            errors.append({
                'field': 'base_url',
                'error': 'API Base URL 格式错误',
                'check_point': 'URL 格式验证',
                'current_value': self.base_url,
                'requirement': 'URL 必须以 http:// 或 https:// 开头',
                'solution': '修正为："https://api.deepseek.com" 或 "http://localhost:8000"'
            })

        return errors

    def _validate_model_params(self) -> list:
        """验证全局模型参数"""
        errors = []

        if not isinstance(self.model_name, str) or not self.model_name.strip():
            errors.append({
                'field': 'model_name',
                'error': '模型名称不能为空字符串',
                'check_point': '模型标识配置',
                'current_value': repr(self.model_name),
                'requirement': '必须指定有效的模型名称',
                'solution': '示例："model_name": "deepseek-chat" 或 "gpt-4"'
            })

        if not (0 <= self.temperature <= 2):
            errors.append({
                'field': 'temperature',
                'error': f'temperature 值 {self.temperature} 超出有效范围',
                'check_point': '模型温度参数',
                'current_value': self.temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.5）',
                'solution': f'建议设置为 0.3（保守翻译）或 0.5（平衡翻译），当前值：{self.temperature}'
            })

        if not (0 <= self.top_p <= 1):
            errors.append({
                'field': 'top_p',
                'error': f'top_p 值 {self.top_p} 超出有效范围',
                'check_point': '核采样参数',
                'current_value': self.top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8-0.9）',
                'solution': f'建议设置为 0.8（稳定）或 0.9（灵活），当前值：{self.top_p}'
            })

        if self.timeout < 1:
            errors.append({
                'field': 'timeout',
                'error': f'timeout 值 {self.timeout} 秒太短',
                'check_point': '超时时间配置',
                'current_value': f'{self.timeout}秒',
                'requirement': '必须 >= 1 秒（推荐值：30-120 秒）',
                'solution': f'建议设置为 60 秒（中等文本）或 90 秒（长文本），当前值：{self.timeout}秒'
            })

        if self.max_retries < 0:
            errors.append({
                'field': 'max_retries',
                'error': f'max_retries 值 {self.max_retries} 无效',
                'check_point': '重试次数配置',
                'current_value': self.max_retries,
                'requirement': '必须 >= 0（推荐值：2-5 次）',
                'solution': f'建议设置为 3 次，当前值：{self.max_retries}'
            })

        return errors

    def _validate_dual_stage_params(self) -> list:
        """验证双阶段参数"""
        errors = []

        # Draft 阶段参数
        if self.draft_temperature is not None and not (0 <= self.draft_temperature <= 2):
            errors.append({
                'field': 'draft_temperature',
                'error': f'draft_temperature 值 {self.draft_temperature} 超出范围',
                'check_point': '初译阶段温度参数',
                'current_value': self.draft_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.3-0.4）',
                'solution': f'初译建议使用较低温度（如 0.3）以保证准确性，当前值：{self.draft_temperature}'
            })

        if self.draft_top_p is not None and not (0 <= self.draft_top_p <= 1):
            errors.append({
                'field': 'draft_top_p',
                'error': f'draft_top_p 值 {self.draft_top_p} 超出范围',
                'check_point': '初译阶段核采样参数',
                'current_value': self.draft_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.8）',
                'solution': f'初译建议使用较保守的 top_p（如 0.8），当前值：{self.draft_top_p}'
            })

        if self.draft_max_tokens < 100:
            errors.append({
                'field': 'draft_max_tokens',
                'error': f'draft_max_tokens 值 {self.draft_max_tokens} 过小',
                'check_point': '初译输出长度限制',
                'current_value': self.draft_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长句子的翻译，当前值：{self.draft_max_tokens}'
            })

        # Review 阶段参数
        if self.review_temperature is not None and not (0 <= self.review_temperature <= 2):
            errors.append({
                'field': 'review_temperature',
                'error': f'review_temperature 值 {self.review_temperature} 超出范围',
                'check_point': '校对阶段温度参数',
                'current_value': self.review_temperature,
                'requirement': '必须在 0 到 2 之间（推荐值：0.5-0.7）',
                'solution': f'校对建议使用较高温度（如 0.5-0.7）以优化表达，当前值：{self.review_temperature}'
            })

        if self.review_top_p is not None and not (0 <= self.review_top_p <= 1):
            errors.append({
                'field': 'review_top_p',
                'error': f'review_top_p 值 {self.review_top_p} 超出范围',
                'check_point': '校对阶段核采样参数',
                'current_value': self.review_top_p,
                'requirement': '必须在 0 到 1 之间（推荐值：0.9）',
                'solution': f'校对建议使用较灵活的 top_p（如 0.9），当前值：{self.review_top_p}'
            })

        if self.review_max_tokens < 100:
            errors.append({
                'field': 'review_max_tokens',
                'error': f'review_max_tokens 值 {self.review_max_tokens} 过小',
                'check_point': '校对输出长度限制',
                'current_value': self.review_max_tokens,
                'requirement': '必须 >= 100（推荐值：512-1024）',
                'solution': f'建议设置为 512 以支持较长的润色说明，当前值：{self.review_max_tokens}'
            })

        return errors

    def _validate_concurrency(self) -> list:
        """验证并发控制配置"""
        errors = []

        if self.initial_concurrency < 1:
            errors.append({
                'field': 'initial_concurrency',
                'error': f'initial_concurrency 值 {self.initial_concurrency} 无效',
                'check_point': '初始并发数配置',
                'current_value': self.initial_concurrency,
                'requirement': '必须 >= 1（推荐值：2-10）',
                'solution': f'建议根据 API 限流情况设置，新手从 2 开始，当前值：{self.initial_concurrency}'
            })

        if self.max_concurrency < self.initial_concurrency:
            errors.append({
                'field': 'max_concurrency',
                'error': f'max_concurrency ({self.max_concurrency}) < initial_concurrency ({self.initial_concurrency})',
                'check_point': '并发上限逻辑校验',
                'current_value': f'max={self.max_concurrency}, initial={self.initial_concurrency}',
                'requirement': 'max_concurrency 必须 >= initial_concurrency',
                'solution': f'请将 max_concurrency 设置为 >= {self.initial_concurrency} 的值'
            })

        if self.concurrency_cooldown_seconds < 0:
            errors.append({
                'field': 'concurrency_cooldown_seconds',
                'error': f'concurrency_cooldown_seconds 值 {self.concurrency_cooldown_seconds} 无效',
                'check_point': '并发冷却时间配置',
                'current_value': f'{self.concurrency_cooldown_seconds}秒',
                'requirement': '必须 >= 0（推荐值：3.0-10.0 秒）',
                'solution': f'建议设置为 5.0 秒，API 限流严重时增加到 10.0 秒，当前值：{self.concurrency_cooldown_seconds}秒'
            })

        return errors

    def _validate_workflow(self) -> list:
        """验证工作流配置"""
        errors = []

        if self.batch_size < 1:
            errors.append({
                'field': 'batch_size',
                'error': f'batch_size 值 {self.batch_size} 无效',
                'check_point': '批处理大小配置',
                'current_value': self.batch_size,
                'requirement': '必须 >= 1（推荐值：500-2000）',
                'solution': f'建议设置为 1000，内存充足可设为 2000，当前值：{self.batch_size}'
            })

        if self.gc_interval < 0:
            errors.append({
                'field': 'gc_interval',
                'error': f'gc_interval 值 {self.gc_interval} 无效',
                'check_point': '垃圾回收间隔配置',
                'current_value': self.gc_interval,
                'requirement': '必须 >= 0（推荐值：2-5）',
                'solution': f'建议每 2 个任务执行一次 GC，当前值：{self.gc_interval}'
            })

        return errors

    def _validate_terminology(self) -> list:
        """验证术语库配置"""
        errors = []

        if not (0 <= self.similarity_low <= 100):
            errors.append({
                'field': 'similarity_low',
                'error': f'similarity_low 值 {self.similarity_low} 超出范围',
                'check_point': '模糊匹配阈值配置',
                'current_value': self.similarity_low,
                'requirement': '必须在 0 到 100 之间（推荐值：60-70）',
                'solution': f'建议设置为 60（平衡）或 70（严格），当前值：{self.similarity_low}'
            })

        if self.exact_match_score != 100:
            errors.append({
                'field': 'exact_match_score',
                'error': f'exact_match_score 值 {self.exact_match_score} 不推荐',
                'check_point': '精确匹配置信度',
                'current_value': self.exact_match_score,
                'requirement': '强烈建议设置为 100',
                'solution': '精确匹配应该使用满分 100 分，不建议修改'
            })

        if self.multiprocess_threshold < 100:
            errors.append({
                'field': 'multiprocess_threshold',
                'error': f'multiprocess_threshold 值 {self.multiprocess_threshold} 过小',
                'check_point': '多进程处理阈值',
                'current_value': self.multiprocess_threshold,
                'requirement': '必须 >= 100（推荐值：1000-2000）',
                'solution': f'术语库少于 1000 条时使用单进程，超过使用多进程，当前阈值：{self.multiprocess_threshold}'
            })

        return errors

    def _validate_performance(self) -> list:
        """验证性能配置"""
        errors = []

        if self.pool_size < 1:
            errors.append({
                'field': 'pool_size',
                'error': f'pool_size 值 {self.pool_size} 无效',
                'check_point': '数据库连接池大小',
                'current_value': self.pool_size,
                'requirement': '必须 >= 1（推荐值：5-10）',
                'solution': f'建议设置为 5，高并发场景可设为 10，当前值：{self.pool_size}'
            })

        if self.cache_capacity < 100:
            errors.append({
                'field': 'cache_capacity',
                'error': f'cache_capacity 值 {self.cache_capacity} 过小',
                'check_point': '缓存容量配置',
                'current_value': self.cache_capacity,
                'requirement': '必须 >= 100（推荐值：2000-5000）',
                'solution': f'建议根据术语库大小设置，至少 2000，当前值：{self.cache_capacity}'
            })

        if self.cache_ttl_seconds < 0:
            errors.append({
                'field': 'cache_ttl_seconds',
                'error': f'cache_ttl_seconds 值 {self.cache_ttl_seconds} 无效',
                'check_point': '缓存过期时间配置',
                'current_value': f'{self.cache_ttl_seconds}秒',
                'requirement': '必须 >= 0（0 表示永不过期，推荐值：3600）',
                'solution': f'建议设置为 3600 秒（1 小时）或 0（永不过期），当前值：{self.cache_ttl_seconds}秒'
            })

        return errors

    def _validate_log(self) -> list:
        """验证日志配置"""
        errors = []

        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            errors.append({
                'field': 'log_level',
                'error': f'log_level 值 "{self.log_level}" 无效',
                'check_point': '日志级别配置',
                'current_value': self.log_level,
                'requirement': f'必须是以下之一：{valid_log_levels}',
                'solution': f'建议设置为 "INFO"（常规）或 "DEBUG"（调试），当前值："{self.log_level}"'
            })

        valid_log_granularities = ['minimal', 'basic', 'normal', 'detailed', 'verbose']
        if self.log_granularity not in valid_log_granularities:
            errors.append({
                'field': 'log_granularity',
                'error': f'log_granularity 值 "{self.log_granularity}" 无效',
                'check_point': '日志粒度配置',
                'current_value': self.log_granularity,
                'requirement': f'必须是以下之一：{valid_log_granularities}',
                'solution': f'建议设置为 "normal"（常规）或 "detailed"（详细），当前值："{self.log_granularity}"'
            })

        if self.log_max_lines < 100:
            errors.append({
                'field': 'log_max_lines',
                'error': f'log_max_lines 值 {self.log_max_lines} 过小',
                'check_point': 'GUI 日志行数限制',
                'current_value': self.log_max_lines,
                'requirement': '必须 >= 100（推荐值：1000-5000）',
                'solution': f'建议设置为 1000 行，需要完整日志可设为 5000，当前值：{self.log_max_lines}'
            })

        return errors

    def _validate_gui(self) -> list:
        """验证GUI配置"""
        errors = []

        if self.gui_window_width < 400:
            errors.append({
                'field': 'gui_window_width',
                'error': f'gui_window_width 值 {self.gui_window_width} 过小',
                'check_point': 'GUI 窗口宽度',
                'current_value': f'{self.gui_window_width}px',
                'requirement': '必须 >= 400（推荐值：950-1200）',
                'solution': f'建议设置为 950px 以获得良好体验，当前值：{self.gui_window_width}px'
            })

        if self.gui_window_height < 300:
            errors.append({
                'field': 'gui_window_height',
                'error': f'gui_window_height 值 {self.gui_window_height} 过小',
                'check_point': 'GUI 窗口高度',
                'current_value': f'{self.gui_window_height}px',
                'requirement': '必须 >= 300（推荐值：800-1000）',
                'solution': f'建议设置为 800px 以获得良好体验，当前值：{self.gui_window_height}px'
            })

        return errors

    def _validate_language(self) -> list:
        """验证语言配置"""
        errors = []

        if not self.default_source_lang or not self.default_source_lang.strip():
            errors.append({
                'field': 'default_source_lang',
                'error': '默认源语言不能为空',
                'check_point': '默认源语言配置',
                'current_value': repr(self.default_source_lang),
                'requirement': '必须设置有效的语言名称',
                'solution': '示例："中文"、"English"、"日本語"'
            })

        if not isinstance(self.supported_source_langs, list) or len(self.supported_source_langs) == 0:
            errors.append({
                'field': 'supported_source_langs',
                'error': '支持的语言列表不能为空',
                'check_point': '支持语言列表配置',
                'current_value': self.supported_source_langs,
                'requirement': '必须包含至少一种语言',
                'solution': '示例：["中文", "英语", "日语"]'
            })

        return errors

    def _validate_backup(self) -> list:
        """验证版本控制和备份配置"""
        errors = []

        if self.enable_auto_backup and not self.backup_dir:
            errors.append({
                'field': 'backup_dir',
                'error': '启用自动备份时必须指定 backup_dir',
                'check_point': '备份目录配置',
                'current_value': repr(self.backup_dir),
                'requirement': 'enable_auto_backup=true 时必须有有效的 backup_dir',
                'solution': '示例：".terminology_backups" 或 "/path/to/backups"'
            })

        valid_backup_strategies = ['hourly', 'daily', 'weekly', 'per_batch']
        if self.enable_auto_backup and self.backup_strategy not in valid_backup_strategies:
            errors.append({
                'field': 'backup_strategy',
                'error': f'backup_strategy 值 "{self.backup_strategy}" 无效',
                'check_point': '备份策略配置',
                'current_value': self.backup_strategy,
                'requirement': f'必须是以下之一：{valid_backup_strategies}',
                'solution': f'建议使用 "daily"（每日备份）或 "per_batch"（每批次备份），当前值："{self.backup_strategy}"'
            })

        return errors

    def _validate_monitor(self) -> list:
        """验证性能监控配置"""
        errors = []

        if self.enable_performance_monitor:
            if self.perf_sample_interval <= 0:
                errors.append({
                    'field': 'perf_sample_interval',
                    'error': f'perf_sample_interval 值 {self.perf_sample_interval} 无效',
                    'check_point': '性能采样间隔',
                    'current_value': f'{self.perf_sample_interval}秒',
                    'requirement': '必须 > 0（推荐值：1.0-5.0 秒）',
                    'solution': f'建议设置为 1.0 秒，当前值：{self.perf_sample_interval}秒'
                })

            if self.perf_history_size < 10:
                errors.append({
                    'field': 'perf_history_size',
                    'error': f'perf_history_size 值 {self.perf_history_size} 过小',
                    'check_point': '性能历史记录大小',
                    'current_value': self.perf_history_size,
                    'requirement': '必须 >= 10（推荐值：300-500）',
                    'solution': f'建议设置为 300 以保留足够历史数据，当前值：{self.perf_history_size}'
                })

        return errors

    def _validate_prompts(self) -> list:
        """验证提示词配置"""
        errors = []

        if not self.draft_prompt or not self.draft_prompt.strip():
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词不能为空',
                'check_point': 'Draft Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 JSON 输出格式要求'
            })
        elif '{target_lang}' not in self.draft_prompt:
            errors.append({
                'field': 'draft_prompt',
                'error': '初译提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.draft_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Translate to {target_lang}"'
            })

        if not self.review_prompt or not self.review_prompt.strip():
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词不能为空',
                'check_point': 'Review Prompt 配置',
                'current_value': '(空)',
                'requirement': '必须包含有效的提示词模板',
                'solution': '必须包含 {target_lang} 占位符和 Reason 字段要求'
            })
        elif '{target_lang}' not in self.review_prompt:
            errors.append({
                'field': 'review_prompt',
                'error': '校对提示词缺少必需的 {target_lang} 占位符',
                'check_point': 'Prompt 变量占位符检查',
                'current_value': self.review_prompt[:100] + '...',
                'requirement': '提示词必须包含 {target_lang} 占位符',
                'solution': '在提示词中添加 "Polish into {target_lang}"'
            })

        return errors
'''

# 读取文件
with open('infrastructure/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到_validate_config方法的起始和结束位置
import re

# 找到_validate_config的定义
match = re.search(r'\n    def _validate_config\(self\):', content)
if match:
    start_pos = match.start()
    
    # 找到下一个方法的定义
    next_method = re.search(r'\n    def [a-z_]+\(', content[start_pos + 1:])
    if next_method:
        end_pos = start_pos + 1 + next_method.start()
        
        # 替换整个_validate_config方法
        new_content = content[:start_pos] + '\n' + new_methods + '\n' + content[end_pos:]
        
        # 保存
        with open('infrastructure/models.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ _validate_config方法重构完成")
        print(f"   - 删除了 {end_pos - start_pos} 字符的旧代码")
        print(f"   - 添加了 {len(new_methods)} 字符的新代码")
        print(f"   - 拆分为 13 个子验证器方法")
    else:
        print("❌ 未找到下一个方法")
else:
    print("❌ 未找到_validate_config方法")
