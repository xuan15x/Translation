"""
日志格式化模块
提供彩色格式化输出和 GUI 日志处理器
"""
import logging
import sys
import tkinter as tk
from typing import Optional


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[34;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;21m"
    reset = "\x1b[0m"
    
    format_str = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


class GUILogHandler(logging.Handler):
    """GUI 文本控件日志处理器"""
    
    def __init__(self, text_widget: tk.Text):
        """
        初始化 GUI 日志处理器

        Args:
            text_widget: Tkinter 文本控件
        """
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord):
        """
        发射日志记录到 GUI 控件

        Args:
            record: 日志记录
        """
        msg = self.format(record)

        def append():
            """在 GUI 线程中添加文本"""
            try:
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.configure(state='disabled')
            except Exception as e:
                # 防止 GUI 控件已销毁
                print(f"GUI log error: {e}")

        # 使用 after 方法在 GUI 线程中执行
        if self.text_widget.winfo_exists():
            self.text_widget.after(0, append)


class GUILogController:
    """GUI 日志控制器 - 管理 GUI 日志显示"""
    
    def __init__(self, text_widget: tk.Text, max_lines: int = 1000):
        """
        初始化 GUI 日志控制器

        Args:
            text_widget: Tkinter 文本控件
            max_lines: 最大显示行数
        """
        self.text_widget = text_widget
        self.max_lines = max_lines
        self.line_count = 0
    
    def append(self, message: str, level: str = "INFO"):
        """
        添加日志消息到 GUI

        Args:
            message: 日志消息
            level: 日志级别
        """
        if not self.text_widget.winfo_exists():
            return
        
        def update():
            """在 GUI 线程中更新"""
            try:
                self.text_widget.configure(state='normal')
                
                # 添加消息
                timestamp = logging.Formatter('%H:%M:%S').format(
                    logging.makeLogRecord({'levelname': level})
                )
                formatted_msg = f"[{timestamp}] {message}"
                self.text_widget.insert(tk.END, formatted_msg + "\n")
                
                # 限制行数
                self.line_count += 1
                if self.line_count > self.max_lines:
                    # 删除最早的一半行
                    lines_to_delete = self.max_lines // 2
                    self.text_widget.delete('1.0', f'{lines_to_delete}.0')
                    self.line_count -= lines_to_delete
                
                self.text_widget.see(tk.END)
                self.text_widget.configure(state='disabled')
            except Exception as e:
                print(f"GUI log controller error: {e}")
        
        self.text_widget.after(0, update)
    
    def clear(self):
        """清空日志显示"""
        if not self.text_widget.winfo_exists():
            return
        
        def clear():
            """在 GUI 线程中清空"""
            try:
                self.text_widget.configure(state='normal')
                self.text_widget.delete('1.0', tk.END)
                self.line_count = 0
                self.text_widget.configure(state='disabled')
            except Exception as e:
                print(f"GUI log clear error: {e}")
        
        self.text_widget.after(0, clear)
    
    def set_max_lines(self, max_lines: int):
        """
        设置最大行数

        Args:
            max_lines: 最大显示行数
        """
        self.max_lines = max_lines
