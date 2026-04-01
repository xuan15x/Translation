"""
gui_app.py 单元测试
测试 GUI 应用类：TranslationApp
注意：由于 tkinter 的复杂性，这些测试主要使用 mock 来验证逻辑
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import tkinter as tk
from tkinter import ttk

from presentation.gui_app import TranslationApp
from config import GUI_CONFIG

# 标记整个模块需要 GUI 环境
pytestmark = pytest.mark.skip(reason="需要 GUI 环境，暂时跳过。窗口弹出问题已修复")



@pytest.fixture
def mock_root():
    """创建模拟 Tk 根窗口"""
    root = MagicMock(spec=tk.Tk)
    root.title = MagicMock()
    root.geometry = MagicMock()
    return root


@pytest.fixture
def mock_tkinter_components():
    """Mock tkinter 组件，包括 StringVar 等"""
    with patch('presentation.gui_app.tk.Tk') as mock_tk, \
         patch('presentation.gui_app.tk.StringVar') as mock_string_var, \
         patch('presentation.gui_app.tk.IntVar') as mock_int_var, \
         patch('presentation.gui_app.tk.BooleanVar') as mock_bool_var, \
         patch('presentation.gui_app.ttk.Style') as mock_style, \
         patch('presentation.gui_app.ttk.Frame') as mock_frame, \
         patch('presentation.gui_app.ttk.LabelFrame') as mock_label_frame, \
         patch('presentation.gui_app.ttk.Label') as mock_label, \
         patch('presentation.gui_app.ttk.Entry') as mock_entry, \
         patch('presentation.gui_app.ttk.Button') as mock_button, \
         patch('presentation.gui_app.ttk.Radiobutton') as mock_radio, \
         patch('presentation.gui_app.ttk.Checkbutton') as mock_check, \
         patch('presentation.gui_app.ttk.Notebook') as mock_notebook, \
         patch('presentation.gui_app.ttk.Progressbar') as mock_progress, \
         patch('presentation.gui_app.scrolledtext.ScrolledText') as mock_scrolled, \
         patch('presentation.gui_app.filedialog') as mock_filedialog, \
         patch('presentation.gui_app.messagebox') as mock_messagebox:
        
        # 设置基本的 mock 行为
        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance
        mock_frame_instance.pack = MagicMock()
        mock_frame_instance.grid = MagicMock()
        
        # Mock StringVar, IntVar, BooleanVar
        mock_string_var_instance = MagicMock()
        mock_string_var.return_value = mock_string_var_instance
        
        mock_int_var_instance = MagicMock()
        mock_int_var.return_value = mock_int_var_instance
        
        mock_bool_var_instance = MagicMock()
        mock_bool_var.return_value = mock_bool_var_instance
        
        yield {
            'tk': mock_tk,
            'string_var': mock_string_var,
            'int_var': mock_int_var,
            'bool_var': mock_bool_var,
            'style': mock_style,
            'frame': mock_frame,
            'label_frame': mock_label_frame,
            'label': mock_label,
            'entry': mock_entry,
            'button': mock_button,
            'radio': mock_radio,
            'check': mock_check,
            'notebook': mock_notebook,
            'progress': mock_progress,
            'scrolled': mock_scrolled,
            'filedialog': mock_filedialog,
            'messagebox': mock_messagebox
        }


class TestTranslationAppInitialization:
    """TranslationApp 初始化测试"""
    
    def test_app_init(self, mock_tkinter_components):
        """测试应用初始化"""
        mock_root = mock_tkinter_components['tk'].return_value
        
        app = TranslationApp(mock_root)
        
        assert app.root == mock_root
        assert hasattr(app, 'term_path')
        assert hasattr(app, 'source_path')
        assert hasattr(app, 'mode_var')
        assert hasattr(app, 'selected_langs')
        assert hasattr(app, 'prompt_draft')
        assert hasattr(app, 'prompt_review')
        assert hasattr(app, 'is_running')
    
    def test_app_init_window_config(self, mock_tkinter_components):
        """测试窗口配置"""
        mock_root = MagicMock(spec=tk.Tk)
        
        with patch('presentation.gui_app.tk.Tk', return_value=mock_root):
            app = TranslationApp(mock_root)
        
        # 验证窗口设置被调用
        mock_root.title.assert_called_once()
        mock_root.geometry.assert_called_once()
    
    def test_app_init_default_values(self, mock_tkinter_components):
        """测试默认值设置"""
        mock_root = MagicMock(spec=tk.Tk)
        
        with patch('presentation.gui_app.tk.Tk', return_value=mock_root):
            app = TranslationApp(mock_root)
        
        assert app.mode_var.get() == 1  # 默认新文档模式
        assert app.is_running is False
        assert isinstance(app.selected_langs, list)
        assert len(app.selected_langs) == 0
    
    def test_app_setup_ui_called(self, mock_tkinter_components):
        """验证 UI 设置被调用"""
        mock_root = MagicMock(spec=tk.Tk)
        
        with patch('presentation.gui_app.tk.Tk', return_value=mock_root), \
             patch.object(TranslationApp, '_setup_ui') as mock_setup_ui:
            app = TranslationApp(mock_root)
            mock_setup_ui.assert_called_once()
    
    def test_app_setup_logger_called(self, mock_tkinter_components):
        """验证日志设置被调用"""
        mock_root = MagicMock(spec=tk.Tk)
        
        with patch('presentation.gui_app.tk.Tk', return_value=mock_root), \
             patch.object(TranslationApp, '_setup_logger') as mock_setup_logger:
            app = TranslationApp(mock_root)
            mock_setup_logger.assert_called_once()


class TestFileSelection:
    """文件选择功能测试"""
    
    def test_select_term_file(self, mock_tkinter_components):
        """测试选择术语库文件"""
        mock_root = MagicMock()
        mock_tkinter_components['filedialog'].asksaveasfilename.return_value = '/path/to/term.xlsx'
        
        app = TranslationApp(mock_root)
        app._select_term_file()
        
        mock_tkinter_components['filedialog'].asksaveasfilename.assert_called_once()
        app.term_path.set.assert_called_with('/path/to/term.xlsx')
    
    def test_select_term_file_cancel(self, mock_tkinter_components):
        """测试取消选择术语库文件"""
        mock_root = MagicMock()
        mock_tkinter_components['filedialog'].asksaveasfilename.return_value = ''
        
        app = TranslationApp(mock_root)
        app._select_term_file()
        
        # 取消时不应设置路径
        app.term_path.set.assert_not_called()
    
    def test_select_source_file(self, mock_tkinter_components):
        """测试选择待翻译文件"""
        mock_root = MagicMock()
        mock_tkinter_components['filedialog'].askopenfilename.return_value = '/path/to/source.xlsx'
        
        app = TranslationApp(mock_root)
        app._select_source_file()
        
        mock_tkinter_components['filedialog'].askopenfilename.assert_called_once()
        app.source_path.set.assert_called_with('/path/to/source.xlsx')
    
    def test_select_source_file_cancel(self, mock_tkinter_components):
        """测试取消选择源文件"""
        mock_root = MagicMock()
        mock_tkinter_components['filedialog'].askopenfilename.return_value = ''
        
        app = TranslationApp(mock_root)
        app._select_source_file()
        
        app.source_path.set.assert_not_called()


class TestLanguageSelection:
    """语言选择功能测试"""
    
    def test_select_all_langs(self, mock_tkinter_components):
        """测试全选所有语言"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        # Mock lang_vars
        mock_vars = {}
        for i in range(3):
            mock_var = MagicMock()
            mock_var.get = MagicMock(return_value=False)
            mock_var.set = MagicMock()
            mock_vars[f'lang_{i}'] = mock_var
        
        app.lang_vars = mock_vars
        app._update_lang_status = MagicMock()
        
        app._select_all_langs()
        
        # 验证所有语言都被设置为选中
        for var in mock_vars.values():
            var.set.assert_called_with(True)
        app._update_lang_status.assert_called_once()
    
    def test_deselect_all_langs(self, mock_tkinter_components):
        """测试取消全选所有语言"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        # Mock lang_vars
        mock_vars = {}
        for i in range(3):
            mock_var = MagicMock()
            mock_var.get = MagicMock(return_value=True)
            mock_var.set = MagicMock()
            mock_vars[f'lang_{i}'] = mock_var
        
        app.lang_vars = mock_vars
        app._update_lang_status = MagicMock()
        
        app._deselect_all_langs()
        
        # 验证所有语言都被设置为未选中
        for var in mock_vars.values():
            var.set.assert_called_with(False)
        app._update_lang_status.assert_called_once()
    
    def test_update_lang_status(self, mock_tkinter_components):
        """测试更新语言选择状态"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        # Mock lang_vars 和 status label
        mock_vars = {}
        for i in range(3):
            mock_var = MagicMock()
            mock_var.get = MagicMock(return_value=(i % 2 == 0))  # 交替返回 True/False
            mock_vars[f'lang_{i}'] = mock_var
        
        app.lang_vars = mock_vars
        app.lang_status_label = MagicMock()
        
        app._update_lang_status()
        
        # 验证状态标签更新
        app.lang_status_label.config.assert_called()
        # 验证 selected_langs 更新
        assert isinstance(app.selected_langs, list)


