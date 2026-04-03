"""
GUI 应用模块 - 重构版
基于MVVM模式，使用视图模型、UI构建器和事件处理器
解决了所有已知的P0/P1问题
"""
import asyncio
import logging
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk, scrolledtext
from typing import List, Dict, Any, Optional

from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT, TARGET_LANGUAGES, GUI_CONFIG, GAME_TRANSLATION_TYPES
from config import T1_LANGUAGES, T2_LANGUAGES, T3_LANGUAGES
from infrastructure.prompt_injector import inject_prompts
from infrastructure.logging import setup_logger, log_with_tag
from infrastructure.logging import GUILogController
from infrastructure.models.models import Config
from infrastructure.di import initialize_container
from data_access.config_persistence import ConfigPersistence
from service.api_provider import get_provider_manager
from service.session_config import get_session_manager, SessionConfigManager
from service.version_history import get_version_manager, VersionHistoryManager
from service.translation_history import get_history_manager as get_translation_history_manager, TranslationHistoryManager, record_translation
from service.terminology_history import get_history_manager as get_terminology_history_manager
from presentation.error_handler import show_error_dialog, log_error_with_solution
from presentation.viewmodels import TranslationViewModel
from presentation.ui_builders import (
    FileConfigUIBuilder,
    ProviderConfigUIBuilder,
    AdvancedParamsUIBuilder,
    GameTranslationUIBuilder,
    LanguageSelectionUIBuilder,
    PromptConfigUIBuilder,
    ControlAndProgressUIBuilder,
    LogAndPreviewUIBuilder
)
from presentation.event_handlers import TranslationEventHandler, SessionEventHandler
from presentation import gui_constants as GC

logger = logging.getLogger(__name__)


