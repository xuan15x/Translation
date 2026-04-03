"""
结果构建器
负责构建、转换和格式化翻译结果
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import logging
from domain.models import TranslationResult, BatchResult, TranslationStatus, TranslationTask

logger = logging.getLogger(__name__)


class ResultBuilder:
    """翻译结果构建器"""
    
    @staticmethod
    def to_dataframe(results: List[TranslationResult]) -> pd.DataFrame:
        """
        将结果列表转换为 DataFrame
        
        Args:
            results: 翻译结果列表
            
        Returns:
            DataFrame 格式的结果
        """
        data = []
        
        for result in results:
            row = {
                '行号': result.task.idx + 1,
                '原文': result.task.source_text,
                '译文': result.final_trans,
                '初译': result.initial_trans,
                '状态': result.status.value,
                '诊断': result.diagnosis,
                '原因': result.reason if result.reason else '',
                '术语匹配': f"{result.tm_match.original} -> {result.tm_match.translation}" if result.tm_match else '',
                '匹配置信度': result.tm_match.score if result.tm_match else 0
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def to_excel(results: List[TranslationResult], output_path: str):
        """
        导出结果到 Excel
        
        Args:
            results: 翻译结果列表
            output_path: 输出文件路径
        """
        df = ResultBuilder.to_dataframe(results)
        df.to_excel(output_path, index=False, engine='openpyxl')
    
    @staticmethod
    def summarize(batch_result: BatchResult) -> Dict[str, Any]:
        """
        生成汇总统计
        
        Args:
            batch_result: 批量结果
            
        Returns:
            统计信息字典
        """
        return {
            '总任务数': batch_result.total,
            '成功数': batch_result.success_count,
            '失败数': batch_result.failed_count,
            '本地命中数': batch_result.local_hit_count,
            '成功率': f"{batch_result.success_rate:.2f}%",
            'AI 翻译数': batch_result.success_count - batch_result.local_hit_count,
            'AI 使用率': f"{(batch_result.success_count - batch_result.local_hit_count) / max(batch_result.total, 1) * 100:.2f}%"
        }
    
    @staticmethod
    def print_summary(batch_result: BatchResult):
        """打印汇总报告"""
        summary = ResultBuilder.summarize(batch_result)

        logger.info("\n" + "="*60)
        logger.info("📊 翻译结果汇总")
        logger.info("="*60)
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        logger.info("="*60)

        # 详细分类统计
        status_counts = {}
        failure_reasons = {}  # 记录失败原因
        
        for result in batch_result.results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # 记录失败原因
            if not result.success and result.reason:
                reason = result.reason[:100]  # 截断过长的原因
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        logger.info("\n📈 状态分布:")
        for status, count in sorted(status_counts.items()):
            percentage = count / max(batch_result.total, 1) * 100
            logger.info(f"  {status}: {count} ({percentage:.1f}%)")
        
        # 输出失败原因统计
        if failure_reasons:
            logger.info("\n❌ 失败原因统计（Top 10）:")
            sorted_reasons = sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
            for i, (reason, count) in enumerate(sorted_reasons[:10], 1):
                logger.info(f"  {i}. [{count}次] {reason}")
        
        # 如果有失败，输出前3个详细示例
        failed_results = [r for r in batch_result.results if not r.success]
        if failed_results:
            logger.info(f"\n💡 失败示例详情（前3个）:")
            for i, result in enumerate(failed_results[:3], 1):
                logger.info(f"  示例{i}:")
                logger.info(f"    - Key: {result.task.key if result.task else 'N/A'}")
                logger.info(f"    - 原文: {result.task.source_text[:50] if result.task else 'N/A'}")
                logger.info(f"    - 目标语言: {result.task.target_lang if result.task else 'N/A'}")
                logger.info(f"    - 错误原因: {result.reason}")
                logger.info(f"    - 诊断信息: {result.diagnosis}")
        
        logger.info("="*60 + "\n")


class TaskFactory:
    """任务工厂 - 从各种数据源创建翻译任务"""
    
    @staticmethod
    def from_excel_row(idx: int, row: Dict[str, Any], target_lang: str, source_lang: Optional[str] = None) -> TranslationTask:
        """
        从 Excel 行创建任务

        Args:
            idx: 行索引
            row: 行数据（字典）
            target_lang: 目标语言
            source_lang: 源语言列名（可选，None 表示自动检测）

        Returns:
            翻译任务
        """
        # 常见的源语言列名列表（按优先级排序）
        common_source_cols = ['中文原文', '中文', '原文', 'Source', 'source_text', '文本', '内容']
        
        # 确定使用哪一列作为原文
        if source_lang and source_lang in row:
            # 使用用户指定的源语言列
            source_text = row.get(source_lang, '')
        else:
            # 自动检测：尝试常见的列名
            source_text = ''
            for col in common_source_cols:
                if col in row and row[col]:
                    source_text = row[col]
                    break
            
            # 如果都没找到，使用第一列非空文本
            if not source_text:
                for key, value in row.items():
                    if value and isinstance(value, str) and key.lower() not in ['key', 'id', '序号']:
                        source_text = value
                        break

        return TranslationTask(
            idx=idx,
            key=row.get('Key', row.get('key', row.get('ID', row.get('id', f'row_{idx}')))),
            source_text=source_text,
            original_trans=row.get(target_lang, None),
            target_lang=target_lang,
            source_lang=source_lang
        )
    
    @staticmethod
    def from_excel_file(excel_path: str, target_langs: List[str], source_lang: Optional[str] = None) -> List[TranslationTask]:
        """
        从 Excel 文件批量创建任务

        Args:
            excel_path: Excel 文件路径
            target_langs: 目标语言列表
            source_lang: 源语言列名（可选，None 表示自动检测）

        Returns:
            任务列表
        """
        import pandas as pd

        df = pd.read_excel(excel_path, engine='openpyxl')
        tasks = []

        for idx, row in df.iterrows():
            row_dict = row.to_dict()

            for lang in target_langs:
                # 即使目标语言列不存在，也创建任务（用于新文档翻译）
                task = TaskFactory.from_excel_row(idx, row_dict, lang, source_lang)
                if task.source_text:  # 只添加有原文的任务
                    tasks.append(task)

        return tasks
    
    @staticmethod
    def from_list(texts: List[str], target_lang: str, source_lang: Optional[str] = None) -> List[TranslationTask]:
        """
        从文本列表创建任务
        
        Args:
            texts: 文本列表
            target_lang: 目标语言
            source_lang: 源语言（可选）
            
        Returns:
            任务列表
        """
        return [
            TranslationTask(
                idx=i,
                key=f'text_{i}',
                source_text=text,
                original_trans=None,
                target_lang=target_lang,
                source_lang=source_lang
            )
            for i, text in enumerate(texts)
        ]
