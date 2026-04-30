"""
UI组件构建器
将UI创建逻辑拆分成独立的构建器类
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, Optional
from presentation.gui_constants import *


class FileConfigUIBuilder:
    """文件配置区UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建文件配置区"""
        frame = ttk.LabelFrame(parent, text="📂 文件配置", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # 术语库选择
        ttk.Label(frame, text="术语库 (Excel):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.app.term_path, width=50, state='readonly').grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="选择...", command=self.app._select_term_file).grid(
            row=0, column=2, pady=5)

        # 待翻译文件选择
        ttk.Label(frame, text="待翻译 (Excel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.app.source_path, width=50, state='readonly').grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="选择...", command=self.app._select_source_file).grid(
            row=1, column=2, pady=5)

        # 模式选择
        mode_frame = ttk.Frame(frame)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="🆕 新文档 (双阶段)", variable=self.app.mode_var, value=1).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="📝 旧文档校对", variable=self.app.mode_var, value=2).pack(side=tk.LEFT, padx=10)

        # 翻译模式选择
        trans_mode_frame = ttk.Frame(frame)
        trans_mode_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Label(trans_mode_frame, text="🔄 翻译模式:", font=("", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.app.mode_combo = ttk.Combobox(
            trans_mode_frame,
            textvariable=self.app.translation_mode_var,
            values=["full", "draft_only", "review_only"],
            state='readonly',
            width=25
        )
        self.app.mode_combo.pack(side=tk.LEFT, padx=5)
        self.app.mode_combo.bind('<<ComboboxSelected>>', self.app._on_translation_mode_changed)

        ttk.Label(trans_mode_frame, text="💡 选择后自动调整界面", foreground="gray").pack(side=tk.LEFT, padx=10)

        return frame


class ProviderConfigUIBuilder:
    """API提供商配置区UI构建器（仅 DeepSeek）"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建API提供商配置区"""
        frame = ttk.LabelFrame(parent, text="🔌 API 提供商", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="API 提供商: DeepSeek", font=("", 9, "bold"), foreground="#0066cc").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="💡 模型请在下方「双阶段翻译参数」中配置（deepseek-chat / deepseek-reasoner）", foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        return frame


