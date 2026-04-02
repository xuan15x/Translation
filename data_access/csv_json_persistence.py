"""
CSV/JSON 数据持久化管理器
支持 CSV 和 JSON 格式的翻译文件读写

新增功能：扩展支持的文件格式
"""
import os
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CSVJSONPersistence:
    """CSV/JSON 文件持久化管理器"""

    # 支持的键列名（用于识别唯一标识）
    KEY_COLUMNS = ['key', 'Key', 'KEY', 'id', 'ID', 'Id', '编号', '键']
    
    # 支持的源文本列名
    SOURCE_COLUMNS = [
        'source_text', 'sourceText', 'SourceText', 'SOURCE_TEXT',
        '中文原文', '原文', '源文', '原文本', 'Source', 'source'
    ]

    def __init__(self, file_path: str):
        """
        初始化

        Args:
            file_path: CSV 或 JSON 文件路径
        """
        self.file_path = file_path
        self.file_type = self._get_file_type(file_path)
        self.data: List[Dict[str, Any]] = []
        self.key_column: Optional[str] = None
        self.source_column: Optional[str] = None

    def _get_file_type(self, file_path: str) -> str:
        """获取文件类型"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            return 'csv'
        elif ext == '.json':
            return 'json'
        else:
            raise ValueError(f"不支持的文件格式：{ext}，支持 .csv 或 .json")

    def load(self) -> List[Dict[str, Any]]:
        """
        加载文件数据

        Returns:
            数据列表
        """
        if not os.path.exists(self.file_path):
            logger.info(f"文件不存在，将创建新文件：{self.file_path}")
            self.data = []
            return self.data

        try:
            if self.file_type == 'csv':
                self.data = self._load_csv()
            else:  # json
                self.data = self._load_json()

            # 自动识别键列和源文本列
            self._auto_detect_columns()

            logger.info(f"📊 已加载 {len(self.data)} 条数据：{self.file_path}")
            return self.data

        except Exception as e:
            logger.error(f"加载文件失败：{e}")
            raise

    def _load_csv(self) -> List[Dict[str, Any]]:
        """加载 CSV 文件"""
        try:
            # 使用 pandas 读取 CSV，自动处理编码
            df = pd.read_csv(self.file_path, encoding='utf-8-sig')
            # 填充空值
            df.fillna('', inplace=True)
            # 转换为字典列表
            return df.to_dict('records')
        except UnicodeDecodeError:
            # 尝试其他编码
            df = pd.read_csv(self.file_path, encoding='gbk')
            df.fillna('', inplace=True)
            return df.to_dict('records')

    def _load_json(self) -> List[Dict[str, Any]]:
        """加载 JSON 文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持两种格式：字典列表或键值对字典
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 转换为列表格式
            return [
                {'key': k, 'source_text': v if isinstance(v, str) else str(v)}
                for k, v in data.items()
            ]
        else:
            raise ValueError("JSON 数据必须是列表或字典")

    def _auto_detect_columns(self):
        """自动识别键列和源文本列"""
        if not self.data:
            return

        # 获取所有列名
        columns = list(self.data[0].keys())

        # 识别键列
        for col in columns:
            if col in self.KEY_COLUMNS:
                self.key_column = col
                logger.debug(f"识别到键列：{col}")
                break
        
        # 如果没有显式键列，使用第一列
        if not self.key_column and columns:
            self.key_column = columns[0]
            logger.debug(f"使用第一列作为键列：{self.key_column}")

        # 识别源文本列
        for col in columns:
            if col in self.SOURCE_COLUMNS:
                self.source_column = col
                logger.debug(f"识别到源文本列：{col}")
                break
        
        # 如果没有显式源文本列，使用第二列（如果有）
        if not self.source_column and len(columns) > 1:
            self.source_column = columns[1]
            logger.debug(f"使用第二列作为源文本列：{self.source_column}")

    def save(self, data: Optional[List[Dict[str, Any]]] = None,
             output_path: Optional[str] = None) -> str:
        """
        保存数据到文件

        Args:
            data: 要保存的数据，如果为 None 则使用内部数据
            output_path: 输出路径，如果为 None 则保存到原文件

        Returns:
            保存的文件路径
        """
        if data is not None:
            self.data = data
        
        output_path = output_path or self.file_path

        try:
            if self.file_type == 'csv':
                self._save_csv(output_path)
            else:  # json
                self._save_json(output_path)

            logger.info(f"💾 已保存 {len(self.data)} 条数据：{output_path}")
            return output_path

        except Exception as e:
            logger.error(f"保存文件失败：{e}")
            raise

    def _save_csv(self, output_path: str):
        """保存为 CSV 文件"""
        if not self.data:
            # 空数据时创建空文件
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                pass
            return

        # 使用 pandas 保存 CSV
        df = pd.DataFrame(self.data)
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

    def _save_json(self, output_path: str):
        """保存为 JSON 文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_translations(self, target_langs: List[str]) -> List[Dict[str, Any]]:
        """
        获取翻译数据（包含目标语言列）

        Args:
            target_langs: 目标语言列表

        Returns:
            翻译数据列表
        """
        if not self.data:
            self.load()

        result = []
        for item in self.data:
            row = {
                'key': item.get(self.key_column, ''),
                'source_text': item.get(self.source_column, '')
            }
            # 添加目标语言列
            for lang in target_langs:
                row[lang] = item.get(lang, '')
            result.append(row)

        return result

    def update_translation(self, key: str, target_lang: str, translation: str) -> bool:
        """
        更新翻译

        Args:
            key: 键值
            target_lang: 目标语言
            translation: 翻译结果

        Returns:
            是否更新成功
        """
        if not self.data:
            self.load()

        for item in self.data:
            if str(item.get(self.key_column)) == str(key):
                item[target_lang] = translation
                logger.debug(f"更新翻译：{key} -> {target_lang}")
                return True

        logger.warning(f"未找到要更新的键：{key}")
        return False

    def add_entry(self, key: str, source_text: str, 
                  translations: Optional[Dict[str, str]] = None) -> bool:
        """
        添加新条目

        Args:
            key: 键值
            source_text: 源文本
            translations: 翻译字典（可选）

        Returns:
            是否添加成功
        """
        if not self.data:
            self.load()

        # 检查是否已存在
        for item in self.data:
            if str(item.get(self.key_column)) == str(key):
                logger.warning(f"键已存在：{key}")
                return False

        # 创建新条目
        new_entry = {
            self.key_column or 'key': key,
            self.source_column or 'source_text': source_text
        }
        
        # 添加翻译
        if translations:
            for lang, trans in translations.items():
                new_entry[lang] = trans

        self.data.append(new_entry)
        logger.debug(f"添加新条目：{key}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.data:
            self.load()

        # 统计所有列
        columns = set()
        for item in self.data:
            columns.update(item.keys())

        # 统计非空翻译数
        lang_counts = {}
        for col in columns:
            if col not in [self.key_column, self.source_column, 'key', 'source_text']:
                count = sum(1 for item in self.data if item.get(col, '').strip())
                lang_counts[col] = count

        return {
            'total_entries': len(self.data),
            'columns': list(columns),
            'languages': lang_counts,
            'file_path': self.file_path
        }

    def to_excel(self, output_path: str) -> str:
        """
        导出为 Excel 文件

        Args:
            output_path: Excel 文件路径

        Returns:
            保存的文件路径
        """
        if not self.data:
            self.load()

        df = pd.DataFrame(self.data)
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        logger.info(f"已导出为 Excel: {output_path}")
        return output_path

    @classmethod
    def from_excel(cls, excel_path: str, output_format: str = 'json') -> 'CSVJSONPersistence':
        """
        从 Excel 文件创建 CSV/JSON 持久化对象

        Args:
            excel_path: Excel 文件路径
            output_format: 输出格式 ('csv' 或 'json')

        Returns:
            CSVJSONPersistence 实例
        """
        # 读取 Excel
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # 生成临时文件路径
        base_path = os.path.splitext(excel_path)[0]
        if output_format == 'csv':
            temp_path = base_path + '.csv'
        else:
            temp_path = base_path + '.json'
        
        # 保存为指定格式
        if output_format == 'csv':
            df.to_csv(temp_path, index=False, encoding='utf-8-sig')
        else:
            data = df.to_dict('records')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已从 Excel 转换为 {output_format}: {temp_path}")
        return cls(temp_path)


def detect_file_format(file_path: str) -> str:
    """
    检测文件格式

    Args:
        file_path: 文件路径

    Returns:
        文件格式 ('excel', 'csv', 'json')
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext == '.csv':
        return 'csv'
    elif ext == '.json':
        return 'json'
    else:
        raise ValueError(f"不支持的文件格式：{ext}")


