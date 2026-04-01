"""
API 阶段处理模块
实现初译、校对和本地命中的处理逻辑
"""
import asyncio
import json
import re
from typing import Any, Optional
import logging

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError

from infrastructure.models import Config, StageResult, TaskContext
from infrastructure.prompt_builder import PromptBuilder
from infrastructure.concurrency_controller import AdaptiveConcurrencyController

logger = logging.getLogger(__name__)


class APIDraftStage:
    """API 初译阶段"""
    
    def __init__(self, client: AsyncOpenAI, controller: AdaptiveConcurrencyController, 
                 semaphore: asyncio.Semaphore, config: Config, system_prompt: str):
        """
        初始化初译阶段
        
        Args:
            client: OpenAI 异步客户端
            controller: 并发度控制器
            semaphore: 信号量
            config: 系统配置
            system_prompt: 系统提示词模板
        """
        self.client = client
        self.controller = controller
        self.semaphore = semaphore
        self.config = config
        self.system_prompt = system_prompt

    async def execute(self, context: TaskContext) -> StageResult:
        """
        执行初译阶段
        
        Args:
            context: 任务上下文
            
        Returns:
            阶段执行结果
        """
        user_msg = PromptBuilder.build_user_message("draft", context)
        messages = [
            {"role": "system", "content": self.system_prompt.replace("{target_lang}", context.target_lang)},
            {"role": "user", "content": user_msg}
        ]
        
        return await self._call_api(
            messages, 
            max_tokens=512, 
            src_preview=context.source_text[:10], 
            target_lang=context.target_lang
        )

    async def _call_api(self, messages: list, max_tokens: int = None,
                       src_preview: str = "", target_lang: str = "") -> StageResult:
        """
        调用 API 进行翻译
        
        Args:
            messages: 消息列表
            max_tokens: 最大 token 数（如果为 None 则使用配置值）
            src_preview: 源文本预览
            target_lang: 目标语言
            
        Returns:
            阶段执行结果
        """
        attempt = 0
        last_error: Optional[str] = None
        
        # 获取当前阶段的配置
        model_name = self.config.get_draft_model_name()
        temperature = self.config.get_draft_temperature()
        top_p = self.config.get_draft_top_p()
        timeout = self.config.get_draft_timeout()
        
        if max_tokens is None:
            max_tokens = self.config.get_draft_max_tokens()
        
        while attempt < self.config.max_retries:
            async with self.semaphore:
                try:
                    response = await self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        response_format={"type": "json_object"},
                        timeout=timeout
                    )
                    
                    await self.controller.adjust(True)
                    
                    # 解析响应
                    if not response.choices or not response.choices[0].message.content:
                        return StageResult(
                            False, 
                            "", 
                            error_msg="Empty API response",
                            source="API"
                        )
                    
                    content = re.sub(
                        r'^```json\s*|\s*```$', 
                        '', 
                        response.choices[0].message.content.strip(), 
                        flags=re.MULTILINE
                    )
                    
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON 解析失败：{e}, content: {content[:100]}")
                        attempt += 1
                        if attempt >= self.config.max_retries:
                            return StageResult(False, "", error_msg="Invalid JSON format", source="API")
                        await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                        continue
                    
                    trans = data.get("Trans", "")
                    if not trans:
                        logger.warning(f"翻译结果为空：{data}")
                        attempt += 1
                        if attempt >= self.config.max_retries:
                            return StageResult(False, "", error_msg="Empty translation result", source="API")
                        await asyncio.sleep(self.config.base_retry_delay)
                        continue
                    
                    return StageResult(
                        success=True, 
                        translation=trans
                    )
                    
                except RateLimitError as e:
                    # 速率限制，指数退避
                    await self.controller.adjust(False)
                    retry_after = getattr(e, 'retry_after', self.config.base_retry_delay * (2 ** attempt))
                    logger.warning(f"API 速率限制，等待 {retry_after}s 后重试")
                    await asyncio.sleep(retry_after)
                    attempt += 1
                    
                except APITimeoutError as e:
                    # 超时错误
                    await self.controller.adjust(False)
                    logger.error(f"API 超时：{e}")
                    attempt += 1
                    if attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=f"API timeout after {attempt} attempts", source="API")
                    await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                    
                except APIError as e:
                    # 其他 API 错误
                    await self.controller.adjust(False)
                    error_msg = str(e)
                    logger.error(f"API 错误：{error_msg}")
                    
                    # 429 错误特殊处理
                    if "429" in error_msg:
                        await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                        attempt += 1
                    elif attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=error_msg, source="API")
                    else:
                        attempt += 1
                        await asyncio.sleep(self.config.base_retry_delay)
                
                except Exception as e:
                    # 未知错误
                    await self.controller.adjust(False)
                    error_msg = f"Unexpected error: {str(e)}"
                    logger.exception(error_msg)
                    attempt += 1
                    if attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=error_msg, source="API")
                    await asyncio.sleep(self.config.base_retry_delay)
        
        return StageResult(False, "", error_msg="Max retries exceeded", source="API")


