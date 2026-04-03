"""
GUI事件处理器
将事件处理逻辑从主GUI类中分离出来
"""
import asyncio
import logging
import threading
import tkinter as tk
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
        logger.info("="*60)
        logger.info("🚀 用户点击开始翻译按钮")
        logger.info("="*60)
        
        # 记录当前状态
        logger.debug(f"当前状态:")
        logger.debug(f"  - 源文件: {self.app.source_path.get() or '未选择'}")
        logger.debug(f"  - 术语库: {self.app.term_path.get() or '未选择'}")
        logger.debug(f"  - 目标语言: {self.app.selected_langs}")
        logger.debug(f"  - 翻译模式: {self.app.translation_mode_var.get()}")
        logger.debug(f"  - API提供商: {self.app.current_provider_var.get()}")
        logger.debug(f"  - 源语言: {self.app.source_lang_var.get()}")
        
        # 使用线程执行异步操作，避免阻塞Tkinter主循环
        logger.debug("创建翻译线程...")
        thread = threading.Thread(target=self._run_translation_async, daemon=True)
        thread.start()
        logger.info("✅ 翻译线程已启动")

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
        logger.info("🚀 开始执行翻译任务...")
        try:
            logger.debug("步骤1: 初始化服务...")
            self.app._initialize_services()
            logger.info("✅ 服务初始化完成")

            # 验证输入
            logger.debug("步骤2: 验证输入参数...")
            source_file = self.app.source_path.get()
            logger.debug(f"  - 源文件: {source_file}")
            logger.debug(f"  - 目标语言数量: {len(self.app.selected_langs)}")
            logger.debug(f"  - 目标语言列表: {self.app.selected_langs}")
            
            if not source_file:
                logger.warning("⚠️ 未选择源文件")
                self.app.root.after(0, lambda: messagebox.showwarning("警告", "请选择待翻译文件"))
                return

            if not self.app.selected_langs:
                logger.warning("⚠️ 未选择目标语言")
                self.app.root.after(0, lambda: messagebox.showwarning("警告", "请至少选择一个目标语言"))
                return

            # 更新UI状态
            logger.debug("步骤3: 更新UI状态为运行中...")
            self.app.translation_vm.start_translation()
            self.app.root.after(0, self._update_ui_for_running_translation)
            logger.info("✅ UI状态已更新")

            # 获取源语言
            selected_source_lang = self.app.source_lang_var.get()
            source_lang = None if selected_source_lang == "自动检测" else selected_source_lang
            logger.debug(f"步骤4: 源语言设置: {source_lang} (原始选择: {selected_source_lang})")

            # 生成批次ID
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.debug(f"步骤5: 生成批次ID: {batch_id}")

            # 确定输出路径
            output_path = self.app.output_path.get().strip() if self.app.output_path.get() else None
            if not output_path:
                output_path = None
            logger.debug(f"步骤6: 输出路径: {output_path or '自动生成'}")

            # 执行翻译
            logger.info(f"📤 开始调用translation_facade.translate_file...")
            logger.debug(f"  - 参数: source_excel_path={self.app.source_path.get()}")
            logger.debug(f"  - 参数: target_langs={self.app.selected_langs}")
            logger.debug(f"  - 参数: output_excel_path={output_path}")
            logger.debug(f"  - 参数: concurrency_limit={DEFAULT_CONCURRENCY_LIMIT}")
            logger.debug(f"  - 参数: source_lang={source_lang}")
            logger.debug(f"  - 参数: use_multilingual=True (多语言模式)")

            # 记录翻译前的状态
            logger.info(f"📊 翻译任务统计:")
            logger.info(f"  - 目标语言数量: {len(self.app.selected_langs)}")
            logger.info(f"  - 目标语言列表: {self.app.selected_langs}")
            logger.info(f"  - 源语言: {source_lang or '自动检测'}")
            
            # 启用多语言翻译模式
            if len(self.app.selected_langs) > 1:
                logger.info("🌐 启用多语言翻译模式（一次请求翻译多种语言）")
                self.app.translation_facade.enable_multilingual_mode(True)

            result = await self.app.translation_facade.translate_file(
                source_excel_path=self.app.source_path.get(),
                target_langs=self.app.selected_langs,
                output_excel_path=output_path,
                concurrency_limit=DEFAULT_CONCURRENCY_LIMIT,
                source_lang=source_lang,
                use_multilingual=True  # 默认启用多语言模式
            )
            
            logger.info(f"✅ 翻译执行完成")
            logger.debug(f"  - 结果类型: {type(result)}")
            logger.debug(f"  - 是否有results属性: {hasattr(result, 'results')}")
            if hasattr(result, 'results'):
                logger.debug(f"  - 结果数量: {len(result.results)}")
                logger.debug(f"  - 成功率: {result.success_rate:.1f}%")
                logger.debug(f"  - total: {result.total}")
                logger.debug(f"  - success_count: {result.success_count}")
                logger.debug(f"  - failed_count: {result.failed_count}")
            else:
                logger.warning("⚠️ 结果对象没有results属性")

            # 记录历史
            if self.app.translation_history_manager and hasattr(result, 'results'):
                logger.debug("步骤7: 记录翻译历史...")
                await self._record_translation_history(result, batch_id)
                logger.info("✅ 历史记录已保存")

            # 更新完成状态
            success_rate = result.success_rate
            logger.debug(f"步骤8: 处理完成结果，成功率: {success_rate:.1f}%")
            self.app.root.after(0, self._handle_translation_complete, success_rate)

        except Exception as e:
            logger.error(f"❌ 翻译执行失败: {e}", exc_info=True)
            logger.error(f"  - 错误类型: {type(e).__name__}")
            logger.error(f"  - 错误信息: {str(e)}")
            import traceback
            logger.error(f"  - 堆栈跟踪:\n{traceback.format_exc()}")
            self.app.root.after(0, self._handle_translation_error, e)
        finally:
            logger.debug("步骤9: 清理翻译资源...")
            self.app.root.after(0, self._cleanup_after_translation)
            logger.info("✅ 资源清理完成")

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
                    from service.translation_history import record_translation
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
        try:
            self.app.translation_vm.reset()
            self.app.start_btn.config(state='normal')
            self.app.stop_btn.config(state='disabled')
            self.app.pause_btn.config(state='disabled')
            self.app.pause_btn.config(text="⏸️ 暂停")
            self.app.progress_var.set(0)
            
            # 关闭API客户端连接，防止连接泄漏导致无响应
            if hasattr(self.app, 'container') and self.app.container:
                try:
                    # 异步关闭客户端（如果有close方法）
                    client = self.app.container._singletons.get('translation_service')
                    if client and hasattr(client, 'client') and hasattr(client.client, 'close'):
                        import asyncio
                        try:
                            loop = asyncio.new_event_loop()
                            loop.run_until_complete(client.client.close())
                            loop.close()
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            logger.error(f"清理翻译状态失败: {e}")

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
