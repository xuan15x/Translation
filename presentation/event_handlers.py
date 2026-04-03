"""
GUI事件处理器
将事件处理逻辑从主GUI类中分离出来
"""
import asyncio
import logging
import threading
from typing import Optional
from datetime import datetime
from tkinter import messagebox

from presentation.gui_constants import *
from presentation.error_handler import show_error_dialog, log_error_with_solution

logger = logging.getLogger(__name__)


class TranslationEventHandler:
    """翻译事件处理器"""

    def __init__(self, app):
        self.app = app

    def start_translation(self):
        """启动翻译（使用线程避免阻塞UI）"""
        # 使用线程执行异步操作，避免阻塞Tkinter主循环
        thread = threading.Thread(target=self._run_translation_async, daemon=True)
        thread.start()

    def _run_translation_async(self):
        """在线程中运行翻译任务"""
        try:
            # 在新线程中创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._execute_translation())
            finally:
                loop.close()
        except Exception as e:
            # 错误会通过回调报告
            logger.error(f"翻译线程异常: {e}", exc_info=True)
            self.app.root.after(0, self._handle_translation_error, e)

    async def _execute_translation(self):
        """执行翻译任务"""
        try:
            self.app._initialize_services()

            if not self.app.source_path.get():
                self.app.root.after(0, lambda: messagebox.showwarning("警告", "请选择待翻译文件"))
                return

            if not self.app.selected_langs:
                self.app.root.after(0, lambda: messagebox.showwarning("警告", "请至少选择一个目标语言"))
                return

            # 更新UI状态
            self.app.translation_vm.start_translation()
            self.app.root.after(0, self._update_ui_for_running_translation)

            # 获取源语言
            selected_source_lang = self.app.source_lang_var.get()
            source_lang = None if selected_source_lang == "自动检测" else selected_source_lang

            # 生成批次ID
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 确定输出路径
            output_path = self.app.output_path.get().strip() if self.app.output_path.get() else None
            if not output_path:
                output_path = None

            # 执行翻译
            result = await self.app.translation_facade.translate_file(
                source_excel_path=self.app.source_path.get(),
                target_langs=self.app.selected_langs,
                output_excel_path=output_path,
                concurrency_limit=DEFAULT_CONCURRENCY_LIMIT,
                source_lang=source_lang
            )

            # 记录历史
            if self.app.translation_history_manager and hasattr(result, 'results'):
                await self._record_translation_history(result, batch_id)

            # 更新完成状态
            success_rate = result.success_rate
            self.app.root.after(0, self._handle_translation_complete, success_rate)

        except Exception as e:
            logger.error(f"翻译执行失败: {e}", exc_info=True)
            self.app.root.after(0, self._handle_translation_error, e)
        finally:
            self.app.root.after(0, self._cleanup_after_translation)

    def _update_ui_for_running_translation(self):
        """更新UI为运行中状态"""
        self.app.start_btn.config(state='disabled')
        self.app.stop_btn.config(state='normal')
        self.app.pause_btn.config(state='normal')
        self.app.pause_btn.config(text="⏸️ 暂停")
        
        # 显示预览面板
        if not self.app.preview_frame.winfo_ismapped():
            self.app.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    async def _record_translation_history(self, result, batch_id):
        """记录翻译历史"""
        try:
            api_provider = self.app.current_provider_var.get()
            draft_model = self.app.draft_model_var.get() or "default"
            file_path = self.app.source_path.get()

            for translation_result in result.results:
                try:
                    from service.translationation_history import record_translation
                    record_translation(
                        result=translation_result,
                        api_provider=api_provider,
                        model_name=draft_model,
                        file_path=file_path,
                        batch_id=batch_id
                    )
                except Exception as e:
                    logger.debug(f"单条历史记录失败: {e}")

            logger.info(f"📝 已记录 {len(result.results)} 条翻译历史到批次 {batch_id}")
        except Exception as e:
            logger.error(f"记录历史失败: {e}")

    def _handle_translation_complete(self, success_rate: float):
        """处理翻译完成"""
        self.app.translation_vm.complete_translation(success_rate)
        messagebox.showinfo("完成", f"翻译完成！\n成功率：{success_rate:.1f}%")
        
        # 保存常用语言
        if self.app.selected_langs:
            self.app._save_favorite_languages(self.app.selected_langs)

    def _handle_translation_error(self, error: Exception):
        """处理翻译错误"""
        log_error_with_solution(error, logger)
        show_error_dialog("翻译失败", error, self.app.root)

    def _cleanup_after_translation(self):
        """清理翻译后的状态"""
        self.app.translation_vm.reset()
        self.app.start_btn.config(state='normal')
        self.app.stop_btn.config(state='disabled')
        self.app.pause_btn.config(state='disabled')
        self.app.pause_btn.config(text="⏸️ 暂停")
        self.app.progress_var.set(0)

    def stop_translation(self):
        """停止翻译"""
        self.app.translation_vm.stop_translation()
        
        if self.app.translation_facade and hasattr(self.app.translation_facade, 'stop'):
            self.app.translation_facade.stop()

        self._cleanup_after_translation()
        logger.info("⏹️ 用户取消翻译")

    def pause_translation(self):
        """暂停翻译"""
        if not self.app.translation_vm.is_running:
            return

        if not self.app.translation_vm.is_paused:
            self.app.translation_vm.pause_translation()
            self.app.pause_btn.config(text="▶️ 恢复")
            
            if self.app.translation_facade and hasattr(self.app.translation_facade, 'pause'):
                self.app.translation_facade.pause()
            
            logger.info("⏸️ 用户暂停翻译")
        else:
            self.app.translation_vm.resume_translation()
            self.app.pause_btn.config(text="⏸️ 暂停")
            
            if self.app.translation_facade and hasattr(self.app.translation_facade, 'resume'):
                self.app.translation_facade.resume()
            
            logger.info("▶️ 用户恢复翻译")