class TestPromptValidation:
    """提示词验证测试"""
    
    @patch('presentation.gui_app.messagebox')
    def test_validate_prompts_success(self, mock_messagebox, mock_tkinter_components):
        """测试提示词验证成功"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        # Mock 文本控件
        app.draft_text = MagicMock()
        app.review_text = MagicMock()
        app.draft_text.get.return_value = 'Translate to {target_lang} in JSON format'
        app.review_text.get.return_value = 'Review for {target_lang} in JSON format'
        app.mode_var = MagicMock()
        app.mode_var.get.return_value = 1
        
        result = app._validate_prompts()
        
        assert result is True
        mock_messagebox.showinfo.assert_called_with("成功", "提示词格式校验通过！")
    
    @patch('presentation.gui_app.messagebox')
    def test_validate_prompts_missing_target_lang(self, mock_messagebox, mock_tkinter_components):
        """测试缺少 target_lang 占位符"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        app.draft_text = MagicMock()
        app.review_text = MagicMock()
        app.draft_text.get.return_value = 'Translate in JSON format'  # 缺少 {target_lang}
        app.review_text.get.return_value = 'Review in JSON format'
        app.mode_var = MagicMock()
        app.mode_var.get.return_value = 1
        
        result = app._validate_prompts()
        
        assert result is False
        mock_messagebox.showerror.assert_called()
    
    @patch('presentation.gui_app.messagebox')
    def test_validate_prompts_missing_json(self, mock_messagebox, mock_tkinter_components):
        """测试缺少 JSON 要求"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        app.draft_text = MagicMock()
        app.review_text = MagicMock()
        app.draft_text.get.return_value = 'Translate to {target_lang}'  # 缺少 JSON
        app.review_text.get.return_value = 'Review for {target_lang}'
        app.mode_var = MagicMock()
        app.mode_var.get.return_value = 1
        
        result = app._validate_prompts()
        
        assert result is False
        mock_messagebox.showerror.assert_called()
    
    @patch('presentation.gui_app.messagebox')
    def test_validate_prompts_proofread_mode(self, mock_messagebox, mock_tkinter_components):
        """测试校对模式下的验证"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        app.draft_text = MagicMock()
        app.review_text = MagicMock()
        app.draft_text.get.return_value = 'Translate to {target_lang} in JSON format'
        app.review_text.get.return_value = 'Review for {target_lang} in JSON format'
        app.mode_var = MagicMock()
        app.mode_var.get.return_value = 2  # 校对模式
        
        result = app._validate_prompts()
        
        assert result is True


