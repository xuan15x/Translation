"""  
AI 智能翻译工作台 GUI - 完全重构版
现代化界面设计，统一样式，功能完整
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import logging
from datetime import datetime

# 导入配置常量（在类定义之前）
from config import (
    T1_LANGUAGES, T2_LANGUAGES, T3_LANGUAGES,
    GAME_TRANSLATION_TYPES
)

# 导入历史管理器
from service.translation_history import get_history_manager, TranslationHistoryManager

logger = logging.getLogger(__name__)


class ModernGUIApp:
    """现代化翻译应用 GUI"""
    
    # 统一的样式配置
    STYLES = {
        'padding': {'padx': 10, 'pady': 10},
        'section_padding': {'pady': (0, 15)},
        'button_padx': 5,
        'button_pady': 8,
        'entry_width': 60,
        'combobox_width': 30,
        'spinbox_width': 15,
        'text_height': 8,
        'log_height': 12,
        'font_family': 'Segoe UI',
        'mono_font': 'Consolas',
        'font_size': 10,
    }
    
    def __init__(self, root, config_file=None):
        """初始化应用"""
        self.root = root
        self.root.title("AI 智能翻译工作台 v3.0")
        self.root.geometry("1200x900")
        
        # 配置样式
        self._setup_styles()
        
        # 状态变量
        self._init_variables()
        
        # 创建主界面（带滚动条）
        self._create_scrollable_main_area()
        
        # 构建各个功能区域
        self._create_file_section()
        self._create_api_section()
        self._create_advanced_params_section()
        self._create_translation_type_section()
        self._create_language_section()
        self._create_prompt_section()
        self._create_control_section()
        
        # 绑定事件
        self._bind_events()
        
        logger.info("✅ 现代化 GUI 初始化完成")
    
    def _setup_styles(self):
        """配置全局样式"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用现代主题
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Section.TLabelFrame', font=('Segoe UI', 11, 'bold'))
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Tool.TButton', font=('Segoe UI', 9))
    
    def _init_variables(self):
        """初始化所有状态变量"""
        # 文件路径
        self.term_path = tk.StringVar()
        self.source_path = tk.StringVar()
        self.mode_var = tk.IntVar(value=1)
        
        # API 配置
        self.current_provider_var = tk.StringVar(value="deepseek")
        
        # 双阶段参数
        self.draft_model_var = tk.StringVar()
        self.draft_temp_var = tk.DoubleVar(value=0.3)
        self.draft_top_p_var = tk.DoubleVar(value=0.8)
        self.draft_timeout_var = tk.IntVar(value=60)
        self.draft_max_tokens_var = tk.IntVar(value=512)
        
        self.review_model_var = tk.StringVar()
        self.review_temp_var = tk.DoubleVar(value=0.5)
        self.review_top_p_var = tk.DoubleVar(value=0.9)
        self.review_timeout_var = tk.IntVar(value=60)
        self.review_max_tokens_var = tk.IntVar(value=512)
        
        # 翻译方向
        self.translation_type_var = tk.StringVar(value="match3_item")
        
        # 语言选择
        self.lang_vars = {}
        self.selected_langs = []
        
        # 提示词
        self.prompt_draft = tk.StringVar()
        self.prompt_review = tk.StringVar()
        
        # 控制状态
        self.is_running = False
        self.progress_var = tk.DoubleVar()
        
        # 日志和性能
        self.log_level_var = tk.StringVar(value="INFO")
        self.log_granularity_var = tk.StringVar(value="normal")
        self.perf_monitor_var = tk.BooleanVar(value=False)
        
        # 历史记录管理器
        self.translation_history_manager: TranslationHistoryManager = None
        self._initialize_history_manager()
    
    def _create_scrollable_main_area(self):
        """创建可滚动的主区域"""
        # 主 Canvas
        self.main_canvas = tk.Canvas(self.root, bg='#f5f5f5')
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        
        # 可滚动框架
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # 创建窗口
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 打包
        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 主内容框架
        self.main_frame = ttk.Frame(self.scrollable_frame, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def _initialize_history_manager(self):
        """初始化历史记录管理器"""
        try:
            self.translation_history_manager = get_history_manager()
            logger.info("✅ 历史记录管理器已初始化")
        except Exception as e:
            logger.error(f"❌ 历史记录管理器初始化失败：{e}")
            self.translation_history_manager = None
    
    def _on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_file_section(self):
        """创建文件配置区"""
        frame = ttk.LabelFrame(self.main_frame, text="📂 文件配置")
        frame.pack(fill=tk.X, **self.STYLES['section_padding'])
        
        # 术语库
        ttk.Label(frame, text="术语库 (Excel):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.term_path, width=self.STYLES['entry_width'], state='readonly').grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...", command=self._select_term_file, style='Tool.TButton').grid(
            row=0, column=2, pady=5)
        
        # 待翻译文件
        ttk.Label(frame, text="待翻译 (Excel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.source_path, width=self.STYLES['entry_width'], state='readonly').grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...", command=self._select_source_file, style='Tool.TButton').grid(
            row=1, column=2, pady=5)
        
        # 翻译模式
        mode_frame = ttk.Frame(frame)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=10)
        ttk.Radiobutton(mode_frame, text="🆕 新文档 (双阶段)", variable=self.mode_var, value=1).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(mode_frame, text="📝 旧文档校对", variable=self.mode_var, value=2).pack(side=tk.LEFT, padx=15)
    
    def _create_api_section(self):
        """创建 API 配置区"""
        frame = ttk.LabelFrame(self.main_frame, text="🔌 API 配置")
        frame.pack(fill=tk.X, **self.STYLES['section_padding'])
        
        # API 提供商选择
        provider_frame = ttk.Frame(frame)
        provider_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(provider_frame, text="API 提供商:", width=15, anchor='w').pack(side=tk.LEFT)
        providers = ["deepseek", "openai", "azure"]  # TODO: 从配置加载
        self.provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.current_provider_var,
            values=providers,
            state='readonly',
            width=self.STYLES['combobox_width']
        )
        self.provider_combo.pack(side=tk.LEFT, padx=10)
        self.provider_combo.bind('<<ComboboxSelected>>', self._on_provider_changed)
        
        # 说明标签
        ttk.Label(
            provider_frame,
            text="💡 模型请在下方「双阶段翻译参数」中配置",
            foreground='gray'
        ).pack(side=tk.LEFT, padx=10)
    
    def _create_advanced_params_section(self):
        """创建双阶段参数区"""
        frame = ttk.LabelFrame(self.main_frame, text="⚙️ 双阶段翻译参数")
        frame.pack(fill=tk.X, **self.STYLES['section_padding'])
        
        # 使用 Notebook 分页
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.X, padx=10, pady=10)
        
        # 初译参数页
        draft_frame = ttk.Frame(notebook, padding=10)
        notebook.add(draft_frame, text="📝 初译参数")
        self._create_model_params_frame(draft_frame, prefix='draft')
        
        # 校对参数页
        review_frame = ttk.Frame(notebook, padding=10)
        notebook.add(review_frame, text="✏️ 校对参数")
        self._create_model_params_frame(review_frame, prefix='review', show_sync=True)
        
        # 重置按钮
        reset_frame = ttk.Frame(frame)
        reset_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(
            reset_frame,
            text="🔄 重置为默认值",
            command=self._reset_advanced_params,
            style='Tool.TButton'
        ).pack(side=tk.LEFT, padx=10)
    
    def _create_model_params_frame(self, parent, prefix='', show_sync=False):
        """创建模型参数框架"""
        # 模型选择行
        model_row = ttk.Frame(parent)
        model_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_row, text="模型:", width=15, anchor='w').grid(row=0, column=0, padx=5, pady=5)
        model_var = getattr(self, f'{prefix}_model_var')
        model_combo = ttk.Combobox(
            model_row,
            textvariable=model_var,
            state='readonly',
            width=self.STYLES['combobox_width']
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(model_row, text="(空=使用默认模型)", foreground='gray').grid(
            row=0, column=2, padx=10, pady=5)
        
        # 同步按钮（仅校对页显示）
        if show_sync:
            ttk.Button(
                model_row,
                text="🔄 同步初译模型",
                command=self._sync_draft_model_to_review,
                style='Tool.TButton'
            ).grid(row=0, column=3, padx=10, pady=5)
        
        # 参数行
        params = [
            ("温度", f'{prefix}_temp_var', 0.0, 2.0, 0.1),
            ("Top P", f'{prefix}_top_p_var', 0.0, 1.0, 0.1),
            ("超时 (秒)", f'{prefix}_timeout_var', 10, 300, 10),
            ("Max Tokens", f'{prefix}_max_tokens_var', 128, 4096, 128),
        ]
        
        for label, var_name, from_val, to_val, inc in params:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=f"{label}:", width=15, anchor='w').pack(side=tk.LEFT)
            var = getattr(self, var_name)
            spinbox = ttk.Spinbox(
                row_frame,
                from_=from_val,
                to=to_val,
                increment=inc,
                textvariable=var,
                width=self.STYLES['spinbox_width']
            )
            spinbox.pack(side=tk.LEFT, padx=10, pady=3)
    
    def _create_translation_type_section(self):
        """创建翻译方向选择区"""
        frame = ttk.LabelFrame(self.main_frame, text="🎮 翻译方向")
        frame.pack(fill=tk.X, **self.STYLES['section_padding'])
        
        type_frame = ttk.Frame(frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(type_frame, text="翻译方向:", width=15, anchor='w').pack(side=tk.LEFT)
        
        types = list(GAME_TRANSLATION_TYPES.values())
        self.type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.translation_type_var,
            values=types,
            state='readonly',
            width=self.STYLES['combobox_width']
        )
        self.type_combo.pack(side=tk.LEFT, padx=10)
        self.type_combo.set("🎮 三消 - 道具元素")
        self.type_combo.bind('<<ComboboxSelected>>', self._on_translation_type_changed)
        
        # 说明标签
        ttk.Label(
            type_frame,
            text="💡 仅用于注入禁止事项，不会修改您的提示词",
            foreground='gray'
        ).pack(side=tk.LEFT, padx=10)
    
    def _create_language_section(self):
        """创建语言选择区（T1/T2/T3 分页）"""
        frame = ttk.LabelFrame(self.main_frame, text="🌍 目标语言")
        frame.pack(fill=tk.BOTH, expand=True, **self.STYLES['section_padding'])
        
        # 顶部按钮行
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_row, text="全选当前页", command=self._select_all_langs, style='Tool.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="取消全选当前页", command=self._deselect_all_langs, style='Tool.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="➕ 添加自定义语言", command=self._add_custom_language, style='Tool.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Notebook 分页
        self.lang_notebook = ttk.Notebook(frame)
        self.lang_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tier_lang_frames = {}
        
        # 创建三个分页
        tiers = [
            ("⭐ T1 核心市场", T1_LANGUAGES, "T1"),
            ("🚀 T2 潜力市场", T2_LANGUAGES, "T2"),
            ("🌱 T3 新兴市场", T3_LANGUAGES, "T3"),
        ]
        
        for title, languages, tier in tiers:
            page_frame = ttk.Frame(self.lang_notebook, padding=10)
            self.lang_notebook.add(page_frame, text=f"{title} ({len(languages)})")
            self._create_language_grid(page_frame, languages, tier)
    
    def _create_language_grid(self, parent, languages, tier):
        """创建语言网格"""
        # Canvas + Scrollbar
        canvas = tk.Canvas(parent, height=150, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        grid_frame = ttk.Frame(canvas)
        
        grid_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 5 列布局
        for i, lang in enumerate(languages):
            var = tk.BooleanVar(value=False)
            self.lang_vars[lang] = var
            cb = ttk.Checkbutton(
                grid_frame,
                text=f"{lang} ({tier})",
                variable=var,
                command=self._update_lang_status
            )
            cb.grid(row=i // 5, column=i % 5, sticky=tk.W, padx=10, pady=3)
        
        self.tier_lang_frames[tier] = grid_frame
    
    def _create_prompt_section(self):
        """创建提示词配置区"""
        frame = ttk.LabelFrame(self.main_frame, text="📝 提示词配置")
        frame.pack(fill=tk.BOTH, expand=True, **self.STYLES['section_padding'])
        
        # Notebook 分页
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初译提示词页
        draft_tab = ttk.Frame(notebook)
        notebook.add(draft_tab, text="初译提示词 (Draft)")
        self.draft_text = scrolledtext.ScrolledText(
            draft_tab,
            height=self.STYLES['text_height'],
            font=(self.STYLES['mono_font'], 10)
        )
        self.draft_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 校对提示词页
        review_tab = ttk.Frame(notebook)
        notebook.add(review_tab, text="校对提示词 (Review)")
        self.review_text = scrolledtext.ScrolledText(
            review_tab,
            height=self.STYLES['text_height'],
            font=(self.STYLES['mono_font'], 10)
        )
        self.review_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons = [
            ("💾 保存提示词", self._save_custom_prompts),
            ("📂 加载提示词", self._load_custom_prompts),
            ("🔄 恢复默认", self._restore_default_prompts),
            ("✅ 验证格式", self._validate_prompts),
        ]
        
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command, style='Tool.TButton').pack(side=tk.LEFT, padx=5)
    
    def _create_control_section(self):
        """创建控制与日志区"""
        frame = ttk.LabelFrame(self.main_frame, text="🚀 执行控制")
        frame.pack(fill=tk.BOTH, expand=True, **self.STYLES['section_padding'])
        
        # 性能监控
        perf_frame = ttk.Frame(frame)
        perf_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.perf_monitor_check = ttk.Checkbutton(
            perf_frame,
            text="📊 启用性能监控",
            variable=self.perf_monitor_var,
            command=self._toggle_performance_monitor
        )
        self.perf_monitor_check.pack(side=tk.LEFT, padx=10)
        
        # 日志控制面板
        self._create_log_control_panel(frame)
        
        # 主操作按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        btn_config = {'style': 'Accent.TButton', 'padding': 10}
        self.start_btn = ttk.Button(
            button_frame,
            text="▶️ 开始翻译",
            command=self._start_translation,
            **btn_config
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ 停止",
            command=self._stop_translation,
            state='disabled',
            **btn_config
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.history_btn = ttk.Button(
            button_frame,
            text="📜 查看历史",
            command=self._show_history_window,
            **btn_config
        )
        self.history_btn.pack(side=tk.LEFT, padx=10)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=600
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(frame, text="📋 运行日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=self.STYLES['log_height'],
            font=(self.STYLES['mono_font'], 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置日志重定向
        self._setup_gui_logging()
    
    def _create_log_control_panel(self, parent):
        """创建日志控制面板"""
        panel = ttk.Frame(parent)
        panel.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(panel, text="日志级别:").pack(side=tk.LEFT, padx=10)
        level_combo = ttk.Combobox(
            panel,
            textvariable=self.log_level_var,
            values=('DEBUG', 'INFO', 'WARNING', 'ERROR'),
            state='readonly',
            width=8
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind('<<ComboboxSelected>>', lambda e: self._update_log_level(level_combo.get()))
        
        ttk.Label(panel, text="日志粒度:").pack(side=tk.LEFT, padx=10)
        granularity_combo = ttk.Combobox(
            panel,
            textvariable=self.log_granularity_var,
            values=('minimal', 'basic', 'normal', 'detailed', 'verbose'),
            state='readonly',
            width=10
        )
        granularity_combo.pack(side=tk.LEFT, padx=5)
        granularity_combo.bind('<<ComboboxSelected>>', lambda e: self._update_log_granularity(granularity_combo.get()))
    
    def _setup_gui_logging(self):
        """设置 GUI 日志重定向"""
        class GUILogHandler(logging.Handler):
            def __init__(self, log_text):
                super().__init__()
                self.log_text = log_text
            
            def emit(self, record):
                try:
                    # 检查控件是否仍然存在
                    if self.log_text and self.log_text.winfo_exists():
                        msg = self.format(record)
                        self.log_text.insert(tk.END, msg + '\n')
                        self.log_text.see(tk.END)
                except Exception:
                    # 控件已销毁，忽略
                    pass
        
        handler = GUILogHandler(self.log_text)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    def _bind_events(self):
        """绑定窗口事件"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    # ========== 事件处理方法 ==========
    
    def _on_closing(self):
        """窗口关闭事件"""
        try:
            save = messagebox.askyesno("保存配置", "是否保存当前配置？")
            if save:
                self._save_current_session()
            self.root.destroy()
        except Exception as e:
            logger.error(f"关闭窗口失败：{e}")
            self.root.destroy()
    
    def _select_term_file(self):
        """选择术语库文件"""
        filename = filedialog.askopenfilename(
            title="选择术语库",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            self.term_path.set(filename)
    
    def _select_source_file(self):
        """选择源文件"""
        filename = filedialog.askopenfilename(
            title="选择待翻译文件",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            self.source_path.set(filename)
    
    def _on_provider_changed(self, event):
        """API 提供商切换"""
        logger.info(f"切换到 API: {self.current_provider_var.get()}")
        self._update_model_list()
    
    def _on_translation_type_changed(self, event):
        """翻译方向切换"""
        logger.info(f"选择翻译方向：{self.translation_type_var.get()}")
    
    def _update_model_list(self):
        """更新模型列表"""
        # TODO: 实现模型列表更新
        pass
    
    def _sync_draft_model_to_review(self):
        """同步初译模型到校对"""
        self.review_model_var.set(self.draft_model_var.get())
        self.review_temp_var.set(self.draft_temp_var.get())
        self.review_top_p_var.set(self.draft_top_p_var.get())
        self.review_timeout_var.set(self.draft_timeout_var.get())
        self.review_max_tokens_var.set(self.draft_max_tokens_var.get())
        messagebox.showinfo("同步成功", "已将初译模型参数同步到校对")
        logger.info("✅ 模型参数已同步")
    
    def _reset_advanced_params(self):
        """重置高级参数"""
        self.draft_temp_var.set(0.3)
        self.draft_top_p_var.set(0.8)
        self.draft_timeout_var.set(60)
        self.draft_max_tokens_var.set(512)
        
        self.review_temp_var.set(0.5)
        self.review_top_p_var.set(0.9)
        self.review_timeout_var.set(60)
        self.review_max_tokens_var.set(512)
        
        logger.info("✅ 参数已重置为默认值")
    
    def _select_all_langs(self):
        """全选当前页语言"""
        current_tab = self.lang_notebook.index(self.lang_notebook.select())
        tier_map = {0: 'T1', 1: 'T2', 2: 'T3'}
        tier = tier_map.get(current_tab)
        
        if tier and tier in self.tier_lang_frames:
            for widget in self.tier_lang_frames[tier].winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    widget.invoke()
    
    def _deselect_all_langs(self):
        """取消全选当前页语言"""
        current_tab = self.lang_notebook.index(self.lang_notebook.select())
        tier_map = {0: 'T1', 1: 'T2', 2: 'T3'}
        tier = tier_map.get(current_tab)
        
        if tier and tier in self.tier_lang_frames:
            for widget in self.tier_lang_frames[tier].winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    # 直接从 lang_vars 获取变量
                    text = widget.cget('text')
                    # 提取语言名称（去掉括号和分级）
                    lang_name = text.split(' (')[0] if ' (' in text else text
                    if lang_name in self.lang_vars:
                        var = self.lang_vars[lang_name]
                        if var.get():
                            var.set(False)
            self._update_lang_status()
    
    def _add_custom_language(self):
        """添加自定义语言"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加自定义语言")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="语言名称:").pack(pady=5)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)
        
        ttk.Label(dialog, text="市场分级:").pack(pady=5)
        tier_var = tk.StringVar(value="T3")
        combo = ttk.Combobox(dialog, textvariable=tier_var, values=["T1", "T2", "T3"], state='readonly')
        combo.pack(pady=5)
        
        def on_add():
            name = entry.get().strip()
            tier = tier_var.get()
            if name and name not in self.lang_vars:
                var = tk.BooleanVar()
                self.lang_vars[name] = var
                # TODO: 添加到对应分页
                dialog.destroy()
                messagebox.showinfo("成功", f"已添加语言：{name} ({tier})")
        
        ttk.Button(dialog, text="添加", command=on_add).pack(pady=10)
    
    def _update_lang_status(self):
        """更新语言选择状态"""
        self.selected_langs = [lang for lang, var in self.lang_vars.items() if var.get()]
    
    def _save_custom_prompts(self):
        """保存自定义提示词"""
        # TODO: 实现保存功能
        messagebox.showinfo("提示", "保存功能待实现")
    
    def _load_custom_prompts(self):
        """加载自定义提示词"""
        # TODO: 实现加载功能
        messagebox.showinfo("提示", "加载功能待实现")
    
    def _restore_default_prompts(self):
        """恢复默认提示词"""
        # TODO: 实现恢复功能
        messagebox.showinfo("提示", "恢复功能待实现")
    
    def _validate_prompts(self):
        """验证提示词格式"""
        draft = self.draft_text.get("1.0", tk.END).strip()
        review = self.review_text.get("1.0", tk.END).strip()
        
        if not draft or not review:
            messagebox.showwarning("警告", "提示词不能为空")
            return
        
        if "{target_lang}" not in draft:
            messagebox.showwarning("警告", "初译提示词缺少占位符 {target_lang}")
            return
        
        messagebox.showinfo("成功", "提示词格式验证通过！")
    
    def _toggle_performance_monitor(self):
        """切换性能监控"""
        enabled = self.perf_monitor_var.get()
        logger.info(f"{'✅ 启用' if enabled else '❌ 禁用'} 性能监控")
    
    def _update_log_level(self, level):
        """更新日志级别"""
        logger.info(f"日志级别：{level}")
    
    def _update_log_granularity(self, granularity):
        """更新日志粒度"""
        logger.info(f"日志粒度：{granularity}")
    
    def _start_translation(self):
        """开始翻译"""
        # TODO: 实现翻译逻辑
        messagebox.showinfo("提示", "翻译功能待实现")
    
    def _stop_translation(self):
        """停止翻译"""
        self.is_running = False
        logger.info("⏹️ 用户取消翻译")
    
    def _show_history_window(self):
        """显示历史记录窗口"""
        try:
            if not self.translation_history_manager:
                messagebox.showwarning("警告", "历史记录管理器未初始化")
                return
            
            # 创建新窗口
            history_window = tk.Toplevel(self.root)
            history_window.title("📜 翻译历史记录")
            history_window.geometry("900x600")
            history_window.transient(self.root)
            
            # 创建主框架
            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 顶部控制区
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 搜索框
            ttk.Label(control_frame, text="🔍 搜索:").pack(side=tk.LEFT, padx=5)
            search_var = tk.StringVar()
            search_entry = ttk.Entry(control_frame, textvariable=search_var, width=30)
            search_entry.pack(side=tk.LEFT, padx=5)
            
            # 搜索按钮
            def on_search():
                self._search_history(search_var.get())
            
            ttk.Button(control_frame, text="搜索", command=on_search).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="刷新", command=lambda: self._load_history_list()).pack(side=tk.LEFT, padx=5)
            
            # 导出按钮
            ttk.Button(
                control_frame,
                text="📤 导出 Excel",
                command=lambda: self._export_history()
            ).pack(side=tk.RIGHT, padx=5)
            
            # 统计信息
            stats_frame = ttk.LabelFrame(main_frame, text="📊 统计信息", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.stats_labels = {}
            stats_grid = [
                ("总记录数", 0, 0),
                ("成功数", 0, 2),
                ("失败数", 0, 4),
                ("成功率", 1, 0),
                ("最近批次", 1, 2),
                ("最后更新", 1, 4)
            ]
            
            for label_text, row, col in stats_grid:
                ttk.Label(stats_frame, text=f"{label_text}:").grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
                value_label = ttk.Label(stats_frame, text="-", foreground="blue")
                value_label.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.stats_labels[label_text] = value_label
            
            # 历史记录列表（带滚动条）
            list_frame = ttk.LabelFrame(main_frame, text="📝 翻译记录", padding="10")
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建 Treeview
            columns = ("时间", "原文", "译文", "语言", "状态", "模型")
            history_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
            
            # 设置列标题和宽度
            for col in columns:
                history_tree.heading(col, text=col)
                history_tree.column(col, width=100 if col != "原文" and col != "译文" else 200)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=history_tree.yview)
            history_tree.configure(yscrollcommand=scrollbar.set)
            
            history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 双击查看详情
            def on_item_double_click(event):
                selection = history_tree.selection()
                if selection:
                    item = history_tree.item(selection[0])
                    self._show_record_detail(item['values'])
            
            history_tree.bind("<Double-Button-1>", on_item_double_click)
            
            # 加载历史数据
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
                # 查找当前打开的窗口中的 tree widget
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
            
            # 清空现有数据
            for item in tree_widget.get_children():
                tree_widget.delete(item)
            
            # 获取最近的记录
            records = self.translation_history_manager.get_recent_records(limit=100)
            
            for record in records:
                status_text = "✅ 成功" if record.status == "SUCCESS" else "❌ 失败"
                tree_widget.insert("", "end", values=(
                    record.created_at[:19],  # 去掉毫秒
                    record.source_text[:50],  # 限制长度
                    record.final_trans[:50],
                    record.target_lang,
                    status_text,
                    record.model_name
                ))
            
            logger.debug(f"已加载 {len(records)} 条历史记录")
            
        except Exception as e:
            logger.error(f"加载历史记录失败：{e}")
    
    def _update_stats(self):
        """更新统计信息"""
        try:
            if not self.translation_history_manager:
                return
            
            stats = self.translation_history_manager.get_statistics()
            
            # 更新统计标签
            if "总记录数" in self.stats_labels:
                self.stats_labels["总记录数"].config(text=str(stats.get('total', 0)))
            if "成功数" in self.stats_labels:
                self.stats_labels["成功数"].config(text=str(stats.get('success', 0)))
            if "失败数" in self.stats_labels:
                self.stats_labels["失败数"].config(text=str(stats.get('failed', 0)))
            if "成功率" in self.stats_labels:
                self.stats_labels["成功率"].config(text=f"{stats.get('success_rate', 0):.1f}%")
            
            # 获取最近的批次
            recent_records = self.translation_history_manager.get_recent_records(limit=1)
            if recent_records:
                batch_id = recent_records[0].batch_id or "无批次"
                if "最近批次" in self.stats_labels:
                    self.stats_labels["最近批次"].config(text=batch_id[:20])
                if "最后更新" in self.stats_labels:
                    last_time = recent_records[0].created_at[:19]
                    self.stats_labels["最后更新"].config(text=last_time)
            
        except Exception as e:
            logger.error(f"更新统计信息失败：{e}")
    
    def _search_history(self, keyword):
        """搜索历史记录"""
        try:
            if not self.translation_history_manager:
                return
            
            # 查找当前窗口中的 tree widget
            tree_widget = None
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Treeview):
                                    tree_widget = grandchild
                                    break
            
            if not tree_widget:
                return
            
            # 清空现有数据
            for item in tree_widget.get_children():
                tree_widget.delete(item)
            
            # 搜索记录
            records = self.translation_history_manager.search_records(keyword=keyword, limit=100)
            
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
            
            logger.info(f"🔍 搜索到 {len(records)} 条记录")
            
        except Exception as e:
            logger.error(f"搜索历史记录失败：{e}")
    
    def _show_record_detail(self, record_values):
        """显示记录详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title("📝 翻译记录详情")
        detail_window.geometry("600x400")
        detail_window.transient(self.root)
        
        frame = ttk.Frame(detail_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示详细信息
        details = [
            ("时间", record_values[0]),
            ("原文", record_values[1]),
            ("译文", record_values[2]),
            ("语言", record_values[3]),
            ("状态", record_values[4]),
            ("模型", record_values[5])
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=value, wraplength=400).grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Button(frame, text="关闭", command=detail_window.destroy).grid(row=len(details), column=0, columnspan=2, pady=20)
    
    def _export_history(self):
        """导出历史记录"""
        try:
            if not self.translation_history_manager:
                messagebox.showwarning("警告", "翻译历史管理器未初始化")
                return
            
            # 选择保存路径
            file_path = filedialog.asksaveasfilename(
                title="导出翻译历史",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"translation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if file_path:
                output_file = self.translation_history_manager.export_to_excel(file_path)
                logger.info(f"📤 翻译历史已导出到：{output_file}")
                messagebox.showinfo("成功", f"翻译历史已导出到:\n{output_file}")
        
        except Exception as e:
            logger.error(f"导出历史记录失败：{e}")
            messagebox.showerror("错误", f"导出失败:\n{str(e)}")
    
    def _save_current_session(self):
        """保存当前会话配置"""
        # TODO: 实现配置保存
        logger.info("💾 配置已保存")


def run_modern_gui(config_file=None):
    """运行现代化 GUI"""
    root = tk.Tk()
    app = ModernGUIApp(root, config_file)
    root.mainloop()


if __name__ == "__main__":
    run_modern_gui()