class SessionEventHandler:
    """会话事件处理器"""

    def __init__(self, app):
        self.app = app

    def save_current_session(self):
        """保存当前会话"""
        if not self.app.session_manager:
            return

        try:
            session = self.app.session_manager.get_current_session()
            if not session:
                session = self.app.session_manager.create_session()

            self.app.session_manager.update_session(
                term_file_path=self.app.term_path.get(),
                source_file_path=self.app.source_path.get(),
                translation_mode=self.app.mode_var.get(),
                api_provider=self.app.current_provider_var.get(),
                draft_model=self.app.draft_model_var.get(),
                draft_temperature=self.app.draft_temp_var.get(),
                draft_top_p=self.app.draft_top_p_var.get(),
                draft_timeout=self.app.draft_timeout_var.get(),
                draft_max_tokens=self.app.draft_max_tokens_var.get(),
                review_model=self.app.review_model_var.get(),
                review_temperature=self.app.review_temp_var.get(),
                review_top_p=self.app.review_top_p_var.get(),
                review_timeout=self.app.review_timeout_var.get(),
                review_max_tokens=self.app.review_max_tokens_var.get(),
                translation_type=self.app.translation_type_var.get(),
                enable_performance_monitor=self.app.perf_monitor_var.get() if hasattr(self.app, 'perf_monitor_var') else False
            )

            logger.debug("💾 会话配置已保存")
        except Exception as e:
            logger.error(f"保存会话失败: {e}")

    def load_last_session(self):
        """加载上次会话"""
        if not self.app.session_manager:
            return

        session = self.app.session_manager.load_from_file()
        if not session:
            logger.info("ℹ️ 未找到上次的会话配置")
            return

        logger.info("🔄 正在还原上次的会话配置...")
        self._apply_session_to_ui(session)

    def _apply_session_to_ui(self, session):
        """将会话配置应用到UI"""
        if session.term_file_path:
            self.app.term_path.set(session.term_file_path)

        if session.source_file_path:
            self.app.source_path.set(session.source_file_path)

        self.app.mode_var.set(session.translation_mode)
        self.app.current_provider_var.set(session.api_provider)

        # 双阶段参数
        if session.draft_model:
            self.app.draft_model_var.set(session.draft_model)
        self.app.draft_temp_var.set(session.draft_temperature)
        self.app.draft_top_p_var.set(session.draft_top_p)
        self.app.draft_timeout_var.set(session.draft_timeout)
        self.app.draft_max_tokens_var.set(session.draft_max_tokens)

        if session.review_model:
            self.app.review_model_var.set(session.review_model)
        self.app.review_temp_var.set(session.review_temperature)
        self.app.review_top_p_var.set(session.review_top_p)
        self.app.review_timeout_var.set(session.review_timeout)
        self.app.review_max_tokens_var.set(session.review_max_tokens)

        if session.translation_type:
            self.app.translation_type_var.set(session.translation_type)

        logger.debug("✅ 会话配置已还原到UI")
