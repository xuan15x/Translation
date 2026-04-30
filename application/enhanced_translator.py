"""
增强型翻译器 v2.0
支持断点续传、实时进度显示、翻译预览等功能

核心特性:
1. 行级断点续传 - 暂停/恢复时精确到行号
2. 实时进度显示 - 支持GUI实时更新
3. 翻译预览 - 显示已完成的翻译结果
4. 状态持久化 - 保存翻译状态到文件
5. 优雅暂停 - 完成当前行后安全暂停
"""
import asyncio
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class TranslationState:
    """翻译状态数据类 - 用于断点续传"""
    batch_id: str = ""
    source_file: str = ""
    output_file: str = ""
    target_langs: List[str] = field(default_factory=list)
    current_line: int = 0
    total_lines: int = 0
    completed_lines: int = 0
    failed_lines: int = 0
    is_paused: bool = False
    is_running: bool = False
    start_time: str = ""
    pause_time: str = ""
    resume_time: str = ""
    completed_rows: List[Dict[str, Any]] = field(default_factory=list)  # 已完成的行
    failed_rows: List[Dict[str, Any]] = field(default_factory=list)  # 失败的行
    preview_rows: List[Dict[str, Any]] = field(default_factory=list)  # 预览用的前N行
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationState':
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def save(self, state_file: str) -> None:
        """保存状态到文件"""
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.debug(f"💾 翻译状态已保存: {state_file}")
    
    @classmethod
    def load(cls, state_file: str) -> Optional['TranslationState']:
        """从文件加载状态"""
        if not os.path.exists(state_file):
            return None
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"❌ 加载翻译状态失败: {e}")
            return None


@dataclass
class TranslationProgress:
    """翻译进度数据类 - 用于实时显示"""
    current_line: int = 0
    total_lines: int = 0
    completed_lines: int = 0
    failed_lines: int = 0
    speed: float = 0.0  # 行/秒
    eta_seconds: float = 0.0  # 预计剩余时间
    current_text: str = ""  # 当前翻译的文本
    preview_text: str = ""  # 预览文本
    status: str = "running"  # running, paused, stopped, completed
    
    @property
    def percentage(self) -> float:
        """进度百分比"""
        return (self.completed_lines / self.total_lines * 100) if self.total_lines > 0 else 0.0


