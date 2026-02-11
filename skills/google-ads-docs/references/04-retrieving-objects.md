# Google Ads API - 检索对象

> `GoogleAdsService` 是 Google Ads API 的统一对象获取和报告服务。

## 概述

```
┌─────────────────────────────────────────────────────────────────┐
│                  GoogleAdsService 功能                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ├── 检索对象的特定属性                                         │
│  ├── 根据日期范围检索效果指标                                   │
│  ├── 根据对象的属性进行排序                                     │
│  ├── 使用条件过滤返回的对象                                     │
│  └── 限制返回的对象数量                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 两种检索方法

### SearchStream vs Search

| 特性 | SearchStream | Search |
|------|-------------|--------|
| 返回方式 | 流式返回所有行 | 分页返回 |
| 适用场景 | 大型结果集 (>10,000 行) | 交互式应用 |
| 性能 | 更快下载数据 | 支持分页控制 |
| 复杂度 | 简单 | 需要处理 page_token |

```
┌─────────────────────────────────────────────────────────────────┐
│                    SearchStream vs Search                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SearchStream:                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  请求 │  流式响应                                      │   │
│  │    │                                                  │   │
│  │    ├─────┬─────┬─────┬─────┬────                         │   │
│  │    ▼     ▼     ▼     ▼     ▼                            │   │
│  │   Row1  Row2  Row3  Row4  Row5 ...                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Search:                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  请求 │  分页响应                                    │   │
│  │    │                                                  │   │
│  │    ▼                                                 │   │
│  │  Page 1 (10 rows)                                      │   │
│  │    │                                                  │   │
│  │    ├──── page_token ─────┐                             │   │
│  │    ▼                    ▼                             │   │
│  │  Page 2 (10 rows)                                      │   │
│  │    │                                                  │   │
│  │    ├──── page_token ─────┐                             │   │
│  │    ▼                    ▼                             │   │
│  │  Page 3 (5 rows)                                       │   │
│  │                                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 发出请求

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `customer_id` | string | ✅ | Google Ads 客户 ID |
| `query` | string | ✅ | GAQL 查询语句 |
| `page_size` | int32 | ❌ | 单页返回的对象数量 |
| `page_token` | string | ❌ | 下一页的令牌 |

### GAQL 查询示例

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions,
  metrics.clicks
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.impressions DESC
LIMIT 100
```

---

## 处理响应

### GoogleAdsRow 对象

```
┌─────────────────────────────────────────────────────────────────┐
│                      GoogleAdsRow 结构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GoogleAdsRow                                                    │
│  ├── campaign (资源对象)                                       │
│  │   ├── id                                                   │
│  │   ├── name                                                 │
│  │   └── status                                              │
│  ├── metrics (指标数据)                                       │
│  │   ├── impressions                                          │
│  │   ├── clicks                                               │
│  │   └── cost                                                │
│  └── segments (细分维度)                                      │
│      ├── date                                                 │
│      └── device                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 重要提示

**只有 `SELECT` 子句中明确包含的字段才会在响应中填充。**

```sql
-- 只选择了 name，所以其他字段不会被填充
SELECT campaign.name
FROM campaign

-- 响应中：
{
  "campaign": {
    "name": "广告系列A",  -- 有值
    "status": null      -- 未选择，所以为 null
  }
}
```

---

## UNKNOWN 枚举类型

### 什么是 UNKNOWN

`UNKNOWN` 表示该资源类型在当前 API 版本中不受支持。

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNKNOWN 资源类型                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  来源：                                                        │
│  • Google Ads 界面中引入的新功能                             │
│  • 比当前 API 版本更新的内容                                  │
│                                                                 │
│  特性：                                                        │
│  • ✅ 可以查询                                               │
│  • ❌ 无法通过 API 更新                                       │
│  • ⚠️ 以后可能受支持，也可能保持 UNKNOWN                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 处理建议

- **允许查询** UNKNOWN 类型资源
- **跳过更新** UNKNOWN 类型资源
- **考虑升级** API 版本以获取支持

---

## 细分 (Segments)

### 细分规则

