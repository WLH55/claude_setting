# Google Ads API - 更改对象

> 本指南介绍如何使用 Google Ads API 更改（创建、更新、删除）对象。

## 概述

Google Ads API 中的每个顶级资源都有相应的特定于资源类型的服务，且该服务支持修改资源实例。

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mutate 操作流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  请求                                                             │
│   │                                                              │
│   ├── customer_id (客户ID)                                       │
│   ├── operations[] (操作列表)                                    │
│   │   ├── Operation 1: CREATE campaign                         │
│   │   ├── Operation 2: UPDATE campaign                         │
│   │   └── Operation 3: REMOVE campaign                         │
│   │                                                              │
│   └── response_content_type (响应类型)                          │
│                                                                 │
│   ▼                                                              │
│  Google Ads API                                                  │
│   │                                                              │
│   ├── 验证请求                                                   │
│   ├── 执行操作 (全部成功或全部失败)                              │
│   └── 返回结果                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mutate 请求结构

### CampaignService 示例

`CampaignService.MutateCampaigns` 方法接受 `MutateCampaignsRequest`，包含：

| 字段 | 说明 |
|------|------|
| `customer_id` | 客户 ID |
| `operations` | `CampaignOperation` 对象集合 |
| `response_content_type` | 响应内容类型 |

---

## 操作类型

### 操作 (Operation) 字段

每个 `CampaignOperation` 支持以下操作类型：

```
┌─────────────────────────────────────────────────────────────────┐
│                      Operation 类型                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   oneof operation (只能选择一种)                                │
│                                                                 │
│   ├── create (创建)                                            │
│   │       创建资源的新实例                                     │
│   │                                                          │
│   ├── update (更新)                                            │
│   │       更新资源以匹配 update 属性                           │
│   │       注意：需要设置 update_mask                           │
│   │                                                          │
│   └── remove (移除)                                            │
│       移除资源                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 操作限制

由于 `operation` 字段为 `oneof` 字段，**单个操作只能修改一个对象**。

**示例：** 要创建一个广告系列并删除另一个，需要添加两个 `CampaignOperation` 实例。

---

## 批量操作

### 最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                    请求策略对比                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 错误方式：                                                  │
│     发送 10 个 mutate 请求，每个包含 1 个操作                    │
│                                                                 │
│  ✅ 正确方式：                                                  │
│     发送 1 个 mutate 请求，包含 10 个操作                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**优势：**
- 提高性能（减少网络往返）
- 原子性保证（全部成功或全部失败）
- 降低配额消耗

---

## Update Mask

### 什么是 Update Mask

`update_mask` 告诉 Google Ads API 应该更新哪些字段。

```
┌─────────────────────────────────────────────────────────────────┐
│                      Update Mask 示例                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Campaign 对象:                                                │
│  ├── name: "新名称"                                             │
│  ├── status: "ENABLED"                                          │
│  ├── budget: "100000"                                           │
│  └── start_date: "2024-01-01"                                  │
│                                                                 │
│  如果 update_mask = ["name", "status"]                         │
│  则只更新这两个字段，其他字段保持不变                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Python 客户端使用

```python
# Python 客户端会自动生成 update_mask
campaign_operation = client.get_type("CampaignOperation")
campaign_operation.update = campaign
# update_mask 会自动生成
```

---

## Mutate 响应

### 响应类型

`response_content_type` 决定返回的内容：

| 类型 | 说明 |
|------|------|
| `MUTABLE_RESOURCE` | 返回更新后的可变字段 |
| `RESOURCE_NAME_ONLY` | 仅返回资源名称 |

### 响应内容

```
响应包含：
├── mutate_results (每个操作的结果)
│   ├── result (成功时返回资源)
│   └── status (失败时包含错误信息)
└── partial_failure_error (部分失败错误)
```

### 原子性保证

**重要：** 只有当请求中的**所有操作都成功**时，操作才会应用到您的 Google Ads 账号。

```
┌─────────────────────────────────────────────────────────────────┐
│                    原子性操作示例                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  请求包含 3 个操作：                                            │
│  ├── 操作 A: 创建广告系列                                       │
│  ├── 操作 B: 更新预算                                           │
│  └── 操作 C: 添加关键词                                         │
│                                                                 │
│  如果操作 B 失败：                                               │
│  ├── 操作 A、B、C 全部不会执行                                  │
│  └── 返回错误信息                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mutate 错误

### 常见错误类型

| 错误类型 | 说明 |
|---------|------|
| `DatabaseError.CONCURRENT_MODIFICATION_ERROR` | 并发修改冲突 |
| `AuthenticationError` | 认证失败 |
| `AuthorizationError.USER_PERMISSION_DENIED` | 权限不足 |
| `QuotaError` | 配额超限 |
| `ResourceExhaustedError` | 资源耗尽 |

### 并发修改冲突

**不能同时由多个来源并行修改 Google Ads 对象。**

包括：
- 从同一应用中的多个线程更新
- 从不同应用更新
- 应用和 Google Ads 界面同时操作

**解决方案：** 重试机制、使用 `validate_only` 预检查

---

## 最佳实践

### 1. 批量操作

```python
# ❌ 错误：循环调用 API
for campaign_data in campaigns:
    response = campaign_service.mutate_campaigns(
        customer_id=customer_id,
        operations=[create_operation(campaign_data)]
    )

# ✅ 正确：批量操作
operations = [create_operation(data) for data in campaigns]
response = campaign_service.mutate_campaigns(
    customer_id=customer_id,
    operations=operations
)
```

### 2. 使用 validate_only

```python
# 验证请求而不执行
request = client.get_type("MutateCampaignsRequest")
request.customer_id = customer_id
request.operations = operations
request.validate_only = True  # 仅验证，不执行

response = campaign_service.mutate_campaigns(request=request)
```

### 3. 错误处理

```python
try:
    response = campaign_service.mutate_campaigns(
        customer_id=customer_id,
        operations=operations
    )
except Exception as e:
    # 处理错误
    logger.error(f"Mutate 失败: {e}")
    raise BusinessValidationException(f"操作失败: {e}")
```

---

## 相关文档

- [API 结构](./01-api-structure.md)
- [调用结构](./02-call-structure.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/concepts/changing-objects?hl=zh-cn
**最后更新：** 2025-06-04 (UTC)
