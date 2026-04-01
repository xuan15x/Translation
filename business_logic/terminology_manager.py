"""
术语库管理模块
负责术语库的加载、查询、更新和保存
"""
import asyncio
import copy
import json
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, Optional, List, Tuple
import logging
import gc
import tracemalloc

import pandas as pd

from data_access.fuzzy_matcher import FuzzyMatcher
from infrastructure.models import Config
from data_access.terminology_update import TerminologyImporter, ImportResult
from service.translation_history import (
    get_history_manager
)
from service.terminology_history import (
    record_term_change, 
    ChangeType
)
from infrastructure.cache import TerminologyCache
from infrastructure.redis_cache import (
    get_redis_cache,
    RedisTerminologyCache,
    RedisCacheConfig
)
from infrastructure.unified_cache import (
    get_cache_manager,
    UnifiedCacheManager,
    CacheIsolationLevel
)
from service.terminology_version import TerminologyVersionController
from service.auto_backup import AutoBackupManager, BackupStrategy

logger = logging.getLogger(__name__)


class TerminologyManager:
    """术语库管理器 - 使用 Excel 存储 + SQLite 内存数据库"""
    
    def __init__(self, filepath: str, config: Config):
        """
        初始化术语库管理器
        
        Args:
            filepath: 术语库文件路径
            config: 系统配置对象
        """
        self.filepath = filepath
        self.config = config
        
        # 使用新的 Excel+SQLite 持久化层
        from data_access.excel_sqlite_persistence import TerminologyPersistence
        self.persistence = TerminologyPersistence(filepath)
        
        # 内存数据库（从持久化层获取连接）
        self.db_conn = self.persistence.manager.conn
        
        # 异步锁和队列
        self.lock = asyncio.Lock()
        self.queue = []
        self.queue_lock = asyncio.Lock()
        self.event = asyncio.Event()
        self.shutdown_flag = False
        self._save_logged = False
        
        # 注册到全局持久化管理器
        from data_access.global_persistence_manager import get_global_persistence_manager
        self.global_manager = get_global_persistence_manager()
        self.global_manager.register_terminology(self.persistence)
        
        # 历史管理器
        self.history_manager = get_history_manager()
        self._current_batch_id = ""
        
        # 性能优化：添加缓存层
        self.cache = TerminologyCache(capacity=config.batch_size * 2)
        
        # Redis 缓存（可选，用于高并发场景）
        self.redis_cache: Optional[RedisTerminologyCache] = None
        self._use_redis_cache = False
        
        # 统一缓存管理器（版本控制、同步保障）
        self.cache_manager: Optional[UnifiedCacheManager] = None
        self._datasource_name = "terminology"
        
        # 内存监控
        self._memory_tracking_enabled = False
        
        # 版本控制和备份（可选功能）
        self.version_controller: Optional[TerminologyVersionController] = None
        self.backup_manager: Optional[AutoBackupManager] = None
    
    async def init_redis_cache(self, host: str = "localhost", port: int = 6379,
                               password: Optional[str] = None, **kwargs):
        """
        初始化 Redis 缓存（可选，用于高并发场景）
        
        Args:
            host: Redis 主机地址
            port: Redis 端口
            password: Redis 密码
            **kwargs: 其他配置参数
        """
        try:
            from infrastructure.redis_cache import init_redis_cache as redis_init
            
            self.redis_cache = await redis_init(
                host=host,
                port=port,
                password=password,
                **kwargs
            )
            self._use_redis_cache = True
            
            logger.info(f"✅ Redis 缓存已初始化：{host}:{port}")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis 缓存初始化失败，将使用本地缓存：{e}")
            self._use_redis_cache = False
    
    def init_unified_cache(self, isolation_level: str = "read_committed",
                          default_ttl: int = 3600,
                          max_memory_mb: int = 500):
        """
        初始化统一缓存管理器（版本控制、同步保障）
        
        Args:
            isolation_level: 隔离级别 ("read_uncommitted"|"read_committed"|"repeatable_read"|"serializable")
            default_ttl: 默认 TTL（秒）
            max_memory_mb: 最大内存（MB）
        """
        from infrastructure.unified_cache import init_cache_manager
        
        self.cache_manager = init_cache_manager(
            isolation_level=isolation_level,
            default_ttl=default_ttl,
            max_memory_mb=max_memory_mb
        )
        
        # 订阅缓存失效事件
        self.cache_manager.subscribe(
            self._datasource_name,
            self._on_cache_invalidated
        )
        
        logger.info(f"✅ 统一缓存管理器已初始化 (隔离级别：{isolation_level})")

    def _load_sync(self):
        """同步加载术语库数据"""
        if os.path.exists(self.filepath):
            try:
                df = pd.read_excel(self.filepath, engine='openpyxl')
                df.fillna('', inplace=True)
                count = 0
                
                for _, row in df.iterrows():
                    src = str(row.get('中文原文', '')).strip()
                    if src:
                        trans = {
                            c: str(row.get(c, '')).strip() 
                            for c in df.columns 
                            if c not in ['Key', '中文原文'] and str(row.get(c, '')).strip()
                        }
                        if trans:
                            self.db[src] = trans
                            count += 1
                            
            except Exception as e:
                logger.error(f"术语库加载失败：{e}")
        else:
            logger.info("新术语库将自动创建")

    async def _background_writer(self):
        """后台异步写入器，定期将内存中的术语库保存到磁盘"""
        while not self.shutdown_flag:
            try:
                await asyncio.wait_for(self.event.wait(), timeout=1.0)
                snapshot = None
                
                async with self.queue_lock:
                    if not self.queue:
                        self.event.clear()
                        continue
                    self.queue.clear()
                    self.event.clear()
                
                async with self.lock:
                    # 使用深拷贝防止数据竞争
                    snapshot = copy.deepcopy(self.db)
                
                if snapshot:
                    try:
                        # 使用临时文件防止写入中断导致数据损坏
                        temp_file = f"{self.tmp_path}.{os.getpid()}"
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(snapshot, f, ensure_ascii=False, indent=2)
                        
                        # 原子性替换
                        if os.path.exists(self.tmp_path):
                            os.remove(self.tmp_path)
                        os.rename(temp_file, self.tmp_path)
                        
                    except IOError as e:
                        logger.error(f"写入临时文件失败：{e}")
                        # 清理可能的临时文件
                        if 'temp_file' in locals() and os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        
            except asyncio.TimeoutError:
                # 正常的超时，继续循环
                pass
            except Exception as e:
                logger.exception(f"后台写入器异常：{e}")

    async def add_entry(self, src: str, lang: str, trans: str):
        """
        添加术语条目（使用 SQLite）
        
        Args:
            src: 源文本
            lang: 目标语言
            trans: 翻译文本
        """
        if not src or not trans:
            return
            
        async with self.lock:
            # 获取旧值
            cursor = self.db_conn.cursor()
            cursor.execute(f'SELECT {lang} FROM terminology WHERE 中文原文 = ?', (src,))
            row = cursor.fetchone()
            old_value = row[0] if row else None
            
            # 添加或更新术语
            self.persistence.add_terminology(src, lang, trans)
            
            # 记录历史
            if old_value:
                record_term_change(
                    change_type=ChangeType.UPDATED.value,
                    source_text=src,
                    language=lang,
                    old_value=old_value,
                    new_value=trans,
                    batch_id=self._current_batch_id,
                    operator="system"
                )
            else:
                record_term_change(
                    change_type=ChangeType.ADDED.value,
                    source_text=src,
                    language=lang,
                    new_value=trans,
                    batch_id=self._current_batch_id,
                    operator="system"
                )
            
            # 清除相关缓存（数据已变更）
            await self.cache.invalidate_source(src)
            
            # 同时更新 Redis 缓存
            if self._use_redis_cache and self.redis_cache:
                try:
                    # 删除旧的缓存条目
                    await self.redis_cache.delete_terminology(src)
                    # 添加新条目到 Redis Hash
                    await self.redis_cache.add_terminology_translation(src, lang, trans)
                except Exception as e:
                    logger.error(f"Redis 更新失败：{e}")
            
            # 更新统一缓存管理器（自动使版本失效）
            if self.cache_manager:
                try:
                    # 递增版本号，自动使旧缓存失效
                    await self.cache_manager.version_manager.increment_version(self._datasource_name)
                    # 删除特定键的缓存
                    cache_key = f"{src}:{lang}"
                    await self.cache_manager.delete(self._datasource_name, cache_key)
                except Exception as e:
                    logger.error(f"统一缓存更新失败：{e}")
            
            async with self.queue_lock:
                self.queue.append(1)
                self.event.set()

    async def find_similar(self, src: str, lang: str, source_lang: Optional[str] = None) -> Optional[Dict]:
        """
        查找相似翻译（使用 SQLite 内存数据库 + Redis 缓存）
                
        Args:
            src: 源文本
            lang: 目标语言
            source_lang: 源语言 (可选)
                    
        Returns:
            最佳匹配结果
        """
        logger.debug(f"🔍 术语查询：'{src}' -> {lang}")
            
        # 优化 1: 先查 Redis 缓存（如果启用）
        if self._use_redis_cache and self.redis_cache:
            try:
                # 精确匹配
                redis_result = await self.redis_cache.get_exact_match(src, lang)
                if redis_result:
                    self.stats['redis_hits'] = self.stats.get('redis_hits', 0) + 1
                    logger.debug(f"✅ Redis 精确命中：{src} -> {redis_result['translation']}")
                    return redis_result
                    
                # 模糊匹配
                fuzzy_results = await self.redis_cache.get_fuzzy_matches(src, lang)
                if fuzzy_results:
                    self.stats['redis_hits'] = self.stats.get('redis_hits', 0) + 1
                    # 返回得分最高的结果
                    best_match = max(fuzzy_results, key=lambda x: x.get('score', 0))
                    logger.debug(f"✅ Redis 模糊命中：{src} -> {best_match['translation']} (得分:{best_match['score']})")
                    return best_match
                    
                self.stats['redis_misses'] = self.stats.get('redis_misses', 0) + 1
            except Exception as e:
                logger.error(f"Redis 查询失败：{e}")
        
        # 优化 2: 查本地 LRU 缓存
        exact_result = await self.cache.get_exact_match(src, lang)
        if exact_result:
            logger.debug(f"✅ 本地缓存精确命中：{src} -> {exact_result['translation']}")
            return exact_result
            
        # 优化 3: 使用 SQLite 查询
        try:
            cursor = self.db_conn.cursor()
                
            # 查询包含目标语言的记录
            cursor.execute(f'''
                SELECT 中文原文，{lang} 
                FROM terminology 
                WHERE {lang} IS NOT NULL AND {lang} != ''
            ''')
                
            rows = cursor.fetchall()
            items = [(row[0], row[1]) for row in rows]
                
            if not items:
                logger.debug(f"❌ 术语库中无 {lang} 数据")
                return None
                
            # 精确匹配检查
            for source, trans in items:
                if source == src:
                    result = {
                        'original': source,
                        'translation': trans,
                        'score': self.config.exact_match_score
                    }
                    # 同时写入两个缓存
                    await self.cache.set_exact_match(src, lang, result)
                    if self._use_redis_cache and self.redis_cache:
                        await self.redis_cache.set_exact_match(src, lang, result)
                    logger.debug(f"💾 缓存精确匹配结果")
                    return result
                
            # 模糊匹配
            if len(items) > self.config.multiprocess_threshold:
                logger.debug(f"📊 检索术语库... (总数:{len(items)}条)")
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(
                    None,
                    FuzzyMatcher.find_best_match,
                    src,
                    items,
                    self.config.similarity_low
                )
            else:
                res = FuzzyMatcher.find_best_match(src, items, self.config.similarity_low)
                
            # 缓存结果
            if res:
                await self.cache.set_fuzzy_match(src, lang, res, res['score'])
                if self._use_redis_cache and self.redis_cache:
                    # 获取 Top 10 结果一起缓存
                    top_results = await self._get_top_fuzzy_matches(src, lang, items, limit=10)
                    await self.redis_cache.set_fuzzy_matches(src, lang, top_results)
                logger.debug(f"💾 缓存模糊匹配结果 (得分:{res['score']})")
                logger.debug(f"✅ 找到最佳匹配：{src} -> {res['translation']} (得分:{res['score']})")
                return res
            else:
                logger.debug(f"❌ 未找到匹配")
                return None
                    
        except Exception as e:
            logger.error(f"术语查询失败：{e}")
            return None
    
    async def _get_top_fuzzy_matches(self, src: str, lang: str, items: List[Tuple[str, str]], 
                                    limit: int = 10) -> List[Dict]:
        """
        获取 Top N 个模糊匹配结果用于 Redis 缓存
        
        Args:
            src: 源文本
            lang: 目标语言
            items: 术语列表
            limit: 返回数量限制
            
        Returns:
            Top N 匹配结果列表
        """
        from data_access.fuzzy_matcher import FuzzyMatcher
        
        # 使用低阈值获取更多结果
        all_matches = FuzzyMatcher.find_all_matches(src, items, 0.3)
        
        # 按得分排序并取 Top N
        sorted_matches = sorted(all_matches, key=lambda x: x['score'], reverse=True)[:limit]
        
        return sorted_matches
    
    def _on_cache_invalidated(self, datasource: str, key: str, event_type: str):
        """
        缓存失效事件处理器（由统一缓存管理器回调）
        
        Args:
            datasource: 数据源名称
            key: 缓存键
            event_type: 事件类型 ('delete'|'invalidate_datasource')
        """
        logger.debug(f"📢 缓存失效事件：{datasource}:{key} ({event_type})")
        
        # 可以在这里添加其他清理逻辑
        # 例如：通知其他组件缓存已失效

    async def shutdown(self):
        """关闭术语库管理器（由全局管理器统一保存）"""
        self.shutdown_flag = True
        self.event.set()
        
        # 关闭 Redis 连接
        if self._use_redis_cache and self.redis_cache:
            try:
                await self.redis_cache.disconnect()
                logger.info("🔒 Redis 缓存连接已关闭")
            except Exception as e:
                logger.error(f"Redis 关闭失败：{e}")
        
        # 注意：不再单独保存，由全局管理器统一保存所有数据库
        logger.info("🛑 术语库管理器已停止（数据将由全局管理器统一保存）")
    
    async def export_to_excel(self, output_path: str = None, export_new_only: bool = False):
        """
        导出术语库到 Excel 文件
        
        Args:
            output_path: 输出文件路径，如果为 None 则保存到原路径
            export_new_only: 是否只导出新增的术语
        """
        if output_path is None:
            output_path = self.filepath
        
        async with self.lock:
            # 获取要导出的数据
            if export_new_only:
                # 只导出本次会话新增的术语
                export_db = await self._get_new_entries_only()
                if not export_db:
                    logger.info("ℹ️ 本次会话无新增术语")
                    return output_path
            else:
                # 导出完整术语库
                export_db = self.db
            
            if not export_db:
                logger.info("ℹ️ 术语库为空")
                return output_path
            
            # 导出为 Excel
            langs = set()
            for t in export_db.values():
                langs.update(t.keys())
            
            cols = ['Key', '中文原文'] + sorted(langs)
            rows = [
                {'Key': f"TM_{i}", '中文原文': s, **t} 
                for i, (s, t) in enumerate(export_db.items())
            ]
            
            pd.DataFrame(rows, columns=cols).to_excel(
                output_path, 
                index=False, 
                engine='openpyxl'
            )
            
            import logging
            if export_new_only:
                logging.info(f"📊 新增术语已导出：{len(export_db)}条 -> {output_path}")
            else:
                logging.info(f"📊 术语库已导出：{len(export_db)}条 -> {output_path}")
            
            return output_path
    
    async def _get_new_entries_only(self) -> Dict[str, Dict[str, str]]:
        """
        获取本次会话新增的术语条目
        
        Returns:
            新增术语字典
        """
        # 从历史记录中获取本次 batch 的新增术语
        changes = self.history_manager.get_changes(
            batch_id=self._current_batch_id,
            change_type='added'
        )
        
        new_db = {}
        for change in changes:
            src = change.source_text
            lang = change.language
            trans = change.new_value
            
            if src not in new_db:
                new_db[src] = {}
            new_db[src][lang] = trans
        
        return new_db
    
    async def import_from_excel(self, excel_file: str, 
                               update_existing: bool = True) -> ImportResult:
        """
        从 Excel 文件增量导入术语
        
        Args:
            excel_file: Excel 文件路径
            update_existing: 是否更新已存在的条目
            
        Returns:
            导入结果统计
        """
        try:
            importer = TerminologyImporter(excel_file)
            result, new_db = importer.import_to_dict(self.db, update_existing)
            
            # 更新内存中的数据库
            async with self.lock:
                self.db = new_db
                # 触发后台写入
                async with self.queue_lock:
                    self.queue.append(1)
                    self.event.set()
            
            logger.info(
                f"术语库导入完成：新增 {result.new_entries} 条，"
                f"更新 {result.updated_entries} 条，跳过 {result.skipped_rows} 条"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"术语库导入失败：{e}")
            result = ImportResult()
            result.errors.append(str(e))
            return result
    
    async def batch_add_entries(self, entries: List[Tuple[str, str, str]]) -> Dict[str, int]:
        """
        批量添加术语条目
        
        Args:
            entries: (source_text, language, translation) 元组列表
            
        Returns:
            统计信息
        """
        from terminology_update import TerminologyUpdater
        
        async with self.lock:
            updater = TerminologyUpdater(self.db)
            stats = updater.add_batch(entries)
            self.db = updater.db
            
            # 触发后台写入
            if stats['added'] > 0 or stats['updated'] > 0:
                async with self.queue_lock:
                    self.queue.append(1)
                    self.event.set()
            
            return stats
    
    async def remove_entry(self, source_text: str, 
                          language: Optional[str] = None) -> bool:
        """
        删除术语条目
        
        Args:
            source_text: 源文本
            language: 语言，如果为 None 则删除整个源文本的所有翻译
            
        Returns:
            是否删除成功
        """
        from terminology_update import TerminologyUpdater
        
        async with self.lock:
            updater = TerminologyUpdater(self.db)
            
            # 记录删除前的值
            if source_text in self.db:
                if language is None:
                    # 删除整个源文本
                    for lang, trans in self.db[source_text].items():
                        record_term_change(
                            change_type=ChangeType.DELETED.value,
                            source_text=source_text,
                            language=lang,
                            old_value=trans,
                            batch_id=self._current_batch_id,
                            operator="system"
                        )
                else:
                    # 删除特定语言
                    if language in self.db[source_text]:
                        old_value = self.db[source_text][language]
                        record_term_change(
                            change_type=ChangeType.DELETED.value,
                            source_text=source_text,
                            language=language,
                            old_value=old_value,
                            batch_id=self._current_batch_id,
                            operator="system"
                        )
            
            success = updater.remove_entry(source_text, language)
            self.db = updater.db
            
            if success:
                # 触发后台写入
                async with self.queue_lock:
                    self.queue.append(1)
                    self.event.set()
            
            return success
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        获取术语库统计信息
        
        Returns:
            统计信息字典
        """
        from terminology_update import TerminologyUpdater
        
        async with self.lock:
            updater = TerminologyUpdater(self.db)
            stats = updater.get_statistics()
            
            # 添加历史统计信息
            history_stats = self.history_manager.get_statistics(days=30)
            stats['history'] = history_stats
            
            return stats
    
    async def get_history_timeline(self, days: int = 7, 
                                  limit: int = 200) -> List[Dict[str, Any]]:
        """
        获取历史时间线
        
        Args:
            days: 最近多少天
            limit: 返回记录数限制
            
        Returns:
            按天分组的变更记录
        """
        return self.history_manager.get_timeline(days=days, limit=limit)
    
    async def get_history_changes(self, **kwargs) -> List[Dict[str, Any]]:
        """
        获取历史记录详情
        
        Args:
            **kwargs: 查询参数（start_date, end_date, change_type 等）
            
        Returns:
            变更记录列表
        """
        changes = self.history_manager.get_changes(**kwargs)
        return [c.to_dict() for c in changes]
    
    async def create_snapshot(self, notes: str = "") -> int:
        """
        创建术语库快照
        
        Args:
            notes: 备注信息
            
        Returns:
            快照 ID
        """
        async with self.lock:
            return self.history_manager.create_snapshot(
                self.db, 
                batch_id=self._current_batch_id,
                notes=notes
            )
    
    def set_batch_id(self, batch_id: str):
        """
        设置当前批次 ID
        
        Args:
            batch_id: 批次标识
        """
        self._current_batch_id = batch_id
    
    async def export_history(self, output_file: str, 
                            format: str = 'json') -> str:
        """
        导出历史记录
        
        Args:
            output_file: 输出文件路径
            format: 导出格式（json/csv）
            
        Returns:
            输出文件路径
        """
        return self.history_manager.export_history(output_file, format)
    
    # ========== 性能优化方法 ==========
    
    def enable_memory_tracking(self):
        """启用内存跟踪"""
        tracemalloc.start()
        self._memory_tracking_enabled = True
        logger.info("已启用内存跟踪")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        获取内存使用情况
        
        Returns:
            内存使用统计（MB）
        """
        import sys
        
        stats = {
            'db_size_mb': 0.0,
            'cache_stats': {},
            'total_objects': 0
        }
        
        # 计算数据库大小
        db_json = json.dumps(self.db, ensure_ascii=False)
        stats['db_size_mb'] = len(db_json.encode('utf-8')) / (1024 * 1024)
        
        # 获取缓存统计
        if hasattr(self, 'cache'):
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                stats['cache_stats'] = loop.run_until_complete(self.cache.get_stats())
            finally:
                loop.close()
        
        # 内存跟踪信息
        if self._memory_tracking_enabled:
            current, peak = tracemalloc.get_traced_memory()
            stats['current_memory_mb'] = current / (1024 * 1024)
            stats['peak_memory_mb'] = peak / (1024 * 1024)
        
        return stats
    
    async def optimize_memory(self):
        """优化内存使用"""
        import gc
        
        # 强制垃圾回收
        collected = gc.collect()
        logger.info(f"内存优化：回收了 {collected} 个对象")
        
        # 清理缓存
        await self.cache.cleanup_expired(max_age_seconds=1800)  # 30 分钟
        
        # 打印内存使用情况
        if self._memory_tracking_enabled:
            current, peak = tracemalloc.get_traced_memory()
            logger.info(
                f"内存使用：当前={current / 1024 / 1024:.2f}MB, "
                f"峰值={peak / 1024 / 1024:.2f}MB"
            )
    
    async def batch_add_entries_optimized(self, entries: List[Tuple[str, str, str]], 
                                         batch_size: int = 100):
        """
        优化的批量添加方法，分批处理并定期清理内存
        
        Args:
            entries: (source_text, language, translation) 元组列表
            batch_size: 每批处理数量
            
        Returns:
            统计信息
        """
        from terminology_update import TerminologyUpdater
        
        total_stats = {'added': 0, 'updated': 0, 'skipped': 0}
        total_count = len(entries)
        
        logger.info(f"开始批量添加 {total_count} 条术语，分批大小：{batch_size}")
        
        for i in range(0, total_count, batch_size):
            batch = entries[i:i + batch_size]
            
            async with self.lock:
                updater = TerminologyUpdater(self.db)
                stats = updater.add_batch(batch)
                self.db = updater.db
                
                # 更新统计
                for key in total_stats:
                    total_stats[key] += stats[key]
            
            # 触发后台写入
            if stats['added'] > 0 or stats['updated'] > 0:
                async with self.queue_lock:
                    self.queue.append(len(batch))
                    self.event.set()
            
            # 每批处理后进行内存优化
            if (i // batch_size) % 10 == 0:  # 每 10 批
                await self.optimize_memory()
                logger.info(
                    f"批量添加进度：{i}/{total_count} "
                    f"({i/total_count*100:.1f}%), "
                    f"本批新增:{stats['added']}, 更新:{stats['updated']}"
                )
        
        logger.info(
            f"批量添加完成：总计{total_count}条，"
            f"新增:{total_stats['added']}, 更新:{total_stats['updated']}, "
            f"跳过:{total_stats['skipped']}"
        )
        
        return total_stats
    
    def _is_source_lang_match(self, source_text: str, source_lang: str) -> bool:
        """
        判断术语是否匹配指定的源语言
        
        Args:
            source_text: 术语原文
            source_lang: 要匹配的源语言
            
        Returns:
            是否匹配
        """
        # 简化实现：根据字符范围判断源语言
        if source_lang == "中文":
            # 中文字符范围
            return any('\u4e00' <= c <= '\u9fff' for c in source_text)
        elif source_lang == "英语":
            # 英文字符范围（主要是 ASCII）
            return all(c.isascii() and c.isprintable() or c.isspace() for c in source_text)
        elif source_lang == "日语":
            # 日文字符（平假名、片假名）
            return any(
                '\u3040' <= c <= '\u309f' or  # 平假名
                '\u30a0' <= c <= '\u30ff'     # 片假名
                for c in source_text
            )
        elif source_lang == "韩语":
            # 韩文字符（谚文）
            return any('\uac00' <= c <= '\ud7af' for c in source_text)
        elif source_lang in ["法语", "德语", "西班牙语", "意大利语"]:
            # 拉丁字母扩展（带重音符号）
            return any(
                c.isalpha() and ord(c) > 127  # 非 ASCII 字母
                for c in source_text
            )
        else:
            # 未知语言，默认返回 True（不过滤）
            return True
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            性能统计字典
        """
        memory_stats = self.get_memory_usage()
        
        return {
            'memory': memory_stats,
            'database': {
                'total_entries': len(self.db),
                'total_translations': sum(len(t) for t in self.db.values())
            },
            'cache': memory_stats.get('cache_stats', {})
        }
    
    # ========== 版本控制和备份功能 ==========
    
    def enable_version_control(self, repo_path: str = None):
        """
        启用版本控制
        
        Args:
            repo_path: Git 仓库路径（默认为当前工作目录）
        """
        if repo_path is None:
            repo_path = os.getcwd()
        
        self.version_controller = TerminologyVersionController(repo_path, self.filepath)
        self._version_control_enabled = True
        
        # 初始化 Git 仓库（如果需要）
        try:
            self.version_controller.initialize_repo()
            logger.info(f"✅ 版本控制已启用 (仓库：{repo_path})")
        except Exception as e:
            logger.warning(f"版本控制初始化失败：{e}")
            self._version_control_enabled = False
    
    def enable_auto_backup(self, backup_dir: str = ".terminology_backups",
                          strategy: Dict = BackupStrategy.DAILY):
        """
        启用自动备份
        
        Args:
            backup_dir: 备份目录
            strategy: 备份策略（默认每日备份）
        """
        self.backup_manager = AutoBackupManager(self.filepath, backup_dir, strategy)
        self._auto_backup_enabled = True
        logger.info(f"✅ 自动备份已启用 (目录：{backup_dir}, 策略：{strategy['prefix']})")
    
    async def start_auto_backup(self):
        """启动自动备份循环"""
        if self.backup_manager and self._auto_backup_enabled:
            await self.backup_manager.start()
            logger.info("🔄 自动备份循环已启动")
    
    async def stop_auto_backup(self):
        """停止自动备份循环"""
        if self.backup_manager:
            await self.backup_manager.stop()
            logger.info("⏹️ 自动备份循环已停止")
    
    async def commit_changes(self, message: str = "更新术语库"):
        """
        提交术语库更改到 Git
        
        Args:
            message: 提交信息
        """
        if not self._version_control_enabled or not self.version_controller:
            logger.warning("版本控制未启用，跳过提交")
            return False
        
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            lambda: self.version_controller.add_and_commit(message)
        )
        
        if success:
            logger.info(f"✅ 已提交：{message}")
        else:
            logger.warning(f"⚠️ 提交失败或无需提交")
        
        return success
    
    async def create_backup(self, reason: str = "手动备份") -> str:
        """
        创建术语库备份
        
        Args:
            reason: 备份原因
            
        Returns:
            备份文件路径
        """
        # 优先使用备份管理器
        if self.backup_manager and self._auto_backup_enabled:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.backup_manager.create_manual_backup(reason)
            )
        
        # 否则使用版本控制器
        elif self.version_controller and self._version_control_enabled:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.version_controller.create_backup(reason)
            )
        
        else:
            logger.warning("备份功能未启用")
            return ""
    
    def list_backups(self, limit: int = 20) -> List[Dict]:
        """
        列出备份历史
        
        Args:
            limit: 最大返回数量
            
        Returns:
            备份信息列表
        """
        backups = []
        
        # 从备份管理器获取
        if self.backup_manager and self._auto_backup_enabled:
            backups.extend(self.backup_manager.list_backups(limit=limit))
        
        # 从版本控制器获取
        if self.version_controller and self._version_control_enabled:
            vc_backups = self.version_controller.list_backups(limit=limit)
            backups.extend(vc_backups)
        
        # 去重并排序
        seen_paths = set()
        unique_backups = []
        for backup in sorted(backups, key=lambda x: x.get('time', ''), reverse=True):
            if backup['path'] not in seen_paths:
                seen_paths.add(backup['path'])
                unique_backups.append(backup)
        
        return unique_backups[:limit]
    
    async def restore_from_backup(self, backup_path: str) -> bool:
        """
        从备份恢复
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功恢复
        """
        if self.version_controller and self._version_control_enabled:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.version_controller.restore_from_backup(backup_path)
            )
        
        logger.error("版本控制未启用，无法恢复备份")
        return False
    
    def get_version_history(self, limit: int = 10) -> List[Dict]:
        """
        获取版本历史
        
        Args:
            limit: 最大返回数量
            
        Returns:
            版本历史列表
        """
        if not self.version_controller or not self._version_control_enabled:
            return []
        
        return self.version_controller.get_history(limit=limit)
    
    async def shutdown(self):
        """关闭术语库管理器（增加清理逻辑）"""
        # 停止自动备份
        await self.stop_auto_backup()
        
        # 调用父类的 shutdown
        await super().shutdown() if hasattr(super(), 'shutdown') else None
        
        # 原有的关闭逻辑
        self.shutdown_flag = True
        self.event.set()
        
        try:
            await asyncio.wait_for(self.writer_task, timeout=5.0)
        except asyncio.TimeoutError:
            self.writer_task.cancel()
        
        if self.tmp_path and os.path.exists(self.tmp_path):
            try:
                with open(self.tmp_path, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    df = pd.DataFrame([
                        {'中文原文': k, **v} for k, v in snapshot.items()
                    ])
                    df.to_excel(self.filepath, index=False, engine='openpyxl')
                
                os.remove(self.tmp_path)
                logger.info(f"✅ 术语库已保存：{self.filepath}")
                
            except Exception as e:
                logger.error(f"保存术语库失败：{e}")
