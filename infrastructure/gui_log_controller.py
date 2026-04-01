"""
GUI 日志控制模块

提供 GUI 界面中的日志控制功能，包括：
1. GUI 操作的打点上报
2. 控制台日志粒度控制
3. 日志级别动态调整
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional
from infrastructure.log_slice import LogCategory, LoggerSlice


class GUILogController:
    """GUI 日志控制器"""
    
    def __init__(self, log_level_var: Optional[tk.StringVar] = None, 
                 granularity_var: Optional[tk.StringVar] = None):
        """
        初始化 GUI 日志控制器
        
        Args:
            log_level_var: 日志级别绑定变量
            granularity_var: 日志粒度绑定变量
        """
        self.log_level_var = log_level_var
        self.granularity_var = granularity_var
        self.logger_slice = LoggerSlice(LogCategory.GUI)
        
        # 记录 GUI 初始化打点
        self._track_gui_initialization()
    
    def _track_gui_initialization(self):
        """跟踪 GUI 初始化（打点上报）"""
        try:
            from infrastructure.config_metrics import record_config_usage
            
            config_data = {
                'gui_initialized': True,
                'log_level': self.log_level_var.get() if self.log_level_var else 'INFO',
                'log_granularity': self.granularity_var.get() if self.granularity_var else 'normal',
            }
            
            record_config_usage(config_data)
            self.logger_slice.debug("GUI 初始化完成", **config_data)
        except Exception as e:
            # 打点失败不影响 GUI 启动
            self.logger_slice.warning(f"GUI 初始化打点失败：{e}")
    
    def track_button_click(self, button_name: str, **kwargs):
        """
        跟踪按钮点击事件
        
        Args:
            button_name: 按钮名称
            **kwargs: 其他参数
        """
        try:
            from infrastructure.config_metrics import record_performance_metric
            
            # 记录用户行为
            event_data = {
                'event_type': 'button_click',
                'button_name': button_name,
                **kwargs
            }
            
            self.logger_slice.info(f"按钮点击：{button_name}", **kwargs)
            
            # 打点上报
            record_performance_metric(
                metric_name='gui_interaction',
                value=1.0,
                unit='clicks',
                tags={'button': button_name}
            )
        except Exception as e:
            self.logger_slice.warning(f"按钮点击打点失败：{button_name}, {e}")
    
    def track_translation_start(self, source_lang: str, target_lang: str, count: int):
        """
        跟踪翻译开始事件
        
        Args:
            source_lang: 源语言
            target_lang: 目标语言
            count: 任务数量
        """
        try:
            from infrastructure.config_metrics import record_performance_metric
            
            self.logger_slice.info(
                f"开始翻译：{source_lang} -> {target_lang}",
                task_count=count
            )
            
            record_performance_metric(
                metric_name='translation_task',
                value=float(count),
                unit='tasks',
                tags={
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            )
        except Exception as e:
            self.logger_slice.warning(f"翻译开始打点失败：{e}")
    
    def track_error(self, error_msg: str, context: str):
        """
        跟踪 GUI 错误事件
        
        Args:
            error_msg: 错误信息
            context: 上下文
        """
        try:
            from infrastructure.config_metrics import record_config_validation_error
            
            self.logger_slice.error(f"{context}: {error_msg}")
            
            record_config_validation_error(
                field=context,
                error_type=error_msg,
                check_point='GUI 操作',
                value=context
            )
        except Exception as e:
            self.logger_slice.error(f"错误打点失败：{e}")
    
    def update_log_level(self, level: str):
        """
        动态更新日志级别
        
        Args:
            level: 新的日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        """
        try:
            # 更新根日志级别
            root_logger = logging.getLogger()
            numeric_level = getattr(logging, level.upper(), logging.INFO)
            root_logger.setLevel(numeric_level)
            
            # 更新所有 handler 的级别
            for handler in root_logger.handlers:
                handler.setLevel(numeric_level)
            
            self.logger_slice.info(f"日志级别已更新为：{level}")
            
            # 打点记录
            if self.log_level_var:
                self.log_level_var.set(level)
                
        except Exception as e:
            self.logger_slice.error(f"更新日志级别失败：{e}")
    
    def update_log_granularity(self, granularity: str):
        """
        动态更新日志粒度
        
        Args:
            granularity: 新的粒度 (minimal/basic/normal/detailed/verbose)
        """
        try:
            self.logger_slice.info(f"日志粒度已更新为：{granularity}")
            
            # 打点记录
            if self.granularity_var:
                self.granularity_var.set(granularity)
                
        except Exception as e:
            self.logger_slice.error(f"更新日志粒度失败：{e}")
    
    def create_log_control_frame(self, parent) -> tk.Frame:
        """
        创建日志控制面板
        
        Args:
            parent: 父容器
            
        Returns:
            tk.Frame: 包含日志控制组件的框架
        """
        frame = tk.Frame(parent)
        
        # 日志级别选择
        tk.Label(frame, text="日志级别:").pack(side=tk.LEFT, padx=5)
        
        level_var = tk.StringVar(value="INFO")
        if self.log_level_var:
            level_var = self.log_level_var
        
        level_combo = ttk.Combobox(frame, textvariable=level_var, width=8, state="readonly")
        level_combo['values'] = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind('<<ComboboxSelected>>', 
                        lambda e: self.update_log_level(level_var.get()))
        
        # 日志粒度选择
        tk.Label(frame, text="日志粒度:").pack(side=tk.LEFT, padx=5)
        
        granularity_var = tk.StringVar(value="normal")
        if self.granularity_var:
            granularity_var = self.granularity_var
        
        granularity_combo = ttk.Combobox(frame, textvariable=granularity_var, width=10, state="readonly")
        granularity_combo['values'] = ('minimal', 'basic', 'normal', 'detailed', 'verbose')
        granularity_combo.pack(side=tk.LEFT, padx=5)
        granularity_combo.bind('<<ComboboxSelected>>',
                              lambda e: self.update_log_granularity(granularity_var.get()))
        
        return frame


# 便捷函数
def setup_gui_logging(gui_app, log_level: str = "INFO", log_granularity: str = "normal"):
    """
    设置 GUI 日志系统
    
    Args:
        gui_app: GUI 应用实例
        log_level: 初始日志级别
        log_granularity: 初始日志粒度
        
    Returns:
        GUILogController: 日志控制器实例
    """
    # 创建绑定变量
    log_level_var = tk.StringVar(value=log_level)
    log_granularity_var = tk.StringVar(value=log_granularity)
    
    # 创建控制器
    controller = GUILogController(log_level_var, log_granularity_var)
    
    # 应用初始配置
    controller.update_log_level(log_level)
    controller.update_log_granularity(log_granularity)
    
    return controller
