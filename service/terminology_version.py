jianc"""
术语库版本控制模块
基于 Git 的术语库版本管理，支持协作和历史追溯
"""
import os
import shutil
import subprocess
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import json

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from infrastructure.exceptions import FileError

logger = logging.getLogger(__name__)


class VersionControlError(Exception):
    """版本控制异常 - 已迁移至 infrastructure.exceptions"""
    # 为了向后兼容保留此类，建议使用新的 VersionControlError from infrastructure.exceptions
    pass


class TerminologyVersionController:
    """术语库版本控制器"""
    
    def __init__(self, repo_path: str, file_path: str):
        """
        初始化版本控制器
        
        Args:
            repo_path: Git 仓库路径（通常是项目根目录）
            file_path: 术语库文件路径
        """
        self.repo_path = repo_path
        self.file_path = file_path
        self.relative_path = os.path.relpath(file_path, repo_path)
        
        # Git 相关路径
        self.git_dir = os.path.join(repo_path, '.git')
        self.backup_dir = os.path.join(repo_path, '.terminology_backups')
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        
        if not os.path.exists(self.git_dir):
            logger.warning(f"未在 {repo_path} 找到 Git 仓库")
    
    def is_git_repo(self) -> bool:
        """检查是否是 Git 仓库"""
        return os.path.exists(self.git_dir)
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """运行 Git 命令"""
        cmd = ['git'] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Git 命令失败：{cmd}, 错误：{e.stderr}")
            raise VersionControlError(f"Git 命令失败：{e.stderr}")
    
    def initialize_repo(self):
        """初始化 Git 仓库（如果不存在）"""
        if not self.is_git_repo():
            logger.info(f"正在 {self.repo_path} 初始化 Git 仓库...")
            self._run_git_command(['init'])
            
            # 创建 .gitignore
            gitignore_path = os.path.join(self.repo_path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write("# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n\n")
                    f.write("# 虚拟环境\n.venv/\nenv/\nvenv/\n\n")
                    f.write("# 临时文件\n*.tmp\n*.log\n\n")
                logger.info("已创建 .gitignore")
    
    def add_and_commit(self, message: str, auto_add: bool = True) -> bool:
        """
        添加并提交更改
        
        Args:
            message: 提交信息
            auto_add: 是否自动添加文件
            
        Returns:
            是否成功提交
        """
        if not self.is_git_repo():
            logger.warning("不是 Git 仓库，跳过提交")
            return False
        
        try:
            # 添加文件
            if auto_add and os.path.exists(self.file_path):
                self._run_git_command(['add', self.relative_path])
            
            # 提交
            result = self._run_git_command(
                ['commit', '-m', message],
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"✅ 已提交：{message}")
                return True
            else:
                logger.warning(f"提交失败（可能没有更改）：{result.stderr.strip()}")
                return False
                
        except VersionControlError as e:
            logger.error(f"提交失败：{e}")
            return False
    
    def create_backup(self, reason: str = "手动备份") -> str:
        """
        创建术语库备份
        
        Args:
            reason: 备份原因
            
        Returns:
            备份文件路径
        """
        if not os.path.exists(self.file_path):
            logger.warning("术语库文件不存在，无法备份")
            return ""
        
        # 生成带时间戳的备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{os.path.basename(self.file_path)}.{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # 复制文件
            shutil.copy2(self.file_path, backup_path)
            
            # 保存备份元数据
            metadata = {
                'original_file': self.file_path,
                'backup_time': datetime.now().isoformat(),
                'reason': reason,
                'file_size': os.path.getsize(backup_path),
                'checksum': self._calculate_checksum(backup_path)
            }
            
            metadata_path = backup_path + '.meta.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 已创建备份：{backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"备份失败：{e}")
            raise VersionControlError(f"备份失败：{e}")
    
    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件校验和（简单 MD5）"""
        import hashlib
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def list_backups(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出最近的备份
        
        Args:
            limit: 最大返回数量
            
        Returns:
            备份信息列表
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        # 查找所有备份文件
        for filename in sorted(os.listdir(self.backup_dir), reverse=True):
            if not filename.endswith('.backup'):
                continue
            
            backup_path = os.path.join(self.backup_dir, filename)
            metadata_path = backup_path + '.meta.json'
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                backups.append({
                    'filename': filename,
                    'path': backup_path,
                    'time': metadata.get('backup_time', ''),
                    'reason': metadata.get('reason', ''),
                    'size': metadata.get('file_size', 0),
                    'checksum': metadata.get('checksum', '')
                })
            else:
                # 没有元数据，使用文件信息
                stat = os.stat(backup_path)
                backups.append({
                    'filename': filename,
                    'path': backup_path,
                    'time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'reason': '未知',
                    'size': stat.st_size,
                    'checksum': ''
                })
            
            if len(backups) >= limit:
                break
        
        return backups
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从备份恢复
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功恢复
        """
        if not os.path.exists(backup_path):
            logger.error(f"备份文件不存在：{backup_path}")
            return False
        
        try:
            # 先备份当前版本
            if os.path.exists(self.file_path):
                self.create_backup("恢复前自动备份")
            
            # 恢复文件
            shutil.copy2(backup_path, self.file_path)
            logger.info(f"✅ 已从备份恢复：{backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"恢复失败：{e}")
            return False
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取 Git 提交历史
        
        Args:
            limit: 最大返回数量
            
        Returns:
            提交历史列表
        """
        if not self.is_git_repo():
            return []
        
        try:
            result = self._run_git_command([
                'log', '--oneline', 
                '--follow', '--', self.relative_path,
                f'-n{limit}'
            ])
            
            history = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(' ', 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    message = parts[1]
                    
                    # 获取详细信息
                    detail_result = self._run_git_command([
                        'show', '-s', '--format=%an|%ae|%ai', commit_hash
                    ])
                    
                    detail_parts = detail_result.stdout.strip().split('|')
                    author_name = detail_parts[0] if len(detail_parts) > 0 else ''
                    author_email = detail_parts[1] if len(detail_parts) > 1 else ''
                    commit_time = detail_parts[2] if len(detail_parts) > 2 else ''
                    
                    history.append({
                        'commit': commit_hash,
                        'message': message,
                        'author': f"{author_name} <{author_email}>",
                        'time': commit_time
                    })
            
            return history
            
        except VersionControlError:
            return []
    
    def diff_versions(self, version1: str, version2: str) -> str:
        """
        比较两个版本的差异
        
        Args:
            version1: 版本 1（commit hash）
            version2: 版本 2（commit hash）
            
        Returns:
            差异文本
        """
        if not self.is_git_repo():
            return "不是 Git 仓库"
        
        try:
            result = self._run_git_command([
                'diff', f'{version1}..{version2}', '--', self.relative_path
            ])
            return result.stdout
            
        except VersionControlError as e:
            return f"比较失败：{e}"
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """
        清理旧备份
        
        Args:
            keep_days: 保留最近 N 天的备份
            keep_count: 至少保留 N 个备份
        """
        backups = self.list_backups(limit=100)
        
        if len(backups) <= keep_count:
            logger.info(f"备份数量不足 {keep_count} 个，不清理")
            return
        
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)
        removed_count = 0
        
        for i, backup in enumerate(backups):
            # 保留最近的 keep_count 个备份
            if i < keep_count:
                continue
            
            # 检查备份时间
            try:
                backup_time = datetime.fromisoformat(backup['time']).timestamp()
                
                if backup_time < cutoff_date:
                    # 删除备份文件和元数据
                    try:
                        os.remove(backup['path'])
                        metadata_path = backup['path'] + '.meta.json'
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        removed_count += 1
                        logger.debug(f"已删除旧备份：{backup['filename']}")
                    except Exception as e:
                        logger.error(f"删除备份失败：{e}")
            except Exception as e:
                logger.error(f"处理备份失败：{e}")
        
        logger.info(f"✅ 已清理 {removed_count} 个旧备份")


# 全局版本控制器实例
_global_version_controller: Optional[TerminologyVersionController] = None


def get_version_controller(repo_path: str, file_path: str) -> TerminologyVersionController:
    """获取全局版本控制器实例"""
    global _global_version_controller
    if _global_version_controller is None:
        _global_version_controller = TerminologyVersionController(repo_path, file_path)
    return _global_version_controller


async def auto_commit_changes(message: str = "自动提交术语库变更"):
    """自动提交术语库变更"""
    from terminology_manager import TerminologyManager
    from models import Config
    
    # 获取当前术语库路径（从配置或默认值）
    config = Config()
    term_path = config.term_path if hasattr(config, 'term_path') else "terms.xlsx"
    
    controller = get_version_controller(os.getcwd(), term_path)
    
    # 异步执行同步操作
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None,
        lambda: controller.add_and_commit(message)
    )
    
    if success:
        logger.info("✅ 自动提交成功")
    else:
        logger.warning("⚠️ 自动提交失败或无需提交")


async def create_manual_backup(reason: str = "手动备份"):
    """手动创建备份"""
    from models import Config
    
    config = Config()
    term_path = config.term_path if hasattr(config, 'term_path') else "terms.xlsx"
    
    controller = get_version_controller(os.getcwd(), term_path)
    
    loop = asyncio.get_event_loop()
    backup_path = await loop.run_in_executor(
        None,
        lambda: controller.create_backup(reason)
    )
    
    logger.info(f"💾 备份已创建：{backup_path}")
    return backup_path
