"""
log_slice.py 单元测试
测试抽象日志切片层功能
"""
import pytest
import logging
from io import StringIO
from infrastructure.log_slice import (
    LoggerSlice, LogCategory, LogLevel, LogContext, 
    log_slice, ModuleLoggerMixin, create_logger_slice,
    get_category_by_module
)


class TestLogCategory:
    """LogCategory 枚举测试"""
    
    def test_all_categories_exist(self):
        """测试所有日志类别都存在"""
        categories = [
            LogCategory.MODEL,
            LogCategory.PROMPT,
            LogCategory.MATCHER,
            LogCategory.CONCURRENCY,
            LogCategory.TERMINOLOGY,
            LogCategory.API,
            LogCategory.WORKFLOW,
            LogCategory.GUI,
            LogCategory.GENERAL
        ]
        
        assert len(categories) == 9
    
    def test_category_values(self):
        """测试类别值"""
        assert LogCategory.MODEL.value == "MODEL"
        assert LogCategory.API.value == "API"
        assert LogCategory.WORKFLOW.value == "WORKFLOW"


class TestLogLevel:
    """LogLevel 枚举测试"""
    
    def test_all_levels_exist(self):
        """测试所有日志级别"""
        levels = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL
        ]
        
        assert len(levels) == 5
    
    def test_level_values_match_logging(self):
        """测试日志级别值与 logging 模块匹配"""
        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


class TestLogContext:
    """LogContext 数据类测试"""
    
    def test_create_context_minimal(self):
        """测试创建最小化日志上下文"""
        ctx = LogContext(
            module_name="test_module",
            function_name="test_func",
            category=LogCategory.GENERAL
        )
        
        assert ctx.module_name == "test_module"
        assert ctx.function_name == "test_func"
        assert ctx.category == LogCategory.GENERAL
        assert ctx.level == LogLevel.INFO
        assert ctx.execution_time == 0.0
        assert ctx.parameters == {}
        assert ctx.result is None
        assert ctx.error is None
    
    def test_create_context_full(self):
        """测试创建完整日志上下文"""
        ctx = LogContext(
            module_name="test_module",
            function_name="test_func",
            category=LogCategory.MODEL,
            level=LogLevel.DEBUG,
            execution_time=1.5,
            parameters={"param1": "value1"},
            result="result_value",
            error=None,
            extra_data={"key": "value"}
        )
        
        assert ctx.level == LogLevel.DEBUG
        assert ctx.execution_time == 1.5
        assert ctx.parameters["param1"] == "value1"
        assert ctx.result == "result_value"
        assert ctx.extra_data["key"] == "value"


