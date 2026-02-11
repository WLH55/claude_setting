# Google Ads API - 错误类型

> 本文档介绍了 Google Ads API 中常见错误类型的分类和处理策略。

---

## 错误分类概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    错误类型分类                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 身份验证错误 (Authentication Errors)                        │
│     └── OAuth2 令牌失效、权限被撤销                              │
│                                                                 │
│  2. 可重试错误 (Retryable Errors)                               │
│     └── 临时性故障、服务暂时不可用                               │
│                                                                 │
│  3. 验证错误 (Validation Errors)                                │
│     └── 输入参数无效、违反政策                                   │
│                                                                 │
│  4. 同步相关错误 (Sync-related Errors)                          │
│     └── 本地数据与 API 不同步                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. 身份验证错误

### 描述

身份验证错误是指应用是否已获得用户授权代表其访问 Google Ads。由 OAuth2 流程生成的凭据进行管理。

### 常见原因

| 原因 | 说明 |
|------|------|
| 令牌被撤销 | 用户撤销了应用的访问权限 |
| 令牌过期 | OAuth2 访问令牌已过期（通常 1 小时） |
| 无效凭据 | 使用了错误的客户端 ID 或密钥 |

### 常见错误代码

| 错误代码 | 说明 |
|---------|------|
| `AuthenticationError.OAUTH_TOKEN_REVOKED` | OAuth2 令牌已被撤销 |
| `AuthenticationError.USER_PERMISSION_DENIED` | 用户权限不足 |

### 处理策略

**用户发起的请求：**
```python
try:
    result = api_call()
except AuthenticationError:
    # 提示用户重新授权
    return redirect("/oauth2/authorize")
```

**后端发起的请求：**
```python
try:
    result = api_call()
except AuthenticationError:
    # 记录错误，通知管理员
    logger.error(f"认证失败: {customer_id}")
    send_notification_to_admin(customer_id)
```

---

## 2. 可重试错误

### 描述

表示临时性问题，通过短暂暂停后重试请求可能会解决。

### 常见错误代码

| 错误代码 | 说明 |
|---------|------|
| `INTERNAL_ERROR` | Google Ads API 内部错误 |
| `UNAVAILABLE` | 服务暂时不可用 |
| `DEADLINE_EXCEEDED` | 请求超时 |

### 处理策略

**指数退避算法：**

```
第 1 次重试：等待 5 秒
第 2 次重试：等待 10 秒
第 3 次重试：等待 20 秒
...
```

**实现示例：**

```python
import time
from google.api_core import exceptions as gcp_exceptions

def retry_with_backoff(func, max_retries=3):
    """使用指数退避重试"""
    for attempt in range(max_retries):
        try:
            return func()
        except (gcp_exceptions.InternalServerError,
                gcp_exceptions.ServiceUnavailable) as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 5 * (2 ** attempt)
            time.sleep(wait_time)

    raise Exception("最大重试次数已达到")
```

### 用户界面策略

| 策略 | 说明 |
|------|------|
| 立即显示错误 | 在 UI 中显示错误，提供重试按钮 |
| 自动重试 | 先自动重试，达到最大次数后再显示错误 |
| 显示进度 | 显示"正在重试..."的进度提示 |

---

## 3. 验证错误

### 描述

表示操作的输入不可接受。

### 常见错误代码

| 错误类型 | 说明 |
|---------|------|
| `PolicyViolationError` | 违反 Google Ads 政策 |
| `DateError` | 日期格式无效 |
| `DateRangeError` | 日期范围无效 |
| `StringLengthError` | 字符串长度超出限制 |
| `UrlFieldError` | URL 格式无效 |

### 处理策略

**前端验证（推荐）：**

```python
def validate_campaign_input(name: str, budget: float) -> Dict[str, str]:
    """验证广告系列输入"""
    errors = {}

    if not name or len(name) > 256:
        errors["name"] = "名称不能为空且不能超过 256 个字符"

    if budget <= 0:
        errors["budget"] = "预算必须大于 0"

    return errors
```

**后端处理：**

```python
try:
    result = create_campaign(data)
except PolicyViolationError as e:
    return {"error": "违反广告政策", "details": e.message}
except StringLengthError as e:
    return {"error": "输入过长", "details": e.message}
except DateError as e:
    return {"error": "日期格式错误", "details": e.message}
```

---

## 4. 同步相关错误

### 描述

当应用的本地数据库与 Google Ads 中的实际对象不同步时发生。

### 常见错误代码

| 错误代码 | 说明 |
|---------|------|
| `DUPLICATE_CAMPAIGN_NAME` | 广告系列名称重复 |
| `DUPLICATE_ADGROUP_NAME` | 广告组名称重复 |
| `AD_NOT_UNDER_ADGROUP` | 广告不属于指定的广告组 |
| `CANNOT_OPERATE_ON_REMOVED_ADGROUPAD` | 无法操作已删除的广告 |