class TestStartWorkflow:
    """启动工作流测试"""
    
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_already_running(self, mock_messagebox, mock_tkinter_components):
        """测试任务正在运行时"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.is_running = True
        
        app._start_workflow()
        
        mock_messagebox.showwarning.assert_called_with("警告", "任务正在运行中...")
    
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_missing_term_file(self, mock_messagebox, mock_tkinter_components):
        """测试缺少术语库文件"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.term_path.get.return_value = ''
        app.source_path.get.return_value = '/path/to/source.xlsx'
        app.selected_langs = ['英语']
        
        with patch.object(app, '_validate_prompts', return_value=True):
            app._start_workflow()
        
        mock_messagebox.showerror.assert_called_with("错误", "请先选择术语库和待翻译文件！")
    
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_missing_source_file(self, mock_messagebox, mock_tkinter_components):
        """测试缺少源文件"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.term_path.get.return_value = '/path/to/term.xlsx'
        app.source_path.get.return_value = ''
        app.selected_langs = ['英语']
        
        with patch.object(app, '_validate_prompts', return_value=True):
            app._start_workflow()
        
        mock_messagebox.showerror.assert_called_with("错误", "请先选择术语库和待翻译文件！")
    
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_no_languages(self, mock_messagebox, mock_tkinter_components):
        """测试未选择语言"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.term_path.get.return_value = '/path/to/term.xlsx'
        app.source_path.get.return_value = '/path/to/source.xlsx'
        app.selected_langs = []
        
        with patch.object(app, '_validate_prompts', return_value=True):
            app._start_workflow()
        
        mock_messagebox.showerror.assert_called_with("错误", "请至少选择一种目标语言！")
    
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_invalid_prompts(self, mock_messagebox, mock_tkinter_components):
        """测试提示词验证失败"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.term_path.get.return_value = '/path/to/term.xlsx'
        app.source_path.get.return_value = '/path/to/source.xlsx'
        app.selected_langs = ['英语']
        
        with patch.object(app, '_validate_prompts', return_value=False):
            app._start_workflow()
        
        # 验证未启动工作流
        assert app.is_running is False
    
    @patch('presentation.gui_app.threading.Thread')
    @patch('presentation.gui_app.messagebox')
    def test_start_workflow_success(self, mock_messagebox, mock_thread, mock_tkinter_components):
        """测试成功启动工作流"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.term_path.get.return_value = '/path/to/term.xlsx'
        app.source_path.get.return_value = '/path/to/source.xlsx'
        app.selected_langs = ['英语']
        app.start_btn = MagicMock()
        app.progress_bar = MagicMock()
        
        with patch.object(app, '_validate_prompts', return_value=True):
            app._start_workflow()
        
        assert app.is_running is True
        app.start_btn.config.assert_called_with(state='disabled')
        mock_thread.assert_called_once()


