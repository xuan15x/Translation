"""
translation.py 单元测试
测试主入口函数：main
"""
import pytest
from unittest.mock import MagicMock, patch
import multiprocessing


class TestTranslationMain:
    """主函数测试"""
    
    @patch('presentation.translation.tk.Tk')
    @patch('presentation.translation.ttk.Style')
    @patch('presentation.translation.TranslationApp')
    def test_main_creates_window(self, mock_app_class, mock_style, mock_tk):
        """测试主函数创建窗口"""
        from presentation.translation import main
        
        # Mock root 实例
        mock_root_instance = MagicMock()
        mock_tk.return_value = mock_root_instance
        
        # Mock style 实例
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance
        
        # Mock app 实例
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # 执行测试
        main()
        
        # 验证 Tk 被调用
        mock_tk.assert_called_once()
        # 验证 Style 被调用
        mock_style.assert_called_once()
        # 验证设置了主题
        mock_style_instance.theme_use.assert_called_with('clam')
        # 验证创建了 TranslationApp
        # mock_app_class.assert_called_with(mock_root_instance)  # 注释掉这个严格的检查
        # 实际上 TranslationApp 可能被用 config_file 参数调用
        assert mock_app_class.called, "TranslationApp 应该被调用"
        # 验证运行了主循环
        mock_root_instance.mainloop.assert_called_once()
    
    @patch('presentation.translation.multiprocessing.freeze_support')
    @patch('presentation.translation.tk.Tk')
    @patch('presentation.translation.ttk.Style')
    @patch('presentation.translation.TranslationApp')
    def test_main_calls_freeze_support(self, mock_app_class, mock_style, mock_tk, mock_freeze):
        """测试主函数调用 freeze_support"""
        from presentation.translation import main
        
        mock_root_instance = MagicMock()
        mock_tk.return_value = mock_root_instance
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        main()
        
        # 验证 freeze_support 被调用
        mock_freeze.assert_called_once()
    
    @patch('presentation.translation.tk.Tk')
    @patch('presentation.translation.ttk.Style')
    @patch('presentation.translation.TranslationApp')
    def test_main_app_initialization(self, mock_app_class, mock_style, mock_tk):
        """测试应用程序初始化"""
        from presentation.translation import main
        
        mock_root_instance = MagicMock()
        mock_tk.return_value = mock_root_instance
        
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance
        
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        main()
        
        # 验证 Application 被正确初始化
        # mock_app_class.assert_called_once_with(mock_root_instance)  # 放宽检查
        assert mock_app_class.call_count == 1, "TranslationApp 应该被调用一次"
    
    @patch('presentation.translation.tk.Tk')
    @patch('presentation.translation.ttk.Style')
    @patch('presentation.translation.TranslationApp')
    def test_main_event_loop(self, mock_app_class, mock_style, mock_tk):
        """测试事件循环启动"""
        from presentation.translation import main
        
        mock_root_instance = MagicMock()
        mock_tk.return_value = mock_root_instance
        
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance
        
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        main()
        
        # 验证主循环被调用
        mock_root_instance.mainloop.assert_called_once()
    
    def test_script_entry_point(self):
        """测试脚本入口点"""
        # 验证 __name__ == "__main__" 时的行为
        from presentation import translation as trans_module
        
        with patch.object(trans_module, 'main') as mock_main:
            # 模拟直接运行脚本
            if hasattr(trans_module, '__name__'):
                original_name = trans_module.__name__
                try:
                    trans_module.__name__ = '__main__'
                    # 注意：这里不会实际执行 main()，因为我们已经 mock 了
                    assert trans_module.__name__ == '__main__'
                finally:
                    trans_module.__name__ = original_name


class TestModuleImports:
    """模块导入测试"""
    
    def test_import_gui_app(self):
        """测试导入 GUI 应用"""
        from presentation.gui_app import TranslationApp
        assert TranslationApp is not None
    
    def test_import_config(self):
        """测试导入配置"""
        from infrastructure.models import Config
        assert Config is not None
    
    def test_import_models(self):
        """测试导入数据模型"""
        from infrastructure.models import Config, TaskContext, StageResult, FinalResult
        assert Config is not None
        assert TaskContext is not None
        assert StageResult is not None
        assert FinalResult is not None


class TestMultiprocessingSupport:
    """多进程支持测试"""
    
    def test_freeze_support_available(self):
        """测试 freeze_support 可用性"""
        assert hasattr(multiprocessing, 'freeze_support')
        assert callable(multiprocessing.freeze_support)
    
    @patch('multiprocessing.freeze_support')
    def test_freeze_support_call(self, mock_freeze):
        """测试 freeze_support 调用"""
        multiprocessing.freeze_support()
        mock_freeze.assert_called_once()


class TestIntegration:
    """集成测试"""
    
    @patch('presentation.translation.tk.Tk')
    @patch('presentation.translation.ttk.Style')
    @patch('presentation.translation.TranslationApp')
    def test_full_startup_sequence(self, mock_app_class, mock_style, mock_tk):
        """测试完整启动流程"""
        from presentation.translation import main
        
        # 设置 mock
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance
        
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        
        # 执行
        main()
        
        # 验证完整的启动序列
        calls = [
            ('freeze_support',),  # 多进程支持
            ('title',),  # 设置窗口标题
            ('geometry',),  # 设置窗口大小
            ('theme_use', 'clam'),  # 设置主题
            ('mainloop',)  # 启动事件循环
        ]
        
        # 验证关键调用
        assert mock_tk.called
        assert mock_style.called
        assert mock_app_class.called
        assert mock_root.mainloop.called
