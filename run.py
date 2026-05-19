#!/usr/bin/env python3
"""
翻译工具 — 黑盒 CLI 入口
用法: python run.py [任务配置文件]

读取 translation_task.json 配置，完成：
  输入 Excel (2列: key, 中文) → AI 翻译 → 输出 Excel (36列: 译文_33语言)
"""
import sys
import os
import json
import time
import asyncio
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("translation.cli")


def load_task_config(config_path: str) -> dict:
    """加载任务配置文件"""
    path = Path(config_path)
    if not path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print(f"   请创建 {config_path} 或运行: cp translation_task.json.example translation_task.json")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # 校验必填字段
    task = cfg.get("task", {})
    if not task.get("input_file"):
        print("❌ 配置缺少: task.input_file (输入文件路径)")
        sys.exit(1)
    if not task.get("output_file"):
        print("❌ 配置缺少: task.output_file (输出文件路径)")
        sys.exit(1)
    if not cfg.get("languages", {}).get("target"):
        print("❌ 配置缺少: languages.target (目标语言列表)")
        sys.exit(1)

    return cfg


def resolve_path(rel_path: str) -> str:
    """解析相对路径为项目根目录的绝对路径"""
    p = Path(rel_path)
    if p.is_absolute():
        return str(p)
    return str(PROJECT_ROOT / p)


def ensure_dir(file_path: str):
    """确保输出目录存在"""
    d = Path(file_path).parent
    d.mkdir(parents=True, exist_ok=True)


async def run_pipeline(task_cfg: dict):
    """执行翻译管线"""
    from config.loader import get_config_loader
    from infrastructure.di.di_container import initialize_container

    # 1. 应用系统配置 (API Key 等)
    loader = get_config_loader()
    loader.reload()
    sys_config = loader.get_all()
    logger.info(f"✅ 系统配置已加载: model={sys_config.get('model_name', 'unknown')}")

    # 2. 任务配置
    input_file = resolve_path(task_cfg["task"]["input_file"])
    output_file = resolve_path(task_cfg["task"]["output_file"])
    target_langs = task_cfg["languages"]["target"]
    concurrency = task_cfg.get("concurrency", {}).get("limit", 5)
    mode = task_cfg.get("translation", {}).get("mode", "multilingual")

    if not Path(input_file).exists():
        print(f"❌ 输入文件不存在: {input_file}")
        sys.exit(1)

    ensure_dir(output_file)

    print("=" * 60)
    print(f"📋 任务: {task_cfg['task'].get('name', '未命名')}")
    print(f"📂 输入: {input_file}")
    print(f"📁 输出: {output_file}")
    print(f"🌐 语言: {len(target_langs)} 种 ({', '.join(target_langs[:5])}...)")
    print(f"⚡ 并发: {concurrency}")
    print("=" * 60)

    # 3. 初始化 DI 容器
    from openai import AsyncOpenAI

    api_key = sys_config.get("api_key", "")
    base_url = sys_config.get("base_url", "https://api.deepseek.com")

    if not api_key or api_key.startswith("sk-your-"):
        print("❌ 请先在 config/config.json 中配置有效的 api_key")
        sys.exit(1)

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    container = initialize_container(
        api_client=client,
        draft_prompt=sys_config.get("draft_prompt", ""),
        review_prompt=sys_config.get("review_prompt", ""),
    )
    facade = container.get("translation_facade")
    logger.info("✅ DI 容器初始化完成")

    # 4. 执行翻译
    print(f"\n🚀 开始翻译...\n")
    t0 = time.time()

    if mode == "multilingual":
        result = await facade.translate_file_wide_format(
            source_excel_path=input_file,
            output_excel_path=output_file,
            concurrency_limit=concurrency,
        )
    else:
        result = await facade.translate_file(
            source_excel_path=input_file,
            target_langs=target_langs,
            output_excel_path=output_file,
            concurrency_limit=concurrency,
            use_multilingual=False,
        )

    elapsed = time.time() - t0

    # 5. 汇报结果
    print(f"\n{'=' * 60}")
    print(f"📊 翻译完成 ({elapsed:.1f}秒)")
    print(f"{'=' * 60}")
    print(f"   总条目:   {result.total}")
    print(f"   成功:     {result.success_count}")
    print(f"   失败:     {result.failed_count}")
    print(f"   术语命中: {result.local_hit_count}")
    print(f"   输出文件: {output_file}")
    print(f"{'=' * 60}")

    return result


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else str(PROJECT_ROOT / "translation_task.json")

    print(f"🔧 翻译工具 — 黑盒模式 (配置: {Path(config_path).name})")
    print(f"   项目根目录: {PROJECT_ROOT}\n")

    task_cfg = load_task_config(config_path)
    result = asyncio.get_event_loop().run_until_complete(run_pipeline(task_cfg))

    if result.failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
