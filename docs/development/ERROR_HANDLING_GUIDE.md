# 统一错误处理指南

**版本**: 1.0  
**创建日期**: 2026-03-31  
**适用范围**: 全项目所有模块

---

## 📋 目录

1. [概述](#概述)
2. [异常体系结构](#异常体系结构)
3. [异常分类与使用场景](#异常分类与使用场景)
4. [错误处理器](#错误处理器)
5. [最佳实践](#最佳实践)
6. [迁移指南](#迁移指南)
7. [示例代码](#示例代码)

---

## 概述

### 目标

建立统一的错误处理标准，提升代码质量和可维护性：

- ✅ **标准化**: 所有异常继承自统一基类
- ✅ **可追溯**: 包含完整的错误上下文信息
- ✅ **易调试**: 提供详细的错误报告和日志
- ✅ **用户友好**: 区分内部错误和用户友好消息

### 核心组件

```python
# 1. 异常类层次结构
TranslationBaseError (基类)
├── APIError
│   ├── RateLimitError
│   ├── APITimeoutError
│   └── AuthenticationError
├── ConfigError
│   └── ValidationError
├── FileError
│   ├── FileNotFoundError
│   └── IOError
├── DataError
│   └── ParsingError
├── TranslationError
├── TerminologyError
├── WorkflowError
├── SystemError
└── NetworkError

# 2. 错误处理器
ErrorHandler
├── handle_error()      # 标准化异常
├── log_error()         # 记录日志
└── get_user_friendly_message()  # 用户友好消息

# 3. 便捷函数
- raise_error()  # 快速抛出指定类型异常
- safe_execute()  # 安全执行函数
```

---

## 异常体系结构

### 基类：TranslationBaseError

```python
from infrastructure.exceptions import TranslationBaseError, ErrorCategory

class TranslationBaseError(Exception):
    """
    属性:
        message: 错误消息
        category: 错误分类 (ErrorCategory 枚举)
        error_code: 错误代码 (如 'API_001')
        details: 详细错误信息 (字典)
        original_exception: 原始异常 (用于包装)
        error_report: 生成的错误报告 (字典)
    
    方法:
        to_dict(): 转换为字典格式
        __str__(): 字符串表示
    """
```

### 使用示例

```python
# 基础用法
try:
    result = api_call()
except Exception as e:
    error = TranslationBaseError(
        message="API 调用失败",
        category=ErrorCategory.API_ERROR,
        error_code="API_CUSTOM_001",
        details={'endpoint': '/translate'},
        original_exception=e
    )
    ErrorHandler.log_error(error, logger)
    raise error

# 或使用子类
try:
    validate_config(config)
except ValueError as e:
    raise ValidationError(
        message="配置验证失败",
        field_name='temperature',
        details={'value': config.temperature}
    )
```

---

## 异常分类与使用场景

### 1. API 相关异常

#### APIError - API 调用失败
```python
from infrastructure.exceptions import APIError

raise APIError(
    "API 响应异常",
    details={'status_code': 500, 'endpoint': '/v1/translate'}
)
```

#### RateLimitError - 速率限制
```python
from infrastructure.exceptions import RateLimitError

raise RateLimitError(
    "请求频率超限",
    details={'retry_after': 60}  # 建议重试时间
)
```

#### APITimeoutError - 超时
```python
from infrastructure.exceptions import APITimeoutError

raise APITimeoutError(
    "请求超时 (30s)",
    details={'timeout': 30, 'operation': 'translate'}
)
```

#### AuthenticationError - 认证失败
```python
from infrastructure.exceptions import AuthenticationError

raise AuthenticationError(
    "API 密钥无效",
    details={'env_var': 'DEEPSEEK_API_KEY'}
)
```

### 2. 配置相关异常

#### ConfigError - 配置错误
```python
from infrastructure.exceptions import ConfigError

raise ConfigError(
    "配置文件格式错误",
    details={'file': 'config.json', 'format': 'json'}
)
```

#### ValidationError - 验证失败
```python
from infrastructure.exceptions import ValidationError

raise ValidationError(
    "参数超出有效范围",
    field_name='temperature',  # 字段名
    details={'value': 2.5, 'valid_range': '0-2'}
)
```

### 3. 文件操作异常

#### FileError - 文件操作失败
```python
from infrastructure.exceptions import FileError

raise FileError(
    "无法读取文件",
    file_path='/path/to/file.xlsx'
)
```

#### FileNotFoundError - 文件未找到
```python
from infrastructure.exceptions import FileNotFoundError

raise FileNotFoundError(
    "配置文件不存在",
    file_path='config/config.json'
)
```

#### IOError - IO 错误
```python
from infrastructure.exceptions import IOError

raise IOError(
    "写入文件失败",
    file_path='output/result.xlsx'
)
```

### 4. 数据处理异常

#### DataError - 数据错误
```python
from infrastructure.exceptions import DataError

raise DataError(
    "数据格式不正确",
    details={'expected': 'dict', 'got': 'list'}
)
```

#### ParsingError - 解析失败
```python
from infrastructure.exceptions import ParsingError

raise ParsingError(
    "JSON 解析失败",
    data_format='json'
)
```

### 5. 业务逻辑异常

#### TranslationError - 翻译错误
```python
from infrastructure.exceptions import TranslationError

raise TranslationError(
    "翻译结果为空",
    task_id='task_123'
)
```

#### TerminologyError - 术语库错误
```python
from infrastructure.exceptions import TerminologyError

raise TerminologyError(
    "术语库加载失败",
    term_path='terms.xlsx'
)
```

#### WorkflowError - 工作流错误
```python
from infrastructure.exceptions import WorkflowError

raise WorkflowError(
    "阶段执行失败",
    stage='review'
)
```

### 6. 系统异常

#### SystemError - 系统错误
```python
from infrastructure.exceptions import SystemError

raise SystemError(
    "未知系统错误",
    details={'component': 'cache_manager'}
)
```

#### NetworkError - 网络错误
```python
from infrastructure.exceptions import NetworkError

raise NetworkError(
    "网络连接失败",
    details={'host': 'api.deepseek.com'}
)
```

---

## 错误处理器

### ErrorHandler.handle_error()

将任意异常转换为标准异常：

```python
from infrastructure.exceptions import ErrorHandler

try:
    risky_operation()
except Exception as e:
    standardized_error = ErrorHandler.handle_error(
        e,
        context={'operation': 'risky_op', 'user': 'admin'}
    )
    ErrorHandler.log_error(standardized_error, logger)
    raise standardized_error
```

### ErrorHandler.log_error()

记录标准化错误日志：

```python
# 自动根据错误类别选择日志级别
ErrorHandler.log_error(error, logger)

# 输出示例:
# ❌ 错误 [API_001] | 分类：api_error | 消息：API 调用失败 | 详情：{'endpoint': '/v1'}
```

### ErrorHandler.get_user_friendly_message()

获取用户友好的错误消息：

```python
user_message = ErrorHandler.get_user_friendly_message(error)
# "API 调用失败：API 响应异常"

# 适用于 GUI 提示或用户通知
show_message_to_user(user_message)
```

---

## 最佳实践

### 1. ✅ 何时抛出自定义异常

```python
# ✅ 推荐：在以下情况使用自定义异常
# - 验证失败
if temperature < 0 or temperature > 2:
    raise ValidationError(
        "temperature 超出范围",
        field_name='temperature',
        details={'value': temperature, 'range': '0-2'}
    )

# - 业务规则违反
if not api_key:
    raise AuthenticationError("API 密钥不能为空")

# - 资源不可用
if not os.path.exists(file_path):
    raise FileNotFoundError("文件不存在", file_path=file_path)
```

### 2. ✅ 何时包装原始异常

```python
# ✅ 推荐：包装第三方库异常
try:
    response = requests.post(url, timeout=30)
except requests.Timeout as e:
    raise APITimeoutError(
        "API 请求超时",
        original_exception=e,
        details={'url': url, 'timeout': 30}
    )
except requests.RequestException as e:
    raise NetworkError(
        "网络请求失败",
        original_exception=e,
        details={'url': url}
    )
```

### 3. ❌ 避免的做法

```python
# ❌ 禁止：空异常处理
try:
    operation()
except Exception:
    pass  # 丢失错误信息！

# ✅ 正确做法
try:
    operation()
except Exception as e:
    error = ErrorHandler.handle_error(e)
    logger.error(f"操作失败：{error.message}")
    raise
```

```python
# ❌ 禁止：过度泛化的异常
try:
    specific_operation()
except Exception as e:  # 捕获所有异常
    raise SystemError("出错了")  # 信息不明确

# ✅ 正确做法
try:
    specific_operation()
except FileNotFoundError:
    raise  # 让上层处理
except ValueError as e:
    raise ValidationError(f"参数错误：{e}")
```

```python
# ❌ 禁止：混用异常类型
def process():
    if error1:
        raise ValueError("错误 1")
    if error2:
        raise Exception("错误 2")

# ✅ 正确做法
def process():
    if error1:
        raise ValidationError("错误 1")
    if error2:
        raise SystemError("错误 2")
```

### 4. ✅ 添加丰富的上下文信息

```python
# ✅ 推荐：提供完整上下文
raise TranslationError(
    message="翻译结果为空",
    task_id=ctx.idx,
    details={
        'source_text': ctx.source_text[:50],
        'target_lang': ctx.target_lang,
        'attempt_count': retry_count,
        'model_used': config.model_name
    }
)
```

### 5. ✅ 使用便捷函数

```python
from infrastructure.exceptions import raise_error, ErrorCategory

# 快速抛出指定类型异常
raise_error(
    message="配置验证失败",
    category=ErrorCategory.VALIDATION_ERROR,
    error_code="CFG_CUSTOM_001",
    details={'field': 'temperature'}
)

# 安全执行函数（返回默认值）
result = safe_execute(risky_function, arg1, arg2, default=None)
```

---

## 迁移指南

### 从旧异常迁移到新异常

#### 1. ValueError → ValidationError

```python
# 旧代码
if value < 0:
    raise ValueError("值必须大于 0")

# 新代码
if value < 0:
    raise ValidationError(
        "值必须大于 0",
        field_name='value',
        details={'current_value': value}
    )
```

#### 2. FileNotFoundError → 新版本

```python
# 旧代码
if not os.path.exists(path):
    raise FileNotFoundError(f"文件不存在：{path}")

# 新代码
if not os.path.exists(path):
    raise FileNotFoundError(
        "文件不存在",
        file_path=path
    )
```

#### 3. RuntimeError → 具体异常

```python
# 旧代码
if not api_key:
    raise RuntimeError("API 密钥缺失")

# 新代码
if not api_key:
    raise AuthenticationError(
        "API 密钥缺失",
        details={'env_var': 'DEEPSEEK_API_KEY'}
    )
```

#### 4. Exception → 分类异常

```python
# 旧代码
try:
    api_call()
except Exception as e:
    raise Exception(f"API 失败：{e}")

# 新代码
try:
    api_call()
except Exception as e:
    error = ErrorHandler.handle_error(e)
    ErrorHandler.log_error(error, logger)
    raise
```

---

## 示例代码

### 完整示例：API 调用错误处理

```python
from infrastructure.exceptions import (
    APIError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    ErrorHandler
)
import logging

logger = logging.getLogger(__name__)

async def call_translation_api(text: str, target_lang: str) -> str:
    """
    调用翻译 API
    
    Raises:
        APITimeoutError: 请求超时
        RateLimitError: 频率超限
        AuthenticationError: 认证失败
        APIError: 其他 API 错误
    """
    try:
        response = await client.translate(
            text=text,
            target_language=target_lang,
            timeout=30
        )
        
        if response.status == 401:
            raise AuthenticationError(
                "API 认证失败",
                details={'status': 401}
            )
        
        if response.status == 429:
            raise RateLimitError(
                "请求频率超限",
                details={'retry_after': response.headers.get('Retry-After', 60)}
            )
        
        if response.status != 200:
            raise APIError(
                f"API 返回错误状态：{response.status}",
                details={'status': response.status, 'body': response.body}
            )
        
        return response.translation
        
    except asyncio.TimeoutError as e:
        raise APITimeoutError(
            "API 请求超时 (30s)",
            original_exception=e,
            details={'timeout': 30, 'text_length': len(text)}
        )
        
    except Exception as e:
        # 包装为通用 API 错误
        error = ErrorHandler.handle_error(
            e,
            context={'operation': 'translate', 'text': text[:50]}
        )
        ErrorHandler.log_error(error, logger)
        raise error
```

### 完整示例：配置文件加载

```python
from infrastructure.exceptions import (
    FileNotFoundError,
    ParsingError,
    ValidationError,
    ErrorHandler
)
import json
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """
    加载配置文件
    
    Raises:
        FileNotFoundError: 文件不存在
        ParsingError: 格式解析失败
        ValidationError: 验证失败
    """
    # 检查文件存在性
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            "配置文件不存在",
            file_path=config_path
        )
    
    try:
        # 读取文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必要字段
        if 'api_key' not in config:
            raise ValidationError(
                "配置文件缺少必要字段",
                field_name='api_key'
            )
        
        if 'base_url' not in config:
            raise ValidationError(
                "配置文件缺少必要字段",
                field_name='base_url'
            )
        
        return config
        
    except json.JSONDecodeError as e:
        raise ParsingError(
            "配置文件 JSON 格式错误",
            data_format='json',
            original_exception=e,
            details={'line': e.lineno, 'column': e.colno}
        )
        
    except Exception as e:
        error = ErrorHandler.handle_error(
            e,
            context={'operation': 'load_config', 'file': config_path}
        )
        ErrorHandler.log_error(error, logger)
        raise
```

### 完整示例：工作流错误处理

```python
from infrastructure.exceptions import (
    WorkflowError,
    TranslationError,
    TerminologyError,
    ErrorHandler
)
import logging

logger = logging.getLogger(__name__)

async def execute_workflow(task_context):
    """
    执行翻译工作流
    
    Raises:
        WorkflowError: 工作流执行失败
        TranslationError: 翻译阶段错误
        TerminologyError: 术语库错误
    """
    try:
        # 阶段 1: 术语匹配
        try:
            term_match = await match_terminology(task_context)
        except Exception as e:
            raise TerminologyError(
                "术语匹配失败",
                term_path='terms.xlsx',
                original_exception=e
            )
        
        # 阶段 2: 翻译
        try:
            translation = await translate_draft(task_context)
        except Exception as e:
            raise TranslationError(
                "翻译阶段失败",
                task_id=task_context.idx,
                original_exception=e
            )
        
        # 阶段 3: 校对
        try:
            final_result = await review_translation(translation)
        except Exception as e:
            raise TranslationError(
                "校对阶段失败",
                task_id=task_context.idx,
                original_exception=e
            )
        
        return final_result
        
    except Exception as e:
        # 工作流级别错误处理
        error = ErrorHandler.handle_error(
            e,
            context={
                'stage': 'workflow_execution',
                'task_idx': task_context.idx,
                'source_text': task_context.source_text[:50]
            }
        )
        ErrorHandler.log_error(error, logger)
        raise WorkflowError(
            "工作流执行失败",
            stage='execution',
            original_exception=e,
            details={'task_id': task_context.idx}
        )
```

---

## 附录：错误代码规范

### 错误代码格式

```
{CATEGORY}_{NUMBER}

例如:
- API_001: API 通用错误
- API_002: 速率限制
- CFG_001: 配置通用错误
- CFG_002: 验证失败
- FILE_001: 文件通用错误
- FILE_002: 文件未找到
- TRANS_001: 翻译通用错误
```

### 错误分类枚举

```python
class ErrorCategory(Enum):
    API_ERROR = "api_error"              # API_001 ~ API_099
    RATE_LIMIT_ERROR = "rate_limit_error"  # 已并入 API_ERROR
    TIMEOUT_ERROR = "timeout_error"       # 已并入 API_ERROR
    AUTHENTICATION_ERROR = "authentication_error"  # 已并入 API_ERROR
    
    CONFIG_ERROR = "config_error"        # CFG_001 ~ CFG_099
    VALIDATION_ERROR = "validation_error"  # 已并入 CONFIG_ERROR
    
    FILE_ERROR = "file_error"            # FILE_001 ~ FILE_099
    FILE_NOT_FOUND_ERROR = "file_not_found_error"  # 已并入 FILE_ERROR
    IO_ERROR = "io_error"                # 已并入 FILE_ERROR
    
    DATA_ERROR = "data_error"            # DATA_001 ~ DATA_099
    PARSING_ERROR = "parsing_error"      # 已并入 DATA_ERROR
    
    TRANSLATION_ERROR = "translation_error"  # TRANS_001 ~ TRANS_099
    TERMINOLOGY_ERROR = "terminology_error"  # TERM_001 ~ TERM_099
    WORKFLOW_ERROR = "workflow_error"    # FLOW_001 ~ FLOW_099
    
    SYSTEM_ERROR = "system_error"        # SYS_001 ~ SYS_099
    NETWORK_ERROR = "network_error"      # NET_001 ~ NET_099
    UNKNOWN_ERROR = "unknown_error"      # 未分类错误
```

---

**维护者**: Development Team  
**最后更新**: 2026-03-31  
**下次审查**: 2026-04-30
