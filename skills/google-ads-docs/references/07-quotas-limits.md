# Google Ads API - 配额和限制

> 本文档详细说明了 Google Ads API 的配额限制和相关错误。

---

## 主要限制概览

| 请求类型 | 限制 | 错误代码 |
|---------|------|---------|
| **探索者访问权限级别** | 生产账号每天 2,880 次操作<br>测试账号每天 15,000 次操作 | `RESOURCE_EXHAUSTED` |
| **基本访问权限级别** | 测试账号和生产账号每天上限 15,000 次操作 | `RESOURCE_EXHAUSTED` |
| **Mutate 请求** | 每个请求 10,000 次操作 | `TOO_MANY_MUTATE_OPERATIONS` |
| **规划服务请求** | 每秒 1 次查询 | `RESOURCE_EXHAUSTED` |
| **转化上传服务请求** | 每个请求 2,000 次转化 | `TOO_MANY_CONVERSIONS_IN_REQUEST` |
| **结算和账号预算服务请求** | 每个 mutate 请求 1 项操作 | `TOO_MANY_MUTATE_OPERATIONS` |

---

## 1. API 每天操作限制

### 配额计算

```
┌─────────────────────────────────────────────────────────────────┐
│                    API 操作配额计算                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  API 操作 = Get 请求 + Mutate 操作的总和                        │
│                                                                 │
│  示例：                                                        │
│  ├── 10 个 Search 请求        = 10 次操作                       │
│  ├── 5 个 Mutate 请求        = 5 次操作                        │
│  └── 1 个 Mutate(5000操作)   = 5,000 次操作                    │
│                                                                 │
│  总计 = 10 + 5 + 5,000 = 5,015 次操作                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 访问权限级别

| 级别 | 生产账号 | 测试账号 |
|------|---------|---------|
| 探索者访问 | 2,880 次/天 | 15,000 次/天 |
| 基本访问 | 15,000 次/天 | 15,000 次/天 |
| 标准访问 | 申请更高配额 | - |

### 超限错误

```
RESOURCE_EXHAUSTED
```

---

## 2. gRPC 限制

### 消息大小限制

| 限制项 | 大小 | 超限错误 |
|-------|------|---------|
| 默认消息大小 | 4 MB | `429 Resource Exhausted` |
| 客户端库上限 | 64 MB | `429 Resource Exhausted` |

### 优化建议

- 减少查询中选择的字段数量
- 使用 `SearchStream` 流式传输
- 分页获取大量数据

```python
# ❌ 选择过多字段
query = """
SELECT
  campaign.*,
  ad_group.*,
  ad_group_ad.*,
  ...
FROM campaign
"""

