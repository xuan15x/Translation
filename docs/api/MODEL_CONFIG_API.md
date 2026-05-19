# Model Config API 参考

**API 类型**: OpenAI 兼容（仅 DeepSeek）

## 代码结构

```
service/api_provider.py
  └── create_api_client()        # 创建 API 客户端

service/api_stage_base.py
  ├── APIStageBase               # 抽象基类
  ├── APIDraftStage              # 初译阶段
  └── APIReviewStage             # 校对阶段

service/api_stages.py
  ├── APIDraftStage (别名)       # 从 base 导入
  ├── APIReviewStage (别名)      # 从 base 导入
  └── LocalHitStage              # 本地命中阶段
```

## API 客户端初始化

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com"
)
```

## 阶段接口

```python
class APIStageBase(ABC):
    async def execute(self, context: TaskContext) -> StageResult:
        ...
```

## 配置获取方法

```python
class Config:
    def get_draft_model_name(self) -> str
    def get_draft_temperature(self) -> float
    def get_draft_top_p(self) -> float
    def get_draft_timeout(self) -> int
    def get_draft_max_tokens(self) -> int
    
    def get_review_model_name(self) -> str
    def get_review_temperature(self) -> float
    def get_review_top_p(self) -> float
    def get_review_timeout(self) -> int
    def get_review_max_tokens(self) -> int
```

## 阶段结果格式

```json
{
  "Trans": "翻译结果文本",
  "Reason": "修改原因（仅校对阶段）"
}
```
