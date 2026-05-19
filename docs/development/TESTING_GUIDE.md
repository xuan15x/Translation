# 测试指南

## 测试框架
- **pytest**（核心框架）
- **pytest-cov**（覆盖率报告）
- **pytest-asyncio**（异步测试，`pytest.ini` 中 `asyncio_mode = auto`）

## 快速开始

```bash
cd translation-tool
source .venv/bin/activate

# 运行所有测试
python -m pytest tests/ -v

# 运行带覆盖率报告
python -m pytest tests/ --cov=. --cov-report=term

# 运行指定测试文件
python -m pytest tests/test_integration.py -v

# 仅显示失败
python -m pytest tests/ -q --tb=short
```

## CI 脚本

```bash
bash ci.sh            # 基础检查（导入 + 测试 + ≥40% 覆盖）
bash ci.sh --full     # 全量检查（含 lint）
```

## 测试结构

```
tests/
├── conftest.py                    # 共享 fixtures
├── test_module_imports.py         # 全模块导入验证
├── test_config_consistency.py     # config.json ↔ Config 字段一致性
├── test_config_validators.py      # Config 验证器
├── test_integration.py            # 端到端集成（完整翻译管线）
├── test_boundaries.py             # 边界/异常测试
├── test_api_provider.py           # API 客户端创建
├── test_api_stage_base.py         # API 阶段基类
├── test_api_stage_full.py         # API 阶段完整流程
├── test_api_stage_multilingual.py # 多语言 API 阶段
├── test_application.py            # 应用层
├── test_di_container.py           # 依赖注入容器
├── test_domain_models.py          # 领域模型
├── test_config_persistence.py     # 配置持久化
├── test_health_check.py           # 健康检查
├── test_multilingual_service.py   # 多语言服务
├── test_repositories.py           # 术语仓储
├── test_terminology_service.py    # 术语服务
├── test_translation_service_impl.py # 翻译服务实现
└── test_utils.py                  # 工具函数
```

## 编写新测试

```python
import pytest

# 异步测试 — asyncio_mode=auto，直接 async def
async def test_my_feature():
    result = await some_async_function()
    assert result.success

# 使用 conftest fixtures
def test_with_config(config_json, valid_config_dict):
    assert config_json["model_name"] == "deepseek-v4-pro"
```

## 覆盖率目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 总覆盖率 | 51% | ≥50% ✅ |
| 测试数量 | 285 | — |
| 测试文件 | 19 | — |
