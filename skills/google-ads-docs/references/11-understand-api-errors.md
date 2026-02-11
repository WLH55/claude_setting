# Google Ads API - 了解 API 错误

> 本文档详细说明了 Google Ads API 的错误模型和错误处理最佳实践。

---

## 概述

Google Ads API 遵循基于 gRPC 状态代码的标准 Google API 错误模型。

### Status 对象结构

每个导致错误的 API 响应都包含一个 `Status` 对象：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Status 对象结构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Status                                                         │
│  ├── code: int            # 数字错误代码                        │
│  ├── message: string      # 错误消息                            │
│  └── details: list        # 可选的额外错误详情                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 规范错误代码

| gRPC 代码 | HTTP 代码 | 枚举名称 | 说明 |
|-----------|-----------|----------|------|
| 0 | 200 | `OK` | 无错误；表示成功 |
| 1 | 499 | `CANCELLED` | 操作已取消（通常是被客户端取消） |
| 2 | 500 | `UNKNOWN` | 发生未知错误 |
| 3 | 400 | `INVALID_ARGUMENT` | 客户端指定的参数无效 |
| 4 | 504 | `DEADLINE_EXCEEDED` | 在操作完成之前截止期限已过 |
| 5 | 404 | `NOT_FOUND` | 找不到某个请求的实体 |
| 6 | 409 | `ALREADY_EXISTS` | 客户端尝试创建的实体已存在 |
| 7 | 403 | `PERMISSION_DENIED` | 调用者无权执行指定的操作 |
| 8 | 429 | `RESOURCE_EXHAUSTED` | 资源已用尽（例如配额超出） |
| 9 | 400 | `FAILED_PRECONDITION` | 操作被拒绝，系统未处于执行操作所需的状态 |
| 10 | 409 | `ABORTED` | 操作已中止（并发问题） |
| 11 | 400 | `OUT_OF_RANGE` | 尝试执行的操作已超出有效范围 |
| 12 | 501 | `UNIMPLEMENTED` | 相应操作未实现或不受支持 |
| 13 | 500 | `INTERNAL` | 发生内部错误 |
| 14 | 503 | `UNAVAILABLE` | 该服务目前不可用 |
| 15 | 500 | `DATA_LOSS` | 数据丢失或损坏且不可恢复 |
| 16 | 401 | `UNAUTHENTICATED` | 请求没有有效的身份验证凭据 |

---

## 错误详情结构

### GoogleAdsFailure 对象

```
┌─────────────────────────────────────────────────────────────────┐
│                  GoogleAdsFailure 对象                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GoogleAdsFailure                                               │
│  ├── request_id: string          # 请求的唯一 ID                │
│  └── errors: GoogleAdsError[]    # 错误列表                     │
│                                                                 │
│  GoogleAdsError                                                 │
│  ├── errorCode:                  # Google Ads API 特有的错误代码 │
│  │   ├── errorType: "ErrorCodeName"                            │
│  │   └── ...                                                   │
│  ├── message: string             # 具体错误的说明               │
│  ├── trigger:                    # 导致错误的值                 │
│  ├── location:                   # 错误发生在请求中的位置        │
│  │   ├── operationIndex: int                                    │
│  │   └── fieldPathElements: []                                 │
│  └── details:                    # 其他错误详情                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 错误示例

```json
{
  "errors": [
    {
      "errorCode": {
        "fieldMaskError": "FIELD_NOT_FOUND"
      },
      "message": "The field mask contained an invalid field: 'keyword/matchtype'.",
      "location": {
        "operationIndex": "1"
      }
    }
  ]
}
```

---

## 查找错误详情的方式

### 1. 标准 API 调用和流式 API 调用

错误作为 gRPC 响应标头中的尾部元数据返回。

### 2. 部分失败

错误返回在响应的 `partial_failure_error` 字段中。

```python
# 启用部分失败
response = service.mutate(
    customer_id=customer_id,
    operations=operations,
    partial_failure=True  # 启用部分失败
)

# 检查部分失败错误
if response.partial_failure_error:
    for error in response.partial_failure_error.errors:
        print(f"操作 {error.location.operation_index} 失败: {error.message}")
```

### 3. 批处理作业

在作业完成后检索批处理作业结果。

---

## 请求 ID 的位置

请求 ID 用于唯一标识每个请求，对于调试非常重要。

| 位置 | 说明 |
|------|------|
| `GoogleAdsFailure` 对象 | 在 `request_id` 字段中 |
| gRPC 响应尾部元数据 | 作为元数据返回 |
| HTTP 响应标头 | 在 `request-id` 标头中 |
| `SearchGoogleAdsStreamResponse` | 在响应消息中 |

### 获取请求 ID 示例

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage("google-ads.yaml")

# 发起请求
response = service.mutate_campaigns(
    customer_id=customer_id,
    operations=operations
)

# 获取请求 ID
request_id = response.metadata.get("request-id")
print(f"请求 ID: {request_id}")
```

---

## 错误处理最佳实践

### 1. 检查错误详情

始终解析 `Status` 对象的 `details` 字段。

```python
def handle_response(response):
    """处理响应并检查错误详情"""

    # 检查是否有部分失败
    if hasattr(response, 'partial_failure_error') and response.partial_failure_error:
        for error in response.partial_failure_error.errors:
            error_code = error.error_code
            field_path = error.location.field_path_elements
            operation_index = error.location.operation_index

            logger.error(
                f"操作 {operation_index} 失败: {error.message}",
                extra={
                    "error_code": str(error_code),
                    "field_path": str(field_path)
                }
            )
```

