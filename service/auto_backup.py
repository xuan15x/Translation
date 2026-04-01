"""
自动备份管理器
定时自动备份术语库，支持多种备份策略
"""
import os
import shutil
import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class BackupStrategy:
    """备份策略配置"""
    
    # 每小时备份
    HOURLY = {
        'interval_seconds': 3600,
        'keep_count': 24,  # 保留 24 小时
        'prefix': 'hourly'
    }
    
    # 每日备份
    DAILY = {
        'interval_seconds': 86400,
        'keep_count': 7,  # 保留 7 天
        'prefix': 'daily'
    }
    
    # 每周备份
    WEEKLY = {
        'interval_seconds': 604800,
        'keep_count': 4,  # 保留 4 周
        'prefix': 'weekly'
    }
    
    # 每次会话后备份
    PER_SESSION = {
        'interval_seconds': 0,  # 特殊值，表示手动触发
        'keep_count': 5,
        'prefix': 'session'
    }


class AutoBackupManager:
    """自动备份管理器"""
    
    def __init__(self, source_path: str, backup_dir: str, 
                 strategy: Dict = BackupStrategy.DAILY):
        """
        初始化备份管理器
        
        Args:
            source_path: 源文件路径
            backup_dir: 备份目录
            strategy: 备份策略配置
        """
        self.source_path = source_path
        self.backup_dir = backup_dir
        self.strategy = strategy
        
        # 确保备份目录存在
        os.makedirs(backup_dir, exist_ok=True)
        
        # 状态变量
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_backup_time: Optional[datetime] = None
        self._backup_count = 0
        
        # 统计信息
        self.stats = {
            'total_backups': 0,
            'failed_backups': 0,
            'last_backup_time': None,
            'last_backup_size': 0
        }
    
    async def start(self):
        """启动自动备份"""
        if self._running:
            logger.warning("自动备份已在运行中")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._backup_loop())
        logger.info(
            f"🔄 自动备份已启动 (间隔:{self.strategy['interval_seconds']}s, "
            f"保留:{self.strategy['keep_count']}个)"
        )
    
    async def stop(self):
        """停止自动备份"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.debug("备份任务已取消")
        
        logger.info("自动备份已停止")
    
    async def _backup_loop(self):
        """备份循环"""
        while self._running:
            try:
                # 等待下一次备份时间
                await asyncio.sleep(self.strategy['interval_seconds'])
                
                if not self._running:
                    break
                
                # 执行备份
                if os.path.exists(self.source_path):
                    await self._create_backup()
                else:
                    logger.debug("源文件不存在，跳过备份")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动备份异常：{e}")
    
    async def _create_backup(self):
        """创建备份（内部方法）"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.strategy['prefix']}_{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, filename)
            
            # 复制文件
            shutil.copy2(self.source_path, backup_path)
            
            # 保存元数据
            metadata = {
                'source_file': self.source_path,
                'backup_time': datetime.now().isoformat(),
                'strategy': self.strategy['prefix'],
                'file_size': os.path.getsize(backup_path),
                'checksum': self._calculate_checksum(backup_path)
            }
            
            metadata_path = backup_path + '.meta.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 更新统计
            self._last_backup_time = datetime.now()
            self._backup_count += 1
            self.stats['total_backups'] += 1
            self.stats['last_backup_time'] = self._last_backup_time.isoformat()
            self.stats['last_backup_size'] = metadata['file_size']
            
            logger.info(f"💾 自动备份已创建：{filename} ({metadata['file_size']} bytes)")
            
            # 清理旧备份
            await self._cleanup_old_backups()
            
        except Exception as e:
            self.stats['failed_backups'] += 1
            logger.error(f"自动备份失败：{e}")
            raise
    
    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件校验和"""
        import hashlib
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def _cleanup_old_backups(self):
        """清理旧备份"""
        try:
            # 获取所有备份文件
            backups = []
            for filename in os.listdir(self.backup_dir):
                if not filename.endswith('.backup'):
                    continue
                if not filename.startswith(f"{self.strategy['prefix']}_"):
                    continue
                
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'mtime': stat.st_mtime,
                    'size': stat.st_size
                })
            
            # 按时间排序
            backups.sort(key=lambda x: x['mtime'], reverse=True)
            
            # 删除超出保留数量的备份
            if len(backups) > self.strategy['keep_count']:
                for backup in backups[self.strategy['keep_count']:]:
                    try:
                        os.remove(backup['path'])
                        metadata_path = backup['path'] + '.meta.json'
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        logger.debug(f"已清理旧备份：{backup['filename']}")
                    except Exception as e:
                        logger.error(f"清理备份失败：{e}")
        
        except Exception as e:
            logger.error(f"清理备份时出错：{e}")
    
    async def create_manual_backup(self, reason: str = "手动备份") -> str:
        """
        手动创建备份
        
        Args:
            reason: 备份原因
            
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"manual_{timestamp}_{reason.replace(' ', '_')}.backup"
        backup_path = os.path.join(self.backup_dir, filename)
        
        try:
            # 复制文件
            shutil.copy2(self.source_path, backup_path)
            
            # 保存元数据
            metadata = {
                'source_file': self.source_path,
                'backup_time': datetime.now().isoformat(),
                'strategy': 'manual',
                'reason': reason,
                'file_size': os.path.getsize(backup_path),
                'checksum': self._calculate_checksum(backup_path)
            }
            
            metadata_path = backup_path + '.meta.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 更新统计
            self._backup_count += 1
            self.stats['total_backups'] += 1
            self.stats['last_backup_time'] = datetime.now().isoformat()
            self.stats['last_backup_size'] = metadata['file_size']
            
            logger.info(f"💾 手动备份已创建：{filename}")
            return backup_path
            
        except Exception as e:
            self.stats['failed_backups'] += 1
            logger.error(f"手动备份失败：{e}")
            raise
    
    def list_backups(self, limit: int = 20) -> List[Dict]:
        """
        列出备份文件
        
        Args:
            limit: 最大返回数量
            
        Returns:
            备份信息列表
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in sorted(os.listdir(self.backup_dir), reverse=True):
            if not filename.endswith('.backup'):
                continue
            
            filepath = os.path.join(self.backup_dir, filename)
            metadata_path = filepath + '.meta.json'
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'time': metadata.get('backup_time', ''),
                    'strategy': metadata.get('strategy', ''),
                    'reason': metadata.get('reason', ''),
                    'size': metadata.get('file_size', 0),
                    'checksum': metadata.get('checksum', '')
                })
            else:
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'strategy': 'unknown',
                    'reason': '',
                    'size': stat.st_size,
                    'checksum': ''
                })
            
            if len(backups) >= limit:
                break
        
        return backups
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'running': self._running,
            'backup_count': self._backup_count,
            'strategy': self.strategy['prefix'],
            'keep_count': self.strategy['keep_count']
        }


# 全局备份管理器实例
_global_backup_manager: Optional[AutoBackupManager] = None


def get_auto_backup_manager(source_path: str, 
                           backup_dir: str = ".terminology_backups",
                           strategy: Dict = BackupStrategy.DAILY) -> AutoBackupManager:
    """获取全局备份管理器实例"""
    global _global_backup_manager
    if _global_backup_manager is None or _global_backup_manager.source_path != source_path:
        _global_backup_manager = AutoBackupManager(source_path, backup_dir, strategy)
    return _global_backup_manager


async def start_auto_backup(source_path: str, strategy: Dict = BackupStrategy.DAILY):
    """启动自动备份"""
    manager = get_auto_backup_manager(source_path, strategy=strategy)
    await manager.start()


async def stop_auto_backup():
    """停止自动备份"""
    global _global_backup_manager
    if _global_backup_manager:
        await _global_backup_manager.stop()


async def create_backup(reason: str = "手动备份") -> str:
    """创建手动备份"""
    if _global_backup_manager:
        return await _global_backup_manager.create_manual_backup(reason)
    else:
        raise RuntimeError("备份管理器未初始化")
