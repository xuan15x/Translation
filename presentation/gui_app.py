"""
GUI 应用模块
提供图形用户界面，包括文件选择、语言配置、提示词编辑和任务执行控制
"""
import asyncio
import gc
import logging
import threading
import time
from datetime import datetime
from typing import List

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT, TARGET_LANGUAGES, GUI_CONFIG
from infrastructure.log_config import (
    setup_logger,
    get_log_manager,
    LogGranularity,
    LogLevel,
    LogConfig,
    LogTag,
    log_with_tag
)
from infrastructure.models import Config, FinalResult, TaskContext
from business_logic.terminology_manager import TerminologyManager
from business_logic.workflow_orchestrator import WorkflowOrchestrator
from openai import AsyncOpenAI
from data_access.config_persistence import ConfigPersistence
from service.api_provider import APIProvider, get_provider_manager, PREDEFINED_PROVIDERS
from service.translation_history import get_history_manager, TranslationHistoryManager
from infrastructure.undo_manager import (
    get_undo_manager,
    OperationType,
    undo_last_operation,
    redo_last_operation
)
from infrastructure.progress_estimator import (
    get_progress_estimator,
    start_progress_tracking,
    update_progress,
    format_progress_summary,
    get_current_progress
)


class TranslationApp:
    """翻译应用程序 GUI"""
    
    def __init__(self, root, config_file: str = None):
        """
        初始化应用程序
        
        Args:
            root: Tkinter 根窗口
            config_file: 配置文件路径（可选）
        """
        self.root = root
        self.root.title(GUI_CONFIG["window_title"])
        self.root.geometry(f"{GUI_CONFIG['window_width']}x{GUI_CONFIG['window_height']}")
        
        # 配置持久化
        self.config_file = config_file
        self.config_persistence = ConfigPersistence(config_file) if config_file else None

        # 状态变量
        self.term_path = tk.StringVar()
        self.source_path = tk.StringVar()
        self.mode_var = tk.IntVar(value=1)
        self.selected_langs = []
        self.prompt_draft = tk.StringVar()
        self.prompt_review = tk.StringVar()
        self.is_running = False

        # 默认提示词
        self.default_draft = DEFAULT_DRAFT_PROMPT
        self.default_review = DEFAULT_REVIEW_PROMPT

        self.prompt_draft.set(self.default_draft)
        self.prompt_review.set(self.default_review)
        
        # API 提供商管理
        self.provider_manager = get_provider_manager()
        self.current_provider_var = tk.StringVar(value="deepseek")
        
        # 加载配置文件（如果有）
        if config_file:
            self._load_config_from_file()
        
        # 初始化可用 API 提供商列表（在加载配置之后）
        self.available_providers = self._get_available_providers_from_config()
        if self.available_providers:
            # 使用第一个可用的提供商作为默认值
            default_provider = list(self.available_providers.keys())[0]
            self.current_provider_var.set(default_provider)

        self._setup_ui()
        self._setup_logger()

    def _setup_ui(self):
        """设置用户界面"""
        # 创建主容器用于滚动
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 垂直滚动条
        self.v_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条
        self.h_scrollbar = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.main_canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置 Canvas
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # 创建可滚动的框架
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # 绑定窗口大小变化事件
        self.main_canvas.bind('<Configure>', self._on_canvas_configure)
        self.scrollable_frame.bind('<Configure>', self._on_frame_configure)
        
        # 绑定鼠标滚轮事件
        self.main_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.main_canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.main_canvas.bind_all('<Button-5>', self._on_mousewheel)
        
        # 主容器
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 文件配置区 ---
        file_frame = ttk.LabelFrame(main_frame, text="📂 文件配置", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        # 术语库
        ttk.Label(file_frame, text="术语库 (Excel):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.term_path, width=50, state='readonly').grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(file_frame, text="选择...", command=self._select_term_file).grid(row=0, column=2, pady=5)

        # 源文件
        ttk.Label(file_frame, text="待翻译 (Excel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.source_path, width=50, state='readonly').grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(file_frame, text="选择...", command=self._select_source_file).grid(row=1, column=2, pady=5)

        # 模式
        mode_frame = ttk.Frame(file_frame)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="🆕 新文档 (双阶段)", variable=self.mode_var, value=1).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Radiobutton(mode_frame, text="📝 旧文档校对", variable=self.mode_var, value=2).pack(
            side=tk.LEFT, padx=10
        )

        # --- 2. API 提供商选择区 ---
        provider_frame = ttk.LabelFrame(main_frame, text="🔌 API 提供商", padding="10")
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 提供商选择下拉框
        ttk.Label(provider_frame, text="选择 API 提供商:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 使用动态加载的可用提供商列表
        providers_list = list(self.available_providers.keys()) if hasattr(self, 'available_providers') and self.available_providers else ["deepseek"]
        self.provider_combo = ttk.Combobox(
            provider_frame, 
            textvariable=self.current_provider_var,
            values=providers_list,
            state='readonly',
            width=30
        )
        self.provider_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.provider_combo.bind('<<ComboboxSelected>>', self._on_provider_changed)
        
        # 显示当前模型信息
        self.provider_info_label = ttk.Label(provider_frame, text="", foreground="gray")
        self.provider_info_label.grid(row=0, column=2, padx=10, pady=5)
        self._update_provider_info()
        
        # --- 3. 语言选择区 ---
        lang_frame = ttk.LabelFrame(main_frame, text="🌍 目标语言", padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 10))

        self.lang_vars = {}
        
        # 按钮行
        btn_row = ttk.Frame(lang_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="全选", command=self._select_all_langs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="取消全选", command=self._deselect_all_langs).pack(side=tk.LEFT, padx=5)
        self.lang_status_label = ttk.Label(btn_row, text="已选：0", foreground="blue")
        self.lang_status_label.pack(side=tk.RIGHT, padx=5)

        # 复选框网格
        cb_frame = ttk.Frame(lang_frame)
        cb_frame.pack(fill=tk.X)
        for i, lang in enumerate(TARGET_LANGUAGES):
            var = tk.BooleanVar(value=False)
            self.lang_vars[lang] = var
            cb = ttk.Checkbutton(cb_frame, text=lang, variable=var, command=self._update_lang_status)
            cb.grid(row=i // 4, column=i % 4, sticky=tk.W, padx=10, pady=2)
        
        # 初始化语言选择状态（确保所有复选框都是未选中状态）
        self._update_lang_status()

        # --- 3. 提示词配置区 ---
        prompt_frame = ttk.LabelFrame(main_frame, text="⚙️ 提示词配置", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 选项卡
        self.notebook = ttk.Notebook(prompt_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Draft Tab
        draft_tab = ttk.Frame(self.notebook)
        self.notebook.add(draft_tab, text="初译提示词 (Draft)")
        self.draft_text = scrolledtext.ScrolledText(draft_tab, height=6, font=("Consolas", 10))
        self.draft_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.draft_text.insert('1.0', self.default_draft)

        # Review Tab
        review_tab = ttk.Frame(self.notebook)
        self.notebook.add(review_tab, text="校对提示词 (Review)")
        self.review_text = scrolledtext.ScrolledText(review_tab, height=6, font=("Consolas", 10))
        self.review_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.review_text.insert('1.0', self.default_review)

        # 校验按钮
        ttk.Button(prompt_frame, text="✅ 校验提示词格式", command=self._validate_prompts).pack(pady=5)
        
        # 配置文件按钮
        config_btn_frame = ttk.Frame(prompt_frame)
        config_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(config_btn_frame, text="📂 加载配置", command=self._load_config_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_btn_frame, text="💾 保存配置", command=self._save_config_dialog).pack(side=tk.LEFT, padx=5)

        # --- 4. 控制与日志区 ---
        control_frame = ttk.LabelFrame(main_frame, text="🚀 执行控制", padding="10")
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志粒度控制
        log_control_frame = ttk.Frame(control_frame)
        log_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：粒度选择
        granularity_row = ttk.Frame(log_control_frame)
        granularity_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(granularity_row, text="📝 日志粒度:").pack(side=tk.LEFT, padx=5)
        self.log_granularity_var = tk.StringVar(value="normal")
        granularity_combo = ttk.Combobox(
            granularity_row,
            textvariable=self.log_granularity_var,
            values=["minimal", "basic", "normal", "detailed", "verbose"],
            state="readonly",
            width=12
        )
        granularity_combo.pack(side=tk.LEFT, padx=5)
        granularity_combo.bind('<<ComboboxSelected>>', self._on_log_granularity_changed)
        
        # 第二行：标签过滤
        tag_filter_row = ttk.Frame(log_control_frame)
        tag_filter_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(tag_filter_row, text="🏷️ 标签过滤:").pack(side=tk.LEFT, padx=5)
        self.log_tag_filter_var = tk.StringVar(value="all")
        tag_filter_combo = ttk.Combobox(
            tag_filter_row,
            textvariable=self.log_tag_filter_var,
            values=["all", "errors_only", "important_only", "progress_only", "no_debug"],
            state="readonly",
            width=15
        )
        tag_filter_combo.pack(side=tk.LEFT, padx=5)
        tag_filter_combo.bind('<<ComboboxSelected>>', self._on_tag_filter_changed)
        
        # 快捷按钮
        shortcut_frame = ttk.Frame(log_control_frame)
        shortcut_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(
            shortcut_frame,
            text="🔍 详细调试",
            command=lambda: self._set_log_level("verbose")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            shortcut_frame,
            text="🧹 只看错误",
            command=lambda: self._set_tag_filter("errors_only")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            shortcut_frame,
            text="⭐ 重要事件",
            command=lambda: self._set_tag_filter("important_only")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            shortcut_frame,
            text="📊 只显示进度",
            command=lambda: self._set_tag_filter("progress_only")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            shortcut_frame,
            text="🔒 隐藏调试",
            command=lambda: self._set_tag_filter("no_debug")
        ).pack(side=tk.LEFT, padx=2)
        
        # 清空日志按钮
        ttk.Button(
            shortcut_frame,
            text="🗑️ 清空日志",
            command=self._clear_log
        ).pack(side=tk.RIGHT, padx=5)
        
        # 退出按钮（放在最右边）
        ttk.Button(
            shortcut_frame,
            text="🚪 退出程序",
            command=self._exit_application
        ).pack(side=tk.RIGHT, padx=5)
        
        # 开始按钮（放在最显眼的位置）
        self.start_btn = ttk.Button(
            control_frame, 
            text="开始翻译任务", 
            command=self._start_workflow,
            width=20
        )
        self.start_btn.pack(pady=(0, 10))
        
        # 撤销/重做按钮行
        undo_redo_frame = ttk.Frame(control_frame)
        undo_redo_frame.pack(fill=tk.X, pady=5)
        self.undo_btn = ttk.Button(
            undo_redo_frame, 
            text="↩️ 撤销",
            command=self._undo_last_operation,
            state='disabled'
        )
        self.undo_btn.pack(side=tk.LEFT, padx=5)
        self.redo_btn = ttk.Button(
            undo_redo_frame,
            text="↪️ 重做",
            command=self._redo_last_operation,
            state='disabled'
        )
        self.redo_btn.pack(side=tk.LEFT, padx=5)
        self.undo_status_label = ttk.Label(undo_redo_frame, text="无操作历史", foreground="gray")
        self.undo_status_label.pack(side=tk.LEFT, padx=10)

        # 进度条和进度信息
        self.progress_bar = ttk.Progressbar(control_frame, mode='determinate', length=300)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 进度详细信息
        self.progress_info_frame = ttk.Frame(control_frame)
        self.progress_info_frame.pack(fill=tk.X, pady=2)
        
        self.progress_percent_label = ttk.Label(
            self.progress_info_frame,
            text="进度：0%",
            font=("Arial", 10, "bold"),
            foreground="blue"
        )
        self.progress_percent_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_eta_label = ttk.Label(
            self.progress_info_frame,
            text="预计剩余：--:--",
            font=("Arial", 9),
            foreground="green"
        )
        self.progress_eta_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_speed_label = ttk.Label(
            self.progress_info_frame,
            text="速度：0 项/秒",
            font=("Arial", 9),
            foreground="gray"
        )
        self.progress_speed_label.pack(side=tk.LEFT, padx=5)

        self.log_text = scrolledtext.ScrolledText(
            control_frame, 
            height=8, 
            state='disabled', 
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _setup_logger(self):
        """设置日志系统"""
        # 使用新的日志配置模块
        config = LogConfig(
            level=LogLevel.INFO,
            granularity=LogGranularity.NORMAL,
            show_colors=True,
            enable_gui=True,
            enable_console=True,
            max_lines=1000
        )
        
        logger = setup_logger(config=config)
        
        # 添加 GUI 处理器
        log_manager = get_log_manager()
        log_manager.add_gui_handler(self.log_text)
        
        logging.info("[LOG] 日志系统已初始化")
        
        # 注册窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 注册所有历史管理器到全局持久化管理器
        self._register_history_managers()

    def _register_history_managers(self):
        """注册所有历史管理器到全局持久化管理器"""
        try:
            from data_access.global_persistence_manager import get_global_persistence_manager
            from service.translation_history import get_history_manager as get_translation_history_manager
            from service.terminology_history import get_history_manager as get_terminology_history_manager
            
            global_manager = get_global_persistence_manager()
            
            # 注册翻译历史管理器
            translation_history_mgr = get_translation_history_manager()
            global_manager.register_translation_history(translation_history_mgr)
            logging.info("📝 翻译历史管理器已注册到全局管理器")
            
            # 注册术语历史管理器
            terminology_history_mgr = get_terminology_history_manager()
            global_manager.register_terminology_history(terminology_history_mgr)
            logging.info("📚 术语历史管理器已注册到全局管理器")
            
        except Exception as e:
            logging.error(f"注册历史管理器失败：{e}")
    
    def _on_canvas_configure(self, event):
        """Canvas 大小变化时调整内部框架宽度"""
        # 设置框架的最小宽度为 Canvas 的宽度
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_frame_configure(self, event):
        """框架大小变化时更新滚动区域"""
        # 更新滚动区域
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # Windows
        if event.delta:
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        # Linux
        elif event.num == 4:
            self.main_canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self.main_canvas.yview_scroll(1, 'units')

    def _on_log_granularity_changed(self, event=None):
        """日志粒度切换处理"""
        try:
            granularity_str = self.log_granularity_var.get()
            granularity_map = {
                "minimal": LogGranularity.MINIMAL,
                "basic": LogGranularity.BASIC,
                "normal": LogGranularity.NORMAL,
                "detailed": LogGranularity.DETAILED,
                "verbose": LogGranularity.VERBOSE
            }
            
            granularity = granularity_map.get(granularity_str, LogGranularity.NORMAL)
            log_manager = get_log_manager()
            log_manager.set_granularity(granularity)
            
            # 添加控制台日志输出
            logging.info(f"[GUI] 日志粒度已切换为：{granularity_str}")
            log_with_tag(f"[STATS] 日志粒度已设置为：{granularity_str}", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
        except Exception as e:
            logging.error(f"设置日志粒度失败：{e}")
    
    def _on_tag_filter_changed(self, event=None):
        """标签过滤器切换处理"""
        try:
            filter_str = self.log_tag_filter_var.get()
            log_manager = get_log_manager()
            
            # 添加控制台日志输出
            logging.info(f"[GUI] 标签过滤器已切换为：{filter_str}")
            
            if filter_str == "all":
                # 显示所有标签
                log_manager.clear_tag_filter()
                log_with_tag("[TAG] 标签过滤器已关闭 (显示所有)", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "errors_only":
                # 只显示错误
                log_manager.set_tag_filter([LogTag.CRITICAL, LogTag.ERROR])
                log_with_tag("[TAG] 标签过滤器：只显示错误", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "important_only":
                # 只显示重要事件
                log_manager.set_tag_filter([LogTag.CRITICAL, LogTag.ERROR, LogTag.WARNING, LogTag.IMPORTANT])
                log_with_tag("[TAG] 标签过滤器：只显示重要事件", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "progress_only":
                # 只显示进度相关
                log_manager.set_tag_filter([LogTag.PROGRESS, LogTag.IMPORTANT])
                log_with_tag("[TAG] 标签过滤器：只显示进度", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "no_debug":
                # 不显示调试信息
                log_manager.set_min_tag(LogTag.NORMAL)
                log_with_tag("[TAG] 标签过滤器：隐藏调试信息", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
        except Exception as e:
            logging.error(f"设置标签过滤器失败：{e}")
    
    def _set_log_level(self, level_str: str):
        """快速设置日志级别"""
        try:
            # 添加控制台日志输出
            logging.info(f"[GUI] 快捷按钮：{level_str}")
            
            if level_str == "verbose":
                self.log_granularity_var.set("verbose")
                log_manager = get_log_manager()
                log_manager.set_granularity(LogGranularity.VERBOSE)
                logging.info("[DEBUG] 已切换到详细调试模式")
            elif level_str == "minimal":
                self.log_granularity_var.set("minimal")
                log_manager = get_log_manager()
                log_manager.set_granularity(LogGranularity.MINIMAL)
                logging.info("[CLEAN] 已切换到最小化模式 (只显示错误)")
        except Exception as e:
            logging.error(f"设置日志级别失败：{e}")
    
    def _set_tag_filter(self, filter_str: str):
        """快速设置标签过滤器"""
        try:
            log_manager = get_log_manager()
            
            # 添加控制台日志输出
            logging.info(f"[GUI] 快捷按钮：{filter_str}")
            
            if filter_str == "important_only":
                # 只显示重要事件
                log_manager.set_tag_filter([LogTag.CRITICAL, LogTag.ERROR, LogTag.WARNING, LogTag.IMPORTANT])
                log_with_tag("[FILTER] 标签过滤器：只显示重要事件", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "errors_only":
                # 只显示错误
                log_manager.set_tag_filter([LogTag.CRITICAL, LogTag.ERROR])
                log_with_tag("[FILTER] 标签过滤器：只显示错误", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "progress_only":
                # 只显示进度
                log_manager.set_tag_filter([LogTag.PROGRESS, LogTag.IMPORTANT])
                log_with_tag("[PROGRESS] 标签过滤器：只显示进度", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "no_debug":
                # 隐藏调试
                log_manager.set_min_tag(LogTag.NORMAL)
                log_with_tag("[DEBUG] 标签过滤器：隐藏调试信息", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            elif filter_str == "all":
                # 显示所有
                log_manager.clear_tag_filter()
                log_with_tag("[TAG] 标签过滤器：显示所有", level=LogLevel.INFO, tag=LogTag.IMPORTANT)
            
            # 更新下拉框显示
            self.log_tag_filter_var.set(filter_str)
            
        except Exception as e:
            logging.error(f"设置标签过滤器失败：{e}")
    
    def _clear_log(self):
        """清空日志窗口"""
        try:
            self.log_text.configure(state='normal')
            self.log_text.delete('1.0', tk.END)
            self.log_text.configure(state='disabled')
            # 添加控制台日志输出
            logging.info("[GUI] 用户操作：清空日志窗口")
            logging.info("[CLEAR] 日志已清空")
        except Exception as e:
            logging.error(f"清空日志失败：{e}")
    
    def _select_term_file(self):
        """选择术语库文件"""
        try:
            path = filedialog.asksaveasfilename(
                title="选择/创建术语库", 
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")]
            )
            if path:
                self.term_path.set(path)
                # 添加控制台日志输出
                logging.info(f"[GUI] 用户操作：选择术语库文件 - {path}")
                
                # 检查文件是否存在
                import os
                if os.path.exists(path):
                    # 询问是否要加载现有术语库
                    result = messagebox.askyesno(
                        "加载术语库",
                        f"检测到现有术语库文件:\n{path}\n\n"
                        f"点击'是'加载并覆盖当前术语库\n"
                        f"点击'否'创建新术语库 (旧数据将丢失)",
                        icon='question'
                    )
                    
                    if result:
                        # 加载并显示术语库预览
                        self._load_and_preview_terminology(path)
                    else:
                        logging.info(f"[FILE] 将创建新术语库：{path}")
                else:
                    logging.info(f"[FILE] 新术语库文件将自动创建：{path}")
                    # 显示提示信息
                    messagebox.showinfo(
                        "提示",
                        "新术语库将在翻译过程中自动填充\n"
                        "翻译完成后会自动保存为 Excel 文件供编辑"
                    )
        except Exception as e:
            logging.error(f"选择术语库文件失败：{e}")

    def _load_and_preview_terminology(self, path: str):
        """加载并预览术语库"""
        try:
            import pandas as pd
            import os
            
            # 检查文件是否存在
            if not os.path.exists(path):
                logging.info(f"[FILE] 新术语库文件将自动创建：{path}")
                return
            
            # 读取 Excel 文件
            df = pd.read_excel(path, engine='openpyxl')
            
            # 统计基本信息
            total_rows = len(df)
            total_terms = df['中文原文'].notna().sum() if '中文原文' in df.columns else 0
            
            # 获取所有语言列
            lang_columns = [col for col in df.columns if col not in ['Key', '中文原文']]
            
            # 统计各语言的术语数量
            lang_stats = {}
            for lang in lang_columns:
                lang_stats[lang] = df[lang].notna().sum()
            
            # 显示预览窗口
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"📚 术语库预览 - {os.path.basename(path)}")
            preview_window.geometry("800x600")
            
            # 主框架
            main_frame = ttk.Frame(preview_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 统计信息
            stats_frame = ttk.LabelFrame(main_frame, text="📊 术语库统计", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            stats_text = f"总行数：{total_rows} | 有效术语：{total_terms} | 语言数：{len(lang_columns)}"
            ttk.Label(stats_frame, text=stats_text, font=("Arial", 10, "bold")).pack(pady=5)
            
            # 语言统计
            if lang_stats:
                lang_frame = ttk.Frame(stats_frame)
                lang_frame.pack(fill=tk.X, pady=5)
                
                for i, (lang, count) in enumerate(sorted(lang_stats.items())):
                    ttk.Label(lang_frame, text=f"{lang}: {count}条", 
                             foreground="blue").grid(row=i//4, column=i%4, padx=10, pady=2)
            
            # 数据预览表格
            preview_frame = ttk.LabelFrame(main_frame, text="📋 数据预览 (前 20 行)", padding="10")
            preview_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建表格
            columns = list(df.columns[:10])  # 最多显示前 10 列
            tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=15)
            
            # 设置列标题
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # 填充数据 (前 20 行)
            for _, row in df.head(20).iterrows():
                values = [str(row.get(col, ''))[:50] for col in columns]
                tree.insert("", tk.END, values=values)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 底部按钮
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(btn_frame, text="✅ 确定", 
                      command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # 如果文件为空，显示提示
            if total_terms == 0:
                messagebox.showinfo("提示", "术语库为空，可以开始添加术语。")
            
            logging.info(f"📚 术语库已加载预览：{total_rows}行，{total_terms}条术语")
            
        except Exception as e:
            logging.error(f"术语库预览失败：{e}")
            messagebox.showerror("错误", f"加载术语库预览失败:\n{str(e)}")
    
    def _select_source_file(self):
        """选择待翻译文件"""
        try:
            path = filedialog.askopenfilename(
                title="选择待翻译文件", 
                filetypes=[("Excel", "*.xlsx")]
            )
            if path:
                self.source_path.set(path)
                # 添加控制台日志输出
                logging.info(f"[GUI] 用户操作：选择待翻译文件 - {path}")
        except Exception as e:
            logging.error(f"选择待翻译文件失败：{e}")

    def _select_all_langs(self):
        """全选所有语言"""
        try:
            for var in self.lang_vars.values():
                var.set(True)
            self._update_lang_status()
            # 添加控制台日志输出
            logging.info(f"[GUI] 用户操作：全选所有语言")
        except Exception as e:
            logging.error(f"全选语言失败：{e}")
    
    def _deselect_all_langs(self):
        """取消全选所有语言"""
        try:
            for var in self.lang_vars.values():
                var.set(False)
            self._update_lang_status()
            # 添加控制台日志输出
            logging.info(f"[GUI] 用户操作：取消全选语言")
        except Exception as e:
            logging.error(f"取消全选语言失败：{e}")

    def _update_lang_status(self):
        """更新语言选择状态显示"""
        count = sum(1 for v in self.lang_vars.values() if v.get())
        self.lang_status_label.config(text=f"已选：{count}")
        self.selected_langs = [k for k, v in self.lang_vars.items() if v.get()]
    
    def _on_provider_changed(self, event=None):
        """API 提供商切换处理"""
        try:
            selected = self.current_provider_var.get()
            from service.api_provider import APIProvider
            
            # 查找对应的枚举值
            provider_enum = None
            for p in APIProvider:
                if p.value == selected:
                    provider_enum = p
                    break
            
            if provider_enum:
                self.provider_manager.set_provider(provider_enum)
                self._update_provider_info()
                logging.info(f"🔌 切换到 API 提供商：{provider_enum.value}")
        except Exception as e:
            messagebox.showerror("错误", f"切换 API 提供商失败:\n{str(e)}")
    
    def _update_provider_info(self):
        """更新提供商信息显示"""
        try:
            provider = self.provider_manager.get_current_provider()
            config = self.provider_manager.get_provider(provider)
            
            if config:
                info = f"{config.name} | 模型：{config.default_model} | URL: {config.base_url[:30]}..."
                self.provider_info_label.config(text=info)
        except Exception:
            self.provider_info_label.config(text="")

    def _validate_prompts(self):
        """验证提示词格式"""
        draft = self.draft_text.get('1.0', tk.END).strip()
        review = self.review_text.get('1.0', tk.END).strip()

        errors = []
        if "{target_lang}" not in draft:
            errors.append("Draft 缺少 {target_lang}")
        if "json" not in draft.lower():
            errors.append("Draft 缺少 JSON 要求")

        if self.mode_var.get() == 1:
            if "{target_lang}" not in review:
                errors.append("Review 缺少 {target_lang}")
            if "json" not in review.lower():
                errors.append("Review 缺少 JSON 要求")

        if errors:
            messagebox.showerror("校验失败", "\n".join(errors))
            return False
            
        messagebox.showinfo("成功", "提示词格式校验通过！")
        self.prompt_draft.set(draft)
        self.prompt_review.set(review)
        return True
    
    def _load_config_from_file(self):
        """从配置文件加载配置"""
        try:
            config_dict = self.config_persistence.load()
            
            # 加载 API 配置
            if 'api_key' in config_dict:
                import os
                os.environ['DEEPSEEK_API_KEY'] = config_dict['api_key']
            
            # 显示加载成功消息
            logging.info(f"✅ 已加载配置文件：{self.config_file}")
            
        except Exception as e:
            messagebox.showerror("加载失败", f"无法加载配置文件:\n{str(e)}")
    
    def _load_config_dialog(self):
        """打开加载配置文件对话框"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[
                ("JSON 文件", "*.json"),
                ("YAML 文件", "*.yaml *.yml"),
                ("TXT 文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 如果是 TXT 文件，加载为提示词
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 询问用户要加载到哪个提示词
                    result = messagebox.askquestion(
                        "选择提示词类型",
                        "要加载为哪个提示词？\n\n点击'是'加载为初译提示词 (Draft)\n点击'否'加载为校对提示词 (Review)",
                        icon='question'
                    )
                    
                    if result == 'yes':
                        self.draft_text.delete('1.0', tk.END)
                        self.draft_text.insert('1.0', content)
                        logging.info(f"📄 已加载初译提示词：{file_path}")
                    else:
                        self.review_text.delete('1.0', tk.END)
                        self.review_text.insert('1.0', content)
                        logging.info(f"📄 已加载校对提示词：{file_path}")
                    
                    messagebox.showinfo("成功", f"已加载提示词:\n{file_path}")
                else:
                    # JSON/YAML 配置文件加载
                    persistence = ConfigPersistence(file_path)
                    config_dict = persistence.load()
                    
                    # 应用配置
                    if 'api_key' in config_dict:
                        import os
                        os.environ['DEEPSEEK_API_KEY'] = config_dict['api_key']
                    
                    # 更新 GUI 中的配置值（如果有相关 UI）
                    # 这里可以添加更多配置项的加载逻辑
                    
                    messagebox.showinfo("成功", f"已加载配置:\n{file_path}")
                    logging.info(f"✅ 已加载配置文件：{file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败:\n{str(e)}")
    
    def _save_config_dialog(self):
        """打开保存配置文件对话框"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[
                ("JSON 文件", "*.json"),
                ("YAML 文件", "*.yaml *.yml"),
                ("TXT 文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 如果是 TXT 文件，保存当前选中的提示词
                if file_path.endswith('.txt'):
                    # 获取当前选中的选项卡
                    current_tab = self.notebook.index(self.notebook.select())
                    
                    if current_tab == 0:  # Draft 选项卡
                        content = self.draft_text.get('1.0', tk.END).strip()
                        prompt_type = "初译提示词"
                    else:  # Review 选项卡
                        content = self.review_text.get('1.0', tk.END).strip()
                        prompt_type = "校对提示词"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    messagebox.showinfo("成功", f"已保存{prompt_type}到:\n{file_path}")
                    logging.info(f"💾 已保存{prompt_type}: {file_path}")
                else:
                    # JSON/YAML 配置文件保存
                    import os
                    provider = self.provider_manager.get_current_provider()
                    provider_config = self.provider_manager.get_provider(provider)
                    
                    config_dict = {
                        'api_key': os.environ.get(provider_config.api_key_env if provider_config else 'DEEPSEEK_API_KEY', ''),
                        'base_url': provider_config.base_url if provider_config else 'https://api.deepseek.com',
                        'model_name': provider_config.default_model if provider_config else 'deepseek-chat',
                        'api_provider': provider.value,
                        'temperature': 0.3,
                        'top_p': 0.8,
                        'initial_concurrency': 8,
                        'max_concurrency': 10,
                        # 可以根据需要从 GUI 中读取更多配置
                    }
                    
                    persistence = ConfigPersistence(file_path)
                    persistence.save(config_dict)
                    
                    messagebox.showinfo("成功", f"配置已保存到:\n{file_path}")
                    logging.info(f"💾 配置已保存：{file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败:\n{str(e)}")

    def _start_workflow(self):
        """启动翻译工作流"""
        try:
            if self.is_running:
                messagebox.showwarning("警告", "任务正在运行中...")
                return

            # 验证输入
            if not self.term_path.get() or not self.source_path.get():
                messagebox.showerror("错误", "请先选择术语库和待翻译文件！")
                return

            if not self.selected_langs:
                messagebox.showerror("错误", "请至少选择一种目标语言！")
                return

            if not self._validate_prompts():
                return

            # 添加控制台日志输出
            logging.info(f"[GUI] 用户操作：点击开始翻译任务")
            logging.info(f"[START] 开始翻译工作流 - 模式：{'新文档 (双阶段)' if self.mode_var.get() == 1 else '旧文档校对'}")
            logging.info(f"[CONFIG] 术语库：{self.term_path.get()}")
            logging.info(f"[CONFIG] 源文件：{self.source_path.get()}")
            logging.info(f"[CONFIG] 目标语言：{', '.join(self.selected_langs)}")

            self.is_running = True
            self.start_btn.config(state='disabled')
            self.progress_bar['value'] = 0

            # 启动异步任务
            threading.Thread(target=self._run_async_loop, daemon=True).start()
        except Exception as e:
            logging.error(f"启动工作流失败：{e}")

    def _run_async_loop(self):
        """运行异步循环"""
        try:
            asyncio.run(self._execute_task())
        except Exception as e:
            import logging
            logging.exception(f"工作流异常：{e}")
            self.root.after(0, lambda: messagebox.showerror("崩溃", str(e)))
        finally:
            self.root.after(0, self._on_task_complete)

    async def _execute_task(self):
        """执行翻译任务"""
        # 优先使用配置文件加载配置
        if self.config_file and self.config_persistence:
            try:
                config = Config.from_file(self.config_file)
            except Exception as e:
                logging.warning(f"配置文件加载失败，使用默认配置：{e}")
                config = Config()
        else:
            config = Config()
        term_path = self.term_path.get()
        source_path = self.source_path.get()
        mode = self.mode_var.get()
        langs = self.selected_langs
        p_draft = self.draft_text.get('1.0', tk.END).strip()
        p_review = self.review_text.get('1.0', tk.END).strip()

        import logging
        logging.info(f"🌍 目标语言：{', '.join(langs)}")
        logging.info("✅ 初始化引擎...")

        tm = TerminologyManager(term_path, config)
        client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
        
        # 生成批次 ID
        import uuid
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        orchestrator = WorkflowOrchestrator(
            config, client, tm, p_draft, p_review,
            file_path=source_path,
            batch_id=batch_id
        )

        df = pd.read_excel(source_path, engine='openpyxl')
        
        # 统计源文件信息
        total_rows = len(df)
        valid_rows = sum(1 for _, row in df.iterrows() if str(row.get('中文原文', '')).strip())
        logging.info(f"📊 源文件分析：共{total_rows}行，有效原文{valid_rows}行")
        
        tasks = []
        for i, row in df.iterrows():
            src = str(row.get('中文原文', '')).strip()
            if not src:
                continue
            
            # 处理原译文：检查是否是空值或"nan"字符串
            original_trans_raw = row.get('原译文', '') if mode == 2 else ""
            if pd.isna(original_trans_raw) or str(original_trans_raw).lower() == 'nan':
                original_trans = ""
            else:
                original_trans = str(original_trans_raw).strip()
            
            for lang in langs:
                ctx = TaskContext(
                    idx=i, 
                    key=str(row.get('key', i)), 
                    source_text=src,
                    original_trans=original_trans, 
                    target_lang=lang
                )
                tasks.append(ctx)
        
        total = len(tasks)
        logging.info(f"📋 任务生成：{total}个任务 ({valid_rows}行 x {len(langs)}语言)")
        logging.info(f"🚀 开始处理 {total} 个任务...")

        # 优化 1: 分批处理，每批大小根据语言数量动态调整
        batch_size = max(config.batch_size // len(langs), 10)  # 至少 10 个任务一批
        
        # 优化 2: 预分配结果列表，避免频繁扩容
        results = []
        results.extend([None] * total)
        
        failed_count = 0
        success_count = 0

        # 启动进度跟踪
        self._start_progress_tracking(total)

        # 优化 3: 自定义 tqdm 用于更新 GUI 进度条
        class GuiTqdm:
            def __init__(self, app, total):
                self.app = app
                self.total = total
                self.current = 0

            def update(self, n=1):
                self.current += n
                # 更新进度显示（包含 ETA）
                self.app.root.after(0, lambda: self.app._update_progress_display(self.current, self.total))

            def close(self): 
                pass

        p_bar = GuiTqdm(self, total)

        # 优化 4: worker 函数增加统计
        async def worker(ctx, idx):
            nonlocal failed_count, success_count
            try:
                res = await orchestrator.process_task(ctx)
                if res.status == "SUCCESS":
                    success_count += 1
                else:
                    failed_count += 1
                p_bar.update(1)
                return res
            except Exception as e:
                failed_count += 1
                p_bar.update(1)
                logger.exception(f"任务 {idx} 处理失败：{e}")
                return None

        # 优化 5: 使用信号量控制并发，而不是在 gather 中创建大量任务
        semaphore = asyncio.Semaphore(self.controller.get_limit())
        
        async def bounded_worker(ctx, idx):
            async with semaphore:
                return await worker(ctx, idx)

        # 优化 6: 分批并发执行
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_indices = range(i, i + len(batch))
            
            # 创建有界并发任务
            batch_tasks = [
                bounded_worker(t, idx) for t, idx in zip(batch, batch_indices)
            ]
            
            # 等待当前批次完成
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # 收集结果
            valid_results = [r for r in batch_results if isinstance(r, FinalResult)]
            for j, result in enumerate(valid_results):
                if j < len(batch):
                    results[i + j] = result
            
            # 优化 7: 定期清理内存和更新并发度
            if (i // batch_size) % config.gc_interval == 0:
                gc.collect()
                # 动态调整并发度
                current_limit = self.controller.get_limit()
                if current_limit != semaphore._value:
                    semaphore = asyncio.Semaphore(current_limit)

        await tm.shutdown()

        # 停止进度跟踪
        self._stop_progress_tracking()

        # 保存结果
        if results:
            # 按 key 和 source_text 分组，将不同语言的翻译放在不同列
            from collections import defaultdict
            grouped_data = defaultdict(lambda: {'key': None, 'source_text': None})
            
            for r in results:
                key = r.key
                grouped_data[key]['key'] = r.key
                grouped_data[key]['source_text'] = r.source_text
                
                # 根据状态填入翻译
                if r.status == "SUCCESS":
                    grouped_data[key][r.target_lang] = r.final_trans
                else:
                    grouped_data[key][r.target_lang] = '(Failed)'
            
            # 转换为 DataFrame，确保列顺序：key, source_text, 其他语言列
            output_data = list(grouped_data.values())
            out_df = pd.DataFrame(output_data)
            
            # 重新排列列顺序：key, source_text 在前，其他语言列按字母顺序
            cols = ['key', 'source_text'] + [c for c in out_df.columns if c not in ['key', 'source_text']]
            out_df = out_df[cols]
            
            # 填充空值为 (Failed)
            out_df = out_df.fillna('(Failed)')
            
            out_file = f"Result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            out_df.to_excel(out_file, index=False, engine='openpyxl')
            logging.info(f"💾 结果已保存：{out_file}")
            
            # 显示完成消息，提示术语库已自动导出
            success_count = len([r for r in results if r.status == 'SUCCESS'])
            message = (
                f"任务完成!\n"
                f"成功：{success_count}\n"
                f"文件：{out_file}\n\n"
                f"✅ 术语库已自动保存并导出:\n{term_path}\n\n"
                f"💡 下次翻译时会自动使用最新的术语库"
            )
            self.root.after(0, lambda: messagebox.showinfo("完成", message))
        else:
            logging.warning("⚠️ 无有效结果生成。")

    def _on_task_complete(self):
        """任务完成回调"""
        self.is_running = False
        self.start_btn.config(state='normal')
    
    def _show_history(self):
        """显示翻译历史窗口"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📊 翻译历史记录")
        history_window.geometry("800x600")
        
        # 创建框架
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="状态:").pack(side=tk.LEFT, padx=(20, 5))
        status_var = tk.StringVar(value="ALL")
        status_combo = ttk.Combobox(search_frame, textvariable=status_var, 
                                   values=["ALL", "SUCCESS", "FAILED"], state="readonly", width=10)
        status_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍 搜索", command=lambda: self._search_history(search_var.get(), status_var.get(), result_tree)).pack(side=tk.LEFT, padx=10)
        ttk.Button(search_frame, text="🔄 刷新", command=lambda: self._refresh_history(result_tree)).pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        try:
            stats = self.history_manager.get_statistics()
            stats_text = f"总记录：{stats['total']} | 成功：{stats['success']} | 失败：{stats['failed']} | 成功率：{stats['success_rate']}%"
            ttk.Label(stats_frame, text=stats_text, foreground="blue").pack()
        except Exception as e:
            ttk.Label(stats_frame, text=f"统计失败：{e}").pack()
        
        # 历史记录表格
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "key", "source", "target", "status", "lang", "time")
        result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        result_tree.heading("id", text="ID")
        result_tree.heading("key", text="键")
        result_tree.heading("source", text="原文")
        result_tree.heading("target", text="译文")
        result_tree.heading("status", text="状态")
        result_tree.heading("lang", text="目标语言")
        result_tree.heading("time", text="时间")
        
        result_tree.column("id", width=50)
        result_tree.column("key", width=100)
        result_tree.column("source", width=200)
        result_tree.column("target", width=200)
        result_tree.column("status", width=80)
        result_tree.column("lang", width=80)
        result_tree.column("time", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=result_tree.yview)
        result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 加载最近记录
        self._refresh_history(result_tree)
        
        # 双击查看详情
        def on_double_click(event):
            selection = result_tree.selection()
            if selection:
                item = result_tree.item(selection[0])
                record_id = item['values'][0]
                self._show_record_detail(record_id)
        
        result_tree.bind("<Double-Button-1>", on_double_click)
    
    def _refresh_history(self, tree):
        """刷新历史记录列表"""
        # 清空现有项
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            records = self.history_manager.get_recent_records(limit=100)
            for record in records:
                tree.insert("", tk.END, values=(
                    record.id,
                    record.key,
                    record.source_text[:50] + "..." if len(record.source_text) > 50 else record.source_text,
                    record.final_trans[:50] + "..." if len(record.final_trans) > 50 else record.final_trans,
                    record.status,
                    record.target_lang,
                    record.created_at[:19].replace('T', ' ')
                ))
        except Exception as e:
            messagebox.showerror("错误", f"加载历史记录失败:\n{str(e)}")
    
    def _search_history(self, keyword: str, status: str, tree):
        """搜索历史记录"""
        try:
            # 清空现有项
            for item in tree.get_children():
                tree.delete(item)
            
            status_filter = None if status == "ALL" else status
            records = self.history_manager.search_records(
                keyword=keyword,
                status=status_filter,
                limit=100
            )
            
            for record in records:
                tree.insert("", tk.END, values=(
                    record.id,
                    record.key,
                    record.source_text[:50] + "..." if len(record.source_text) > 50 else record.source_text,
                    record.final_trans[:50] + "..." if len(record.final_trans) > 50 else record.final_trans,
                    record.status,
                    record.target_lang,
                    record.created_at[:19].replace('T', ' ')
                ))
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败:\n{str(e)}")
    
    def _show_record_detail(self, record_id: int):
        """显示记录详情"""
        try:
            record = self.history_manager.get_record_by_id(record_id)
            if not record:
                messagebox.showerror("错误", "记录不存在")
                return
            
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"📝 翻译记录详情 - ID:{record.id}")
            detail_window.geometry("600x500")
            
            main_frame = ttk.Frame(detail_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 信息标签
            info_text = f"""
ID: {record.id}
批次 ID: {record.batch_id}
源文件：{record.file_path}

【原文】
Key: {record.key}
内容：{record.source_text}

【译文】
原译：{record.original_trans or '无'}
初译：{record.draft_trans}
最终：{record.final_trans}

【信息】
目标语言：{record.target_lang}
状态：{record.status}
诊断：{record.diagnosis}
原因：{record.reason}

【API 信息】
提供商：{record.api_provider}
模型：{record.model_name}
时间：{record.created_at.replace('T', ' ')}
"""
            
            text_widget = scrolledtext.ScrolledText(main_frame, height=30, font=("Consolas", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', info_text)
            text_widget.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("错误", f"显示详情失败:\n{str(e)}")
    
    def _export_history(self):
        """导出历史记录"""
        file_path = filedialog.asksaveasfilename(
            title="导出历史记录",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                output_file = self.history_manager.export_to_json(file_path)
                messagebox.showinfo("成功", f"历史已导出到:\n{output_file}")
                logging.info(f"💾 翻译历史已导出：{output_file}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")
    
    def _clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有翻译历史记录吗？\n此操作不可恢复！"):
            try:
                count = self.history_manager.clear_history()
                messagebox.showinfo("成功", f"已清空 {count} 条历史记录")
                logging.info(f"🗑️ 已清空 {count} 条翻译历史")
            except Exception as e:
                messagebox.showerror("错误", f"清空失败:\n{str(e)}")
    
    def _import_terminology(self):
        """导入术语库"""
        file_path = filedialog.askopenfilename(
            title="选择要导入的术语库文件",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 创建异步任务
            threading.Thread(
                target=self._run_import_task, 
                args=(file_path,), 
                daemon=True
            ).start()
    
    def _run_import_task(self, file_path: str):
        """运行导入任务的后台线程"""
        try:
            import asyncio
            from business_logic.terminology_manager import TerminologyManager
            from infrastructure.models import Config
            
            # 获取配置
            config = Config()
            
            # 创建术语管理器（临时）
            tm = TerminologyManager(file_path, config)
            
            # 这里需要从当前术语库导入到现有术语库
            # 由于 GUI 中 term_path 是用户选择的术语库路径
            # 我们需要重新创建一个管理器来操作实际的术语库
            self.root.after(0, lambda: messagebox.showinfo(
                "提示", 
                "术语库导入功能需要在翻译任务执行时自动进行。\n\n"
                "每次翻译完成后，新术语会自动添加到术语库中。\n\n"
                "如需批量导入外部术语库，请使用命令行工具或 Python API。"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"导入失败:\n{str(e)}"))
    
    def _show_tm_statistics(self):
        """显示术语库统计信息"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 术语库统计")
        stats_window.geometry("600x400")
        
        main_frame = ttk.Frame(stats_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="📚 术语库统计信息", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # 统计信息文本
        stats_text = scrolledtext.ScrolledText(main_frame, height=20, font=("Consolas", 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            # 获取当前术语库路径
            term_path = self.term_path.get()
            
            if not term_path:
                stats_text.insert('1.0', "请先选择术语库文件")
                stats_text.configure(state='disabled')
                return
            
            # 创建临时管理器读取统计
            import asyncio
            from business_logic.terminology_manager import TerminologyManager
            from infrastructure.models import Config
            
            config = Config()
            tm = TerminologyManager(term_path, config)
            
            # 由于 get_statistics 是异步方法，需要同步调用
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            stats = loop.run_until_complete(tm.get_statistics())
            loop.close()
            
            # 格式化输出
            output = f"""
术语库文件：{term_path}

【基本统计】
源文本数量：{stats.get('total_source_texts', 0)}
翻译总数：{stats.get('total_translations', 0)}
支持语言：{stats.get('languages_count', 0)} 种

【支持的语言】
{chr(10).join(f'  • {lang}' for lang in stats.get('languages', []))}

【说明】
• 源文本：唯一的中文原文条目数
• 翻译总数：所有语言的翻译总数（同一源文本可能有多种语言）
• 支持语言：术语库中包含的不同语言种类
"""
            
            stats_text.insert('1.0', output)
            stats_text.configure(state='disabled')
            
        except Exception as e:
            error_msg = f"获取统计信息失败：\n{str(e)}\n\n"
            error_msg += "可能原因：\n"
            error_msg += "1. 术语库文件不存在或未加载\n"
            error_msg += "2. 术语库格式不正确\n"
            error_msg += "3. 术语库为空"
            
            stats_text.insert('1.0', error_msg)
            stats_text.configure(state='disabled')
    
    def _show_tm_history(self):
        """显示术语库历史窗口"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📜 术语库变更历史")
        history_window.geometry("900x600")
        
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="📚 术语库变更历史", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # 筛选器
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="天数:").pack(side=tk.LEFT, padx=5)
        days_var = tk.StringVar(value="7")
        days_spin = ttk.Spinbox(filter_frame, from_=1, to=365, 
                               textvariable=days_var, width=5)
        days_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍 查看时间线", 
                  command=lambda: self._load_timeline(tree, days_var.get())).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(filter_frame, text="💾 导出历史", 
                  command=self._export_tm_history).pack(side=tk.LEFT, padx=5)
        
        # 时间线表格
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("date", "change_type", "count", "sources")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        tree.heading("date", text="日期")
        tree.heading("change_type", text="变更类型")
        tree.heading("count", text="数量")
        tree.heading("sources", text="示例源文本")
        
        tree.column("date", width=100)
        tree.column("change_type", width=100)
        tree.column("count", width=80)
        tree.column("sources", width=500)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 变更记录详情表格
        detail_tree_frame = ttk.Frame(main_frame)
        detail_tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(detail_tree_frame, text="变更记录详情", 
                 font=("Arial", 12, "bold")).pack()
        
        detail_columns = ("time", "type", "source", "lang", "old", "new")
        detail_tree = ttk.Treeview(detail_tree_frame, columns=detail_columns, 
                                  show="headings", height=10)
        
        detail_tree.heading("time", text="时间")
        detail_tree.heading("type", text="类型")
        detail_tree.heading("source", text="源文本")
        detail_tree.heading("lang", text="语言")
        detail_tree.heading("old", text="旧值")
        detail_tree.heading("new", text="新值")
        
        for col in detail_columns:
            detail_tree.column(col, width=120)
        
        detail_scrollbar = ttk.Scrollbar(detail_tree_frame, orient=tk.VERTICAL, 
                                        command=detail_tree.yview)
        detail_tree.configure(yscrollcommand=detail_scrollbar.set)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 加载数据
        self._load_timeline(tree, days_var.get())
        
        # 双击查看详情
        def on_double_click(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                date = item['values'][0]
                change_type = item['values'][1]
                self._load_detail_changes(detail_tree, date, change_type)
        
        tree.bind("<Double-Button-1>", on_double_click)
    
    def _load_timeline(self, tree, days: str):
        """加载时间线数据"""
        # 清空现有项
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            import asyncio
            from business_logic.terminology_manager import TerminologyManager
            from infrastructure.models import Config
            
            term_path = self.term_path.get()
            if not term_path:
                messagebox.showwarning("警告", "请先选择术语库文件")
                return
            
            config = Config()
            tm = TerminologyManager(term_path, config)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            timeline = loop.run_until_complete(tm.get_history_timeline(days=int(days)))
            loop.close()
            
            type_names = {
                'added': '➕ 新增',
                'updated': '✏️ 更新',
                'deleted': '❌ 删除',
                'imported': '📥 导入'
            }
            
            for entry in timeline:
                type_name = type_names.get(entry['change_type'], entry['change_type'])
                sources_text = ', '.join(entry['sources'][:3])
                if len(entry['sources']) > 3:
                    sources_text += f'... 等{len(entry["sources"])}条'
                
                tree.insert("", tk.END, values=(
                    entry['date'],
                    type_name,
                    entry['count'],
                    sources_text
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"加载时间线失败:\n{str(e)}")
    
    def _load_detail_changes(self, tree, date: str, change_type: str):
        """加载详细变更记录"""
        # 清空现有项
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            import asyncio
            from business_logic.terminology_manager import TerminologyManager
            from infrastructure.models import Config
            
            term_path = self.term_path.get()
            config = Config()
            tm = TerminologyManager(term_path, config)
            
            # 查询该日期的变更记录
            start_date = f"{date}T00:00:00"
            end_date = f"{date}T23:59:59"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            changes = loop.run_until_complete(
                tm.get_history_changes(
                    start_date=start_date,
                    end_date=end_date,
                    change_type=change_type,
                    limit=100
                )
            )
            loop.close()
            
            type_names = {
                'added': '➕',
                'updated': '✏️',
                'deleted': '❌',
                'imported': '📥'
            }
            
            for change in changes:
                time_str = change['timestamp'].replace('T', ' ')
                type_icon = type_names.get(change['change_type'], '')
                old_value = change.get('old_value', '') or '-'
                new_value = change.get('new_value', '') or '-'
                
                tree.insert("", tk.END, values=(
                    time_str[:16],
                    f"{type_icon} {change['change_type']}",
                    change['source_text'],
                    change['language'],
                    old_value[:30] + ('...' if len(old_value) > 30 else ''),
                    new_value[:30] + ('...' if len(new_value) > 30 else '')
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"加载详情失败:\n{str(e)}")
    
    def _export_tm_history(self):
        """导出术语库历史"""
        file_path = filedialog.asksaveasfilename(
            title="导出术语库历史",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                import asyncio
                from business_logic.terminology_manager import TerminologyManager
                from infrastructure.models import Config
                
                term_path = self.term_path.get()
                config = Config()
                tm = TerminologyManager(term_path, config)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                output_file = loop.run_until_complete(tm.export_history(file_path))
                loop.close()
                
                messagebox.showinfo("成功", f"历史已导出到:\n{output_file}")
                logging.info(f"💾 术语库历史已导出：{output_file}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")
    
    # ========== 撤销/重做功能 ==========
    
    def _undo_last_operation(self):
        """撤销最后一个操作"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            op = loop.run_until_complete(undo_last_operation())
            loop.close()
            
            if op:
                # 添加控制台日志输出
                logging.info(f"[GUI] 用户操作：撤销 - {op.type.value}")
                logging.info(f"↩️ 已撤销操作：{op.type.value} - {op.description}")
                messagebox.showinfo(
                    "撤销成功",
                    f"已撤销操作:\n{op.description}\n\n"
                    f"类型：{op.type.value}\n"
                    f"时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(op.timestamp))}"
                )
                self._update_undo_buttons()
            else:
                messagebox.showinfo("提示", "没有可撤销的操作")
        except Exception as e:
            messagebox.showerror("错误", f"撤销失败:\n{str(e)}")
            logging.error(f"撤销操作失败：{e}")
    
    def _redo_last_operation(self):
        """重做最近撤销的操作"""
        try:
            import asyncio
            from infrastructure.undo_manager import redo_last_operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            op = loop.run_until_complete(redo_last_operation())
            loop.close()
            
            if op:
                # 添加控制台日志输出
                logging.info(f"[GUI] 用户操作：重做 - {op.type.value}")
                logging.info(f"↪️ 已重做操作：{op.type.value} - {op.description}")
                messagebox.showinfo(
                    "重做成功",
                    f"已重做操作:\n{op.description}\n\n"
                    f"类型：{op.type.value}\n"
                    f"时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(op.timestamp))}"
                )
                self._update_undo_buttons()
            else:
                messagebox.showinfo("提示", "没有可重做的操作")
        except Exception as e:
            messagebox.showerror("错误", f"重做失败:\n{str(e)}")
            logging.error(f"重做操作失败：{e}")
    
    def _update_undo_buttons(self):
        """更新撤销/重做按钮状态"""
        can_undo = self.undo_manager.can_undo()
        can_redo = self.undo_manager.can_redo()
        
        self.undo_btn.config(state='normal' if can_undo else 'disabled')
        self.redo_btn.config(state='normal' if can_redo else 'disabled')
        
        stats = self.undo_manager.get_stats()
        if stats['history_size'] > 0:
            self.undo_status_label.config(
                text=f"历史：{stats['history_size']} | 撤销：{stats['undo_count']} | 重做：{stats['redo_count']}"
            )
        else:
            self.undo_status_label.config(text="无操作历史")
    
    # ========== 进度更新功能 ==========
    
    def _update_progress_display(self, completed: int, total: int):
        """
        更新进度显示
        
        Args:
            completed: 已完成数量
            total: 总数量
        """
        try:
            # 更新进度估计器
            update_progress(completed)
            
            # 获取进度信息
            progress_info = get_current_progress()
            
            # 更新进度条
            percent = progress_info['progress_percent']
            self.progress_bar['value'] = percent
            
            # 更新百分比标签
            self.progress_percent_label.config(text=f"进度：{percent:.1f}%")
            
            # 更新预计剩余时间
            eta_formatted = progress_info['eta_formatted']
            if eta_formatted != "--:--:--":
                self.progress_eta_label.config(text=f"预计剩余：{eta_formatted}")
            
            # 更新速度
            speed = progress_info['speed_per_second']
            if speed > 0:
                self.progress_speed_label.config(text=f"速度：{speed:.1f} 项/秒")
            
            # 刷新界面
            self.root.update_idletasks()
            
        except Exception as e:
            logging.error(f"更新进度显示失败：{e}")
    
    def _start_progress_tracking(self, total_items: int):
        """开始进度跟踪"""
        start_progress_tracking(total_items)
        self._update_progress_display(0, total_items)
    
    def _stop_progress_tracking(self):
        """停止进度跟踪"""
        self.progress_estimator.reset()
        self.progress_percent_label.config(text="进度：0%")
        self.progress_eta_label.config(text="预计剩余：--:--")
        self.progress_speed_label.config(text="速度：0 项/秒")
        self.progress_bar['value'] = 0
    
    # ========================================================================
    # API 提供商动态配置方法（新增）
    # ========================================================================
    
    def _get_available_providers_from_config(self) -> dict:
        """
        从配置文件加载已配置的 API 提供商（只显示配置了 api_key 的）
        
        Returns:
            包含所有已配置提供商的字典
        """
        if not self.config_persistence:
            # 如果没有配置文件，返回空字典
            return {}
        
        try:
            file_config = self.config_persistence.load()
            api_providers = file_config.get('api_providers', {})
            
            if not api_providers:
                # 如果没有配置多提供商，使用单个提供商配置
                api_key = file_config.get('api_key', '')
                if api_key and api_key.strip():
                    provider_name = file_config.get('api_provider', 'deepseek')
                    return {
                        provider_name: {
                            'api_key': api_key,
                            'base_url': file_config.get('base_url', ''),
                            'model_name': file_config.get('model_name', ''),
                            'models': [file_config.get('model_name', '')]
                        }
                    }
                return {}
            
            # 过滤出配置了 api_key 的提供商
            available = {}
            for provider_name, provider_config in api_providers.items():
                api_key = provider_config.get('api_key', '')
                if api_key and api_key.strip():
                    available[provider_name] = provider_config
            
            return available
            
        except Exception as e:
            logging.error(f"加载 API 提供商配置失败：{e}")
            return {}
    
    def _update_provider_combo_values(self):
        """更新提供商下拉框的可选值"""
        if hasattr(self, 'available_providers') and self.available_providers:
            providers_list = list(self.available_providers.keys())
            self.provider_combo['values'] = providers_list
            
            # 设置默认选中项
            if providers_list:
                self.current_provider_var.set(providers_list[0])
                self._on_provider_changed(None)
    
    # ========================================================================
    # 退出程序方法（新增）
    # ========================================================================
    
    def _exit_application(self):
        """退出程序并保存所有数据库到 Excel"""
        try:
            # 显示确认对话框
            result = messagebox.askyesno(
                "确认退出",
                "确定要退出程序吗？\n\n系统将自动保存所有数据到 Excel 文件。"
            )
            
            if result:
                # 记录退出日志
                logging.info("[GUI] 用户操作：点击退出程序")
                logging.info("💾 开始保存所有数据库到 Excel...")
                
                # 调用全局管理器统一保存
                from data_access.global_persistence_manager import shutdown_all_databases
                results = shutdown_all_databases()
                
                # 显示保存结果
                if results['total_failed'] == 0:
                    logging.info(f"✅ 保存成功：共保存 {results['total_saved']} 个数据库")
                    messagebox.showinfo(
                        "退出成功",
                        f"所有数据已保存到 Excel 文件！\n\n"
                        f"保存成功：{results['total_saved']} 个数据库"
                    )
                else:
                    logging.warning(f"⚠️ 保存失败：{results['total_failed']} 个数据库")
                    messagebox.showwarning(
                        "退出警告",
                        f"部分数据保存失败：{results['total_failed']} 个数据库\n\n"
                        f"请检查日志获取详细信息。"
                    )
                
                # 关闭 GUI
                logging.info("👋 程序即将退出...")
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            logging.error(f"退出程序失败：{e}")
            messagebox.showerror("错误", f"退出程序失败:\n{str(e)}")
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        self._exit_application()