class APIReviewStage(APIDraftStage):
    """API 校对阶段"""
    
    async def execute(self, context: TaskContext, draft_trans: str) -> StageResult:
        """
        执行校对阶段
        
        Args:
            context: 任务上下文
            draft_trans: 初译文本
            
        Returns:
            阶段执行结果
        """
        user_msg = PromptBuilder.build_user_message("review", context, draft_trans)
        messages = [
            {"role": "system", "content": self.system_prompt.replace("{target_lang}", context.target_lang)},
            {"role": "user", "content": user_msg}
        ]
        
        return await self._call_api(
            messages, 
            max_tokens=None,  # 使用 review_max_tokens 配置
            src_preview=context.source_text[:10], 
            target_lang=context.target_lang
        )
    
    async def _call_api(self, messages: list, max_tokens: int = None,
                       src_preview: str = "", target_lang: str = "") -> StageResult:
        """
        重写父类方法，使用校对阶段的配置
        
        Args:
            messages: 消息列表
            max_tokens: 最大 token 数（如果为 None 则使用配置值）
            src_preview: 源文本预览
            target_lang: 目标语言
            
        Returns:
            阶段执行结果
        """
        attempt = 0
        last_error: Optional[str] = None
        
        # 获取校对阶段的配置
        model_name = self.config.get_review_model_name()
        temperature = self.config.get_review_temperature()
        top_p = self.config.get_review_top_p()
        timeout = self.config.get_review_timeout()
        
        if max_tokens is None:
            max_tokens = self.config.get_review_max_tokens()
        
        while attempt < self.config.max_retries:
            async with self.semaphore:
                try:
                    response = await self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        response_format={"type": "json_object"},
                        timeout=timeout
                    )
                    
                    await self.controller.adjust(True)
                    
                    # 解析响应
                    if not response.choices or not response.choices[0].message.content:
                        return StageResult(
                            False, 
                            "", 
                            error_msg="Empty API response",
                            source="API"
                        )
                    
                    content = re.sub(
                        r'^```json\s*|\s*```$', 
                        '', 
                        response.choices[0].message.content.strip(), 
                        flags=re.MULTILINE
                    )
                    
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON 解析失败：{e}, content: {content[:100]}")
                        attempt += 1
                        if attempt >= self.config.max_retries:
                            return StageResult(False, "", error_msg="Invalid JSON format", source="API")
                        await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                        continue
                    
                    trans = data.get("Trans", "")
                    reason = data.get("Reason", "")
                    
                    if not trans:
                        logger.warning(f"翻译结果为空：{data}")
                        attempt += 1
                        if attempt >= self.config.max_retries:
                            return StageResult(False, "", error_msg="Empty translation result", source="API")
                        await asyncio.sleep(self.config.base_retry_delay)
                        continue
                    
                    return StageResult(
                        success=True, 
                        translation=trans
                    )
                    
                except RateLimitError as e:
                    # 速率限制，指数退避
                    await self.controller.adjust(False)
                    retry_after = getattr(e, 'retry_after', self.config.base_retry_delay * (2 ** attempt))
                    logger.warning(f"API 速率限制，等待 {retry_after}s 后重试")
                    await asyncio.sleep(retry_after)
                    attempt += 1
                    
                except APITimeoutError as e:
                    # 超时错误
                    await self.controller.adjust(False)
                    logger.error(f"API 超时：{e}")
                    attempt += 1
                    if attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=f"API timeout after {attempt} attempts", source="API")
                    await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                    
                except APIError as e:
                    # 其他 API 错误
                    await self.controller.adjust(False)
                    error_msg = str(e)
                    logger.error(f"API 错误：{error_msg}")
                    
                    # 429 错误特殊处理
                    if "429" in error_msg:
                        await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
                        attempt += 1
                    elif attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=error_msg, source="API")
                    else:
                        attempt += 1
                        await asyncio.sleep(self.config.base_retry_delay)
                
                except Exception as e:
                    # 未知错误
                    await self.controller.adjust(False)
                    error_msg = f"Unexpected error: {str(e)}"
                    logger.exception(error_msg)
                    attempt += 1
                    if attempt >= self.config.max_retries:
                        return StageResult(False, "", error_msg=error_msg, source="API")
                    await asyncio.sleep(self.config.base_retry_delay)
        
        return StageResult(False, "", error_msg="Max retries exceeded", source="API")


class LocalHitStage:
    """本地术语命中阶段"""
    
    async def execute(self, context: TaskContext) -> StageResult:
        """
        执行本地术语匹配检查
        
        Args:
            context: 任务上下文
            
        Returns:
            阶段执行结果
        """
        if not context.tm_suggestion:
            return StageResult(False, "", source="NONE")
        
        return StageResult(
            success=True, 
            translation=context.tm_suggestion['translation'], 
            source="LOCAL_HIT"
        )
