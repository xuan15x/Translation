"""
GUI错误处理优化
提供友好的错误消息和解决方案建议
"""
from typing import Optional
import tkinter.messagebox as messagebox
from infrastructure.exceptions import ErrorHandler, TranslationBaseError


def show_error_dialog(title: str, error: Exception, parent=None) -> None:
    """
    显示友好的错误对话框，包含解决方案建议
    
    Args:
        title: 对话框标题
        error: 异常对象
        parent: 父窗口
    """
    # 获取用户友好的消息
    if isinstance(error, TranslationBaseError):
        user_message = error.to_user_friendly_string()
        solution = error.get_solution()
    else:
        # 使用ErrorHandler转换
        translated_error = ErrorHandler.handle_error(error)
        user_message = ErrorHandler.get_user_friendly_message(translated_error)
        solution = translated_error.get_solution()
    
    # 构建消息文本
    message_lines = [user_message]
    
    if solution:
        message_lines.append(f"\n💡 解决方案：")
        message_lines.append(solution)
    
    message_text = "\n".join(message_lines)
    
    # 显示对话框
    messagebox.showerror(title, message_text, parent=parent)


def log_error_with_solution(error: Exception, logger) -> None:
    """
    记录错误日志，包含解决方案建议
    
    Args:
        error: 异常对象
        logger: 日志记录器
    """
    if isinstance(error, TranslationBaseError):
        logger.error(f"❌ 错误：{error.message}")
        solution = error.get_solution()
        if solution:
            logger.info(f"💡 解决方案：{solution}")
    else:
        # 使用ErrorHandler转换
        translated_error = ErrorHandler.handle_error(error)
        logger.error(f"❌ 错误：{translated_error.message}")
        solution = translated_error.get_solution()
        if solution:
            logger.info(f"💡 解决方案：{solution}")
