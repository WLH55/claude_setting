# Google Ads API - 系统限制

> 本文档列出了 Google Ads API 中的各种限制，以及超出限制时抛出的相应错误。

---

## Account（账号）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 经理账号层次结构中的 Google Ads 账号数量上限 | 不定 | `ManagerLinkError.TOO_MANY_ACCOUNTS` |
| 经理账号层次结构中的测试账号数量上限 | 50 | `ManagerLinkError.TOO_MANY_ACCOUNTS` |
| 一个 Google Ads 账号可由经理账号管理的账号数量上限 | 5 | `ManagerLinkError.TOO_MANY_MANAGERS` |
| 层次结构中的层级数量上限（从顶级经理账号到最底层的 Google Ads 账号） | 6 | `ManagerLinkError.MAX_DEPTH_EXCEEDED` |
| 同一层次结构中待处理的经理账号邀请数量上限 | 20 | `ManagerLinkError.TOO_MANY_INVITES` |
| 名称长度 | 255 个字符 | `StringLengthError.TOO_LONG` |

---

## Ads（广告）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 标题长度 | 30 个字符 | `AdError.LINE_TOO_WIDE` |
| Description1 或 description2 的长度 | 90 个字符 | `AdError.LINE_TOO_WIDE` |
| Path1 或 path2 长度 | 15 个字符 | `AdError.LINE_TOO_WIDE` |
| 最终到达网址的长度 | 2,084 字节 | `StringLengthError.TOO_LONG` |

> 注意：最终到达网址必须包含协议前缀（例如 "https://"），并且会计入此限制。

---

## Ad group（广告组）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 名称长度 | 256 个字符 | `AdGroupError.INVALID_ADGROUP_NAME` |

---

## Campaign budget（广告系列预算）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 账号中的共享预算数量上限 | 11,000 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 账号中不共享的预算数量上限 | 20,000 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |

> 预算上限比广告系列数量上限多 1,000 个，以便您在需要时有足够的空间重新分配预算。

---

## Campaign（广告系列）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 每个广告系列中可附加到广告组的出价策略数量上限 | 1,000 | `ResourceCountLimitExceededError.CAMPAIGN_LIMIT` |
| 名称长度 | 256 个字符 | `StringLengthError.TOO_LONG` |

---

## Conversion upload（转化上传）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 每次 API 调用可上传的线下点击转化数据的数量上限 | 2,000 | `ConversionUploadError.TOO_MANY_CONVERSIONS_IN_REQUEST` |

---

## Criterion（条件）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 关键字长度 | 80 个字符 | `CriterionError.KEYWORD_TEXT_TOO_LONG` |
| 展示位置网址长度 | 250 个字符 | `CriterionError.PLACEMENT_URL_IS_TOO_LONG` |
| 最终到达网址的长度 | 2,047 字节 | `StringLengthError.TOO_LONG` |
| 邻近区域半径 | 800 公里 / 500 英里 | `CriterionError.INVALID_PROXIMITY_RADIUS` |
| 修改 ProductPartition 树结构的单个请求中包含的购物广告组的数量上限 | 2 | `AdGroupCriterionError.OPERATIONS_FOR_TOO_MANY_SHOPPING_ADGROUPS` |
| 每个广告系列的已排除 IP 段数量上限 | 500 | `ResourceCountLimitExceededError.CAMPAIGN_LIMIT` |

> 注意：
> - 展示位置网址：系统会移除协议前缀（例如 "http://"），这些前缀不会计入限制。
> - 最终到达网址：协议前缀（例如 "http://"）会计入限制。
> - ProductPartition 树修改限制不适用于仅修改现有分区出价的请求。如需修改两个以上购物广告组的树结构，建议使用批处理作业。

---

## Feed（Feed）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 每个账号的 Feed 数量上限 | 100 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 每个账号的 Feed 项数量上限 | 5,000,000 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 每个 Feed 的 Feed 属性数量上限 | 30 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 每个匹配函数的 Feed 项数量上限 | 20 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |

> 建议尽可能为每种扩展程序类型使用一个 Feed。

---