class TestLoggerSlice:
    """LoggerSlice 核心类测试"""
    
    @pytest.fixture
    def logger_with_capture(self):
        """创建带日志捕获的 LoggerSlice"""
        # 创建字符串缓冲区用于捕获日志
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        # 创建 logger
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        # 创建 LoggerSlice
        slice = LoggerSlice(LogCategory.GENERAL, logger)
        
        yield slice, log_stream
        
        # 清理
        logger.removeHandler(handler)
    
    def test_initialization(self):
        """测试 LoggerSlice 初始化"""
        slice = LoggerSlice(LogCategory.MODEL)
        
        assert slice.category == LogCategory.MODEL
        assert slice.logger is not None
        assert slice._execution_times == []
    
    def test_log_method_basic(self, logger_with_capture):
        """测试基本日志记录"""
        slice, stream = logger_with_capture
        
        slice.log(LogLevel.INFO, "Test message")
        
        log_output = stream.getvalue()
        assert "[GENERAL]" in log_output
        assert "Test message" in log_output
    
    def test_log_method_with_category(self, logger_with_capture):
        """测试带类别的日志记录"""
        slice = LoggerSlice(LogCategory.API, logging.getLogger("test_api"))
        slice.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        slice.logger.addHandler(handler)
        
        slice.info("API call")
        
        handler.stream.seek(0)
        log_output = handler.stream.read()
        assert "[API]" in log_output
    
    def test_convenience_methods(self, logger_with_capture):
        """测试便捷方法"""
        slice, stream = logger_with_capture
        
        slice.debug("Debug message")
        slice.info("Info message")
        slice.warning("Warning message")
        
        log_output = stream.getvalue()
        assert "Debug message" in log_output
        assert "Info message" in log_output
        assert "Warning message" in log_output
    
    def test_create_context(self):
        """测试创建上下文"""
        slice = LoggerSlice(LogCategory.MODEL)
        
        ctx = slice.create_context("test_func", {"param": "value"})
        
        assert ctx.function_name == "test_func"
        assert ctx.category == LogCategory.MODEL
        assert ctx.parameters["param"] == "value"
    
    def test_log_entry_exit(self, logger_with_capture):
        """测试入口和出口日志"""
        slice, stream = logger_with_capture
        
        slice.log_entry("test_function", {"arg1": "value1"})
        slice.log_exit("test_function", "result", 0.123)
        
        log_output = stream.getvalue()
        assert "进入 test_function" in log_output
        assert "离开 test_function" in log_output
        assert "耗时=0.1230s" in log_output
    
    def test_log_error(self, logger_with_capture):
        """测试错误日志"""
        slice, stream = logger_with_capture
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            slice.log_error("test_function", e)
        
        log_output = stream.getvalue()
        assert "test_function 发生错误" in log_output
        assert "Test error" in log_output
    
    def test_record_execution_time(self):
        """测试记录执行时间"""
        slice = LoggerSlice(LogCategory.GENERAL)
        
        slice.record_execution_time(0.1)
        slice.record_execution_time(0.2)
        slice.record_execution_time(0.3)
        
        avg_time = slice.get_average_execution_time()
        assert avg_time == pytest.approx(0.2)
    
    def test_clear_execution_times(self):
        """测试清空执行时间"""
        slice = LoggerSlice(LogCategory.GENERAL)
        
        slice.record_execution_time(0.1)
        slice.clear_execution_times()
        
        assert slice._execution_times == []
        assert slice.get_average_execution_time() == 0.0


