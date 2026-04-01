"""
GUI 应用模块 - 重构版
基于新的分层架构，使用依赖注入和外观模式
"""
import asyncio
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from typing import List

from config import DEFAULT_DRAFT_PROMPT, DEFAULT_REVIEW_PROMPT, TARGET_LANGUAGES, GUI_CONFIG, GAME_TRANSLATION_TYPES, GAME_DRAFT_PROMPTS, GAME_REVIEW_PROMPTS
from infrastructure.prompt_injector import inject_prompts
from infrastructure.log_config import setup_logger, LogTag, log_with_tag, LogLevel
from infrastructure.log_slice import LoggerSlice, LogCategory
from infrastructure.models import Config
from infrastructure.di_container import initialize_container
from data_access.config_persistence import ConfigPersistence
from service.api_provider import get_provider_manager
from infrastructure.gui_log_controller import GUILogController

logger = logging.getLogger(__name__)


class TranslationApp:
    """翻译应用程序 GUI - 基于新架构"""
    
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
        
        # 游戏翻译方向
        self.translation_type_var = tk.StringVar(value="match3_item")
        
        # API 提供商管理
        self.provider_manager = get_provider_manager()
        self.current_provider_var = tk.StringVar(value="deepseek")
        
        # 日志控制器
        self.log_controller = None
        
        # 加载配置
        if config_file:
            self._load_config_from_file()
        
        # 初始化 API 提供商列表
        self.available_providers = self._get_available_providers_from_config()
        if self.available_providers:
            # _get_available_providers_from_config 返回的是列表，需要转换为字典
            providers_dict = {provider: provider for provider in self.available_providers}
            self.available_providers = providers_dict
            
            # 使用第一个可用的提供商作为默认值
            default_provider = list(self.available_providers.keys())[0]
            self.current_provider_var.set(default_provider)
        
        # 服务容器（延迟初始化）
        self.container = None
        self.translation_facade = None
        
        self._setup_ui()
        self._setup_logger()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主容器 - 添加滚动条
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
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 主内容区域
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- 1. 文件配置区 ---
        file_frame = ttk.LabelFrame(main_frame, text="📂 文件配置", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="术语库 (Excel):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.term_path, width=50, state='readonly').grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="选择...", command=self._select_term_file).grid(
            row=0, column=2, pady=5)
        
        ttk.Label(file_frame, text="待翻译 (Excel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.source_path, width=50, state='readonly').grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="选择...", command=self._select_source_file).grid(
            row=1, column=2, pady=5)
        
        # 模式
        mode_frame = ttk.Frame(file_frame)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="🆕 新文档 (双阶段)", variable=self.mode_var, value=1).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="📝 旧文档校对", variable=self.mode_var, value=2).pack(side=tk.LEFT, padx=10)
        
        # --- 2. API 提供商选择区 ---
        provider_frame = ttk.LabelFrame(main_frame, text="🔌 API 提供商", padding="10")
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(provider_frame, text="选择 API 提供商:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        providers_list = list(self.available_providers.keys()) if self.available_providers else ["deepseek"]
        self.provider_combo = ttk.Combobox(
            provider_frame, 
            textvariable=self.current_provider_var,
            values=providers_list,
            state='readonly',
            width=30
        )
        self.provider_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.provider_combo.bind('<<ComboboxSelected>>', self._on_provider_changed)
        
        # 模型选择
        ttk.Label(provider_frame, text="选择模型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.current_model_var = tk.StringVar(value="")
        self.model_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.current_model_var,
            state='readonly',
            width=30
        )
        self.model_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # --- 2.1 双阶段翻译参数（高级选项）---
        advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ 双阶段翻译参数（高级）", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用 Notebook 分页显示初译和校对参数
        self.advanced_notebook = ttk.Notebook(advanced_frame)
        self.advanced_notebook.pack(fill=tk.X)
        
        # 初译参数页
        draft_params_frame = ttk.Frame(self.advanced_notebook, padding="5")
        self.advanced_notebook.add(draft_params_frame, text="📝 初译参数")
        
        ttk.Label(draft_params_frame, text="初译模型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.draft_model_var = tk.StringVar(value="")
        self.draft_model_combo = ttk.Combobox(draft_params_frame, textvariable=self.draft_model_var, state='readonly', width=25)
        self.draft_model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(draft_params_frame, text="(空=使用全局模型)", foreground="gray").grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(draft_params_frame, text="温度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.draft_temp_var = tk.DoubleVar(value=0.3)
        self.draft_temp_spin = ttk.Spinbox(draft_params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.draft_temp_var, width=28)
        self.draft_temp_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(draft_params_frame, text="Top P:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.draft_top_p_var = tk.DoubleVar(value=0.8)
        self.draft_top_p_spin = ttk.Spinbox(draft_params_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.draft_top_p_var, width=28)
        self.draft_top_p_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(draft_params_frame, text="超时 (秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.draft_timeout_var = tk.IntVar(value=60)
        self.draft_timeout_spin = ttk.Spinbox(draft_params_frame, from_=10, to=300, increment=10, textvariable=self.draft_timeout_var, width=28)
        self.draft_timeout_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(draft_params_frame, text="Max Tokens:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.draft_max_tokens_var = tk.IntVar(value=512)
        self.draft_max_tokens_spin = ttk.Spinbox(draft_params_frame, from_=128, to=4096, increment=128, textvariable=self.draft_max_tokens_var, width=28)
        self.draft_max_tokens_spin.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 校对参数页
        review_params_frame = ttk.Frame(self.advanced_notebook, padding="5")
        self.advanced_notebook.add(review_params_frame, text="✏️ 校对参数")
        
        ttk.Label(review_params_frame, text="校对模型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_model_var = tk.StringVar(value="")
        self.review_model_combo = ttk.Combobox(review_params_frame, textvariable=self.review_model_var, state='readonly', width=25)
        self.review_model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(review_params_frame, text="(空=使用全局模型)", foreground="gray").grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(review_params_frame, text="温度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_temp_var = tk.DoubleVar(value=0.5)
        self.review_temp_spin = ttk.Spinbox(review_params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.review_temp_var, width=28)
        self.review_temp_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(review_params_frame, text="Top P:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_top_p_var = tk.DoubleVar(value=0.9)
        self.review_top_p_spin = ttk.Spinbox(review_params_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.review_top_p_var, width=28)
        self.review_top_p_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(review_params_frame, text="超时 (秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_timeout_var = tk.IntVar(value=60)
        self.review_timeout_spin = ttk.Spinbox(review_params_frame, from_=10, to=300, increment=10, textvariable=self.review_timeout_var, width=28)
        self.review_timeout_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(review_params_frame, text="Max Tokens:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_max_tokens_var = tk.IntVar(value=512)
        self.review_max_tokens_spin = ttk.Spinbox(review_params_frame, from_=128, to=4096, increment=128, textvariable=self.review_max_tokens_var, width=28)
        self.review_max_tokens_spin.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 重置按钮
        reset_btn_frame = ttk.Frame(advanced_frame)
        reset_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(reset_btn_frame, text="🔄 重置为默认值", command=self._reset_advanced_params).pack(side=tk.LEFT, padx=5)
        
        # 初始化模型列表（必须在双阶段控件创建之后）
        self._update_model_list()
        
        # --- 3. 游戏翻译方向选择区 ---
        game_type_frame = ttk.LabelFrame(main_frame, text="🎮 游戏翻译方向", padding="10")
        game_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        type_selector_frame = ttk.Frame(game_type_frame)
        type_selector_frame.pack(fill=tk.X)
        
        ttk.Label(type_selector_frame, text="选择翻译方向:").pack(side=tk.LEFT, padx=5)
        
        self.type_combo = ttk.Combobox(
            type_selector_frame,
            textvariable=self.translation_type_var,
            values=list(GAME_TRANSLATION_TYPES.values()),
            state='readonly',
            width=25
        )
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.set("🎮 三消 - 道具元素")  # 默认值
        self.type_combo.bind('<<ComboboxSelected>>', self._on_translation_type_changed)
        
        # 说明标签 - 强调不会改变用户提示词
        self.type_desc_label = ttk.Label(
            type_selector_frame,
            text="💡 仅用于注入禁止事项，不会修改您的提示词",
            foreground="gray"
        )
        self.type_desc_label.pack(side=tk.LEFT, padx=10)
        
        # --- 4. 语言选择区 ---
        lang_frame = ttk.LabelFrame(main_frame, text="🌍 目标语言", padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lang_vars = {}
        btn_row = ttk.Frame(lang_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="全选", command=self._select_all_langs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="取消全选", command=self._deselect_all_langs).pack(side=tk.LEFT, padx=5)
        
        # 使用可滚动的 Frame 来放置语言选项
        lang_canvas = tk.Canvas(lang_frame, height=180)
        lang_scrollbar = ttk.Scrollbar(lang_frame, orient="vertical", command=lang_canvas.yview)
        scrollable_lang_frame = ttk.Frame(lang_canvas)
        
        scrollable_lang_frame.bind(
            "<Configure>",
            lambda e: lang_canvas.configure(scrollregion=lang_canvas.bbox("all"))
        )
        
        lang_canvas.create_window((0, 0), window=scrollable_lang_frame, anchor="nw")
        lang_canvas.configure(yscrollcommand=lang_scrollbar.set)
        
        lang_canvas.pack(side="left", fill="both", expand=True)
        lang_scrollbar.pack(side="right", fill="y")
        
        # 从配置加载语言列表（如果配置文件中有自定义）
        languages_to_show = TARGET_LANGUAGES
        if hasattr(self, 'config') and self.config and hasattr(self.config, 'target_languages'):
            languages_to_show = self.config.target_languages
        
        # 放置语言选项（改为 5 列布局）
        for i, lang in enumerate(languages_to_show):
            var = tk.BooleanVar(value=False)
            self.lang_vars[lang] = var
            cb = ttk.Checkbutton(scrollable_lang_frame, text=lang, variable=var, command=self._update_lang_status)
            cb.grid(row=i // 5, column=i % 5, sticky=tk.W, padx=10, pady=2)
        
        # --- 5. 提示词配置区 ---
        prompt_frame = ttk.LabelFrame(main_frame, text="⚙️ 提示词配置", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.notebook = ttk.Notebook(prompt_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        draft_tab = ttk.Frame(self.notebook)
        self.notebook.add(draft_tab, text="初译提示词 (Draft)")
        self.draft_text = scrolledtext.ScrolledText(draft_tab, height=6, font=("Consolas", 10))
        self.draft_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.draft_text.insert('1.0', self.default_draft)
        
        review_tab = ttk.Frame(self.notebook)
        self.notebook.add(review_tab, text="校对提示词 (Review)")
        self.review_text = scrolledtext.ScrolledText(review_tab, height=6, font=("Consolas", 10))
        self.review_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.review_text.insert('1.0', self.default_review)
        
        # 提示词操作按钮
        prompt_btn_frame = ttk.Frame(prompt_frame)
        prompt_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(prompt_btn_frame, text="💾 保存自定义提示词", command=self._save_custom_prompts).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="📂 加载已保存提示词", command=self._load_custom_prompts).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="🔄 恢复默认模板", command=self._restore_default_prompts).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="✅ 验证提示词格式", command=self._validate_prompts).pack(side=tk.LEFT, padx=5)
        
        # --- 6. 控制与日志区 ---
        control_frame = ttk.LabelFrame(main_frame, text="🚀 执行控制", padding="10")
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        # 性能监控开关
        perf_monitor_frame = ttk.Frame(control_frame)
        perf_monitor_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.perf_monitor_var = tk.BooleanVar(value=False)
        self.perf_monitor_check = ttk.Checkbutton(
            perf_monitor_frame,
            text="📊 启用性能监控",
            variable=self.perf_monitor_var,
            command=self._toggle_performance_monitor
        )
        self.perf_monitor_check.pack(side=tk.LEFT, padx=5)
        
        # 日志控制面板
        self._create_log_control_panel(control_frame)
        
        # 按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=5)
        
        self.start_btn = ttk.Button(
            btn_frame, 
            text="▶️ 开始翻译", 
            command=self._start_translation,
            style='Accent.TButton'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame, 
            text="⏹️ 停止", 
            command=self._stop_translation,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 日志
        log_frame = ttk.LabelFrame(main_frame, text="📋 运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 重定向日志到 GUI
        self._setup_gui_logging()
        
        # 初始化日志控制器
        self._initialize_log_controller()
    
    def _setup_gui_logging(self):
        """设置 GUI 日志重定向"""
        class GUILogHandler(logging.Handler):
            def __init__(self, log_text):
                super().__init__()
                self.log_text = log_text
            
            def emit(self, record):
                msg = self.format(record)
                self.log_text.insert(tk.END, msg + '\n')
                self.log_text.see(tk.END)
        
        handler = GUILogHandler(self.log_text)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    def _initialize_log_controller(self):
        """初始化 GUI 日志控制器"""
        try:
            # 创建绑定变量
            self.log_level_var = tk.StringVar(value="INFO")
            self.log_granularity_var = tk.StringVar(value="normal")
            
            # 创建控制器
            self.log_controller = GUILogController(
                self.log_level_var,
                self.log_granularity_var
            )
            
            # 应用初始配置
            if hasattr(self, 'config') and self.config:
                self.log_controller.update_log_level(self.config.log_level)
                self.log_controller.update_log_granularity(self.config.log_granularity)
            
            logger.info("✅ GUI 日志控制器初始化完成")
        except Exception as e:
            logger.error(f"❌ GUI 日志控制器初始化失败：{e}")
    
    def _create_log_control_panel(self, parent):
        """创建日志控制面板"""
        if not self.log_controller:
            return
        
        # 使用 log_controller 的方法创建控制面板
        control_frame = self.log_controller.create_log_control_frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 5))
    
    def _select_term_file(self):
        """选择术语库文件"""
        filename = filedialog.askopenfilename(
            title="选择术语库文件",
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
        provider_name = self.current_provider_var.get()
        logger.info(f"切换到 API 提供商：{provider_name}")
        # 更新模型列表
        self._update_model_list()
    
    def _select_all_langs(self):
        """全选语言"""
        for var in self.lang_vars.values():
            var.set(True)
        self._update_lang_status()
    
    def _update_model_list(self):
        """更新模型列表"""
        provider_name = self.current_provider_var.get()
        try:
            # 转换为枚举类型
            from service.api_provider import APIProvider
            
            # 处理 provider_name 可能是 APIProvider 枚举或字符串
            if provider_name.startswith('APIProvider.'):
                # 如果是 'APIProvider.DEEPSEEK' 格式，提取 'deepseek'
                provider_name = provider_name.split('.')[-1].lower()
            
            provider = APIProvider(provider_name)
            
            # 获取模型列表
            models = self.provider_manager.list_models(provider)
            
            if models:
                # 更新全局模型列表
                self.model_combo['values'] = models
                # 设置默认模型
                config = self.provider_manager.get_provider(provider)
                if config and config.default_model in models:
                    self.current_model_var.set(config.default_model)
                else:
                    self.current_model_var.set(models[0] if models else "")
                
                # 更新初译和校对模型列表
                self.draft_model_combo['values'] = [''] + models  # 空值表示使用全局模型
                self.review_model_combo['values'] = [''] + models
                
                # 从配置加载双阶段参数
                self._load_advanced_params_from_config()
                
                logger.debug(f"提供商 {provider_name} 的模型列表：{models}")
            else:
                self.model_combo['values'] = []
                self.current_model_var.set("")
                self.draft_model_combo['values'] = []
                self.review_model_combo['values'] = []
                
        except Exception as e:
            logger.error(f"更新模型列表失败：{e}")
            self.model_combo['values'] = []
            self.current_model_var.set("")
            self.draft_model_combo['values'] = []
            self.review_model_combo['values'] = []
    
    def _deselect_all_langs(self):
        """取消全选"""
        for var in self.lang_vars.values():
            var.set(False)
        self._update_lang_status()
    
    def _load_advanced_params_from_config(self):
        """从配置文件加载双阶段翻译参数"""
        if not hasattr(self, 'config') or not self.config:
            return
        
        try:
            # 加载初译参数
            if hasattr(self.config, 'draft_model_name') and self.config.draft_model_name:
                self.draft_model_var.set(self.config.draft_model_name)
            if hasattr(self.config, 'draft_temperature') and self.config.draft_temperature:
                self.draft_temp_var.set(self.config.draft_temperature)
            if hasattr(self.config, 'draft_top_p') and self.config.draft_top_p:
                self.draft_top_p_var.set(self.config.draft_top_p)
            if hasattr(self.config, 'draft_timeout') and self.config.draft_timeout:
                self.draft_timeout_var.set(self.config.draft_timeout)
            if hasattr(self.config, 'draft_max_tokens') and self.config.draft_max_tokens:
                self.draft_max_tokens_var.set(self.config.draft_max_tokens)
            
            # 加载校对参数
            if hasattr(self.config, 'review_model_name') and self.config.review_model_name:
                self.review_model_var.set(self.config.review_model_name)
            if hasattr(self.config, 'review_temperature') and self.config.review_temperature:
                self.review_temp_var.set(self.config.review_temperature)
            if hasattr(self.config, 'review_top_p') and self.config.review_top_p:
                self.review_top_p_var.set(self.config.review_top_p)
            if hasattr(self.config, 'review_timeout') and self.config.review_timeout:
                self.review_timeout_var.set(self.config.review_timeout)
            if hasattr(self.config, 'review_max_tokens') and self.config.review_max_tokens:
                self.review_max_tokens_var.set(self.config.review_max_tokens)
            
            logger.debug("已加载双阶段翻译参数配置")
        except Exception as e:
            logger.error(f"加载双阶段参数配置失败：{e}")
    
    def _update_lang_status(self):
        """更新语言选择状态"""
        count = sum(1 for var in self.lang_vars.values() if var.get())
        self.selected_langs = [lang for lang, var in self.lang_vars.items() if var.get()]
    
    def _reset_advanced_params(self):
        """重置高级参数为默认值"""
        # 清空模型选择（使用全局模型）
        self.draft_model_var.set("")
        self.review_model_var.set("")
        
        # 重置为默认参数值
        self.draft_temp_var.set(0.3)
        self.draft_top_p_var.set(0.8)
        self.draft_timeout_var.set(60)
        self.draft_max_tokens_var.set(512)
        
        self.review_temp_var.set(0.5)
        self.review_top_p_var.set(0.9)
        self.review_timeout_var.set(60)
        self.review_max_tokens_var.set(512)
        
        logger.info("🔄 已重置双阶段翻译参数为默认值")
    
    def _toggle_performance_monitor(self):
        """切换性能监控开关"""
        enabled = self.perf_monitor_var.get()
        logger.info(f"{'✅ 已启用' if enabled else '❌ 已禁用'} 性能监控")
        
        # 更新配置（如果已加载）
        if hasattr(self, 'config') and self.config:
            self.config.enable_performance_monitor = enabled
    
    def _on_translation_type_changed(self, event):
        """翻译方向切换 - 仅记录选择，不改变提示词内容"""
        # 获取选中的方向（中文名称）
        selected_name = self.translation_type_var.get()
        
        # 仅记录日志，不做任何修改
        logger.info(f"🎯 已选择翻译方向：{selected_name}")
        logger.info(f"💡 提示：禁止事项将在点击「开始翻译」时自动注入到当前提示词中")
    
    def _get_translation_type_key(self) -> str:
        """获取当前选择的翻译类型的 key"""
        selected_name = self.translation_type_var.get()
        
        # 根据中文名称找到对应的 key
        for key, name in GAME_TRANSLATION_TYPES.items():
            if name == selected_name:
                return key
        
        # 默认返回 custom
        return 'custom'
    
    def _validate_prompts(self):
        """校验提示词"""
        draft = self.draft_text.get("1.0", tk.END).strip()
        review = self.review_text.get("1.0", tk.END).strip()
        
        if not draft or not review:
            messagebox.showwarning("警告", "提示词不能为空")
            return
        
        if "{target_lang}" not in draft:
            messagebox.showwarning("警告", "初译提示词缺少占位符 {target_lang}")
            return
        
        messagebox.showinfo("成功", "提示词格式校验通过！")
    
    def _save_custom_prompts(self):
        """保存自定义提示词到文件"""
        try:
            from tkinter import filedialog
            import json
            
            draft = self.draft_text.get("1.0", tk.END).strip()
            review = self.review_text.get("1.0", tk.END).strip()
            
            # 获取保存路径
            file_path = filedialog.asksaveasfilename(
                title="保存自定义提示词",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="custom_prompts.json"
            )
            
            if file_path:
                # 保存到文件
                custom_prompts = {
                    'draft_prompt': draft,
                    'review_prompt': review,
                    'translation_type': self.translation_type_var.get()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(custom_prompts, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 已保存自定义提示词到：{file_path}")
                messagebox.showinfo("成功", f"自定义提示词已保存到:\n{file_path}")
        
        except Exception as e:
            logger.error(f"❌ 保存提示词失败：{e}")
            messagebox.showerror("错误", f"保存提示词失败:\n{str(e)}")
    
    def _load_custom_prompts(self):
        """从文件加载自定义提示词"""
        try:
            from tkinter import filedialog
            import json
            
            # 选择文件
            file_path = filedialog.askopenfilename(
                title="加载自定义提示词",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                # 从文件加载
                with open(file_path, 'r', encoding='utf-8') as f:
                    custom_prompts = json.load(f)
                
                # 应用到 GUI
                self.draft_text.delete('1.0', tk.END)
                self.draft_text.insert('1.0', custom_prompts['draft_prompt'])
                
                self.review_text.delete('1.0', tk.END)
                self.review_text.insert('1.0', custom_prompts['review_prompt'])
                
                logger.info(f"📂 已从 {file_path} 加载自定义提示词")
                messagebox.showinfo("成功", f"已加载自定义提示词:\n{file_path}")
        
        except Exception as e:
            logger.error(f"❌ 加载提示词失败：{e}")
            messagebox.showerror("错误", f"加载提示词失败:\n{str(e)}")
    
    def _restore_default_prompts(self):
        """恢复默认提示词模板"""
        try:
            # 确认操作
            confirm = messagebox.askyesno(
                "确认恢复",
                "确定要恢复默认提示词模板吗？\n\n⚠️ 未保存的自定义内容将丢失！"
            )
            
            if confirm:
                # 根据当前选择的翻译方向恢复对应模板
                type_key = self._get_translation_type_key()
                
                if type_key in GAME_DRAFT_PROMPTS:
                    self.draft_text.delete('1.0', tk.END)
                    self.draft_text.insert('1.0', GAME_DRAFT_PROMPTS[type_key])
                
                if type_key in GAME_REVIEW_PROMPTS:
                    self.review_text.delete('1.0', tk.END)
                    self.review_text.insert('1.0', GAME_REVIEW_PROMPTS[type_key])
                
                logger.info(f"🔄 已恢复默认提示词模板 - 方向：{self.translation_type_var.get()}")
                messagebox.showinfo("成功", "已恢复默认提示词模板")
        
        except Exception as e:
            logger.error(f"❌ 恢复默认提示词失败：{e}")
            messagebox.showerror("错误", f"恢复失败:\n{str(e)}")
    
    def _initialize_services(self):
        """初始化服务容器 - 从配置文件加载配置并自动注入禁止事项"""
        if self.container:
            return
        
        try:
            # 获取用户配置的提示词（从 GUI）
            user_draft_prompt = self.draft_text.get("1.0", tk.END).strip()
            user_review_prompt = self.review_text.get("1.0", tk.END).strip()
            
            # 根据翻译方向自动注入禁止事项
            translation_type_key = self._get_translation_type_key()
            injected_draft, injected_review = inject_prompts(
                user_draft_prompt,
                user_review_prompt,
                translation_type_key
            )
            
            logger.info(f"✅ 已自动注入禁止事项到提示词 - 类型：{translation_type_key}")
            
            # 获取配置（从配置文件加载）
            config = self._create_config()
            
            # 获取 API 客户端
            provider_name = self.current_provider_var.get()
            provider = self.provider_manager.get_provider(provider_name)
            api_client = provider.get_client()
            
            # 初始化容器（传入注入后的提示词）
            self.container = initialize_container(
                config_file=self.config_file,
                api_client=api_client,
                draft_prompt=injected_draft,
                review_prompt=injected_review
            )
            
            # 获取外观服务
            self.translation_facade = self.container.get('translation_facade')
            
            # 设置进度回调
            self.translation_facade.set_progress_callback(self._update_progress)
            
            logger.info("✅ 服务初始化完成（使用配置文件 + 注入禁止事项）")
            
        except Exception as e:
            logger.error(f"❌ 服务初始化失败：{e}")
            raise
    
    def _create_config(self) -> Config:
        """从配置文件或 GUI 状态创建 Config 对象"""
        from config.loader import get_config_loader
        
        loader = get_config_loader()
        
        # 如果有配置文件，从文件加载
        if self.config_file:
            from data_access.config_persistence import ConfigPersistence
            persistence = ConfigPersistence(self.config_file)
            file_config = persistence.load_config()
            loader.update(file_config)
        
        # 转换为 Config 数据类
        return loader.to_dataclass(Config)
    
    async def _start_translation_async(self):
        """异步启动翻译"""
        try:
            self._initialize_services()
            
            if not self.source_path.get():
                messagebox.showwarning("警告", "请选择待翻译文件")
                return
            
            if not self.selected_langs:
                messagebox.showwarning("警告", "请至少选择一个目标语言")
                return
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            logger.info("🚀 开始翻译任务...")
            
            # 执行翻译
            result = await self.translation_facade.translate_file(
                source_excel_path=self.source_path.get(),
                target_langs=self.selected_langs,
                output_excel_path=None,  # TODO: 指定输出路径
                concurrency_limit=10
            )
            
            # 显示结果
            success_rate = result.success_rate
            messagebox.showinfo("完成", f"翻译完成！\n成功率：{success_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ 翻译失败：{e}")
            messagebox.showerror("错误", f"翻译失败：{e}")
        
        finally:
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.progress_var.set(0)
    
    def _start_translation(self):
        """启动翻译（同步调用）"""
        asyncio.run(self._start_translation_async())
    
    def _stop_translation(self):
        """停止翻译"""
        self.is_running = False
        logger.info("⏹️ 用户取消翻译")
    
    def _update_progress(self, current: int, total: int):
        """更新进度"""
        progress = (current / total * 100) if total > 0 else 0
        self.progress_var.set(progress)
        logger.info(f"📊 进度：{current}/{total} ({progress:.1f}%)")
    
    def _load_config_from_file(self):
        """从文件加载配置并应用到 GUI"""
        if not self.config_persistence:
            return
        
        try:
            config_data = self.config_persistence.load_config()
            
            # 应用配置到 GUI 状态
            if 'api_provider' in config_data:
                self.current_provider_var.set(config_data['api_provider'])
            
            if 'draft_prompt' in config_data:
                self.draft_text.delete('1.0', tk.END)
                self.draft_text.insert('1.0', config_data['draft_prompt'])
            
            if 'review_prompt' in config_data:
                self.review_text.delete('1.0', tk.END)
                self.review_text.insert('1.0', config_data['review_prompt'])
            
            if 'gui_window_title' in config_data:
                self.root.title(config_data['gui_window_title'])
            
            if 'gui_window_width' in config_data and 'gui_window_height' in config_data:
                self.root.geometry(f"{config_data['gui_window_width']}x{config_data['gui_window_height']}")
            
            logger.info(f"✅ 配置加载成功：{self.config_file}")
        except Exception as e:
            logger.warning(f"配置加载失败：{e}")
    
    def _get_available_providers_from_config(self) -> list:
        """获取可用的 API 提供商列表
        
        Returns:
            APIProvider 名称列表
        """
        return self.provider_manager.list_providers() if self.provider_manager else []
    
    def _setup_logger(self):
        """设置日志系统"""
        # 使用默认配置初始化日志
        setup_logger
        # 添加 GUI handler
        self._setup_gui_logging()


def run_gui_app(config_file: str = None):
    """运行 GUI 应用"""
    root = tk.Tk()
    app = TranslationApp(root, config_file)
    root.mainloop()


if __name__ == "__main__":
    run_gui_app()
