"""
新架构使用示例
演示如何使用重构后的分层架构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def example_1_basic_usage():
    """示例 1: 基本使用 - 依赖注入容器"""
    print("\n" + "="*60)
    print("示例 1: 使用依赖注入容器")
    print("="*60)
    
    from infrastructure.di_container import initialize_container
    
    # 初始化容器（不包含翻译服务）
    container = initialize_container()
    
    # 获取术语服务
    term_service = container.get('terminology_service')
    
    # 测试术语查询
    match = await term_service.find_match("示例文本", "en")
    
    if match:
        print(f"✅ 找到匹配：{match.original} -> {match.translation}")
        print(f"   置信度：{match.score}")
        print(f"   类型：{match.match_type.value}")
    else:
        print("❌ 未找到匹配")


async def example_2_with_cache():
    """示例 2: 使用缓存装饰器"""
    print("\n" + "="*60)
    print("示例 2: 使用缓存装饰器提升性能")
    print("="*60)
    
    from infrastructure.di_container import initialize_container
    
    container = initialize_container()
    
    # 获取带缓存的术语服务
    cached_service = container.get('terminology_service_cached')
    
    # 第一次查询（会访问数据库）
    print("第一次查询...")
    result1 = await cached_service.find_match("测试", "en")
    
    # 第二次查询（从缓存返回）
    print("第二次查询（缓存命中）...")
    result2 = await cached_service.find_match("测试", "en")
    
    if result1 and result2:
        print(f"✅ 两次查询结果一致：{result1.translation}")


async def example_3_facade_pattern():
    """示例 3: 外观模式 - 简化 API"""
    print("\n" + "="*60)
    print("示例 3: 使用外观模式简化调用")
    print("="*60)
    
    # 这个示例需要实际的配置和 API 客户端
    # 这里只展示接口
    
    print("""
# 完整的外观模式使用示例：

from infrastructure.di_container import initialize_container
from openai import AsyncOpenAI

# 1. 创建 API 客户端
client = AsyncOpenAI(api_key="your-key", base_url="...")

# 2. 初始化容器（包含翻译服务）
container = initialize_container(
    api_client=client,
    terminology_manager=term_manager,  # 可选
    draft_prompt=DRAFT_PROMPT,
    review_prompt=REVIEW_PROMPT
)

# 3. 获取外观服务
facade = container.get('translation_facade')

# 4. 设置进度回调
facade.set_progress_callback(lambda c, t: print(f"进度：{c}/{t}"))

# 5. 翻译文件
result = await facade.translate_file(
    source_excel_path="source.xlsx",
    target_langs=["en", "ja"],
    output_excel_path="output.xlsx",
    concurrency_limit=10
)

# 6. 查看统计
stats = await facade.get_statistics("source.xlsx", ["en"])
print(stats)
    """)


async def example_4_custom_workflow():
    """示例 4: 自定义工作流"""
    print("\n" + "="*60)
    print("示例 4: 自定义工作流组装")
    print("="*60)
    
    from infrastructure.di_container import initialize_container
    from application.batch_processor import SequentialTaskProcessor
    from application.result_builder import TaskFactory, ResultBuilder
    
    container = initialize_container()
    
    # 获取协调器
    coordinator = container.get('workflow_coordinator')
    
    # 创建顺序处理器（便于调试）
    processor = SequentialTaskProcessor(
        task_executor=coordinator.execute_task,
        progress_callback=lambda c, t: print(f"处理中：{c}/{t}")
    )
    
    # 创建测试任务
    tasks = TaskFactory.from_list(
        texts=["测试文本 1", "测试文本 2", "测试文本 3"],
        target_lang="en",
        source_lang="zh"
    )
    
    print(f"创建了 {len(tasks)} 个测试任务")
    
    # 执行批量处理
    result = await processor.process_batch(tasks)
    
    # 输出结果
    ResultBuilder.print_summary(result)


async def example_5_adapter_pattern():
    """示例 5: 适配器模式 - 新旧代码共存"""
    print("\n" + "="*60)
    print("示例 5: 适配器模式连接新旧架构")
    print("="*60)
    
    print("""
# 适配器模式使用场景：

# 场景 1: 渐进式迁移
# 旧的 TerminologyManager 继续使用
from business_logic.terminology_adapter import TerminologyManagerAdapter

adapter = TerminologyManagerAdapter(old_term_manager)

# 新的领域服务可以使用适配器
from domain.terminology_service_impl import TerminologyDomainService

service = TerminologyDomainService(repo=adapter)

# 场景 2: 在 GUI 中同时使用新旧组件
# GUI 继续使用旧的 TerminologyManager
# 新的工作流使用适配后的服务

# 优势：
# - 保护现有投资
# - 平滑迁移
# - 降低风险
    """)


async def main():
    """运行所有示例"""
    print("\n" + "🚀 " * 20)
    print("新架构使用示例演示")
    print("🚀 " * 20)
    
    try:
        # 运行示例
        await example_1_basic_usage()
        await example_2_with_cache()
        await example_3_facade_pattern()
        await example_4_custom_workflow()
        await example_5_adapter_pattern()
        
    except Exception as e:
        print(f"\n❌ 示例执行失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
