# Google Ads API - 问题排查

> 本指南探讨了 Google Ads API 错误问题排查的最佳实践。

---

## 问题排查流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    问题排查流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 确保网络连接正常                                            │
│     │                                                           │
│     ▼                                                           │
│  2. 确定问题（查看错误响应）                                    │
│     │                                                           │
│     ▼                                                           │
│  3. 研究错误（查阅文档）                                        │
│     │                                                           │
│     ▼                                                           │
│  4. 找出原因（分析请求）                                        │
│     │                                                           │
│     ▼                                                           │
│  5. 解决问题（测试修复）                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. 确保网络连接正常

### 检查清单

- [ ] 确保可以访问 Google Ads API
- [ ] 验证凭据配置正确
- [ ] 确认使用的是正确凭据
- [ ] 检查请求和响应结构

### 常见认证错误示例

```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential.",
    "status": "UNAUTHENTICATED"
  }
}
```

**解决方案：**
1. 检查 OAuth2 令牌是否有效
2. 验证开发者令牌配置
3. 确认 `login-customer-id` 设置正确

---

## 2. 确定问题

### 错误响应结构

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

### 关键字段

| 字段 | 说明 |
|------|------|
| `errorCode` | Google Ads API 特有的错误代码 |
| `message` | 具体错误的说明 |
| `location.operationIndex` | 错误发生在第几个操作 |
| `location.fieldPathElements` | 错误发生在哪个字段 |

---

## 3. 研究错误

### 研究步骤

1. **查阅常见错误文档** - 参考本文档第 10 节
2. **查找错误字符串** - 在参考文档中搜索
3. **搜索支持渠道** - 论坛中查找相似问题
4. **访问帮助中心** - 获取验证和账号限制相关信息

### 资源链接

| 资源 | 用途 |
|------|------|
| [常见错误](./10-error-types.md) | 最常遇到的错误说明 |
| [错误代码参考](./11-understand-api-errors.md) | 完整的错误代码列表 |
| [系统限制](./08-system-limits.md) | 账号和资源限制 |
| [配额限制](./07-quotas-limits.md) | API 配额和速率限制 |

---

## 4. 找出原因

### 错误位置示例

```json
{
  "errors": [
    {
      "errorCode": {"criterionError": "CANNOT_ADD_CRITERIA_TYPE"},
      "message": "Criteria type can not be targeted.",
      "location": {
        "operationIndex": "0",
        "fieldPathElements": [
          {"fieldName": "keyword"}
        ]
      }
    }
  ]
}
```

### 调试技巧

1. **使用 IDE 调试器**
   - 设置断点
   - 逐行验证代码
   - 检查变量值

2. **验证请求匹配**
   - 广告系列名称是否正确
   - ID 是否有效
   - 字段掩码是否匹配更新

3. **检查字段可更新性**
   - 参考文档确认字段是否可更新
   - 检查更新时机是否正确

### 常见问题

| 问题 | 可能原因 |
|------|---------|
| `FIELD_NOT_FOUND` | 字段掩码包含无效字段 |
| `CANNOT_OPERATE_ON_REMOVED_ADGROUPAD` | 操作已删除的广告 |
| `DUPLICATE_CAMPAIGN_NAME` | 广告系列名称重复 |

---

## 5. 如何获取帮助

### 论坛提问模板

```
问题：[简要描述问题]

请求：
[移除敏感信息的 JSON 请求]

响应：
[移除敏感信息的 JSON 响应]

代码片段：
[相关代码片段]

RequestId：[请求 ID]

其他信息：
- 运行时/解释器版本
- 平台
- 客户端库版本
```

### 需要提供的信息

| 信息 | 说明 |
|------|------|
| JSON 请求/响应 | 移除敏感信息（开发者令牌、AuthToken） |
| 代码段 | 解释你的操作 |
| RequestId | 帮助 Google 团队定位你的请求 |
| 运行环境 | 运行时版本、平台等 |

---

## 6. 解决问题

### 测试修复

1. **在测试账号中验证**（推荐）
2. **生产环境测试**（仅当错误特定于生产数据时）

### 分享解决方案

如果你在论坛中发布了关于之前没有出现过的错误的问题，并且找到了解决方案，请考虑将解决方案添加到讨论帖中。

---

## 后续步骤

### 改进代码

1. **添加单元测试**
   - 提高代码质量
   - 加快新功能测试
   - 确保不破坏现有功能