## Label（标签）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 经理账号可向账号应用的标签数量上限 | 200 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 一个标签可应用于的账号数量上限 | 1,000 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 每个账号可对实体（广告系列、广告组等）应用的标签数量上限 | 100,000 | `ResourceCountLimitExceededError.CAMPAIGN_LIMIT, ADGROUP_LIMIT, etc.` |
| 可应用于单个实体（广告系列、广告组等）的标签数量上限 | 50 | `ResourceCountLimitExceededError.CAMPAIGN_LIMIT, ADGROUP_LIMIT, etc.` |

> 注意：所有实体类型的标签都会计入同一上限。

---

## Listing groups（产品信息组）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 每个广告组最多可包含的产品信息组数量 | 20,000 | `ResourceCountLimitExceededError.RESOURCE_LIMIT` |

---

## Payments account（付款账号）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 可与付款账号关联的结算设置数量上限 | 75,000 | `BillingSetupError.PAYMENTS_ACCOUNT_INELIGIBLE` |

---

## Performance Max（效果最大化广告系列）

| 限制项 | 限制值 | 错误代码 |
|-------|--------|---------|
| 一个账号中可投放的效果最大化广告系列的数量上限 | 100 | `ResourceCountLimitExceededError.ACCOUNT_LIMIT` |
| 广告系列中的素材资源组数量上限 | 100 | `ResourceCountLimitExceededError.RESOURCE_LIMIT` |
| 素材资源组中的产品信息组过滤条件的数量上限 | 1,000 | `ResourceCountLimitExceededError.RESOURCE_LIMIT` |
| 广告系列中产品信息组过滤条件子类的数量上限 | 7 | `AssetGroupListingGroupFilterError.TREE_TOO_DEEP` |

> 如需提高效果最大化广告系列的数量上限，请与 Google 业务发展代表联系。

---

## 特殊情况

在极少数情况下，即使您未超出上述任何限制，也可能会收到 `INTERNAL_ERROR`。

当内部资源被序列化且依赖项扇出超出内部限制时，就会发生这种情况。

**解决方案：**
- 尝试缩减查询的大小或复杂性
- 执行多个查询来获得所需结果

---

## 限制对照表（快速参考）

```
┌─────────────────────────────────────────────────────────────────┐
│                    常用系统限制速查                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  名称长度：                                                     │
│  • Account / Campaign / AdGroup: 256 字符                      │
│  • Ad 标题: 30 字符                                            │
│  • Ad 描述: 90 字符                                            │
│                                                                 │
│  数量限制：                                                     │
│  • 经理账号测试账号: 50 个                                     │
│  • 共享预算: 11,000 个                                         │
│  • 不共享预算: 20,000 个                                       │
│  • Feed 项: 5,000,000 个                                       │
│  • 标签（账号级）: 100,000 个                                  │
│  • 效果最大化广告系列: 100 个                                  │
│                                                                 │
│  网址长度：                                                     │
│  • Ad 最终到达网址: 2,084 字节                                 │
│  • Criterion 最终到达网址: 2,047 字节                          │
│  • 展示位置网址: 250 字符                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Python 客户端验证示例

```python
def validate_campaign_name(name: str) -> bool:
    """验证广告系列名称长度"""
    max_length = 256
    if len(name) > max_length:
        raise ValueError(f"广告系列名称不能超过 {max_length} 个字符")
    return True


def validate_ad_text(headline: str, description: str) -> bool:
    """验证广告文本长度"""
    if len(headline) > 30:
        raise ValueError("标题不能超过 30 个字符")
    if len(description) > 90:
        raise ValueError("描述不能超过 90 个字符")
    return True


def validate_url(url: str, max_bytes: int = 2047) -> bool:
    """验证 URL 字节长度"""
    byte_length = len(url.encode('utf-8'))
    if byte_length > max_bytes:
        raise ValueError(f"URL 不能超过 {max_bytes} 字节")
    return True
```

---

## 相关文档

- [最佳实践概览](./06-best-practices-overview.md)
- [配额和限制](./07-quotas-limits.md)
- [错误类型](./10-error-types.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/best-practices/system-limits?hl=zh-cn
**最后更新：** 2026-02-11
