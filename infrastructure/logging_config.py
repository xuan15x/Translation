"""
日志配置模块
提供彩色格式化输出和 GUI 日志处理器
"""
import logging
import sys
import tkinter as tk


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

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


class GUILogHandler(logging.Handler):
    """GUI 文本控件日志处理器"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')

        self.text_widget.after(0, append)


def setup_logger(gui_handler=None):
    """
    设置日志记录器
    
    Args:
        gui_handler: 可选的 GUI 日志处理器
        
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        logger.handlers.clear()

    # 控制台 Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)

    # GUI Handler (如果有)
    if gui_handler:
        logger.addHandler(gui_handler)

    return logger