class AdvancedParamsUIBuilder:
    """高级参数配置区UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建高级参数配置区"""
        frame = ttk.LabelFrame(parent, text="⚙️ 双阶段翻译参数（高级）", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # 使用Notebook分页
        self.app.advanced_notebook = ttk.Notebook(frame)
        self.app.advanced_notebook.pack(fill=tk.X)

        # 初译参数页
        self._build_draft_params()
        # 校对参数页
        self._build_review_params()

        # 重置按钮
        reset_btn_frame = ttk.Frame(frame)
        reset_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(reset_btn_frame, text="🔄 重置为默认值", command=self.app._reset_advanced_params).pack(side=tk.LEFT, padx=5)

        # 初始化模型列表
        self.app._update_model_list()

        return frame

    def _build_draft_params(self):
        """构建初译参数页"""
        draft_params_frame = ttk.Frame(self.app.advanced_notebook, padding="5")
        self.app.advanced_notebook.add(draft_params_frame, text="📝 初译参数")

        ttk.Label(draft_params_frame, text="初译模型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.draft_model_combo = ttk.Combobox(draft_params_frame, textvariable=self.app.draft_model_var, state='readonly', width=30)
        self.app.draft_model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(draft_params_frame, text="(空=使用 API 提供商默认模型)", foreground="gray").grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(draft_params_frame, text="温度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.draft_temp_spin = ttk.Spinbox(draft_params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.app.draft_temp_var, width=30)
        self.app.draft_temp_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(draft_params_frame, text="Top P:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.draft_top_p_spin = ttk.Spinbox(draft_params_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.app.draft_top_p_var, width=30)
        self.app.draft_top_p_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(draft_params_frame, text="超时 (秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.draft_timeout_spin = ttk.Spinbox(draft_params_frame, from_=10, to=300, increment=10, textvariable=self.app.draft_timeout_var, width=30)
        self.app.draft_timeout_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(draft_params_frame, text="Max Tokens:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.draft_max_tokens_spin = ttk.Spinbox(draft_params_frame, from_=128, to=4096, increment=128, textvariable=self.app.draft_max_tokens_var, width=30)
        self.app.draft_max_tokens_spin.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

    def _build_review_params(self):
        """构建校对参数页"""
        review_params_frame = ttk.Frame(self.app.advanced_notebook, padding="5")
        self.app.advanced_notebook.add(review_params_frame, text="✏️ 校对参数")

        # 模型选择 + 同步按钮
        model_sync_frame = ttk.Frame(review_params_frame)
        model_sync_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(model_sync_frame, text="校对模型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.review_model_combo = ttk.Combobox(model_sync_frame, textvariable=self.app.review_model_var, state='readonly', width=30)
        self.app.review_model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(model_sync_frame, text="(空=使用 API 提供商默认模型)", foreground="gray").grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(model_sync_frame, text="🔄 同步初译模型", command=self.app._sync_draft_model_to_review).grid(row=0, column=3, padx=10, pady=5)

        ttk.Label(review_params_frame, text="温度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.review_temp_spin = ttk.Spinbox(review_params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.app.review_temp_var, width=30)
        self.app.review_temp_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(review_params_frame, text="Top P:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.review_top_p_spin = ttk.Spinbox(review_params_frame, from_=0.0, to=1.0, increment=0.1, textvariable=self.app.review_top_p_var, width=30)
        self.app.review_top_p_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(review_params_frame, text="超时 (秒):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.review_timeout_spin = ttk.Spinbox(review_params_frame, from_=10, to=300, increment=10, textvariable=self.app.review_timeout_var, width=30)
        self.app.review_timeout_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(review_params_frame, text="Max Tokens:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.app.review_max_tokens_spin = ttk.Spinbox(review_params_frame, from_=128, to=4096, increment=128, textvariable=self.app.review_max_tokens_var, width=30)
        self.app.review_max_tokens_spin.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)


class GameTranslationUIBuilder:
    """游戏翻译方向UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建游戏翻译方向区"""
        from config import GAME_TRANSLATION_TYPES
        
        frame = ttk.LabelFrame(parent, text="🎮 游戏翻译方向", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        type_selector_frame = ttk.Frame(frame)
        type_selector_frame.pack(fill=tk.X)

        ttk.Label(type_selector_frame, text="选择翻译方向:").pack(side=tk.LEFT, padx=5)

        self.app.type_combo = ttk.Combobox(
            type_selector_frame,
            textvariable=self.app.translation_type_var,
            values=list(GAME_TRANSLATION_TYPES.values()),
            state='readonly',
            width=25
        )
        self.app.type_combo.pack(side=tk.LEFT, padx=5)
        self.app.type_combo.set("🎮 三消 - 道具元素")
        self.app.type_combo.bind('<<ComboboxSelected>>', self.app._on_translation_type_changed)

        self.app.type_desc_label = ttk.Label(
            type_selector_frame,
            text="💡 仅用于注入禁止事项，不会修改您的提示词",
            foreground="gray"
        )
        self.app.type_desc_label.pack(side=tk.LEFT, padx=10)

        return frame


class LanguageSelectionUIBuilder:
    """语言选择区UI构建器 — 单一列表，多选"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建语言选择区（全部语言在单一可滚动列表中，多选）"""
        from config import TARGET_LANGUAGES, T1_LANGUAGES, T2_LANGUAGES, T3_LANGUAGES

        frame = ttk.LabelFrame(parent, text="🌍 目标语言（多选）", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # 顶部按钮
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="✅ 全选", command=self.app._select_all_langs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="❌ 取消全选", command=self.app._deselect_all_langs).pack(side=tk.LEFT, padx=5)

        # 已选计数
        self.app.lang_count_var = tk.StringVar(value="已选: 0 / 33")
        ttk.Label(btn_row, textvariable=self.app.lang_count_var, font=("", 9, "bold"),
                  foreground=ACCENT_COLOR).pack(side=tk.LEFT, padx=20)

        ttk.Button(btn_row, text="➕ 添加自定义语言", command=self.app._add_custom_language).pack(side=tk.RIGHT, padx=5)

        # 单一可滚动列表区
        canvas = tk.Canvas(frame, height=200, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.app.lang_scroll_frame = ttk.Frame(canvas)

        self.app.lang_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.app.lang_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 鼠标滚轮
        def _on_lang_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_lang_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # 按 T1 → T2 → T3 顺序排列，用分隔标签区分
        all_langs = list(TARGET_LANGUAGES)
        self.app.tier_lang_frames = {}

        row = 0
        for tier_name, tier_color, tier_langs in [
            ("⭐ T1 核心市场", "#0066cc", T1_LANGUAGES),
            ("🚀 T2 潜力市场", "#cc6600", T2_LANGUAGES),
            ("🌱 T3 新兴市场", "#00aa00", T3_LANGUAGES),
        ]:
            # 分隔标签
            sep = ttk.Label(self.app.lang_scroll_frame, text=tier_name,
                            font=("", 9, "bold"), foreground=tier_color)
            sep.grid(row=row, column=0, columnspan=5, sticky=tk.W, padx=10, pady=(8 if row > 0 else 2, 2))
            row += 1

            # 该 tier 的语言复选框
            for i, lang_name in enumerate(tier_langs):
                var = tk.BooleanVar(value=False)
                self.app.lang_vars[lang_name] = var
                cb = ttk.Checkbutton(
                    self.app.lang_scroll_frame, text=lang_name,
                    variable=var, command=self.app._update_lang_status
                )
                cb.grid(row=row + i // 5, column=i % 5, sticky=tk.W, padx=10, pady=2)

            row += (len(tier_langs) + 4) // 5  # 向上取整

        # 默认选中 T1 全部语言
        for lang in T1_LANGUAGES:
            if lang in self.app.lang_vars:
                self.app.lang_vars[lang].set(True)
        self.app._update_lang_status()

        return frame


class PromptConfigUIBuilder:
    """提示词配置区UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建提示词配置区"""
        frame = ttk.LabelFrame(parent, text="⚙️ 提示词配置（只需输入风格，其他自动处理）", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 风格输入区
        style_frame = ttk.Frame(frame)
        style_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(style_frame, text="📝 初译风格（例如：专业严谨、轻松活泼、简洁直接）:", font=("", 9, "bold")).pack(anchor=tk.W)
        self.app.draft_style_entry = ttk.Entry(style_frame, textvariable=self.app.draft_style_var, font=("Microsoft YaHei", 10))
        self.app.draft_style_entry.pack(fill=tk.X, pady=(5, 10))

        ttk.Label(style_frame, text="✨ 校对风格（例如：流畅自然、地道表达、保持原文语气）:", font=("", 9, "bold")).pack(anchor=tk.W)
        self.app.review_style_entry = ttk.Entry(style_frame, textvariable=self.app.review_style_var, font=("Microsoft YaHei", 10))
        self.app.review_style_entry.pack(fill=tk.X, pady=(5, 0))

        # 提示预览区
        self.app.prompt_preview_frame = ttk.LabelFrame(frame, text="👁️ 提示词预览（自动生成，无需手动编辑）", padding="10")
        self.app.prompt_preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.app.preview_notebook = ttk.Notebook(self.app.prompt_preview_frame)
        self.app.preview_notebook.pack(fill=tk.BOTH, expand=True)

        # 初译预览
        draft_preview_tab = ttk.Frame(self.app.preview_notebook)
        self.app.preview_notebook.add(draft_preview_tab, text="初译提示词（自动生成）")
        self.app.draft_preview_text = scrolledtext.ScrolledText(draft_preview_tab, height=PROMPT_PREVIEW_HEIGHT, font=("Consolas", PREVIEW_FONT_SIZE), state='disabled', bg=PREVIEW_BG_COLOR)
        self.app.draft_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 校对预览
        review_preview_tab = ttk.Frame(self.app.preview_notebook)
        self.app.preview_notebook.add(review_preview_tab, text="校对提示词（自动生成）")
        self.app.review_preview_text = scrolledtext.ScrolledText(review_preview_tab, height=PROMPT_PREVIEW_HEIGHT, font=("Consolas", PREVIEW_FONT_SIZE), state='disabled', bg=PREVIEW_BG_COLOR)
        self.app.review_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 向后兼容
        self.app.draft_text = self.app.draft_preview_text
        self.app.review_text = self.app.review_preview_text

        # 操作按钮
        prompt_btn_frame = ttk.Frame(frame)
        prompt_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(prompt_btn_frame, text="🔄 更新预览", command=self.app._update_prompt_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="⚙️ 高级设置", command=self.app._show_prompt_advanced_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="💾 导出完整提示词", command=self.app._export_full_prompts).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="📂 导入自定义提示词", command=self.app._load_custom_prompts).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_btn_frame, text="🔍 查看完整结构", command=self.app._show_full_prompt_structure).pack(side=tk.LEFT, padx=5)

        # 绑定风格变化
        self.app.draft_style_var.trace('w', lambda *args: self.app._on_style_changed())
        self.app.review_style_var.trace('w', lambda *args: self.app._on_style_changed())

        # 初始化预览
        self.app._update_prompt_preview()

        return frame


class ControlAndProgressUIBuilder:
    """控制和进度区UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent) -> ttk.LabelFrame:
        """创建控制和进度区"""
        frame = ttk.LabelFrame(parent, text="🚀 执行控制", padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 初始化日志控制器
        self.app._initialize_log_controller()

        # 性能监控开关
        perf_monitor_frame = ttk.Frame(frame)
        perf_monitor_frame.pack(fill=tk.X, pady=(0, 5))

        self.app.perf_monitor_var = tk.BooleanVar(value=False)
        self.app.perf_monitor_check = ttk.Checkbutton(
            perf_monitor_frame,
            text="📊 启用性能监控",
            variable=self.app.perf_monitor_var,
            command=self.app._toggle_performance_monitor
        )
        self.app.perf_monitor_check.pack(side=tk.LEFT, padx=5)

        # 日志控制面板
        self.app._create_log_control_panel(frame)

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        self.app.start_btn = ttk.Button(btn_frame, text="▶️ 开始翻译", command=self.app._start_translation, style='Accent.TButton')
        self.app.start_btn.pack(side=tk.LEFT, padx=5)

        self.app.stop_btn = ttk.Button(btn_frame, text="⏹️ 停止", command=self.app._stop_translation, state='disabled')
        self.app.stop_btn.pack(side=tk.LEFT, padx=5)

        self.app.pause_btn = ttk.Button(btn_frame, text="⏸️ 暂停", command=self.app._pause_translation, state='disabled')
        self.app.pause_btn.pack(side=tk.LEFT, padx=5)

        self.app.history_btn = ttk.Button(btn_frame, text="📜 查看历史", command=self.app._show_history_window)
        self.app.history_btn.pack(side=tk.LEFT, padx=5)

        self.app.exit_btn = ttk.Button(btn_frame, text="🚪 退出程序", command=self.app._on_closing)
        self.app.exit_btn.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.app.progress_var = tk.DoubleVar()
        self.app.progress_bar = ttk.Progressbar(frame, variable=self.app.progress_var, maximum=100, mode='determinate')
        self.app.progress_bar.pack(fill=tk.X, pady=(5, 2))

        # 进度详情
        self.app._create_progress_details(frame)

        # 性能监控面板
        self.app._create_performance_panel(frame)

        return frame


class LogAndPreviewUIBuilder:
    """日志和预览区UI构建器"""

    def __init__(self, app):
        self.app = app

    def build(self, parent):
        """创建日志和预览区"""
        # 日志区
        log_frame = ttk.LabelFrame(parent, text="📋 运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.app.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9))
        self.app.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 重定向日志到GUI
        self.app._setup_gui_logging()

        # 翻译预览面板
        self.app._create_translation_preview_panel(parent)
