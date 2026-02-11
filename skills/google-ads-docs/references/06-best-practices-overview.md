# Google Ads API - 最佳实践概览

> 本指南介绍了优化应用效率和性能的最佳实践。

---

## 日常维护

### 保持联系信息更新

- 确保 API 中心内的开发者联系电子邮件地址是最新地址
- 避免使用与个人账号或无人监控的账号相关联的个人电子邮件地址

### 订阅更新渠道

订阅以下渠道以获取产品更改、维护停机、弃用日期等信息：

| 渠道 | 用途 |
|------|------|
| 论坛 | 提问和分享 API 问题 |
| API 博客 | 产品更新和公告 |
| 产品博客 | 新功能和变更 |

### 遵守条款和条件

- 确保应用遵守 Google Ads API 条款及条件 (T&C)
- 如有疑问，回复审核团队发送的电子邮件

---

## 优化

### 批量操作

```
┌─────────────────────────────────────────────────────────────────┐
│                    批量操作对比                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 错误方式：                                                  │
│     发送 50,000 个请求，每个请求包含 1 个操作                   │
│                                                                 │
│  ✅ 正确方式：                                                  │
│     发送 100 个请求，每个请求包含 500 个操作                    │
│     或发送 10 个请求，每个请求包含 5,000 个操作                 │
│                                                                 │
│  优势：                                                        │
│  • 减少网络往返延迟                                            │
│  • 降低序列化/反序列化开销                                      │
│  • 提高总体性能                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**示例：** 向广告系列添加 50,000 个关键字

```python
# ❌ 错误：循环调用
for keyword in keywords:
    response = ad_group_criterion_service.mutate_ad_group_criteria(
        customer_id=customer_id,
        operations=[create_operation(keyword)]
    )

# ✅ 正确：批量操作
operations = [create_operation(kw) for kw in keywords]
# 分批处理，每批 5000 个
for i in range(0, len(operations), 5000):
    batch = operations[i:i+5000]
    response = ad_group_criterion_service.mutate_ad_group_criteria(
        customer_id=customer_id,
        operations=batch
    )
```

### 重用访问令牌

```
┌─────────────────────────────────────────────────────────────────┐
│                    OAuth2 令牌复用                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  优势：                                                        │
│  • 减少令牌刷新开销                                            │
│  • 降低因过度刷新而受到速率限制的可能性                         │
│                                                                 │
│  实现：                                                        │
│  • 在不同线程和进程间共享同一令牌                               │
│  • 使用令牌缓存机制                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 发送稀疏对象

只填充需要更改的字段，而不是发送完整对象：

```python
# ❌ 错误：发送完整对象
campaign = get_campaign(campaign_id)  # 获取所有字段
campaign.name = "新名称"
campaign.status = "ENABLED"
# campaign 包含所有字段，处理慢

# ✅ 正确：稀疏更新
campaign = client.get_type("Campaign")
campaign.resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"
campaign.name = "新名称"
# 只设置需要更新的字段
```

---

## 错误处理和管理

### 区分请求来源

```
┌─────────────────────────────────────────────────────────────────┐
│                    请求类型区分                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户发起的请求：                                              │
│  • 优先级：用户体验                                           │
│  • 策略：在界面中提供详细错误信息和修正步骤                     │
│                                                                 │
│  后端发起的请求：                                              │
│  • 优先级：自动化处理                                         │
│  • 策略：为每种错误类型实现处理程序                             │
│          将失败操作加入队列供人工审查                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 区分错误类型

| 错误类型 | 说明 | 处理策略 |
|---------|------|---------|
| 身份验证错误 | OAuth2 令牌失效 | 引导用户重新授权 |
| 可重试错误 | 临时性错误（如 INTERNAL_ERROR） | 使用指数退避重试 |
| 验证错误 | 输入无效 | 向用户显示具体错误信息 |
| 同步相关错误 | 本地数据与 API 不同步 | 更新本地数据库 |

### 同步后端

**主动策略：** 每晚执行同步作业，获取 Google Ads 对象并与本地数据库比较。

### 记录错误

应记录的最小信息：

| 信息 | 说明 |
|------|------|
| 请求 ID | 唯一标识请求，用于调试 |
| 操作 | 引发错误的操作 |
| 错误本身 | 错误代码和消息 |
| 客户 ID | Google Ads 客户 ID |
| API 服务 | 调用的服务 |
| 往返延迟 | 请求耗时 |
| 重试次数 | 重试尝试次数 |
| 原始请求/响应 | 完整的请求和响应内容 |

### 监控趋势

- 使用日志生成交互式仪表板
- 自动发送错误趋势警报
- 检测和解决应用问题

---

## 开发

### 使用测试账号

```
┌─────────────────────────────────────────────────────────────────┐
│                    测试账号优势                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • 不会实际投放广告                                            │
│  • 开发者令牌无需批准即可使用                                  │
│  • 可在应用审核完成前开始开发                                  │
│  • 用于测试连接性、管理逻辑等                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Python 客户端示例

