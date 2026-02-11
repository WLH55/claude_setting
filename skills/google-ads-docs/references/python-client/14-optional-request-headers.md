# 可选请求标头

> 使用可选字段（如 validate_only）的正确方式

---

## 概述

在请求方法中使用任何可选字段时，必须在方法之外构建请求消息，并将其作为单个参数传入。

---

## 原理说明

可选请求标头（例如 `GoogleAdsService.Search` 方法中的 `validate_only` 标头）不会作为关键字参数出现在方法签名中，因此必须直接在请求消息中设置这些标头。

---

## 确定字段是否必需

如需确定请求对象字段是必需字段还是可选字段，您可以参考服务的 protobuf 定义，并查找包含注解 `[(google.api.field_behavior) = REQUIRED]` 的字段。

---

## 使用示例

### 设置 validate_only 字段

```python
request = client.get_type("SearchGoogleAdsRequest")
request.customer_id = customer_id
request.query = query
request.validate_only = True

response = googleads_service.search(request=request)
```

### 完整示例

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage()
googleads_service = client.get_service("GoogleAdsService")

# 构建请求对象
request = client.get_type("SearchGoogleAdsRequest")
request.customer_id = "1234567890"
request.query = "SELECT campaign.name FROM campaign"
request.validate_only = True  # 可选字段
request.return_total_results_count = True  # 另一个可选字段

# 将请求对象作为参数传入
response = googleads_service.search(request=request)
```

---

## 常用可选字段

| 方法 | 可选字段 | 说明 |
|------|---------|------|
| `Search` | `validate_only` | 仅验证请求，不执行 |
| `Search` | `return_total_results_count` | 返回总结果数 |
| `Mutate` | `validate_only` | 仅验证请求，不执行 |
| `Mutate` | `partial_failure` | 允许部分失败 |

---

## 关键要点

1. **构建请求对象**：在方法调用外构建请求消息
2. **设置可选字段**：直接在请求对象上设置可选字段
3. **传递请求对象**：将请求对象作为单个参数传入方法

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/optional-request-headers?hl=zh-cn
**最后更新：** 2026-02-11