2. **完善错误处理**
   - 记录完整的错误信息
   - 提供有意义的用户反馈
   - 实现自动重试机制

---

## Python 客户端错误处理示例

```python
import logging
from google.api_core import exceptions as gcp_exceptions
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GoogleAdsError(Exception):
    """Google Ads API 错误基类"""
    def __init__(self, message: str, request_id: str = None, details: Dict = None):
        self.message = message
        self.request_id = request_id
        self.details = details or {}
        super().__init__(self.message)


def handle_api_error(error: Exception, context: Dict[str, Any] = None) -> GoogleAdsError:
    """
    处理 Google Ads API 错误

    Args:
        error: 原始异常
        context: 额外上下文信息（客户 ID、操作等）

    Returns:
        格式化的 GoogleAdsError
    """
    context = context or {}

    # 记录完整错误信息
    logger.error(
        f"API 错误: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context
        }
    )

    # 提取请求 ID（如果可用）
    request_id = None
    if hasattr(error, 'metadata'):
        request_id = error.metadata.get('request-id')

    # 解析错误代码
    error_code = None
    error_message = str(error)

    if isinstance(error, gcp_exceptions.InvalidArgument):
        error_code = "INVALID_ARGUMENT"
        error_message = "请求参数无效，请检查输入"
    elif isinstance(error, gcp_exceptions.PermissionDenied):
        error_code = "PERMISSION_DENIED"
        error_message = "没有权限执行此操作"
    elif isinstance(error, gcp_exceptions.ResourceExhausted):
        error_code = "RESOURCE_EXHAUSTED"
        error_message = "API 配额已用尽，请稍后重试"
    elif isinstance(error, gcp_exceptions.NotFound):
        error_code = "NOT_FOUND"
        error_message = "请求的资源不存在"
    elif isinstance(error, gcp_exceptions.InternalServerError):
        error_code = "INTERNAL_ERROR"
        error_message = "服务器内部错误，请稍后重试"
    elif isinstance(error, gcp_exceptions.ServiceUnavailable):
        error_code = "UNAVAILABLE"
        error_message = "服务暂时不可用，请稍后重试"

    return GoogleAdsError(
        message=error_message,
        request_id=request_id,
        details={
            "error_code": error_code,
            "original_error": str(error),
            **context
        }
    )


def mutate_with_retry(client: GoogleAdsClient, customer_id: str,
                     operations: List, max_retries: int = 3) -> Dict:
    """
    带重试和错误处理的 mutate 操作

    Args:
        client: Google Ads 客户端
        customer_id: 客户 ID
        operations: 操作列表
        max_retries: 最大重试次数

    Returns:
        操作结果

    Raises:
        GoogleAdsError: 当所有重试失败时
    """
    service = client.get_service("CampaignService")

    for attempt in range(max_retries):
        try:
            response = service.mutate_campaigns(
                customer_id=customer_id,
                operations=operations
            )

            return {
                "success": True,
                "results": [
                    {"resource_name": r.resource_name}
                    for r in response.results
                ]
            }

        except gcp_exceptions.GoogleAPICallError as e:
            # 最后一次尝试失败
            if attempt == max_retries - 1:
                raise handle_api_error(e, context={
                    "customer_id": customer_id,
                    "operations_count": len(operations),
                    "attempt": attempt + 1
                })

            # 检查是否为可重试错误
            if isinstance(e, (gcp_exceptions.InternalServerError,
                             gcp_exceptions.ServiceUnavailable)):
                import time
                wait_time = 5 * (2 ** attempt)  # 指数退避
                logger.warning(
                    f"可重试错误，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries}): {e}"
                )
                time.sleep(wait_time)
                continue

            # 不可重试的错误，直接抛出
            raise handle_api_error(e, context={
                "customer_id": customer_id,
                "operations_count": len(operations)
            })
```

---

## FastAPI 集成示例

### 全局异常处理器

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

async def google_ads_exception_handler(
    request: Request,
    exc: GoogleAdsError
) -> JSONResponse:
    """Google Ads 错误处理器"""

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": exc.details.get("error_code"),
                "message": exc.message,
                "request_id": exc.request_id
            }
        }
    )
```

---

## 相关文档

- [最佳实践概览](./06-best-practices-overview.md)
- [错误类型](./10-error-types.md)
- [了解 API 错误](./11-understand-api-errors.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/troubleshooting?hl=zh-cn
**最后更新：** 2026-02-11