def load_translation_file(file_path: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    加载翻译文件（自动检测格式）

    Args:
        file_path: 文件路径

    Returns:
        (数据列表，文件格式)
    """
    file_format = detect_file_format(file_path)
    
    if file_format == 'excel':
        df = pd.read_excel(file_path, engine='openpyxl')
        return df.to_dict('records'), file_format
    elif file_format == 'csv':
        persistence = CSVJSONPersistence(file_path)
        return persistence.load(), file_format
    elif file_format == 'json':
        persistence = CSVJSONPersistence(file_path)
        return persistence.load(), file_format
    else:
        raise ValueError(f"不支持的文件格式：{file_format}")


def save_translation_file(data: List[Dict[str, Any]], 
                         output_path: str,
                         output_format: Optional[str] = None) -> str:
    """
    保存翻译文件（自动检测格式）

    Args:
        data: 数据列表
        output_path: 输出路径
        output_format: 输出格式（可选，None 表示从扩展名推断）

    Returns:
        保存的文件路径
    """
    if output_format is None:
        output_format = detect_file_format(output_path)

    if output_format == 'excel':
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
    elif output_format == 'csv':
        persistence = CSVJSONPersistence(output_path)
        persistence.save(data)
    elif output_format == 'json':
        persistence = CSVJSONPersistence(output_path)
        persistence.save(data)
    else:
        raise ValueError(f"不支持的输出格式：{output_format}")

    logger.info(f"已保存 {len(data)} 条数据：{output_path}")
    return output_path
