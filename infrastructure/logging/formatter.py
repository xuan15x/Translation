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
                pass

        # 使用 after 方法在 GUI 线程中执行，增加异常处理
        try:
            if self.text_widget.winfo_exists():
                self.text_widget.after(0, append)
        except Exception:
            # GUI已销毁，静默忽略
            pass