class TestLogSliceDecorator:
    """日志切片装饰器测试"""
    
    @pytest.fixture
    def setup_logger(self):
        """设置测试日志器"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger("decorator_test")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        yield logger, log_stream
        
        logger.removeHandler(handler)
    
    def test_decorator_basic(self, setup_logger):
        """测试基本装饰器功能"""
        logger, stream = setup_logger
        
        @log_slice(LogCategory.GENERAL)
        def test_func(x, y):
            return x + y
        
        result = test_func(2, 3)
        
        assert result == 5
        log_output = stream.getvalue()
        assert "进入 test_func" in log_output
        assert "离开 test_func" in log_output
    
    def test_decorator_with_exception(self, setup_logger):
        """测试装饰器异常处理"""
        logger, stream = setup_logger
        
        @log_slice(LogCategory.GENERAL)
        def failing_func():
            raise ValueError("Expected error")
        
        with pytest.raises(ValueError):
            failing_func()
        
        log_output = stream.getvalue()
        assert "failing_func 发生错误" in log_output
        assert "Expected error" in log_output
    
    def test_decorator_no_params(self, setup_logger):
        """测试无参数函数装饰器"""
        logger, stream = setup_logger
        
        @log_slice(LogCategory.GENERAL)
        def no_param_func():
            return "result"
        
        result = no_param_func()
        
        assert result == "result"
        log_output = stream.getvalue()
        assert "进入 no_param_func" in log_output
    
    def test_decorator_custom_settings(self, setup_logger):
        """测试自定义装饰器设置"""
        logger, stream = setup_logger
        
        @log_slice(
            LogCategory.API,
            entry_level=LogLevel.INFO,
            exit_level=LogLevel.INFO,
            log_result=True
        )
        def api_call(data):
            return f"Processed: {data}"
        
        result = api_call("input")
        
        assert result == "Processed: input"
        log_output = stream.getvalue()
        assert "[API]" in log_output
        assert "Processed: input" in log_output  # 因为 log_result=True


class TestModuleLoggerMixin:
    """ModuleLoggerMixin 混合类测试"""
    
    class TestClass(ModuleLoggerMixin):
        """测试用类"""
        LOG_CATEGORY = LogCategory.MODEL
        
        def test_method(self):
            self.log_info("Test method called")
            return "result"
    
    def test_mixin_initialization(self):
        """测试混合类初始化"""
        obj = self.TestClass()
        
        assert hasattr(obj, '_logger_slice')
        assert isinstance(obj._logger_slice, LoggerSlice)
        assert obj._logger_slice.category == LogCategory.MODEL
    
    def test_logger_property(self):
        """测试 logger 属性"""
        obj = self.TestClass()
        
        logger = obj.logger
        assert isinstance(logger, LoggerSlice)
    
    def test_log_methods(self):
        """测试日志方法"""
        obj = self.TestClass()
        
        # 不应该抛出异常
        obj.log_debug("Debug")
        obj.log_info("Info")
        obj.log_warning("Warning")
        obj.log_error("Error")
        obj.log_critical("Critical")
    
    def test_method_with_logging(self, caplog):
        """测试方法中的日志记录"""
        obj = self.TestClass()
        
        with caplog.at_level(logging.INFO):
            result = obj.test_method()
            
            assert result == "result"
            assert "Test method called" in caplog.text


class TestHelperFunctions:
    """辅助函数测试"""
    
    def test_create_logger_slice(self):
        """测试创建日志切片"""
        slice = create_logger_slice(LogCategory.MODEL, "test")
        
        assert slice.category == LogCategory.MODEL
        assert slice.logger.name == "test"
    
    def test_create_logger_slice_default_name(self):
        """测试使用默认名称创建"""
        slice = create_logger_slice(LogCategory.GENERAL)
        
        assert slice.category == LogCategory.GENERAL
    
    def test_get_category_by_module(self):
        """测试根据模块名获取类别"""
        assert get_category_by_module("models") == LogCategory.MODEL
        assert get_category_by_module("api_stages") == LogCategory.API
        assert get_category_by_module("workflow_orchestrator") == LogCategory.WORKFLOW
        assert get_category_by_module("unknown_module") == LogCategory.GENERAL
    
    def test_get_category_by_module_with_path(self):
        """测试带路径的模块名"""
        assert get_category_by_module("package.models") == LogCategory.MODEL
        assert get_category_by_module("src/api_stages") == LogCategory.API


class TestLoggerSliceIntegration:
    """LoggerSlice 集成测试"""
    
    def test_full_logging_workflow(self, caplog):
        """测试完整的日志工作流"""
        from infrastructure.log_slice import LoggerSlice, LogCategory
        
        slice = LoggerSlice(LogCategory.TERMINOLOGY)
        
        with caplog.at_level(logging.DEBUG):
            # 模拟完整的工作流程
            slice.log_entry("add_term", {"src": "你好", "lang": "英语"})
            slice.record_execution_time(0.05)
            slice.log_exit("add_term", "success", 0.05)
            
            assert "进入 add_term" in caplog.text
            assert "离开 add_term" in caplog.text
            assert "耗时=0.0500s" in caplog.text
    
    def test_multiple_categories(self, caplog):
        """测试多个日志类别"""
        model_slice = LoggerSlice(LogCategory.MODEL)
        api_slice = LoggerSlice(LogCategory.API)
        
        with caplog.at_level(logging.INFO):
            model_slice.info("Model initialized")
            api_slice.info("API called")
            
            assert "[MODEL]" in caplog.text
            assert "[API]" in caplog.text