# ✅ 只选择需要的字段
query = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status
FROM campaign
"""
```

---

## 3. Mutate 请求

### 操作数量限制

每个 mutate 请求最多 **10,000** 项操作。

### 超限错误

```
TOO_MANY_MUTATE_OPERATIONS
```

### 分批处理示例

```python
def batch_mutate(client: GoogleAdsClient, customer_id: str,
                 operations: List, batch_size: int = 5000) -> None:
    """分批执行 mutate 操作"""
    service = client.get_service("CampaignService")

    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]

        try:
            response = service.mutate_campaigns(
                customer_id=customer_id,
                operations=batch
            )
            print(f"批次 {i//batch_size + 1}: 成功 {len(response.results)} 个操作")
        except Exception as e:
            print(f"批次 {i//batch_size + 1}: 失败 - {e}")
```

---

## 4. 搜索请求

### 操作计数

| 请求类型 | 计算方式 |
|---------|---------|
| `Search` 或 `SearchStream` | 1 次操作 |
| 分页请求（有效 `next_page_token`） | **不计入** 配额 |
| 分页请求（无效/过期 `page_token`） | **计入** 配额 |

### 示例

```python
# SearchStream 请求：无论返回多少行，都只计为 1 次操作
stream = ga_service.search_stream(
    customer_id=customer_id,
    query=query  # 返回 100,000 行
)
# 配额消耗：1 次操作
```

---

## 5. 关键字规划服务

### 请求速率限制（每个客户 ID）

| 服务 | 限制 |
|------|------|
| `GenerateKeywordIdeas` | 每秒 1 个请求 |
| `GenerateKeywordHistoricalMetrics` | 每秒 1 个请求 |
| `GenerateKeywordForecastMetrics` | 每秒 1 个请求 |
| `GenerateAdGroupTheme` | 每秒 2 个请求 |

### 对象数量限制

| 对象类型 | 数量上限 |
|---------|---------|
| 每个账号 `KeywordPlan` | 10,000 |
| 每 `KeywordPlan` 的 `KeywordPlanAdGroup` | 200 |
| 每 `KeywordPlan` 的 `KeywordPlanAdGroupKeyword` | 10,000 |
| `KeywordPlanCampaignKeyword`（否定关键字） | 1,000 |
| 每 `KeywordPlan` 的 `KeywordPlanCampaign` | 1 |

---

## 6. 受众群体分析服务

### 请求限制

| 服务 | 限制 |
|------|------|
| `GenerateAudienceCompositionInsights` | 每客户 ID 每天 ~200 个请求 |
| `GenerateSuggestedTargetingInsights` | 每客户 ID 每天 ~200 个请求 |
| `GenerateTargetingSuggestionMetrics` | 每开发者令牌每秒 2 个请求 |

---

## 7. 转化上传服务

### 每次请求限制

| 服务 | 限制 | 超限错误 |
|------|------|---------|
| `UploadCallConversions` | 2,000 次转化 | `TOO_MANY_CONVERSIONS_IN_REQUEST` |
| `UploadClickConversions` | 2,000 次转化 | `TOO_MANY_CONVERSIONS_IN_REQUEST` |
| `UploadConversionAdjustments` | 2,000 次转化调整 | `TOO_MANY_ADJUSTMENTS_IN_REQUEST` |

### 转化价值规则

- 每个账号上限：**100,000** 条规则
- 超限错误：`ResourceCountLimitExceededError.ACCOUNT_LIMIT`

---

## 8. 结算和账号预算服务

### 限制条件

| 限制项 | 说明 |
|-------|------|
| 结算类型 | 只能针对按月账单结算的账号执行 mutate 操作 |
| 操作数量 | mutate 请求仅允许 **1** 项操作 |
| 更改间隔 | 对同一账号预算的更改间隔应至少 **12 小时** |

---

## 9. 客户账号邀请

### 邀请限制

| 限制项 | 数量 | 超限错误 |
|-------|------|---------|
| 每用户待处理邀请 | 1 个（同一客户账号） | - |
| 客户账号待处理邀请 | 最多 70 个 | `ACCESS_INVITATION_ERROR_PENDING_INVITATIONS_LIMIT_EXCEEDED` |

---

## 10. 用户数据

### 用户标识符限制

| 限制项 | 数量 | 超限错误 |
|-------|------|---------|
| 每组 `user_identifiers` | 应仅针对单个用户 | - |
| 每组最大标识符数量 | 20 个 | `OfflineUserDataJobError.TOO_MANY_USER_IDENTIFIERS` |
| 总计用户标识符 | 100,000 个 | `UserDataError.TOO_MANY_USER_IDENTIFIERS` |

---

## 11. GAQL 查询限制

### `IN` 子句限制

```sql
-- ❌ 错误：超过 20,000 项
WHERE campaign.id IN (1, 2, 3, ..., 20001)

-- ✅ 正确：分批查询
WHERE campaign.id IN (1, 2, 3, ..., 20000)
```

超限错误：`FILTER_HAS_TOO_MANY_VALUES`

---

## 配额管理最佳实践

### 1. 监控配额使用

```python
def log_quota_usage(operation: str, count: int = 1) -> None:
    """记录配额使用情况"""
    logger.info(f"API 操作: {operation}, 消耗: {count}")

# 使用示例
log_quota_usage("search", 1)
log_quota_usage("mutate", 5000)
```

### 2. 优先级处理

```python
# 批量操作时，优先处理重要数据
high_priority_operations = [...]  # 重要操作
low_priority_operations = [...]   # 次要操作

# 先处理高优先级
batch_mutate(client, customer_id, high_priority_operations)
# 再处理低优先级
batch_mutate(client, customer_id, low_priority_operations)
```

### 3. 使用测试账号

- 开发阶段使用测试账号（15,000 次/天配额）
- 生产账号的探索者级别配额较低（2,880 次/天）

### 4. 请求优化

```python
# ❌ 多次小请求
for i in range(100):
    mutate([operations[i]])

# ✅ 批量请求
mutate(operations)  # 100 个操作一次请求
```

---

## 相关文档

- [最佳实践概览](./06-best-practices-overview.md)
- [系统限制](./08-system-limits.md)
- [错误类型](./10-error-types.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/quotas?hl=zh-cn
**最后更新：** 2026-02-11
