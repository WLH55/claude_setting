# 将空消息对象设置为字段

> 设置空的 protobuf 消息字段

---

## 概述

在 Google Ads API 中，某些消息字段被定义为空消息对象（例如 `campaign.manual_cpm`），或者可能仅包含不需要设置的可选字段（例如 `campaign.manual_cpc`）。

设置这些字段非常重要，因为这有助于告知 API 应为给定广告系列使用哪种出价策略。

---

## 更新嵌套字段

### 更新字符串字段

```python
campaign.name = "Test campaign value"
```

### 更新嵌套字段

`campaign.manual_cpc` 是一个嵌套字段，包含另一个 protobuf 消息。可以直接更新其字段：

```python
campaign.manual_cpc.enhanced_cpc_enabled = True
```

这告知 API 此广告系列的出价策略为 `manual_cpc`，且已启用智能点击付费。

---

## 设置空消息对象

如果您想使用空的 `manual_cpm` 或 `manual_cpc` 未启用智能点击付费，需要将该类的单独空实例复制到广告系列中：

```python
client = GoogleAdsClient.load_from_storage()

empty_cpm = client.get_type('ManualCpm')
client.copy_from(campaign.manual_cpm, empty_cpm)
```

### 结果结构

```protobuf
name {
  value: "Test campaign value"
}
manual_cpm {
}
```

`manual_cpm` 字段已设置，但其所有字段均没有值。

---

## 验证设置

向使用此模式的 API 发送请求时，可以通过启用日志记录并检查请求载荷来验证是否正确设置了空消息对象。

---

## 更新掩码

最后，需要手动将此字段添加到请求对象的 `update_mask`。字段掩码辅助程序没有任何机制来确定已明确设置为空对象的字段与未设置的字段之间的区别。

```python
from google.api_core.protobuf_helpers import field_mask

campaign_operation.create = campaign
campaign_operation.update_mask = field_mask(None, campaign)
# 手动添加 "manual_cpm" 字段
campaign_operation.update_mask.append("manual_cpm")
```

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/empty-message-fields?hl=zh-cn
**最后更新：** 2026-02-11