### 发生场景

```
┌─────────────────────────────────────────────────────────────────┐
│                    同步错误场景                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户在 Google Ads 界面中：                                     │
│  1. 删除了一个广告组                                            │
│  2. 重命名了广告系列                                            │
│                                                                 │
│  但应用不知道这些更改：                                         │
│  • 本地数据库仍然显示旧数据                                     │
│  • API 调用失败，返回同步错误                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 处理策略

**用户发起的请求：**

```python
try:
    result = update_ad(ad_data)
except SyncRelatedError as e:
    # 1. 提示用户可能存在同步问题
    # 2. 立即启动同步作业
    sync_account(customer_id)
    # 3. 提示用户刷新 UI
    return {"message": "数据已更新，请刷新页面重试"}
```

**后端发起的请求：**

```python
def handle_sync_error(error, customer_id, operation):
    """处理同步错误"""

    # 自动增量修正本地数据库
    if error.error_code == "CANNOT_OPERATE_ON_REMOVED_ADGROUPAD":
        # 标记广告为已删除
        mark_ad_removed(operation.ad_id)

    # 无法自动处理，启动完整同步
    else:
        queue_full_sync(customer_id)
```

### 主动预防

**定期同步作业：**

```python
def nightly_sync_job():
    """每晚执行的同步作业"""
    for customer_id in get_all_customers():
        # 1. 获取 Google Ads 中的所有对象
        ads_objects = fetch_all_google_ads_objects(customer_id)

        # 2. 与本地数据库比较
        differences = compare_with_local_db(ads_objects)

        # 3. 更新本地数据库
        update_local_db(differences)
```

---

## 错误处理流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    错误处理决策树                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  收到错误                                                       │
│    │                                                            │
│    ▼                                                            │
│  是身份验证错误？ ──▶ YES: 引导用户重新授权                      │
│    │ NO                                                         │
│    ▼                                                            │
│  是可重试错误？ ──▶ YES: 指数退避重试                           │
│    │ NO                                                         │
│    ▼                                                            │
│  是验证错误？ ──▶ YES: 显示具体错误给用户                       │
│    │ NO                                                         │
│    ▼                                                            │
│  是同步错误？ ──▶ YES: 更新本地数据库/启动同步                  │
│    │ NO                                                         │
│    ▼                                                            │
│  记录到日志，添加到人工审查队列                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## FastAPI 集成示例

```python
from fastapi import HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def classify_error(error: Exception) -> Dict[str, Any]:
    """
    分类错误并返回处理建议

    Args:
        error: 原始异常

    Returns:
        包含错误类型和处理建议的字典
    """
    error_type = type(error).__name__
    error_message = str(error)

    # 身份验证错误
    if "AuthenticationError" in error_type or "UNAUTHENTICATED" in error_message:
        return {
            "category": "authentication",
            "user_message": "授权已失效，请重新登录",
            "action": "redirect_to_auth",
            "retry": False
        }

    # 可重试错误
    if error_type in ["InternalServerError", "ServiceUnavailable", "UNAVAILABLE"]:
        return {
            "category": "retryable",
            "user_message": "服务暂时不可用，请稍后重试",
            "action": "auto_retry",
            "retry": True
        }

    # 验证错误
    if "ValidationError" in error_type or "INVALID_ARGUMENT" in error_message:
        return {
            "category": "validation",
            "user_message": f"输入无效：{error_message}",
            "action": "show_error_to_user",
            "retry": False
        }

    # 同步错误
    if "DUPLICATE_" in error_message or "REMOVED" in error_message:
        return {
            "category": "sync",
            "user_message": "数据可能已过期，正在同步...",
            "action": "sync_and_retry",
            "retry": True
        }

    # 默认：未知错误
    return {
        "category": "unknown",
        "user_message": "操作失败，请联系支持",
        "action": "log_and_notify",
        "retry": False
    }


async def handle_google_ads_error(error: Exception, context: Dict = None) -> Dict[str, Any]:
    """
    统一的 Google Ads 错误处理器

    Args:
        error: 原始异常
        context: 额外上下文信息

    Returns:
        标准化的错误响应
    """
    context = context or {}
    error_info = classify_error(error)

    # 记录错误
    logger.error(
        f"Google Ads 错误 [{error_info['category']}]: {error}",
        extra={**context, "error_category": error_info["category"]}
    )

    return {
        "success": False,
        "error": {
            "category": error_info["category"],
            "message": error_info["user_message"],
            "retry": error_info["retry"]
        }
    }
```

---

## 相关文档

- [最佳实践概览](./06-best-practices-overview.md)
- [问题排查](./09-troubleshooting.md)
- [了解 API 错误](./11-understand-api-errors.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/error-types?hl=zh-cn
**最后更新：** 2026-02-11
