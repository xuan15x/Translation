"""
术语库增量更新模块
支持从 Excel 文件增量导入术语、批量更新和合并
"""
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """导入结果统计"""
    total_rows: int = 0  # 总行数
    new_entries: int = 0  # 新增条目数
    updated_entries: int = 0  # 更新条目数
    skipped_rows: int = 0  # 跳过行数
    errors: List[str] = None  # 错误列表
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> dict:
        return {
            'total_rows': self.total_rows,
            'new_entries': self.new_entries,
            'updated_entries': self.updated_entries,
            'skipped_rows': self.skipped_rows,
            'errors_count': len(self.errors),
            'errors': self.errors[:10]  # 只返回前 10 个错误
        }


class TerminologyImporter:
    """术语库导入器"""
    
    def __init__(self, filepath: str):
        """
        初始化导入器
        
        Args:
            filepath: Excel 文件路径
        """
        self.filepath = filepath
        self._validate_file()
    
    def _validate_file(self):
        """验证文件是否存在且可读"""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"文件不存在：{self.filepath}")
        
        if not self.filepath.endswith('.xlsx'):
            raise ValueError("仅支持 Excel (.xlsx) 文件格式")
        
        # 检查文件是否可读且有内容
        try:
            file_size = os.path.getsize(self.filepath)
            if file_size == 0:
                raise ValueError("文件为空")
            if file_size > 100 * 1024 * 1024:  # 限制 100MB
                raise ValueError("文件过大（最大 100MB）")
        except OSError as e:
            raise RuntimeError(f"无法访问文件：{e}")
    
    def load_excel(self) -> pd.DataFrame:
        """
        加载 Excel 文件
        
        Returns:
            DataFrame 对象
        
        Raises:
            RuntimeError: 读取失败时抛出
        """
        try:
            df = pd.read_excel(self.filepath, engine='openpyxl')
            
            # 验证 DataFrame 有效性
            if df.empty:
                logger.warning(f"Excel 文件为空：{self.filepath}")
            
            return df
            
        except Exception as e:
            logger.error(f"读取 Excel 失败：{self.filepath}, error: {e}")
            raise RuntimeError(f"读取 Excel 失败：{type(e).__name__}: {str(e)}")
    
    def detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        检测列名映射
        
        Args:
            df: DataFrame 对象
            
        Returns:
            列名映射字典 {source: column_name, target: language_columns}
        """
        columns = df.columns.tolist()
        
        # 检测源文本列（中文原文）
        source_col = None
        possible_source_names = ['中文原文', '源文', '原文', 'Source', 'Chinese']
        
        for col in columns:
            if col in possible_source_names:
                source_col = col
                break
        
        if not source_col:
            # 尝试使用第一列作为源文本
            source_col = columns[0] if columns else None
        
        # 检测目标语言列
        target_cols = []
        exclude_names = ['Key', 'key', 'ID', 'id', '序号', '编号']
        
        for col in columns:
            if col != source_col and col not in exclude_names:
                # 检查是否包含非空数据
                if df[col].notna().any():
                    target_cols.append(col)
        
        return {
            'source': source_col,
            'targets': target_cols
        }
    
    def parse_entries(self, df: pd.DataFrame, 
                     col_mapping: Optional[Dict[str, str]] = None) -> List[Tuple[str, str, str]]:
        """
        解析术语条目
        
        Args:
            df: DataFrame 对象
            col_mapping: 列映射，如果为 None 则自动检测
            
        Returns:
            (source_text, language, translation) 元组列表
        """
        if col_mapping is None:
            col_mapping = self.detect_columns(df)
        
        source_col = col_mapping.get('source')
        target_cols = col_mapping.get('targets', [])
        
        if not source_col:
            raise ValueError("无法识别源文本列")
        
        entries = []
        
        for _, row in df.iterrows():
            source_text = str(row.get(source_col, '')).strip()
            
            # 跳过空行
            if not source_text or source_text == 'nan':
                continue
            
            # 遍历所有语言列
            for lang_col in target_cols:
                translation = str(row.get(lang_col, '')).strip()
                
                # 跳过空翻译
                if not translation or translation == 'nan':
                    continue
                
                # 将列名转换为语言名称
                language = self._col_to_language(lang_col)
                entries.append((source_text, language, translation))
        
        return entries
    
    def _col_to_language(self, col_name: str) -> str:
        """
        将列名转换为语言名称
        
        Args:
            col_name: 列名
            
        Returns:
            语言名称
        """
        # 常见语言列名映射
        lang_mapping = {
            '英语': '英语', 'English': '英语', 'EN': '英语',
            '日语': '日语', 'Japanese': '日语', 'JP': '日语',
            '韩语': '韩语', 'Korean': '韩语', 'KO': '韩语',
            '法语': '法语', 'French': '法语', 'FR': '法语',
            '德语': '德语', 'German': '法语', 'DE': '德语',
            '西班牙语': '西班牙语', 'Spanish': '西班牙语', 'ES': '西班牙语',
            '俄语': '俄语', 'Russian': '俄语', 'RU': '俄语',
            '葡萄牙语': '葡萄牙语', 'Portuguese': '葡萄牙语', 'PT': '葡萄牙语',
            '意大利语': '意大利语', 'Italian': '意大利语', 'IT': '意大利语',
            '阿拉伯语': '阿拉伯语', 'Arabic': '阿拉伯语', 'AR': '阿拉伯语',
            '泰语': '泰语', 'Thai': '泰语', 'TH': '泰语',
            '越南语': '越南语', 'Vietnamese': '越南语', 'VI': '越南语',
        }
        
        return lang_mapping.get(col_name, col_name)
    
    def import_to_dict(self, existing_db: Dict[str, Dict[str, str]], 
                      update_existing: bool = True) -> Tuple[ImportResult, Dict[str, Dict[str, str]]]:
        """
        导入到现有数据库
        
        Args:
            existing_db: 现有术语库字典
            update_existing: 是否更新已存在的条目
            
        Returns:
            (ImportResult, 更新后的数据库)
        """
        result = ImportResult()
        new_db = {k: dict(v) for k, v in existing_db.items()}  # 深拷贝
        
        try:
            df = self.load_excel()
            result.total_rows = len(df)
            
            col_mapping = self.detect_columns(df)
            entries = self.parse_entries(df, col_mapping)
            
            for source_text, language, translation in entries:
                if source_text not in new_db:
                    # 新条目
                    new_db[source_text] = {language: translation}
                    result.new_entries += 1
                elif language not in new_db[source_text]:
                    # 已有源文本，但语言是新的
                    new_db[source_text][language] = translation
                    result.new_entries += 1
                elif update_existing:
                    # 更新已有语言的翻译
                    old_translation = new_db[source_text][language]
                    if old_translation != translation:
                        new_db[source_text][language] = translation
                        result.updated_entries += 1
                else:
                    # 跳过已存在的条目
                    result.skipped_rows += 1
            
        except Exception as e:
            result.errors.append(f"导入过程出错：{str(e)}")
        
        return result, new_db


class TerminologyUpdater:
    """术语库更新器"""
    
    def __init__(self, db: Dict[str, Dict[str, str]]):
        """
        初始化更新器
        
        Args:
            db: 术语库字典
        """
        self.db = db
    
    def add_batch(self, entries: List[Tuple[str, str, str]]) -> Dict[str, int]:
        """
        批量添加条目
        
        Args:
            entries: (source_text, language, translation) 元组列表
            
        Returns:
            统计信息
        """
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        for source_text, language, translation in entries:
            if source_text not in self.db:
                self.db[source_text] = {language: translation}
                stats['added'] += 1
            elif language not in self.db[source_text]:
                self.db[source_text][language] = translation
                stats['added'] += 1
            else:
                old_value = self.db[source_text][language]
                if old_value != translation:
                    self.db[source_text][language] = translation
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1
        
        return stats
    
    def remove_entry(self, source_text: str, language: Optional[str] = None) -> bool:
        """
        删除条目
        
        Args:
            source_text: 源文本
            language: 语言，如果为 None 则删除整个源文本的所有翻译
            
        Returns:
            是否删除成功
        """
        if source_text not in self.db:
            return False
        
        if language is None:
            del self.db[source_text]
            return True
        else:
            if language in self.db[source_text]:
                del self.db[source_text][language]
                # 如果该源文本没有其他翻译了，删除整个条目
                if not self.db[source_text]:
                    del self.db[source_text]
                return True
            return False
    
    def update_entry(self, source_text: str, language: str, 
                    new_translation: str) -> bool:
        """
        更新条目
        
        Args:
            source_text: 源文本
            language: 语言
            new_translation: 新翻译
            
        Returns:
            是否更新成功
        """
        if source_text not in self.db:
            return False
        
        if language not in self.db[source_text]:
            return False
        
        self.db[source_text][language] = new_translation
        return True
    
    def merge_from(self, other_db: Dict[str, Dict[str, str]], 
                  prefer_newer: bool = True) -> Dict[str, int]:
        """
        从另一个数据库合并
        
        Args:
            other_db: 另一个术语库字典
            prefer_newer: 是否优先使用其他数据库的值
            
        Returns:
            统计信息
        """
        stats = {'merged': 0, 'conflicts_resolved': 0, 'unchanged': 0}
        
        for source_text, translations in other_db.items():
            if source_text not in self.db:
                # 直接添加新条目
                self.db[source_text] = dict(translations)
                stats['merged'] += len(translations)
            else:
                # 合并各语言的翻译
                for language, translation in translations.items():
                    if language not in self.db[source_text]:
                        self.db[source_text][language] = translation
                        stats['merged'] += 1
                    elif prefer_newer:
                        # 优先使用新值
                        if self.db[source_text][language] != translation:
                            self.db[source_text][language] = translation
                            stats['conflicts_resolved'] += 1
                    else:
                        # 保留旧值
                        stats['unchanged'] += 1
        
        return stats
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total_sources = len(self.db)
        total_translations = sum(len(t) for t in self.db.values())
        languages = set()
        
        for translations in self.db.values():
            languages.update(translations.keys())
        
        return {
            'total_source_texts': total_sources,
            'total_translations': total_translations,
            'languages_count': len(languages),
            'languages': sorted(list(languages))
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        导出为 DataFrame
        
        Returns:
            DataFrame 对象
        """
        if not self.db:
            return pd.DataFrame()
        
        # 收集所有语言
        all_languages = set()
        for translations in self.db.values():
            all_languages.update(translations.keys())
        
        # 构建行数据
        rows = []
        for i, (source_text, translations) in enumerate(self.db.items()):
            row = {
                'Key': f"TM_{i}",
                '中文原文': source_text
            }
            
            # 添加各语言的翻译
            for lang in all_languages:
                row[lang] = translations.get(lang, '')
            
            rows.append(row)
        
        # 创建 DataFrame
        columns = ['Key', '中文原文'] + sorted(list(all_languages))
        df = pd.DataFrame(rows, columns=columns)
        
        return df


def incremental_import(existing_db: Dict[str, Dict[str, str]], 
                       excel_file: str,
                       update_existing: bool = True) -> Tuple[ImportResult, Dict[str, Dict[str, str]]]:
    """
    便捷函数：从 Excel 文件增量导入术语
    
    Args:
        existing_db: 现有术语库
        excel_file: Excel 文件路径
        update_existing: 是否更新已存在条目
        
    Returns:
        (导入结果，更新后的数据库)
    """
    importer = TerminologyImporter(excel_file)
    return importer.import_to_dict(existing_db, update_existing)


def merge_databases(db1: Dict[str, Dict[str, str]], 
                   db2: Dict[str, Dict[str, str]],
                   prefer_db2: bool = True) -> Tuple[Dict[str, int], Dict[str, Dict[str, str]]]:
    """
    便捷函数：合并两个术语库
    
    Args:
        db1: 第一个数据库
        db2: 第二个数据库
        prefer_db2: 是否优先使用 db2 的值
        
    Returns:
        (统计信息，合并后的数据库)
    """
    updater = TerminologyUpdater(db1)
    stats = updater.merge_from(db2, prefer_newer=prefer_db2)
    return stats, updater.db