### 2. 区分客户端和服务器错误

```
┌─────────────────────────────────────────────────────────────────┐
│                  客户端错误 vs 服务器错误                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  客户端错误（需要更改请求）：                                   │
│  ├── INVALID_ARGUMENT      # 参数无效                           │
│  ├── NOT_FOUND             # 资源不存在                         │
│  ├── PERMISSION_DENIED     # 权限不足                           │
│  ├── UNAUTHENTICATED       # 未认证                             │
│  └── ALREADY_EXISTS        # 资源已存在                         │
│                                                                 │
│  服务器错误（可以重试）：                                       │
│  ├── UNAVAILABLE           # 服务不可用                         │
│  ├── INTERNAL              # 内部错误                           │
│  └── DEADLINE_EXCEEDED     # 请求超时                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. 实现重试策略

**仅针对临时服务器错误重试：**

```python
from google.api_core import exceptions as gcp_exceptions
import time

SERVER_ERROR_CODES = [
    gcp_exceptions.StatusCode.UNAVAILABLE,
    gcp_exceptions.StatusCode.INTERNAL,
    gcp_exceptions.StatusCode.DEADLINE_EXCEEDED,
]

def should_retry(error: Exception) -> bool:
    """判断错误是否可以重试"""
    if isinstance(error, gcp_exceptions.GoogleAPICallError):
        return error.grpc_status_code in SERVER_ERROR_CODES
    return False


def retry_with_backoff(func, max_retries=3, base_delay=1):
    """使用指数退避重试"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if not should_retry(e) or attempt == max_retries - 1:
                raise

            # 指数退避 + 抖动
            delay = base_delay * (2 ** attempt)
            jitter = delay * 0.1 * (hash(time.time()) % 10) / 10
            time.sleep(delay + jitter)

    raise Exception("最大重试次数已达到")
```

### 4. 完整记录

记录完整的错误响应，包括请求 ID：

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_error_response(error: Exception, request_data: dict):
    """记录完整的错误响应"""

    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_data": request_data,
    }

    # 添加请求 ID（如果可用）
    if hasattr(error, 'metadata'):
        error_info["request_id"] = error.metadata.get('request-id')

    # 添加 gRPC 状态码（如果可用）
    if isinstance(error, gcp_exceptions.GoogleAPICallError):
        error_info["grpc_status_code"] = error.grpc_status_code.name

    logger.error(f"API 错误: {json.dumps(error_info, ensure_ascii=False)}")
```

### 5. 提供用户反馈

根据具体错误代码向用户提供清晰的反馈：

```python
ERROR_USER_MESSAGES = {
    "INVALID_ARGUMENT": "输入参数无效，请检查后重试",
    "PERMISSION_DENIED": "您没有权限执行此操作",
    "NOT_FOUND": "请求的资源不存在",
    "RESOURCE_EXHAUSTED": "API 配额已用尽，请稍后重试",
    "UNAVAILABLE": "服务暂时不可用，请稍后重试",
    "UNAUTHENTICATED": "授权已失效，请重新登录",
}


def get_user_message(error_code: str) -> str:
    """获取用户友好的错误消息"""
    return ERROR_USER_MESSAGES.get(
        error_code,
        "操作失败，请稍后重试或联系支持"
    )
```

---

## Python 客户端错误处理示例

```python
from google.ads.googleads.client import GoogleAdsClient
from google.api_core import exceptions as gcp_exceptions
from typing import Callable, Any, TypeVar
import functools
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def handle_google_ads_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Google Ads API 错误处理装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)

        except gcp_exceptions.InvalidArgument as e:
            logger.error(f"无效参数: {e}")
            raise ValueError("输入参数无效，请检查后重试") from e

        except gcp_exceptions.PermissionDenied as e:
            logger.error(f"权限拒绝: {e}")
            raise PermissionError("您没有权限执行此操作") from e

        except gcp_exceptions.NotFound as e:
            logger.error(f"资源不存在: {e}")
            raise ValueError("请求的资源不存在") from e

        except gcp_exceptions.ResourceExhausted as e:
            logger.error(f"资源耗尽: {e}")
            raise RuntimeError("API 配额已用尽，请稍后重试") from e

        except gcp_exceptions.Unauthenticated as e:
            logger.error(f"未认证: {e}")
            raise PermissionError("授权已失效，请重新登录") from e

        except (gcp_exceptions.InternalServerError,
                gcp_exceptions.ServiceUnavailable) as e:
            logger.error(f"服务错误: {e}")
            raise ConnectionError("服务暂时不可用，请稍后重试") from e

        except gcp_exceptions.GoogleAPICallError as e:
            logger.error(f"API 错误: {e}")
            raise RuntimeError(f"API 调用失败: {str(e)}") from e

    return wrapper


# 使用示例
@handle_google_ads_errors
def create_campaign(client: GoogleAdsClient, customer_id: str, campaign_data: dict) -> str:
    """创建广告系列"""
    service = client.get_service("CampaignService")

    operation = client.get_type("CampaignOperation")
    campaign = operation.create
    campaign.name = campaign_data["name"]
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH

    response = service.mutate_campaigns(
        customer_id=customer_id,
        operations=[operation]
    )

    return response.results[0].resource_name
```

---

## 相关文档

- [最佳实践概览](./06-best-practices-overview.md)
- [错误类型](./10-error-types.md)
- [问题排查](./09-troubleshooting.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/understand-api-errors?hl=zh-cn
**最后更新：** 2026-02-11
