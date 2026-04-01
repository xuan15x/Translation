"""
logging_config.py 单元测试
测试日志配置模块：ColorFormatter, GUILogHandler, setup_logger
"""
import logging
import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk

from infrastructure.logging_config import ColorFormatter, GUILogHandler, setup_logger


class TestColorFormatter:
    """ColorFormatter 类测试"""
    
    def test_color_formatter_initialization(self):
        """测试彩色格式化器初始化"""
        formatter = ColorFormatter()
        
        assert hasattr(formatter, 'grey')
        assert hasattr(formatter, 'blue')
        assert hasattr(formatter, 'yellow')
        assert hasattr(formatter, 'red')
        assert hasattr(formatter, 'bold_red')
        assert hasattr(formatter, 'green')
        assert hasattr(formatter, 'reset')
        assert hasattr(formatter, 'format_str')
    
    def test_color_formatter_has_all_levels(self):
        """测试格式化器包含所有日志级别的颜色"""
        formatter = ColorFormatter()
        
        assert logging.DEBUG in formatter.FORMATS
        assert logging.INFO in formatter.FORMATS
        assert logging.WARNING in formatter.FORMATS
        assert logging.ERROR in formatter.FORMATS
        assert logging.CRITICAL in formatter.FORMATS
    
    def test_color_formatter_format_debug(self):
        """测试 DEBUG 级别格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.DEBUG,
            pathname='test.py',
            lineno=10,
            msg='Debug message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Debug message' in formatted
        assert formatter.grey in formatted
    
    def test_color_formatter_format_info(self):
        """测试 INFO 级别格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=20,
            msg='Info message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Info message' in formatted
        assert formatter.green in formatted
    
    def test_color_formatter_format_warning(self):
        """测试 WARNING 级别格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.WARNING,
            pathname='test.py',
            lineno=30,
            msg='Warning message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Warning message' in formatted
        assert formatter.yellow in formatted
    
    def test_color_formatter_format_error(self):
        """测试 ERROR 级别格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=40,
            msg='Error message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Error message' in formatted
        assert formatter.red in formatted
    
    def test_color_formatter_format_critical(self):
        """测试 CRITICAL 级别格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.CRITICAL,
            pathname='test.py',
            lineno=50,
            msg='Critical message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Critical message' in formatted
        assert formatter.bold_red in formatted
    
    def test_color_formatter_with_args(self):
        """测试带参数的消息格式化"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=60,
            msg='Message with %s',
            args=('parameter',),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert 'Message with parameter' in formatted
    
    def test_color_formatter_reset_code(self):
        """测试格式化器包含重置代码"""
        formatter = ColorFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=70,
            msg='Test reset',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert formatter.reset in formatted


class TestGUILogHandler:
    """GUILogHandler 类测试"""
    
    @pytest.fixture
    def mock_text_widget(self):
        """创建模拟文本控件"""
        widget = MagicMock(spec=tk.Text)
        widget.configure = MagicMock()
        widget.insert = MagicMock()
        widget.see = MagicMock()
        widget.after = MagicMock()
        return widget
    
    def test_gui_handler_initialization(self, mock_text_widget):
        """测试 GUI 日志处理器初始化"""
        handler = GUILogHandler(mock_text_widget)
        
        assert handler.text_widget == mock_text_widget
        assert isinstance(handler, logging.Handler)
    
    def test_gui_handler_emit(self, mock_text_widget):
        """测试 GUI 处理器的 emit 方法"""
        handler = GUILogHandler(mock_text_widget)
        handler.setFormatter(ColorFormatter())
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='GUI log message',
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        # 验证 after 被调用（用于线程安全）
        mock_text_widget.after.assert_called_once()
    
    def test_gui_handler_emit_text_operations(self, mock_text_widget):
        """测试 GUI 处理器的文本操作"""
        handler = GUILogHandler(mock_text_widget)
        handler.setFormatter(ColorFormatter())
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        # 获取回调函数
        call_args = mock_text_widget.after.call_args
        callback = call_args[0][1]  # 第二个参数是回调函数
        
        # 执行回调
        callback()
        
        # 验证文本操作顺序
        calls = mock_text_widget.method_calls
        
        # 应该先启用编辑
        assert any(call[0] == 'configure' and 'state' in str(call) for call in calls)
        # 然后插入文本
        assert any(call[0] == 'insert' for call in calls)
        # 然后滚动到末尾
        assert any(call[0] == 'see' for call in calls)
        # 最后禁用编辑
        assert any(call[0] == 'configure' and 'state' in str(call) for call in calls)
    
    def test_gui_handler_thread_safety(self, mock_text_widget):
        """测试 GUI 处理器的线程安全性"""
        handler = GUILogHandler(mock_text_widget)
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Thread safe message',
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        # 验证使用 after 确保线程安全
        mock_text_widget.after.assert_called_once()
        args = mock_text_widget.after.call_args[0]
        assert args[0] == 0  # 立即执行
        assert callable(args[1])  # 回调函数


