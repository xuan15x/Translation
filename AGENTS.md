# AGENTS.md — 翻译工具开发项目

## 项目信息
- **名称**: AI 智能翻译工作台 v3.3
- **路径**: `/home/admin/openclaw/workspace/translation-tool/`
- **API**: DeepSeek（唯一提供商）
- **模型**: deepseek-v4-pro（默认开启思考模式）

## 多 Agent 架构

### main — 翻译管道核心开发
**职责**: service/api_stage_base.py、思考模式集成、DeepSeek API 调用链路、双阶段翻译编排

### infra — 基础设施维护
**职责**: infrastructure/models/（config/validators/context）、config/、cache/、database/、依赖注入

### qa — 测试与质量
**职责**: 全模块导入验证、API mock 测试、validator 单元测试、性能基准测试

## 关键规则

1. **API 提供商唯一**: 仅 DeepSeek，AsyncOpenAI 兼容协议
2. **思考模式**: enable_thinking_mode=true 时跳过 temperature/top_p
3. **配置一致性**: config.json 与 Config dataclass 必须字段完全一致（当前状态: ✅）
4. **禁止扫描**: .venv/ 目录
5. **修改后验证**: 改 Config 类 → 立即用 `python -c "from infrastructure.models.config import Config; Config(api_key='test')"` 自测

## 配置字段清单 (69 字段)

参见: `config/config.json` 和 `infrastructure/models/config.py`
config.py`
