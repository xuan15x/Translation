"""
配置打点上报模块

用于收集和上报配置使用情况、验证错误、性能指标等数据，
帮助发现配置问题、优化默认值、提供精准帮助。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ConfigMetrics:
    """配置指标收集器"""
    
    def __init__(self, metrics_dir: str = ".config_metrics"):
        """
        初始化配置指标收集器
        
        Args:
            metrics_dir: 指标文件存储目录
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        
        # 指标数据
        self.validation_errors = defaultdict(int)  # 验证错误统计
        self.config_usage = defaultdict(int)  # 配置使用统计
        self.error_hotspots = defaultdict(int)  # 错误热力图
        self.performance_metrics = []  # 性能指标
        
        # 会话 ID（匿名）
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def record_validation_error(self, field: str, error_type: str, 
                                check_point: str, value: Any):
        """
        记录配置验证错误
        
        Args:
            field: 字段名称
            error_type: 错误类型
            check_point: 检查点
            value: 当前值
        """
        error_key = f"{field}:{error_type}"
        self.validation_errors[error_key] += 1
        self.error_hotspots[check_point] += 1
        
        # 记录详细错误信息
        error_detail = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'field': field,
            'error_type': error_type,
            'check_point': check_point,
            'value': str(value)[:100],  # 截断长值
        }
        
        # 写入详细日志文件
        self._write_error_log(error_detail)
        
        logger.debug(f"记录验证错误：{error_key} - {check_point}")
    
    def record_config_usage(self, config_data: Dict[str, Any]):
        """
        记录配置使用情况
        
        Args:
            config_data: 配置字典
        """
        # 提取关键配置项（匿名化）
        usage = {
            'api_provider': config_data.get('api_provider', 'unknown'),
            'model_name': config_data.get('model_name', 'unknown'),
            'temperature_range': self._get_range_bucket(
                config_data.get('temperature', 0.3), 
                [0, 0.3, 0.5, 0.7, 1.0, 2.0]
            ),
            'top_p_range': self._get_range_bucket(
                config_data.get('top_p', 0.8),
                [0, 0.5, 0.8, 0.9, 1.0]
            ),
            'concurrency_level': config_data.get('initial_concurrency', 8),
            'cache_capacity_range': self._get_range_bucket(
                config_data.get('cache_capacity', 2000),
                [0, 500, 1000, 2000, 5000, 10000]
            ),
            'two_pass_enabled': config_data.get('enable_two_pass', True),
            'log_level': config_data.get('log_level', 'INFO'),
            'log_granularity': config_data.get('log_granularity', 'normal'),
            'version': config_data.get('_version', 'unknown'),
        }
        
        # 统计使用分布
        for key, value in usage.items():
            self.config_usage[f"{key}:{value}"] += 1
        
        logger.debug(f"记录配置使用：{usage}")
    
    def record_performance_metric(self, metric_name: str, value: float, 
                                  unit: str = "", tags: Optional[Dict] = None):
        """
        记录性能指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            unit: 单位
            tags: 附加标签
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {},
        }
        self.performance_metrics.append(metric)
        
        # 如果性能指标超过阈值，立即写入文件
        if len(self.performance_metrics) >= 100:
            self.flush_performance_metrics()
    
    def flush_performance_metrics(self):
        """刷写性能指标到文件"""
        if not self.performance_metrics:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d')
        perf_file = self.metrics_dir / f"performance_{timestamp}.jsonl"
        
        with open(perf_file, 'a', encoding='utf-8') as f:
            for metric in self.performance_metrics:
                f.write(json.dumps(metric, ensure_ascii=False) + '\n')
        
        self.performance_metrics.clear()
        logger.info(f"已刷写 {len(self.performance_metrics)} 条性能指标")
    
    def get_error_hotspots(self, top_n: int = 10) -> List[tuple]:
        """
        获取错误热力图 Top N
        
        Args:
            top_n: 返回前 N 个
            
        Returns:
            [(检查点，错误次数), ...]
        """
        sorted_hotspots = sorted(
            self.error_hotspots.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_hotspots[:top_n]
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        获取验证错误摘要
        
        Returns:
            验证错误统计摘要
        """
        total_errors = sum(self.validation_errors.values())
        
        # 按字段分组
        field_errors = defaultdict(int)
        for error_key, count in self.validation_errors.items():
            field = error_key.split(':')[0]
            field_errors[field] += count
        
        return {
            'total_errors': total_errors,
            'unique_error_types': len(self.validation_errors),
            'top_fields': sorted(
                field_errors.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            'top_hotspots': self.get_error_hotspots(5),
            'session_id': self.session_id,
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        获取配置使用摘要
        
        Returns:
            配置使用统计摘要
        """
        return {
            'total_samples': sum(self.config_usage.values()),
            'api_providers': self._filter_keys('api_provider:'),
            'model_names': self._filter_keys('model_name:'),
            'temperature_distribution': self._filter_keys('temperature_range:'),
            'concurrency_distribution': self._filter_keys('concurrency_level:'),
        }
    
    def export_report(self, output_file: Optional[str] = None) -> str:
        """
        导出完整报告
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_lines = [
            "=" * 70,
            "配置打点上报报告",
            "=" * 70,
            f"生成时间：{timestamp}",
            f"会话 ID: {self.session_id}",
            "",
            "-" * 70,
            "一、验证错误统计",
            "-" * 70,
        ]
        
        # 验证错误
        validation_summary = self.get_validation_summary()
        report_lines.append(f"总错误数：{validation_summary['total_errors']}")
        report_lines.append(f"唯一错误类型：{validation_summary['unique_error_types']}")
        report_lines.append("")
        report_lines.append("Top 5 错误字段:")
        for field, count in validation_summary['top_fields']:
            report_lines.append(f"  - {field}: {count} 次")
        
        report_lines.append("")
        report_lines.append("Top 5 错误检查点:")
        for checkpoint, count in validation_summary['top_hotspots']:
            report_lines.append(f"  - {checkpoint}: {count} 次")
        
        # 配置使用统计
        report_lines.append("")
        report_lines.append("-" * 70)
        report_lines.append("二、配置使用统计")
        "-" * 70
        usage_summary = self.get_usage_summary()
        report_lines.append(f"总样本数：{usage_summary['total_samples']}")
        report_lines.append("")
        report_lines.append("API 提供商分布:")
        for provider, count in usage_summary['api_providers'].items():
            report_lines.append(f"  - {provider}: {count} 次")
        
        report_lines.append("")
        report_lines.append("温度参数分布:")
        for temp_range, count in usage_summary['temperature_distribution'].items():
            report_lines.append(f"  - {temp_range}: {count} 次")
        
        report_lines.append("")
        report_lines.append("并发数分布:")
        for concurrency, count in usage_summary['concurrency_distribution'].items():
            report_lines.append(f"  - {concurrency}: {count} 次")
        
        # 性能指标
        report_lines.append("")
        report_lines.append("-" * 70)
        report_lines.append("三、性能指标")
        "-" * 70
        if self.performance_metrics:
            report_lines.append(f"性能指标数量：{len(self.performance_metrics)}")
            # 按指标名称分组统计
            metric_groups = defaultdict(list)
            for metric in self.performance_metrics:
                metric_groups[metric['name']].append(metric['value'])
            
            for name, values in metric_groups.items():
                avg_value = sum(values) / len(values)
                min_value = min(values)
                max_value = max(values)
                report_lines.append(
                    f"  - {name}: 平均={avg_value:.2f}, "
                    f"最小={min_value:.2f}, 最大={max_value:.2f}"
                )
        else:
            report_lines.append("暂无性能指标数据")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        
        report_content = "\n".join(report_lines)
        
        # 写入文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已导出至：{output_file}")
        
        return report_content
    
    def _write_error_log(self, error_detail: Dict[str, Any]):
        """写入详细错误日志"""
        timestamp = datetime.now().strftime('%Y%m%d')
        error_file = self.metrics_dir / f"errors_{timestamp}.jsonl"
        
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_detail, ensure_ascii=False) + '\n')
    
    def _get_range_bucket(self, value: float, buckets: List[float]) -> str:
        """
        获取值所在的区间
        
        Args:
            value: 值
            buckets: 区间边界
            
        Returns:
            区间字符串
        """
        for i in range(len(buckets) - 1):
            if buckets[i] <= value < buckets[i + 1]:
                return f"{buckets[i]}-{buckets[i+1]}"
        return f">={buckets[-1]}" if value >= buckets[-1] else f"<{buckets[0]}"
    
    def _filter_keys(self, prefix: str) -> Dict[str, int]:
        """过滤指定前缀的键"""
        result = {}
        for key, value in self.config_usage.items():
            if key.startswith(prefix):
                result_key = key[len(prefix):]
                result[result_key] = value
        return result
    
    def flush(self):
        """刷写所有指标到文件"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 刷写验证错误统计
        if self.validation_errors:
            summary_file = self.metrics_dir / f"validation_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'validation_errors': dict(self.validation_errors),
                    'error_hotspots': dict(self.error_hotspots),
                }, f, indent=2, ensure_ascii=False)
        
        # 刷写配置使用统计
        if self.config_usage:
            usage_file = self.metrics_dir / f"usage_summary_{timestamp}.json"
            with open(usage_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'config_usage': dict(self.config_usage),
                }, f, indent=2, ensure_ascii=False)
        
        # 刷写性能指标
        self.flush_performance_metrics()
        
        logger.info("已刷写所有配置指标")


# 全局指标收集器实例
_global_metrics: Optional[ConfigMetrics] = None


def get_metrics_collector() -> ConfigMetrics:
    """获取全局指标收集器"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = ConfigMetrics()
    return _global_metrics


def record_config_validation_error(field: str, error_type: str, 
                                   check_point: str, value: Any):
    """记录配置验证错误（便捷函数）"""
    metrics = get_metrics_collector()
    metrics.record_validation_error(field, error_type, check_point, value)


def record_config_usage(config_data: Dict[str, Any]):
    """记录配置使用情况（便捷函数）"""
    metrics = get_metrics_collector()
    metrics.record_config_usage(config_data)


def record_performance_metric(metric_name: str, value: float, 
                             unit: str = "", tags: Optional[Dict] = None):
    """记录性能指标（便捷函数）"""
    metrics = get_metrics_collector()
    metrics.record_performance_metric(metric_name, value, unit, tags)


def export_metrics_report(output_file: Optional[str] = None) -> str:
    """导出指标报告（便捷函数）"""
    metrics = get_metrics_collector()
    return metrics.export_report(output_file)


def flush_metrics():
    """刷写所有指标（便捷函数）"""
    metrics = get_metrics_collector()
    metrics.flush()
