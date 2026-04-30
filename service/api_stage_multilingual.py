"""
多语言 API 调用阶段
支持一次请求翻译多种语言
"""
import json
import logging
from typing import Dict, List, Any, Optional

from openai import AsyncOpenAI
from infrastructure.models.models import Config, TaskContext, StageResult
from infrastructure.utils import AdaptiveConcurrencyController
from domain.models import MultiLanguageTask, MultiLanguageResult, TranslationStatus
import asyncio

logger = logging.getLogger(__name__)


class MultilingualAPIStage:
    """多语言 API 调用阶段 - 一次请求翻译多种语言"""

    def __init__(self,
                 client: AsyncOpenAI,
                 controller: AdaptiveConcurrencyController,
                 semaphore: asyncio.Semaphore,
                 config: Config,
                 system_prompt: str):
        """
        初始化多语言 API 阶段

        Args:
            client: OpenAI 异步客户端
            controller: 并发度控制器
            semaphore: 信号量
            config: 配置对象
            system_prompt: 系统提示词
        """
        self.client = client
        self.controller = controller
        self.semaphore = semaphore
        self.config = config
        self.system_prompt = system_prompt

    def _build_multilingual_prompt(self, task: MultiLanguageTask) -> str:
        """
        构建多语言翻译提示词

        Args:
            task: 多语言任务

        Returns:
            提示词字符串
        """
        # 构建语言列表
        lang_list = ", ".join(task.target_langs)
        
        # 构建术语建议（如果有）
        tm_suggestions = ""
        for lang, match in task.tm_matches.items():
            if match and match.score >= 60:
                tm_suggestions += f"\nTM({lang}, {match.score}): {match.original} -> {match.translation}"
        
        # 构建输出格式要求
        output_format = "{" + ", ".join([f'"{lang}": "..."' for lang in task.target_langs]) + "}"
        
        prompt = f"""Src: {task.source_text}
{tm_suggestions}

Output ONLY valid JSON: {output_format}
"""
        return prompt

    def _build_system_prompt(self, target_langs: List[str]) -> str:
        """
        构建多语言系统提示词

        Args:
            target_langs: 目标语言列表

        Returns:
            系统提示词
        """
        lang_list = ", ".join(target_langs)
        
        return f"""Role: Professional Multi-lingual Translator.
Task: Translate the source text into ALL specified target languages: {lang_list}.
Constraints:
1. Output ONLY valid JSON with language codes as keys
2. Each translation must be accurate and natural
3. Strictly follow provided TM suggestions
4. Do not include any explanation or extra text
5. Preserve original formatting and line breaks

Example Output:
{{"en": "Hello", "ja": "こんにちは", "ko": "안녕하세요"}}
"""

    async def execute(self, task: MultiLanguageTask) -> MultiLanguageResult:
        """
        执行多语言翻译

        Args:
            task: 多语言任务

        Returns:
            多语言翻译结果
        """
        max_retries = self.config.max_retries
        attempt = 0
        
        # 计算 max_tokens（每语言约 200 tokens）
        max_tokens = max(self.config.max_tokens, len(task.target_langs) * 200)
        
        while attempt < max_retries:
            # 信号量仅包裹API调用本身，sleep在信号量外执行
            try:
                # 构建提示词
                user_prompt = self._build_multilingual_prompt(task)
                system_prompt = self._build_system_prompt(task.target_langs)

                logger.debug(f"多语言翻译请求: {task.source_text[:50]}... -> {task.target_langs}")

                async with self.semaphore:
                    response = await self.client.chat.completions.create(
                        model=self.config.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=self.config.temperature,
                        max_tokens=max_tokens,
                        top_p=self.config.top_p,
                        response_format={"type": "json_object"},
                        timeout=self.config.timeout
                    )

                # 解析响应
                content = response.choices[0].message.content
                logger.debug(f"API 响应: {content[:200]}...")

                # 尝试解析 JSON
                translations = json.loads(content)

                # 验证结果
                success_langs = []
                failed_langs = []

                for lang in task.target_langs:
                    if lang in translations and translations[lang]:
                        success_langs.append(lang)
                    else:
                        failed_langs.append(lang)
                        logger.warning(f"语言 {lang} 翻译结果缺失或为空")

                # 创建结果
                result = MultiLanguageResult(
                    task=task,
                    translations=translations,
                    success_langs=success_langs,
                    failed_langs=failed_langs,
                    diagnosis="API Success",
                    status=TranslationStatus.SUCCESS if not failed_langs else TranslationStatus.FAILED
                )

                await self.controller.adjust(True)

                logger.info(f"多语言翻译完成: {len(success_langs)}/{len(task.target_langs)} 成功")

                return result

            except json.JSONDecodeError as e:
                logger.warning(f"JSON 解析失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                await self.controller.adjust(False)
                await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))

            except Exception as e:
                logger.exception(f"多语言翻译异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                await self.controller.adjust(False)

                # 检查是否为速率限制
                if "rate limit" in str(e).lower():
                    await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt) * 2)
                else:
                    await asyncio.sleep(self.config.base_retry_delay * (2 ** attempt))
        
        # 所有重试失败
        logger.error(f"多语言翻译失败，已重试 {max_retries} 次")
        return MultiLanguageResult(
            task=task,
            translations={},
            success_langs=[],
            failed_langs=task.target_langs.copy(),
            diagnosis=f"Failed after {max_retries} retries",
            status=TranslationStatus.FAILED
        )