class TranslationApp:
    """翻译应用程序 GUI - 重构版（基于MVVM）"""

    def __init__(self, root, config_file: str = None):
        """
        初始化应用程序

        Args:
            root: Tkinter 根窗口
            config_file: 配置文件路径（可选）
        """
        logger.info("="*60)
        logger.info("🚀 TranslationApp 初始化开始")
        logger.info("="*60)
        logger.debug(f"参数: config_file={config_file}")
        
        self.root = root
        self.root.title(GUI_CONFIG["window_title"])
        self.root.geometry(f"{GUI_CONFIG['window_width']}x{GUI_CONFIG['window_height']}")
        logger.debug("✅ 窗口基本属性设置完成")

        # 配置持久化
        self.config_file = config_file
        self.config_persistence = ConfigPersistence(config_file) if config_file else None
        self._pending_config_data = None
        logger.debug(f"✅ 配置持久化初始化完成, config_file={config_file}")

        # 视图模型
        logger.debug("初始化TranslationViewModel...")
        self.translation_vm = TranslationViewModel()
        self.translation_vm.set_progress_callback(self._on_progress_update)
        logger.debug("✅ TranslationViewModel初始化完成")

        # 事件处理器
        logger.debug("初始化事件处理器...")
        self.translation_handler = TranslationEventHandler(self)
        self.session_handler = SessionEventHandler(self)
        logger.debug("✅ 事件处理器初始化完成")

        # Tkinter变量
        self.term_path = tk.StringVar()
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.output_path.set("")
        self.mode_var = tk.IntVar(value=1)
        self.translation_mode_var = tk.StringVar(value="full")
        self.selected_langs = []
        self.lang_vars = {}
        
        # 提示词变量
        self.draft_style_var = tk.StringVar(value="专业、准确、直接")
        self.review_style_var = tk.StringVar(value="流畅、自然、地道")
        self.draft_model_var = tk.StringVar(value="")
        self.draft_temp_var = tk.DoubleVar(value=0.3)
        self.draft_top_p_var = tk.DoubleVar(value=0.8)
        self.draft_timeout_var = tk.IntVar(value=60)
        self.draft_max_tokens_var = tk.IntVar(value=512)
        self.review_model_var = tk.StringVar(value="")
        self.review_temp_var = tk.DoubleVar(value=0.5)
        self.review_top_p_var = tk.DoubleVar(value=0.9)
        self.review_timeout_var = tk.IntVar(value=60)
        self.review_max_tokens_var = tk.IntVar(value=512)

        # 游戏翻译
        self.translation_type_var = tk.StringVar(value="match3_item")

        # API提供商
        self.provider_manager = get_provider_manager()
        self.current_provider_var = tk.StringVar(value="deepseek")
        self.available_providers = self._get_available_providers_from_config()
        if self.available_providers:
            providers_dict = {provider: provider for provider in self.available_providers}
            self.available_providers = providers_dict
            default_provider = list(self.available_providers.keys())[0]
            self.current_provider_var.set(default_provider)

        # 源语言
        self.source_lang_var = tk.StringVar(value="自动检测")

        # 日志
        self.log_controller = None
        self.log_level_var = tk.StringVar(value=GC.DEFAULT_LOG_LEVEL)
        self.log_granularity_var = tk.StringVar(value=GC.DEFAULT_LOG_GRANULARITY)

        # 历史管理器
        self.session_manager = None
        self.version_manager = None
        self.translation_history_manager = None
        self.terminology_history_manager = None

        # 加载配置
        if config_file:
            self._pending_config_data = self._load_config_data()

        # 服务容器
        self.container = None
        self.translation_facade = None

        # UI组件引用
        self.progress_var = tk.DoubleVar()
        self.progress_bar = None
        self.progress_details_frame = None
        self.progress_current_var = tk.StringVar(value="0")
        self.progress_total_var = tk.StringVar(value="0")
        self.progress_percent_var = tk.StringVar(value="0.0%")
        self.progress_speed_var = tk.StringVar(value="0 行/秒")
        self.progress_eta_var = tk.StringVar(value="--:--:--")
        self.progress_status_var = tk.StringVar(value="等待开始")
        self.status_indicator = None

        # 性能监控
        self.performance_frame = None
        self.perf_monitor_var = tk.BooleanVar(value=False)
        self.perf_cpu_var = tk.StringVar(value="0%")
        self.perf_memory_var = tk.StringVar(value="0 MB")
        self.perf_api_calls_var = tk.StringVar(value="0")
        self.perf_success_rate_var = tk.StringVar(value="0%")
        self._perf_monitor_timer = None

        # 预览面板
        self.preview_frame = None
        self.preview_text = None
        self.preview_data = []

        # UI构建器
        self.file_config_builder = None
        self.provider_builder = None
        self.advanced_params_builder = None
        self.game_translation_builder = None
        self.language_builder = None
        self.prompt_builder = None
        self.control_builder = None
        self.log_builder = None

        # Notebook引用
        self.advanced_notebook = None
        self.lang_notebook = None
        self.preview_notebook = None

        # 文本控件（向后兼容）
        self.draft_text = None
        self.review_text = None
        self.draft_preview_text = None
        self.review_preview_text = None

        # 常用语言
        self.favorite_langs = []
        self.favorite_frame = None
        self.tier_lang_frames = {}

        # 按钮
        self.start_btn = None
        self.stop_btn = None
        self.pause_btn = None
        self.history_btn = None
        self.exit_btn = None

        # 绑定窗口关闭
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        logger.debug("✅ 窗口关闭事件绑定完成")

        # 构建UI
        logger.info("开始构建UI...")
        self._setup_ui()
        logger.info("✅ UI构建完成")
        
        self._setup_logger()
        logger.debug("✅ 日志系统设置完成")
        
        self._initialize_history_managers()
        logger.debug("✅ 历史管理器初始化完成")

        # 应用配置
        if self._pending_config_data:
            logger.debug("应用暂存的配置数据...")
            self._apply_config_to_gui(self._pending_config_data)
            self._pending_config_data = None
            logger.debug("✅ 配置数据应用完成")
        
        logger.info("="*60)
        logger.info("✅ TranslationApp 初始化完成")
        logger.info("="*60)

    def _setup_ui(self):
        """设置用户界面"""
        # 主容器 - 滚动
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 鼠标滚轮
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 主内容区
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 初始化UI构建器
        self.file_config_builder = FileConfigUIBuilder(self)
        self.provider_builder = ProviderConfigUIBuilder(self)
        self.advanced_params_builder = AdvancedParamsUIBuilder(self)
        self.game_translation_builder = GameTranslationUIBuilder(self)
        self.language_builder = LanguageSelectionUIBuilder(self)
        self.prompt_builder = PromptConfigUIBuilder(self)
        self.control_builder = ControlAndProgressUIBuilder(self)
        self.log_builder = LogAndPreviewUIBuilder(self)

        # 构建各UI区域
        self.file_config_builder.build(main_frame)
        self.provider_builder.build(main_frame)
        self.advanced_params_builder.build(main_frame)
        self.game_translation_builder.build(main_frame)
        
        # 源语言选择（内联构建）
        self._build_source_language_section(main_frame)
        
        self.language_builder.build(main_frame)
        self.prompt_builder.build(main_frame)
        self.control_builder.build(main_frame)
        self.log_builder.build(main_frame)

    def _build_source_language_section(self, parent):
        """构建源语言选择区"""
        frame = ttk.LabelFrame(parent, text="📝 源语言选择", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        source_select_frame = ttk.Frame(frame)
        source_select_frame.pack(fill=tk.X)

        ttk.Label(source_select_frame, text="选择源语言:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.source_lang_combo = ttk.Combobox(
            source_select_frame,
            textvariable=self.source_lang_var,
            values=["自动检测"],
            state='readonly',
            width=30
        )
        self.source_lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(source_select_frame, text="💡 选择文件后将自动检测可用源语言", foreground="gray").grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(source_select_frame, text="🔄 刷新源语言列表", command=self._refresh_source_languages).grid(row=0, column=3, padx=5, pady=5)

        # 输出路径
        output_select_frame = ttk.Frame(frame)
        output_select_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(output_select_frame, text="输出路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.output_path_entry = ttk.Entry(output_select_frame, textvariable=self.output_path, width=50)
        self.output_path_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Button(output_select_frame, text="📁 浏览", command=self._browse_output_path).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(output_select_frame, text="🔄 自动", command=lambda: self.output_path.set("")).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(output_select_frame, text="💡 留空将自动生成输出文件", foreground="gray").grid(row=0, column=4, padx=10, pady=5)

    def _setup_logger(self):
        """设置日志系统 - 修复了未正确调用的问题"""
        setup_logger("TranslationApp")  # 修复：添加必需的name参数
        self._setup_gui_logging()

    def _initialize_log_controller(self):
        """初始化GUI日志控制器"""
        try:
            self.log_controller = GUILogController(
                self.log_level_var,
                self.log_granularity_var
            )
            logger.info("✅ GUI 日志控制器初始化完成")
        except Exception as e:
            logger.error(f"❌ GUI 日志控制器初始化失败：{e}")

    def _create_log_control_panel(self, parent):
        """创建日志控制面板"""
        if not self.log_controller:
            return

        control_frame = self.log_controller.create_log_control_frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        self.log_control_frame = control_frame

    def _create_progress_details(self, parent):
        """创建进度详情区"""
        self.progress_details_frame = ttk.Frame(parent)
        self.progress_details_frame.pack(fill=tk.X, pady=(2, 5))

        top_row = ttk.Frame(self.progress_details_frame)
        top_row.pack(fill=tk.X, pady=2)

        ttk.Label(top_row, text="📊 进度:", font=("", 9, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(top_row, textvariable=self.progress_percent_var, font=("", 9, "bold"),
                  foreground=GC.ACCENT_COLOR).pack(side=tk.LEFT, padx=5)

        self.status_indicator = ttk.Label(top_row, text="⏸ 等待", font=("", 8), foreground="gray")
        self.status_indicator.pack(side=tk.RIGHT, padx=5)

        detail_grid = ttk.Frame(self.progress_details_frame)
        detail_grid.pack(fill=tk.X, pady=2)

        ttk.Label(detail_grid, text="当前行:", foreground=GC.DISABLED_COLOR).grid(row=0, column=0, sticky=tk.W, padx=10)
        ttk.Label(detail_grid, textvariable=self.progress_current_var,
                  foreground=GC.ACCENT_COLOR, font=("Consolas", 9)).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(detail_grid, text="/", foreground=GC.DISABLED_COLOR).grid(row=0, column=2, sticky=tk.W, padx=2)

        ttk.Label(detail_grid, text="总行数:", foreground=GC.DISABLED_COLOR).grid(row=0, column=3, sticky=tk.W, padx=10)
        ttk.Label(detail_grid, textvariable=self.progress_total_var,
                  foreground=GC.ACCENT_COLOR, font=("Consolas", 9)).grid(row=0, column=4, sticky=tk.W, padx=5)

        ttk.Label(detail_grid, text="⚡ 速度:", foreground=GC.DISABLED_COLOR).grid(row=0, column=5, sticky=tk.W, padx=15)
        ttk.Label(detail_grid, textvariable=self.progress_speed_var,
                  foreground=GC.SUCCESS_COLOR, font=("Consolas", 9, "bold")).grid(row=0, column=6, sticky=tk.W, padx=5)

        ttk.Label(detail_grid, text="⏱ ETA:", foreground=GC.DISABLED_COLOR).grid(row=0, column=7, sticky=tk.W, padx=15)
        ttk.Label(detail_grid, textvariable=self.progress_eta_var,
                  foreground=GC.WARNING_COLOR, font=("Consolas", 9, "bold")).grid(row=0, column=8, sticky=tk.W, padx=5)

    def _create_performance_panel(self, parent):
        """创建性能监控面板 - 修复了未pack问题"""
        self.performance_frame = ttk.LabelFrame(parent, text="📊 性能监控", padding="8")
        # 先pack再隐藏，确保widget被正确管理
        self.performance_frame.pack(fill=tk.X, pady=(5, 5))
        self.performance_frame.pack_forget()

        perf_grid = ttk.Frame(self.performance_frame)
        perf_grid.pack(fill=tk.X)

        cpu_frame = ttk.Frame(perf_grid)
        cpu_frame.grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(cpu_frame, text="CPU:", font=("", 8, "bold"), foreground=GC.DISABLED_COLOR).pack(side=tk.LEFT, padx=5)
        ttk.Label(cpu_frame, textvariable=self.perf_cpu_var,
                  font=("Consolas", 10, "bold"), foreground=GC.ACCENT_COLOR).pack(side=tk.LEFT)

        mem_frame = ttk.Frame(perf_grid)
        mem_frame.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(mem_frame, text="内存:", font=("", 8, "bold"), foreground=GC.DISABLED_COLOR).pack(side=tk.LEFT, padx=5)
        ttk.Label(mem_frame, textvariable=self.perf_memory_var,
                  font=("Consolas", 10, "bold"), foreground=GC.SUCCESS_COLOR).pack(side=tk.LEFT)

        api_frame = ttk.Frame(perf_grid)
        api_frame.grid(row=0, column=2, padx=10, pady=5)
        ttk.Label(api_frame, text="API调用:", font=("", 8, "bold"), foreground=GC.DISABLED_COLOR).pack(side=tk.LEFT, padx=5)
        ttk.Label(api_frame, textvariable=self.perf_api_calls_var,
                  font=("Consolas", 10, "bold"), foreground=GC.WARNING_COLOR).pack(side=tk.LEFT)

        success_frame = ttk.Frame(perf_grid)
        success_frame.grid(row=0, column=3, padx=10, pady=5)
        ttk.Label(success_frame, text="成功率:", font=("", 8, "bold"), foreground=GC.DISABLED_COLOR).pack(side=tk.LEFT, padx=5)
        ttk.Label(success_frame, textvariable=self.perf_success_rate_var,
                  font=("Consolas", 10, "bold"), foreground=GC.SUCCESS_COLOR).pack(side=tk.LEFT)

    def _create_translation_preview_panel(self, parent):
        """创建翻译预览面板 - 修复了未pack问题"""
        self.preview_frame = ttk.LabelFrame(parent, text="🔍 翻译预览（前10行）", padding="8")
        # 先pack再隐藏，确保widget被正确管理
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preview_frame.pack_forget()

        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame,
            height=10,
            font=("Consolas", 9),
            state='disabled',
            bg="#f8f8f8"
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_text.config(state='normal')
        self.preview_text.insert('1.0', "翻译预览将在此显示...\n\n开始翻译后，这里会显示前10行翻译结果。")
        self.preview_text.config(state='disabled')

    # ========== 事件处理方法（委托给事件处理器） ==========

    def _start_translation(self):
        """启动翻译 - 委托给TranslationEventHandler"""
        self.translation_handler.start_translation()

    def _stop_translation(self):
        """停止翻译 - 委托给TranslationEventHandler"""
        self.translation_handler.stop_translation()

    def _pause_translation(self):
        """暂停/恢复翻译 - 委托给TranslationEventHandler"""
        self.translation_handler.pause_translation()

    def _on_progress_update(self, progress):
        """进度更新回调（由ViewModel调用，线程安全）"""
        try:
            self.progress_percent_var.set(f"{progress.percentage:.1f}%")
            self.progress_current_var.set(str(progress.current))
            self.progress_total_var.set(str(progress.total))
            self.progress_speed_var.set(f"{progress.speed:.1f} 行/秒")
            self.progress_eta_var.set(progress.format_eta())
            self.progress_status_var.set(progress.status)
            
            if self.status_indicator:
                self.status_indicator.config(
                    text=self.translation_vm.get_status_text(),
                    foreground=self.translation_vm.get_status_color()
                )
            
            self.progress_var.set(progress.percentage)
        except Exception as e:
            logger.debug(f"进度更新失败: {e}")

    # ========== 从原gui_app.py保留的辅助方法 ==========
    # 这些方法保持不变，因为它们已经是良好实现的

    def _select_term_file(self):
        """选择术语库文件"""
        filename = filedialog.askopenfilename(
            title="选择术语库文件",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.term_path.set(filename)
            logger.info(f"已选择术语库文件：{filename}")

    def _select_source_file(self):
        """选择源文件"""
        filename = filedialog.askopenfilename(
            title="选择待翻译文件",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.source_path.set(filename)
            logger.info(f"已选择待翻译文件：{filename}")
            self._refresh_source_languages()

    def _browse_output_path(self):
        """浏览输出路径"""
        source_file = self.source_path.get()
        if source_file:
            import os
            base_name, ext = os.path.splitext(os.path.basename(source_file))
            default_output = f"{base_name}_translated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            initial_dir = os.path.dirname(source_file)
            initial_file = os.path.join(initial_dir, default_output)
        else:
            initial_file = "translated_output.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            defaultextension=".xlsx",
            initialfile=os.path.basename(initial_file) if initial_file else None
        )
        if file_path:
            self.output_path.set(file_path)
            logger.info(f"已设置输出路径：{file_path}")

    def _on_provider_changed(self, event):
        """API提供商切换"""
        provider_name = self.current_provider_var.get()
        logger.info(f"切换到 API 提供商：{provider_name}")
        self._update_model_list()

    def _on_translation_type_changed(self, event):
        """翻译方向切换"""
        translation_type = self.translation_type_var.get()
        logger.info(f"翻译方向已更改为：{translation_type}")

    def _on_translation_mode_changed(self, event):
        """翻译模式更改"""
        mode = self.translation_mode_var.get()
        logger.info(f"翻译模式已更改为：{mode}")

    def _on_style_changed(self):
        """风格更改"""
        self._update_prompt_preview()

    def _select_all_langs(self):
        """全选当前页语言"""
        for var in self.lang_vars.values():
            var.set(True)
        self._update_lang_status()

    def _deselect_all_langs(self):
        """取消全选当前页语言"""
        for var in self.lang_vars.values():
            var.set(False)
        self._update_lang_status()

    def _update_lang_status(self):
        """更新语言选择状态"""
        self.selected_langs = [lang for lang, var in self.lang_vars.items() if var.get()]
        logger.debug(f"已选择 {len(self.selected_langs)} 个语言")

    def _add_custom_language(self):
        """添加自定义语言"""
        from tkinter import simpledialog
        lang_name = simpledialog.askstring("添加自定义语言", "请输入语言名称：")
        if lang_name:
            if lang_name not in self.lang_vars:
                var = tk.BooleanVar(value=True)
                self.lang_vars[lang_name] = var
                self._update_lang_status()
                logger.info(f"✅ 已添加自定义语言：{lang_name}")
            else:
                messagebox.showinfo("提示", f"语言 {lang_name} 已存在")

    def _refresh_source_languages(self):
        """刷新源语言列表"""
        try:
            source_file = self.source_path.get()
            if not source_file or not os.path.exists(source_file):
                return

            import pandas as pd
            df = pd.read_excel(source_file)
            
            available_langs = ["自动检测"]
            for col in df.columns:
                if col not in ['ID', 'id', '序号']:
                    available_langs.append(col)
            
            available_langs = list(dict.fromkeys(available_langs))
            self.source_lang_combo['values'] = available_langs
            
            logger.info(f"✅ 已刷新源语言列表，发现 {len(available_langs)-1} 个可用语言")
        except Exception as e:
            logger.error(f"刷新源语言列表失败: {e}")

    def _update_model_list(self):
        """更新模型列表"""
        provider_name = self.current_provider_var.get()
        try:
            from service.api_provider import APIProvider
            if provider_name.startswith('APIProvider.'):
                provider_name = provider_name.split('.')[-1].lower()

            provider = APIProvider(provider_name)
            provider_instance = self.provider_manager.get_provider(provider)
            
            if hasattr(provider_instance, 'models'):
                models = provider_instance.models if isinstance(provider_instance.models, list) else []
            else:
                models = []
            
            model_list = [""] + models
            self.draft_model_combo['values'] = model_list
            self.review_model_combo['values'] = model_list
            
            logger.debug(f"✅ 已更新模型列表，共 {len(models)} 个模型")
        except Exception as e:
            logger.error(f"更新模型列表失败: {e}")
            self.draft_model_combo['values'] = [""]
            self.review_model_combo['values'] = [""]

    def _sync_draft_model_to_review(self):
        """同步初译模型到校对"""
        draft_model = self.draft_model_var.get()
        self.review_model_var.set(draft_model)
        logger.info(f"🔄 已将初译模型同步到校对：{draft_model}")

    def _reset_advanced_params(self):
        """重置高级参数"""
        self.draft_model_var.set("")
        self.draft_temp_var.set(0.3)
        self.draft_top_p_var.set(0.8)
        self.draft_timeout_var.set(60)
        self.draft_max_tokens_var.set(512)

        self.review_model_var.set("")
        self.review_temp_var.set(0.5)
        self.review_top_p_var.set(0.9)
        self.review_timeout_var.set(60)
        self.review_max_tokens_var.set(512)

        logger.info("🔄 高级参数已重置为默认值")

    def _update_prompt_preview(self):
        """更新提示词预览"""
        try:
            draft_style = self.draft_style_var.get()
            review_style = self.review_style_var.get()

            draft_prompt = f"[风格: {draft_style}]\n{DEFAULT_DRAFT_PROMPT}"
            review_prompt = f"[风格: {review_style}]\n{DEFAULT_REVIEW_PROMPT}"

            self.draft_preview_text.config(state='normal')
            self.draft_preview_text.delete('1.0', tk.END)
            self.draft_preview_text.insert('1.0', draft_prompt)
            self.draft_preview_text.config(state='disabled')

            self.review_preview_text.config(state='normal')
            self.review_preview_text.delete('1.0', tk.END)
            self.review_preview_text.insert('1.0', review_prompt)
            self.review_preview_text.config(state='disabled')

            logger.debug("✅ 提示词预览已更新")
        except Exception as e:
            logger.error(f"更新提示词预览失败: {e}")

    def _show_prompt_advanced_settings(self):
        """显示高级提示词设置"""
        messagebox.showinfo("高级设置", "请在「双阶段翻译参数」中调整模型参数")

    def _export_full_prompts(self):
        """导出完整提示词"""
        from tkinter import filedialog
        draft_prompt = self.draft_preview_text.get('1.0', tk.END)
        review_prompt = self.review_preview_text.get('1.0', tk.END)
        
        filename = filedialog.asksaveasfilename(
            title="导出提示词",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== 初译提示词 ===\n\n")
                f.write(draft_prompt)
                f.write("\n\n=== 校对提示词 ===\n\n")
                f.write(review_prompt)
            logger.info(f"💾 提示词已导出到：{filename}")

    def _load_custom_prompts(self):
        """导入自定义提示词"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="选择提示词文件",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                defaultextension=".txt"
            )
            
            if not filename:
                return
            
            logger.info(f"📂 正在加载自定义提示词: {filename}")
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析：尝试分割为初译和校对提示词
            if "=== 校对提示词 ===" in content or "=== Review Prompt ===" in content:
                # 双提示词格式
                parts = content.split("=== 校对提示词 ===" if "=== 校对提示词 ===" in content else "=== Review Prompt ===")
                draft_prompt = parts[0].replace("=== 初译提示词 ===", "").strip()
                review_prompt = parts[1].strip()
                
                self.draft_preview_text.config(state='normal')
                self.draft_preview_text.delete('1.0', tk.END)
                self.draft_preview_text.insert('1.0', draft_prompt)
                self.draft_preview_text.config(state='disabled')
                
                self.review_preview_text.config(state='normal')
                self.review_preview_text.delete('1.0', tk.END)
                self.review_preview_text.insert('1.0', review_prompt)
                self.review_preview_text.config(state='disabled')
                
                logger.info("✅ 已导入初译和校对提示词")
            else:
                # 单提示词格式，默认导入到初译
                self.draft_preview_text.config(state='normal')
                self.draft_preview_text.delete('1.0', tk.END)
                self.draft_preview_text.insert('1.0', content)
                self.draft_preview_text.config(state='disabled')
                
                logger.info("✅ 已导入提示词（单格式，仅初译）")
            
            messagebox.showinfo("成功", f"提示词已从文件导入：\n{filename}")
            
        except Exception as e:
            logger.error(f"导入自定义提示词失败: {e}", exc_info=True)
            messagebox.showerror("错误", f"导入提示词失败：\n{str(e)}")

    def _show_full_prompt_structure(self):
        """显示完整提示词结构"""
        messagebox.showinfo(
            "提示词结构说明",
            "提示词由以下部分组成：\n\n"
            "1. 系统角色定义\n"
            "2. 翻译风格设置\n"
            "3. 翻译规则和要求\n"
            "4. 输出格式说明\n\n"
            "您可以在配置文件中自定义这些内容。"
        )

    def _toggle_performance_monitor(self):
        """切换性能监控"""
        enabled = self.perf_monitor_var.get()
        logger.info(f"{'✅ 已启用' if enabled else '❌ 已禁用'} 性能监控")

        if enabled:
            self.performance_frame.pack(fill=tk.X, pady=(5, 5))
            self._update_performance_display_task()
        else:
            self.performance_frame.pack_forget()
            self._stop_performance_monitoring()

    def _update_performance_display_task(self):
        """更新性能显示（Tkinter after循环）"""
        if not self.perf_monitor_var.get():
            return

        try:
            from infrastructure.utils import get_performance_monitor
            monitor = get_performance_monitor()

            if monitor.history:
                latest = monitor.history[-1]
                metrics = {
                    'cpu_percent': latest.cpu_percent,
                    'memory_mb': latest.memory_mb,
                }
                self._update_performance_display(metrics)

            self._perf_monitor_timer = self.root.after(1000, self._update_performance_display_task)
        except Exception as e:
            logger.debug(f"性能监控更新失败: {e}")
            self._perf_monitor_timer = self.root.after(1000, self._update_performance_display_task)

    def _update_performance_display(self, metrics: Dict):
        """更新性能显示"""
        self.perf_cpu_var.set(f"{metrics.get('cpu_percent', 0):.1f}%")
        self.perf_memory_var.set(f"{metrics.get('memory_mb', 0):.1f} MB")
        self.perf_api_calls_var.set(str(self.translation_vm.performance.api_calls))
        self.perf_success_rate_var.set(f"{self.translation_vm.performance.success_rate:.1f}%")

    def _stop_performance_monitoring(self):
        """停止性能监控"""
        if self._perf_monitor_timer:
            self.root.after_cancel(self._perf_monitor_timer)
            self._perf_monitor_timer = None

    def _setup_gui_logging(self):
        """设置GUI日志重定向"""
        try:
            from infrastructure.logging import GUILogHandler
            
            root_logger = logging.getLogger()
            
            gui_handler = GUILogHandler(self.log_text)
            gui_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            gui_handler.setFormatter(formatter)
            
            root_logger.addHandler(gui_handler)
            
            logger.info("✅ GUI日志处理器已添加")
        except Exception as e:
            logger.error(f"设置GUI日志处理器失败: {e}")

    def _initialize_services(self):
        """初始化服务"""
        logger.info("🔧 开始初始化服务容器...")
        
        if self.container is None:
            logger.debug("创建新的依赖容器...")
            from infrastructure.di.di_container import initialize_container
            from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT
            
            # 检查配置文件中是否有API密钥
            try:
                if self.config_persistence:
                    config_data = self.config_persistence.load(self.config_file)
                    logger.debug(f"加载到的配置数据: {list(config_data.keys())}")
                    
                    # 支持两种配置格式：
                    # 1. 直接格式: {"api_key": "xxx"}
                    # 2. 嵌套格式: {"api_keys": {"deepseek": {"api_key": "xxx"}}}
                    api_key = config_data.get('api_key', '')
                    logger.debug(f"直接读取api_key字段: {'已找到' if api_key else '未找到'}")

                    if not api_key and 'api_keys' in config_data:
                        # 嵌套格式，获取当前选择的API提供商的密钥
                        api_provider = self.current_provider_var.get()
                        logger.info(f"📌 当前API提供商: {api_provider}")

                        api_keys_config = config_data.get('api_keys', {})
                        logger.debug(f"api_keys配置: {list(api_keys_config.keys())}")
                        
                        if api_provider in api_keys_config:
                            provider_config = api_keys_config[api_provider]
                            api_key = provider_config.get('api_key', '')
                            provider_base_url = provider_config.get('base_url', '')
                            logger.info(f"✅ 从api_keys.{api_provider}读取API密钥: {'已配置' if api_key else '未配置'}")
                            logger.info(f"✅ 从api_keys.{api_provider}读取base_url: {provider_base_url}")
                        else:
                            logger.warning(f"⚠️ 未找到提供商 '{api_provider}' 的配置，可用提供商: {list(api_keys_config.keys())}")
                    elif api_key:
                        logger.debug("从api_key字段读取API密钥: 已配置")
                    else:
                        logger.debug("配置文件中未找到API密钥")
                else:
                    api_key = ''
            except Exception as e:
                logger.warning(f"读取API密钥失败: {e}")
                api_key = ''
            
            if not api_key:
                logger.error("❌ 配置文件中未找到API密钥")
                logger.error("💡 请在config/config.json中配置api_key字段")
                raise ValueError("API密钥未配置，无法初始化翻译服务")
            
            # 创建API客户端
            logger.debug("创建API客户端...")
            from openai import AsyncOpenAI
            from service.api_provider import get_provider_manager, APIProvider
            try:
                # 获取当前选择的API提供商
                api_provider_name = self.current_provider_var.get()
                logger.info(f"📌 当前界面选择的API提供商: {api_provider_name}")

                # 获取提供商管理器
                provider_manager = get_provider_manager()
                logger.debug(f"提供商管理器: {provider_manager}")
                logger.debug(f"预定义提供商: {list(provider_manager._providers.keys())}")

                # 获取提供商配置
                base_url = None
                try:
                    provider_enum = APIProvider(api_provider_name.lower())
                    logger.debug(f"转换后的APIProvider枚举: {provider_enum}")
                    
                    provider_config = provider_manager.get_provider(provider_enum)
                    logger.debug(f"获取到的提供商配置: {provider_config}")
                    
                    if provider_config:
                        base_url = provider_config.base_url
                        logger.info(f"✅ 从提供商配置获取base_url: {base_url}")
                    else:
                        logger.warning(f"⚠️ get_provider返回None")
                        base_url = "https://api.deepseek.com"
                        
                except (ValueError, KeyError, AttributeError) as e:
                    # 如果无法解析提供商，使用默认
                    logger.warning(f"⚠️ 解析提供商失败 (异常: {type(e).__name__}: {e})，使用默认DeepSeek配置")
                    base_url = "https://api.deepseek.com"
                
                # 如果配置文件中提供了base_url，优先使用配置文件中的
                if provider_base_url:
                    logger.info(f"🔄 使用配置文件中的base_url: {provider_base_url}")
                    base_url = provider_base_url
                
                logger.info(f"🌐 最终使用的base_url: {base_url}")
                logger.info(f"🔑 API密钥前缀: {api_key[:10]}...")
                
                # 创建异步API客户端，传入api_key和base_url
                api_client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                logger.info(f"✅ API客户端创建成功 (提供商: {api_provider_name}, base_url: {base_url})")
            except Exception as e:
                logger.error(f"❌ API客户端创建失败: {e}", exc_info=True)
                raise
            
            # 初始化容器，传递必要参数
            logger.debug("初始化依赖容器，传递API客户端和提示词...")
            self.container = initialize_container(
                config_file=self.config_file,
                api_client=api_client,
                draft_prompt=DEFAULT_DRAFT_PROMPT,
                review_prompt=DEFAULT_REVIEW_PROMPT
            )
            logger.info("✅ 依赖容器创建完成")
        
        if self.translation_facade is None:
            logger.debug("尝试从容器获取TranslationFacade...")
            try:
                # 使用get方法而不是resolve
                self.translation_facade = self.container.get('translation_facade')
                logger.info("✅ 翻译外观服务已初始化")
            except KeyError as e:
                logger.error(f"❌ 无法从容器获取translation_facade: {e}")
                logger.error("💡 这可能是因为容器初始化时没有提供api_client")
                logger.error("💡 请检查配置文件中的API密钥是否正确配置")
                raise
            except Exception as e:
                logger.error(f"❌ 获取TranslationFacade失败: {e}", exc_info=True)
                raise

    def _initialize_history_managers(self):
        """初始化历史记录管理器"""
        try:
            self.session_manager = get_session_manager(GC.SESSION_CONFIG_FILE)
            self.version_manager = get_version_manager()
            self.translation_history_manager = get_translation_history_manager()
            self.terminology_history_manager = get_terminology_history_manager()

            logger.info("✅ 历史记录管理器初始化完成")

            self.session_handler.load_last_session()
            self._load_favorite_languages_from_config()
            
            if self.favorite_langs:
                self._create_favorite_tab()
        except Exception as e:
            logger.error(f"❌ 初始化历史记录管理器失败：{e}")

    def _load_config_data(self) -> dict:
        """加载配置数据"""
        if self.config_persistence:
            return self.config_persistence.load(self.config_file)
        return {}

    def _apply_config_to_gui(self, config_data: dict):
        """应用配置到GUI"""
        try:
            if 'api_provider' in config_data:
                self.current_provider_var.set(config_data['api_provider'])

            if config_data.get('draft_temperature') is not None:
                self.draft_temp_var.set(config_data['draft_temperature'])
            elif config_data.get('temperature') is not None:
                self.draft_temp_var.set(config_data['temperature'])

            if config_data.get('draft_top_p') is not None:
                self.draft_top_p_var.set(config_data['draft_top_p'])
            elif config_data.get('top_p') is not None:
                self.draft_top_p_var.set(config_data['top_p'])

            if config_data.get('draft_timeout') is not None:
                self.draft_timeout_var.set(config_data['draft_timeout'])
            elif config_data.get('timeout') is not None:
                self.draft_timeout_var.set(config_data['timeout'])

            if config_data.get('draft_max_tokens') is not None:
                self.draft_max_tokens_var.set(config_data['draft_max_tokens'])

            if config_data.get('review_temperature') is not None:
                self.review_temp_var.set(config_data['review_temperature'])
            elif config_data.get('temperature') is not None:
                self.review_temp_var.set(config_data['temperature'])

            if config_data.get('review_top_p') is not None:
                self.review_top_p_var.set(config_data['review_top_p'])
            elif config_data.get('top_p') is not None:
                self.review_top_p_var.set(config_data['top_p'])

            if config_data.get('review_timeout') is not None:
                self.review_timeout_var.set(config_data['review_timeout'])
            elif config_data.get('timeout') is not None:
                self.review_timeout_var.set(config_data['timeout'])

            if config_data.get('review_max_tokens') is not None:
                self.review_max_tokens_var.set(config_data['review_max_tokens'])

            if 'translation_type' in config_data:
                self.translation_type_var.set(config_data['translation_type'])

            if 'draft_prompt' in config_data:
                self.draft_text.delete('1.0', tk.END)
                self.draft_text.insert('1.0', config_data['draft_prompt'])

            if 'review_prompt' in config_data:
                self.review_text.delete('1.0', tk.END)
                self.review_text.insert('1.0', config_data['review_prompt'])

            logger.info("✅ 配置数据已应用到 GUI")
        except Exception as e:
            logger.error(f"❌ 应用配置到 GUI 失败：{e}")

    def _get_available_providers_from_config(self) -> list:
        """获取可用的API提供商"""
        if self.provider_manager:
            return [p.value for p in self.provider_manager.list_providers()]
        return ["deepseek"]

    def _load_favorite_languages_from_config(self):
        """从配置加载常用语言"""
        try:
            if not self.config_persistence:
                return
            
            config = self.config_persistence.load(self.config_file)
            if 'favorite_languages' in config:
                self.favorite_langs = config['favorite_languages']
                logger.info(f"📌 从配置加载了 {len(self.favorite_langs)} 个常用语言")
        except Exception as e:
            logger.error(f"加载常用语言失败: {e}")

    def _create_favorite_tab(self):
        """创建常用语言分页"""
        try:
            for i in range(self.lang_notebook.index("end")):
                if self.lang_notebook.tab(i, "text") == "⭐ 常用语言":
                    self.lang_notebook.forget(i)
                    break

            for widget in self.favorite_frame.winfo_children():
                widget.destroy()

            if not self.favorite_langs:
                return False

            self.lang_notebook.insert(0, self.favorite_frame, text="⭐ 常用语言")

            for i, lang in enumerate(self.favorite_langs):
                var = tk.BooleanVar(value=False)
                self.lang_vars[lang] = var
                lang_text = f"{lang} (常用)"
                cb = ttk.Checkbutton(self.favorite_frame, text=lang_text, variable=var, command=self._update_lang_status)
                cb.grid(row=i // GC.LANGUAGES_PER_ROW, column=i % GC.LANGUAGES_PER_ROW, sticky=tk.W, padx=10, pady=2)

            self.tier_lang_frames["FAVORITE"] = self.favorite_frame
            logger.info(f"✅ 已创建常用语言分页，包含 {len(self.favorite_langs)} 个语言")
            return True
        except Exception as e:
            logger.error(f"❌ 创建常用语言分页失败：{e}")
            return False

    def _save_favorite_languages(self, langs: List[str]):
        """保存常用语言"""
        try:
            if self.config_persistence:
                config = self.config_persistence.load(self.config_file)
                config['favorite_languages'] = langs[:10]
                self.config_persistence.save(config, self.config_file)
                logger.info(f"📌 已保存 {len(langs)} 个常用语言")
        except Exception as e:
            logger.error(f"保存常用语言失败: {e}")

    def _show_history_window(self):
        """显示历史窗口"""
        try:
            history_window = tk.Toplevel(self.root)
            history_window.title("翻译历史记录")
            history_window.geometry("900x600")

            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            stats_frame = ttk.LabelFrame(main_frame, text="📊 统计信息", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))

            self.history_total_var = tk.StringVar(value="0")
            self.history_success_var = tk.StringVar(value="0")
            self.history_failed_var = tk.StringVar(value="0")

            ttk.Label(stats_frame, text="总计:").grid(row=0, column=0, padx=10)
            ttk.Label(stats_frame, textvariable=self.history_total_var).grid(row=0, column=1, padx=10)
            ttk.Label(stats_frame, text="成功:").grid(row=0, column=2, padx=10)
            ttk.Label(stats_frame, textvariable=self.history_success_var, foreground=GC.SUCCESS_COLOR).grid(row=0, column=3, padx=10)
            ttk.Label(stats_frame, text="失败:").grid(row=0, column=4, padx=10)
            ttk.Label(stats_frame, textvariable=self.history_failed_var, foreground=GC.ERROR_COLOR).grid(row=0, column=5, padx=10)

            list_frame = ttk.LabelFrame(main_frame, text="📝 翻译记录", padding="10")
            list_frame.pack(fill=tk.BOTH, expand=True)

            columns = ("时间", "原文", "译文", "语言", "状态", "模型")
            history_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

            for col in columns:
                history_tree.heading(col, text=col)
                history_tree.column(col, width=150)

            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=history_tree.yview)
            history_tree.configure(yscrollcommand=scrollbar.set)
            history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self._load_history_list(history_tree)
            self._update_stats()

        except Exception as e:
            logger.error(f"打开历史记录窗口失败：{e}")
            messagebox.showerror("错误", f"无法打开历史记录:\n{str(e)}")

    def _load_history_list(self, tree_widget=None):
        """加载历史记录列表"""
        try:
            if not self.translation_history_manager:
                return

            if not tree_widget:
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.LabelFrame):
                                for grandchild in child.winfo_children():
                                    if isinstance(grandchild, ttk.Treeview):
                                        tree_widget = grandchild
                                        break

            if not tree_widget:
                logger.warning("未找到历史记录树控件")
                return

            for item in tree_widget.get_children():
                tree_widget.delete(item)

            records = self.translation_history_manager.get_recent_records(limit=GC.HISTORY_LIST_LIMIT)

            for record in records:
                status_text = "✅ 成功" if record.status == "SUCCESS" else "❌ 失败"
                tree_widget.insert("", "end", values=(
                    record.created_at[:19],
                    record.source_text[:50],
                    record.final_trans[:50],
                    record.target_lang,
                    status_text,
                    record.model_name
                ))

            logger.debug(f"📝 已加载 {len(records)} 条历史记录")
        except Exception as e:
            logger.error(f"加载历史记录列表失败: {e}")

    def _update_stats(self):
        """更新统计信息"""
        try:
            if not self.translation_history_manager:
                return

            records = self.translation_history_manager.get_recent_records(limit=1000)
            total = len(records)
            success = sum(1 for r in records if r.status == "SUCCESS")
            failed = total - success

            if hasattr(self, 'history_total_var'):
                self.history_total_var.set(str(total))
                self.history_success_var.set(str(success))
                self.history_failed_var.set(str(failed))
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    def _on_closing(self):
        """窗口关闭处理"""
        try:
            logger.info("🔄 正在关闭应用程序...")
            
            # 1. 保存会话
            try:
                self.session_handler.save_current_session()
                logger.debug("✅ 会话已保存")
            except Exception as e:
                logger.warning(f"保存会话失败: {e}")

            # 2. 停止性能监控
            try:
                self._stop_performance_monitoring()
                logger.debug("✅ 性能监控已停止")
            except Exception as e:
                logger.warning(f"停止性能监控失败: {e}")

            # 3. 清理容器（使用shutdown而非cleanup）
            try:
                if self.container:
                    self.container.shutdown()
                    logger.debug("✅ 容器已关闭")
            except Exception as e:
                logger.warning(f"关闭容器失败: {e}")

            # 4. 关闭日志控制器
            try:
                if hasattr(self, 'log_controller') and self.log_controller:
                    # 清理日志处理器
                    root_logger = logging.getLogger()
                    for handler in root_logger.handlers[:]:
                        if hasattr(handler, 'flush'):
                            handler.flush()
                    logger.debug("✅ 日志处理器已清理")
            except Exception as e:
                logger.warning(f"清理日志处理器失败: {e}")

            logger.info("👋 应用程序已关闭")
            
            # 5. 销毁窗口
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {e}", exc_info=True)
            try:
                self.root.destroy()
            except:
                pass


def run_gui_app(config_file: str = None):
    """运行 GUI 应用"""
    root = tk.Tk()
    app = TranslationApp(root, config_file)
    root.mainloop()


if __name__ == "__main__":
    run_gui_app()