class TestAsyncExecution:
    """异步执行测试"""
    
    @patch('gui_app.asyncio.run')
    @patch('presentation.gui_app.messagebox')
    def test_run_async_loop_success(self, mock_messagebox, mock_asyncio_run, mock_tkinter_components):
        """测试异步循环成功执行"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app._execute_task = AsyncMock()
        
        app._run_async_loop()
        
        mock_asyncio_run.assert_called_once()
    
    @patch('gui_app.asyncio.run')
    @patch('presentation.gui_app.logging.exception')
    @patch('presentation.gui_app.messagebox')
    def test_run_async_loop_exception(self, mock_messagebox, mock_logging, mock_asyncio_run, mock_tkinter_components):
        """测试异步循环异常处理"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app._execute_task = AsyncMock(side_effect=Exception("Test error"))
        
        app._run_async_loop()
        
        mock_logging.assert_called()
        mock_messagebox.showerror.assert_called()
    
    def test_on_task_complete(self, mock_tkinter_components):
        """测试任务完成回调"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.start_btn = MagicMock()
        
        app._on_task_complete()
        
        assert app.is_running is False
        app.start_btn.config.assert_called_with(state='normal')


class TestLoggerSetup:
    """日志设置测试"""
    
    @patch('presentation.gui_app.setup_logger')
    @patch('presentation.gui_app.GUILogHandler')
    def test_setup_logger(self, mock_gui_handler, mock_setup_logger, mock_tkinter_components):
        """测试日志设置"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        app.log_text = MagicMock()
        
        # 手动调用 _setup_logger
        with patch('gui_app.ColorFormatter'):
            app._setup_logger()
        
        mock_gui_handler.assert_called_once()
        mock_setup_logger.assert_called()


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.skip(reason="需要完整的 GUI 环境")
    def test_full_app_workflow(self):
        """测试完整的应用工作流（需要 GUI 环境）"""
        # 这个测试需要在真实的 GUI 环境中运行
        # 目前跳过
        pass
    
    def test_app_component_interaction(self, mock_tkinter_components):
        """测试各组件交互"""
        mock_root = MagicMock()
        
        app = TranslationApp(mock_root)
        
        # 模拟用户操作流程
        # 1. 选择文件
        app.term_path.set('/path/to/term.xlsx')
        app.source_path.set('/path/to/source.xlsx')
        
        # 2. 选择语言
        mock_var = MagicMock()
        mock_var.get = MagicMock(return_value=True)
        app.lang_vars = {'英语': mock_var}
        app.selected_langs = ['英语']
        
        # 3. 验证提示词
        app.draft_text = MagicMock()
        app.review_text = MagicMock()
        app.draft_text.get.return_value = 'Translate to {target_lang} in JSON'
        app.review_text.get.return_value = 'Review for {target_lang} in JSON'
        app.mode_var = MagicMock()
        app.mode_var.get.return_value = 1
        
        # 验证可以成功验证提示词
        assert app._validate_prompts() is True