```
┌─────────────────────────────────────────────────────────────────┐
│                    细分 (Segment) 概念                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  查询：                                                          │
│  SELECT campaign.status, metrics.impressions                    │
│  FROM campaign                                                 │
│  WHERE segments.date DURING LAST_7_DAYS                       │
│    AND segments.ad_network_type IN [SEARCH, DISPLAY]           │
│                                                                 │
│  结果：                                                          │
│  对于 campaign、date、ad_network_type 的每种组合各占一行         │
│                                                                 │
│  示例：                                                          │
│  - Campaign A + 2024-01-01 + SEARCH                            │
│  - Campaign A + 2024-01-01 + DISPLAY                           │
│  - Campaign A + 2024-01-02 + SEARCH                            │
│  - Campaign A + 2024-01-02 + DISPLAY                           │
│  - ...                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 隐式细分

```
结果按主要资源的每个实例进行隐式细分，
而不是按所选各个字段的值。
```

**示例：**

```sql
SELECT campaign.status, metrics.impressions
FROM campaign
WHERE segments.date DURING LAST_14_DAYS

-- 结果：每个 campaign 占一行，而不是按 campaign.status 细分
```

---

## 最佳实践

### 1. 选择合适的方法

| 数据量 | 推荐方法 | 原因 |
|--------|---------|------|
| 小于 10,000 行 | Search 或 SearchStream | 都可以 |
| 大于 10,000 行 | SearchStream | 避免分页复杂性 |
| 交互式 UI | Search | 支持分页和增量加载 |

### 2. 查询优化

```sql
-- ❌ 不推荐：选择所有字段
SELECT * FROM campaign

-- ✅ 推荐：只选择需要的字段
SELECT
  campaign.id,
  campaign.name,
  metrics.clicks,
  metrics.cost
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

### 3. 使用日期范围限制

```sql
-- ✅ 推荐：总是添加日期范围
WHERE segments.date DURING LAST_30_DAYS
-- 或
WHERE segments.date BETWEEN '2024-01-01' AND '2024-01-31'
```

### 4. 处理 UNKNOWN 类型

```python
# 处理 UNKNOWN 状态
if campaign.status == "UNKNOWN":
    logger.warning(f"Campaign {campaign.id} has UNKNOWN status")
    # 跳过或标记
    continue
```

---

## Python 客户端使用

### SearchStream 示例

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_dict(config_dict)
ga_service = client.get_service("GoogleAdsService")

query = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions,
  metrics.clicks
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.impressions DESC
"""

# 流式查询（推荐）
stream = ga_service.search_stream(
    customer_id=customer_id,
    query=query
)

for batch in stream:
    for row in batch.results:
        print(f"Campaign: {row.campaign.name}")
        print(f"Impressions: {row.metrics.impressions}")
```

### Search 示例（分页）

```python
# 分页查询
page_size = 100
query = "SELECT campaign.id, campaign.name FROM campaign"

# 第一页
search_request = client.get_type("SearchGoogleAdsRequest")
search_request.customer_id = customer_id
search_request.query = query
search_request.page_size = page_size

response = ga_service.search(request=search_request)

# 处理第一页
for row in response.results:
    print(f"Campaign: {row.campaign.name}")

# 获取下一页
while response.next_page_token:
    search_request.page_token = response.next_page_token
    response = ga_service.search(request=search_request)

    for row in response.results:
        print(f"Campaign: {row.campaign.name}")
```

---

## FastAPI 集成

### Service 层示例

```python
from typing import List, Dict
from google.ads.googleads.client import GoogleAdsClient

def get_account_campaigns(client: GoogleAdsClient, customer_id: str) -> List[Dict]:
    """获取账户的广告系列"""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          metrics.impressions,
          metrics.clicks,
          metrics.cost
        FROM campaign
        ORDER BY metrics.impressions DESC
    """

    campaigns = []
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in stream:
        for row in batch.results:
            campaigns.append({
                "id": str(row.campaign.id),
                "name": row.campaign.name,
                "status": row.campaign.status.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost": float(row.metrics.cost) if row.metrics.cost else 0
            })

    return campaigns
```

---

## 相关文档

- [API 结构](./01-api-structure.md)
- [更改对象](./03-changing-objects.md)
- [GAQL 查询语言](https://developers.google.com/google-ads/api/docs/query/grammar)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/concepts/retrieving-objects?hl=zh-cn
**最后更新：** 2024-08-29 (UTC)