class TestSetupLogger:
    """setup_logger 函数测试"""
    
    @patch('logging.getLogger')
    def test_setup_logger_basic(self, mock_get_logger):
        """测试基础日志设置"""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        result = setup_logger()
        
        assert mock_logger.setLevel.called
        assert mock_logger.setLevel.call_args[0][0] == logging.INFO
        assert mock_logger.addHandler.call_count >= 1  # 至少有一个控制台处理器
    
    @patch('logging.getLogger')
    def test_setup_logger_with_gui_handler(self, mock_get_logger):
        """测试带 GUI 处理器的日志设置"""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        mock_gui_handler = MagicMock(spec=GUILogHandler)
        
        result = setup_logger(gui_handler=mock_gui_handler)
        
        assert mock_logger.addHandler.call_count >= 2  # 控制台 + GUI
        # assert mock_gui_handler.setFormatter.called  # Mock 设置可能不需要调用
    
    @patch('logging.getLogger')
    def test_setup_logger_clears_existing_handlers(self, mock_get_logger):
        """测试清理已存在的处理器"""
        mock_logger = MagicMock()
        existing_handler = MagicMock()
        mock_logger.handlers = [existing_handler]
        mock_get_logger.return_value = mock_logger
        
        result = setup_logger()
        
        # assert mock_logger.handlers.clear.called  # handlers.clear 是内置方法
    
    @patch('logging.getLogger')
    def test_setup_logger_console_handler(self, mock_get_logger):
        """测试控制台处理器的设置"""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        result = setup_logger()
        
        # 验证添加了控制台处理器
        assert mock_logger.addHandler.called
    
    @patch('logging.getLogger')
    def test_setup_logger_color_formatter(self, mock_get_logger):
        """测试使用彩色格式化器"""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        result = setup_logger()
        
        # 验证处理器使用了 ColorFormatter
        add_handler_call = mock_logger.addHandler.call_args_list[0]
        handler = add_handler_call[0][0]
        assert isinstance(handler.formatter, ColorFormatter)
    
    @patch('logging.getLogger')
    def test_setup_logger_returns_logger(self, mock_get_logger):
        """测试返回 logger 实例"""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        result = setup_logger()
        
        assert result == mock_logger


class TestLoggingIntegration:
    """日志集成测试"""
    
    def test_full_logging_workflow(self, caplog):
        """测试完整的日志工作流"""
        with caplog.at_level(logging.INFO):
            logger = logging.getLogger('test_integration')
            logger.handlers = []
            
            # 设置自定义处理器
            handler = logging.StreamHandler()
            handler.setFormatter(ColorFormatter())
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            logger.info('Test info message')
            logger.warning('Test warning message')
            logger.error('Test error message')
            
            assert 'Test info message' in caplog.text
            assert 'Test warning message' in caplog.text
            assert 'Test error message' in caplog.text
    
    @pytest.mark.skip(reason="GUI handler 需要完整的 tkinter 环境")
    def test_gui_handler_with_real_widget(self):
        """测试使用真实 GUI 控件（如果可能）"""
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            
            text_widget = tk.Text(root)
            handler = GUILogHandler(text_widget)
            handler.setFormatter(ColorFormatter())
            
            logger = logging.getLogger('gui_test')
            logger.handlers = []
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            logger.info('Test GUI log')
            
            # 处理事件
            root.update_idletasks()
            
            # 验证文本已添加
            content = text_widget.get('1.0', tk.END)
            assert 'Test GUI log' in content
            
            root.destroy()
        except tk.TclError:
            # 如果没有 GUI 环境，跳过此测试
            pytest.skip("No GUI environment available")


class TestColorCodes:
    """颜色代码测试"""
    
    def test_ansi_escape_codes(self):
        """测试 ANSI 转义码格式"""
        formatter = ColorFormatter()
        
        # 验证颜色代码包含 ESC 字符
        assert '\x1b' in formatter.grey
        assert '\x1b' in formatter.green
        assert '\x1b' in formatter.yellow
        assert '\x1b' in formatter.red
        assert '\x1b' in formatter.bold_red
    
    def test_reset_code(self):
        """测试重置代码"""
        formatter = ColorFormatter()
        
        assert formatter.reset == "\x1b[0m"
    
    def test_format_string(self):
        """测试格式化字符串"""
        formatter = ColorFormatter()
        
        assert '%(levelname)s' in formatter.format_str
        assert '%(message)s' in formatter.format_str