class EnhancedTranslator:
    """
    增强型翻译器
    
    支持功能:
    - 行级断点续传
    - 实时进度回调
    - 翻译预览
    - 优雅暂停/恢复
    - 状态持久化
    """
    
    def __init__(
        self,
        translation_facade,
        state_dir: str = ".translation_state",
        preview_lines: int = 10
    ):
        """
        初始化增强型翻译器
        
        Args:
            translation_facade: 翻译外观实例
            state_dir: 状态文件存储目录
            preview_lines: 预览行数
        """
        self.facade = translation_facade
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.preview_lines = preview_lines
        
        # 当前翻译状态
        self.state: Optional[TranslationState] = None
        self.progress = TranslationProgress()
        
        # 控制标志（使用threading.Event保证GUI线程安全）
        self._pause_event = threading.Event()
        self._pause_event.set()  # 默认运行状态
        self._stop_flag = False
        
        # 回调函数
        self.on_progress: Optional[Callable[[TranslationProgress], None]] = None
        self.on_preview: Optional[Callable[[List[Dict]], None]] = None
        self.on_complete: Optional[Callable[[TranslationState], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # 性能统计
        self._start_time = None
        self._last_update_time = None
        self._lines_per_second = 0.0
    
    async def translate_with_resume(
        self,
        source_excel_path: str,
        target_langs: List[str],
        output_excel_path: Optional[str] = None,
        concurrency_limit: int = 10,
        source_lang: Optional[str] = None,
        batch_size: int = 100
    ) -> TranslationState:
        """
        执行翻译（支持断点续传）
        
        Args:
            source_excel_path: 源Excel路径
            target_langs: 目标语言列表
            output_excel_path: 输出路径（可选）
            concurrency_limit: 并发限制
            source_lang: 源语言
            batch_size: 批次大小
            
        Returns:
            TranslationState: 翻译状态
        """
        try:
            # 生成批次ID
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            state_file = self.state_dir / f"{batch_id}.json"
            
            # 检查是否有可恢复的状态
            resume_state = self._find_resume_state(source_excel_path, target_langs)
            
            if resume_state:
                logger.info(f"🔄 发现可恢复的翻译状态: {resume_state.batch_id}")
                logger.info(f"   已完成: {resume_state.completed_lines}/{resume_state.total_lines} 行")
                logger.info(f"   从第 {resume_state.current_line + 1} 行继续")
                
                self.state = resume_state
                self.state.is_running = True
                self.state.is_paused = False
                self.state.resume_time = datetime.now().isoformat()
            else:
                # 创建新状态
                self.state = TranslationState(
                    batch_id=batch_id,
                    source_file=source_excel_path,
                    output_file=output_excel_path or "",
                    target_langs=target_langs,
                    start_time=datetime.now().isoformat()
                )
                
                # 读取源文件
                logger.info(f"📖 读取源文件: {source_excel_path}")
                source_data = await self._read_source_file(source_excel_path)
                self.state.total_lines = len(source_data)
                self.state.current_line = 0
            
            # 保存初始状态
            self.state.save(str(state_file))
            
            # 执行翻译
            await self._execute_translation(
                source_excel_path=source_excel_path,
                target_langs=target_langs,
                output_excel_path=output_excel_path,
                concurrency_limit=concurrency_limit,
                source_lang=source_lang,
                batch_size=batch_size,
                state_file=str(state_file)
            )
            
            return self.state
            
        except Exception as e:
            logger.error(f"❌ 翻译失败: {e}")
            if self.on_error:
                self.on_error(e)
            raise
    
    def pause(self) -> bool:
        """
        暂停翻译（优雅暂停 - 完成当前行后暂停）
        
        Returns:
            bool: 是否成功暂停
        """
        if not self.state or not self.state.is_running:
            logger.warning("⚠️ 翻译未在运行，无法暂停")
            return False
        
        logger.info("⏸️ 请求暂停翻译...")
        self.state.is_paused = True
        self.state.pause_time = datetime.now().isoformat()
        self._pause_event.clear()  # 阻止继续执行
        
        # 保存状态
        if self.state:
            state_file = self.state_dir / f"{self.state.batch_id}.json"
            self.state.save(str(state_file))
        
        return True
    
    def resume(self) -> bool:
        """
        恢复翻译
        
        Returns:
            bool: 是否成功恢复
        """
        if not self.state or not self.state.is_paused:
            logger.warning("⚠️ 翻译未暂停，无法恢复")
            return False
        
        logger.info("▶️ 恢复翻译...")
        self.state.is_paused = False
        self.state.resume_time = datetime.now().isoformat()
        self._pause_event.set()  # 允许继续执行
        
        # 保存状态
        if self.state:
            state_file = self.state_dir / f"{self.state.batch_id}.json"
            self.state.save(str(state_file))
        
        return True
    
    def stop(self) -> bool:
        """
        停止翻译（立即停止）
        
        Returns:
            bool: 是否成功停止
        """
        if not self.state or not self.state.is_running:
            logger.warning("⚠️ 翻译未在运行，无法停止")
            return False
        
        logger.info("⏹️ 请求停止翻译...")
        self._stop_flag = True
        self._pause_event.set()  # 释放阻塞
        
        if self.state:
            self.state.is_running = False
            self.state.is_paused = False
        
        return True
    
    async def _execute_translation(
        self,
        source_excel_path: str,
        target_langs: List[str],
        output_excel_path: Optional[str],
        concurrency_limit: int,
        source_lang: Optional[str],
        batch_size: int,
        state_file: str
    ) -> None:
        """
        执行翻译逻辑
        
        Args:
            source_excel_path: 源文件路径
            target_langs: 目标语言列表
            output_excel_path: 输出路径
            concurrency_limit: 并发限制
            source_lang: 源语言
            batch_size: 批次大小
            state_file: 状态文件路径
        """
        import time
        import pandas as pd
        
        # 读取源数据
        df = pd.read_excel(source_excel_path)
        total_rows = len(df)
        
        # 从上次完成的位置继续
        start_row = self.state.current_line
        
        logger.info(f"🚀 开始翻译: {start_row}/{total_rows} 行")
        
        # 逐行翻译
        for idx in range(start_row, total_rows):
            # 检查停止标志
            if self._stop_flag:
                logger.info(f"⏹️ 翻译已停止在第 {idx} 行")
                break
            
            # 检查暂停标志（等待恢复，使用run_in_executor避免阻塞事件循环）
            if self.state.is_paused:
                logger.info(f"⏸️ 翻译已暂停，等待恢复... (第 {idx} 行)")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._pause_event.wait)
                logger.info(f"▶️ 翻译已恢复，继续第 {idx} 行")
            
            try:
                # 更新当前行号
                self.state.current_line = idx + 1
                
                # 获取当前行数据
                row_data = df.iloc[idx].to_dict()
                
                # 执行单行翻译（调用facade）
                translated_row = await self._translate_single_row(
                    row_data=row_data,
                    target_langs=target_langs,
                    source_lang=source_lang
                )
                
                # 保存已完成的行
                self.state.completed_lines += 1
                self.state.completed_rows.append(translated_row)
                
                # 更新预览（前N行）
                if len(self.state.preview_rows) < self.preview_lines:
                    self.state.preview_rows.append(translated_row)
                    if self.on_preview:
                        self.on_preview(self.state.preview_rows)
                
                # 更新进度
                self._update_progress(idx + 1, total_rows)
                
                # 保存状态（每10行保存一次）
                if (idx + 1) % 10 == 0:
                    self.state.save(state_file)
                
                # 批次达到时保存中间状态（仅保存状态文件，不写入Excel避免覆盖）
                if len(self.state.completed_rows) >= batch_size:
                    state_file_path = state_file
                    self.state.save(state_file_path)
                    logger.debug(f"💾 中间状态已保存: {self.state.completed_lines} 行已完成")
                
            except Exception as e:
                logger.error(f"❌ 第 {idx + 1} 行翻译失败: {e}")
                self.state.failed_lines += 1
                self.state.failed_rows.append({
                    'row_index': idx,
                    'error': str(e),
                    'data': row_data
                })
        
        # 保存所有已完成的数据到Excel（一次性写入，避免覆盖丢失）
        if self.state.completed_rows:
            await self._save_batch_to_excel(
                self.state.completed_rows,
                output_excel_path or self._generate_output_path(source_excel_path)
            )
            logger.info(f"📁 翻译结果已写入: {len(self.state.completed_rows)} 行")
        
        # 完成翻译
        if not self._stop_flag:
            self.state.is_running = False
            self.state.is_paused = False
            logger.info(f"✅ 翻译完成! 成功: {self.state.completed_lines}, 失败: {self.state.failed_lines}")
            
            if self.on_complete:
                self.on_complete(self.state)
    
    async def _translate_single_row(
        self,
        row_data: Dict[str, Any],
        target_langs: List[str],
        source_lang: Optional[str]
    ) -> Dict[str, Any]:
        """
        翻译单行数据
        
        Args:
            row_data: 行数据
            target_langs: 目标语言列表
            source_lang: 源语言
            
        Returns:
            翻译后的行数据
        """
        # 调用facade的翻译方法
        # 这里需要根据实际的facade API调整
        text_to_translate = row_data.get('source_text', '')
        
        if not text_to_translate:
            return row_data
        
        # 对每个目标语言进行翻译
        translated_row = row_data.copy()
        
        for target_lang in target_langs:
            # 调用facade翻译
            translated_text = await self.facade.translate_text(
                text=text_to_translate,
                target_lang=target_lang,
                source_lang=source_lang
            )
            translated_row[target_lang] = translated_text
        
        return translated_row
    
    async def _read_source_file(self, source_path: str) -> List[Dict]:
        """读取源文件"""
        import pandas as pd
        df = pd.read_excel(source_path)
        return df.to_dict('records')
    
    def _generate_output_path(self, source_path: str) -> str:
        """生成输出文件路径"""
        from pathlib import Path
        
        source = Path(source_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"{source.stem}_translated_{timestamp}.xlsx"
        return str(source.parent / output_name)
    
    async def _save_batch_to_excel(
        self,
        rows: List[Dict],
        output_path: str
    ) -> None:
        """保存批次数据到Excel"""
        import pandas as pd
        
        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)
        logger.debug(f"💾 已保存 {len(rows)} 行到: {output_path}")
    
    def _update_progress(self, current: int, total: int) -> None:
        """更新进度"""
        import time
        
        now = time.time()
        
        # 计算速度
        if self._last_update_time:
            elapsed = now - self._last_update_time
            if elapsed > 0:
                self._lines_per_second = (current - self.progress.current_line) / elapsed
        
        self._last_update_time = now
        
        # 更新进度对象
        self.progress.current_line = current
        self.progress.total_lines = total
        self.progress.completed_lines = self.state.completed_lines if self.state else 0
        self.progress.failed_lines = self.state.failed_lines if self.state else 0
        self.progress.speed = self._lines_per_second
        
        remaining = total - current
        self.progress.eta_seconds = remaining / self._lines_per_second if self._lines_per_second > 0 else 0
        
        # 调用进度回调
        if self.on_progress:
            self.on_progress(self.progress)
    
    def _find_resume_state(
        self,
        source_file: str,
        target_langs: List[str]
    ) -> Optional[TranslationState]:
        """查找可恢复的翻译状态"""
        state_files = list(self.state_dir.glob("batch_*.json"))
        
        for state_file in sorted(state_files, reverse=True):
            try:
                state = TranslationState.load(str(state_file))
                if state and state.source_file == source_file:
                    # 检查目标语言是否匹配
                    if set(state.target_langs) == set(target_langs):
                        # 检查是否未完成
                        if state.current_line < state.total_lines:
                            return state
            except Exception as e:
                logger.debug(f"跳过无效状态文件: {state_file}, 错误: {e}")
        
        return None
    
    def cleanup_old_states(self, days: int = 7) -> None:
        """清理旧的状态文件"""
        import time
        
        cutoff_time = time.time() - (days * 86400)
        
        for state_file in self.state_dir.glob("batch_*.json"):
            if state_file.stat().st_mtime < cutoff_time:
                state_file.unlink()
                logger.debug(f"🗑️ 已清理旧状态文件: {state_file}")