### 批量操作

```python
from google.ads.googleads.client import GoogleAdsClient

def add_keywords_batch(client: GoogleAdsClient, customer_id: str,
                       ad_group_id: str, keywords: List[str]) -> None:
    """批量添加关键字"""
    service = client.get_service("AdGroupCriterionService")

    # 构建操作列表
    operations = []
    for keyword_text in keywords:
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.create

        criterion.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = "EXACT"

        operations.append(operation)

    # 分批处理（每批 5000 个）
    batch_size = 5000
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        response = service.mutate_ad_group_criteria(
            customer_id=customer_id,
            operations=batch
        )
        print(f"已添加 {len(response.results)} 个关键字")
```

### 稀疏更新

```python
def update_campaign_bid(client: GoogleAdsClient, customer_id: str,
                       campaign_resource_name: str, new_bid: float) -> None:
    """稀疏更新广告系列出价"""
    service = client.get_service("CampaignService")

    operation = client.get_type("CampaignOperation")

    # 只设置需要更新的字段
    campaign = operation.update
    campaign.resource_name = campaign_resource_name

    # 使用 Float 类型设置出价
    campaign.maximize_conversions.target_cpa_micros = int(new_bid * 1_000_000)

    # 客户端库会自动生成 update_mask
    response = service.mutate_campaigns(
        customer_id=customer_id,
        operations=[operation]
    )
```

### 错误处理

```python
import logging
from google.api_core import exceptions as gcp_exceptions

logger = logging.getLogger(__name__)

def mutate_with_retry(service, customer_id: str, operations: List,
                     max_retries: int = 3) -> Any:
    """带重试的 mutate 操作"""

    for attempt in range(max_retries):
        try:
            return service.mutate(
                customer_id=customer_id,
                operations=operations
            )
        except gcp_exceptions.GoogleAPICallError as e:
            if attempt == max_retries - 1:
                logger.error(f"操作失败，已达最大重试次数: {e}")
                raise

            # 检查是否为可重试错误
            if hasattr(e, 'grpc_status_code') and e.grpc_status_code in [
                gcp_exceptions.StatusCode.INTERNAL,
                gcp_exceptions.StatusCode.UNAVAILABLE,
            ]:
                wait_time = 5 * (2 ** attempt)  # 指数退避
                logger.warning(f"可重试错误，{wait_time}秒后重试: {e}")
                time.sleep(wait_time)
                continue

            # 不可重试的错误，直接抛出
            raise
```

---

## FastAPI 集成示例

### Service 层错误处理

```python
from typing import List, Dict
from google.ads.googleads.client import GoogleAdsClient
from google.api_core import exceptions as gcp_exceptions
import logging

logger = logging.getLogger(__name__)

class GoogleAdsException(Exception):
    """Google Ads API 异常基类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def mutate_with_error_handling(
    client: GoogleAdsClient,
    customer_id: str,
    operations: List
) -> Dict:
    """
    带错误处理的 mutate 操作

    Args:
        client: Google Ads 客户端
        customer_id: 客户 ID
        operations: 操作列表

    Returns:
        操作结果字典

    Raises:
        GoogleAdsException: 当操作失败时
    """
    service = client.get_service("CampaignService")

    try:
        response = service.mutate_campaigns(
            customer_id=customer_id,
            operations=operations
        )

        return {
            "success": True,
            "results": [
                {
                    "resource_name": result.resource_name
                }
                for result in response.results
            ]
        }

    except gcp_exceptions.InvalidArgument as e:
        # 验证错误 - 用户输入问题
        logger.error(f"验证错误: {e}")
        raise GoogleAdsException(
            message="输入参数无效，请检查后重试",
            error_code="VALIDATION_ERROR"
        )

    except gcp_exceptions.PermissionDenied as e:
        # 权限错误
        logger.error(f"权限错误: {e}")
        raise GoogleAdsException(
            message="没有权限执行此操作",
            error_code="PERMISSION_DENIED"
        )

    except gcp_exceptions.ResourceExhausted as e:
        # 配额超限
        logger.error(f"配额超限: {e}")
        raise GoogleAdsException(
            message="API 调用配额已用尽，请稍后重试",
            error_code="QUOTA_EXCEEDED"
        )

    except gcp_exceptions.GoogleAPICallError as e:
        # 其他 API 错误
        logger.error(f"API 调用错误: {e}")
        raise GoogleAdsException(
            message=f"API 调用失败: {str(e)}",
            error_code="API_ERROR"
        )
```

---

## 相关文档

- [API 限制和配额](./07-quotas-limits.md)
- [系统限制](./08-system-limits.md)
- [问题排查](./09-troubleshooting.md)
- [错误类型](./10-error-types.md)
- [了解 API 错误](./11-understand-api-errors.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/overview?hl=zh-cn
**最后更新：** 2026-02-11
