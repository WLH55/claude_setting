# 使用字段掩码进行更新

> 在 Google Ads API 中使用字段掩码进行更新操作

---

## 概述

在 Google Ads API 中，更新是使用字段掩码来完成的。字段掩码列出您打算随更新而更改的所有字段，任何指定的字段掩码范围外的其他字段，即使发送到服务器，也会被忽略。

---

## 字段掩码辅助函数

如需生成字段掩码，建议使用 `google.api_core.protobuf_helpers.field_mask` 辅助函数。它接受两个 protobuf 对象，返回一个字段掩码对象。

### 创建新广告系列

```python
from google.api_core import protobuf_helpers
from google.ads.googleads.client import GoogleAdsClient

# 检索 GoogleAdsClient 实例
client = GoogleAdsClient.load_from_storage()
# 创建新的广告系列操作
campaign_operation = client.get_type('CampaignOperation')
# 从 update 字段检索新的广告系列对象
campaign = campaign_operation.update
# 修改广告系列
campaign.network_settings.target_search_network.value = False

# 使用更新的广告系列创建字段掩码
# field_mask 辅助函数仅兼容原始 protobuf 消息实例
# 使用 ._pb 属性访问
field_mask = protobuf_helpers.field_mask(None, campaign._pb)

# 将 field_mask 复制到操作的 update_mask 字段
client.copy_from(campaign_operation.update_mask, field_mask)
```

### 更新现有广告系列

```python
import proto

from google.api_core import protobuf_helpers
from google.ads.googleads.client import GoogleAdsClient

# 检索 GoogleAdsClient 实例
client = GoogleAdsClient.load_from_storage()
# 检索 GoogleAdsService 实例
googleads_service = client.get_service('GoogleAdsService')

# 查询以检索广告系列
query = f"""
    SELECT
      campaign.network_settings.target_search_network,
      campaign.resource_name
    FROM campaign
    WHERE campaign.resource_name = {resource_name}
"""

# 提交查询以检索广告系列实例
response = googleads_service.search_stream(customer_id=customer_id, query=query)

# 遍历结果以检索广告系列
for batch in response:
    for row in batch.results:
        initial_campaign = row.campaign

# 创建新的广告系列操作
campaign_operation = client.get_type('CampaignOperation')
# 设置复制的广告系列对象以便于引用
updated_campaign = campaign_operation.update
# 将检索的广告系列复制到新广告系列
# 使用 proto.Message.copy_from 方法，因为与 proto-plus 包装的消息兼容
proto.Message.copy_from(updated_campaign, initial_campaign)
# 修改新广告系列
updated_campaign.network_settings.target_search_network = False

# 使用更新的广告系列创建字段掩码
field_mask = protobuf_helpers.field_mask(
    initial_campaign._pb, updated_campaign._pb
)

# 将字段掩码复制到操作的 update_mask 字段
client.copy_from(campaign_operation.update_mask, field_mask)
```

### 字段掩码生成说明

- **新建对象**：传递 `None` 作为第一个参数，字段掩码列表将仅包含第二个对象上未设置为默认值的字段
- **更新对象**：传递原始对象和更新后的对象，字段掩码将包含两个对象之间存在差异的字段

---

## 使用要点

1. 使用 `._pb` 属性访问原始 protobuf 消息实例（用于 field_mask 辅助函数）
2. 使用 `client.copy_from()` 方法复制字段掩码（兼容 proto-plus 和原生消息）
3. 生成的字段掩码告知 API 哪些字段需要更改

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/field-masks?hl=zh-cn
**最后更新：** 2026-02-11
