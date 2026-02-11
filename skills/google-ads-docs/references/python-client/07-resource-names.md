# 资源名称

> Google Ads API 中实体的唯一标识符

---

## 概述

Google Ads API 中实体的唯一标识符称为资源名称，表示为格式可预测的字符串。如果您知道资源名称的组成部分，则可以使用许多 Service 对象上提供的辅助方法生成资源名称。

---

## 服务路径方法

所有旨在处理 API 中特定类型对象的读取或更改操作的服务都具有用于构建 resource_names 的辅助方法。

### 创建资源名称

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage()
customer_id = "7892134783"
campaign_id = "1234567890"
campaign_service = client.get_service("CampaignService")
resource_name = campaign_service.campaign_path(customer_id, campaign_id)
```

### 解析资源名称

每项服务还附带一个 `parse_*_path` 方法，用于将 resource_name 解构为其各个部分：

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage()
resource_name = "customers/7892134783/campaigns/1234567890"
campaign_service = client.get_service('CampaignService')
segments = campaign_service.parse_campaign_path(resource_name)
customer_id = segments["customer_id"]
campaign_id = segments["campaign_id"]
```

---

## 复合资源名称

服务上的路径帮助程序用于构建资源名称的复合部分。该方法接受复合 ID 的不同部分作为单独的参数。

```python
from google.ads.google_ads.client import GoogleAdsClient

customer_id = "0987654321"
ad_group_id = "1234567890"
criterion_id = "74932"

client = GoogleAdsClient.load_from_storage()
ad_group_criterion_service = client.get_service("AdGroupCriterionService")

# AdGroupCriterion 资源名称格式：
# "customers/0987654321/adGroupCriteria/1234567890~74932"
resource_name = ad_group_criterion_service.ad_group_criterion_path(
    customer_id, ad_group_id, criterion_id
)
```

---

## 资源名称格式

| 资源类型 | 格式示例 |
|---------|---------|
| Campaign | `customers/{customer_id}/campaigns/{campaign_id}` |
| AdGroup | `customers/{customer_id}/adGroups/{ad_group_id}` |
| AdGroupCriterion | `customers/{customer_id}/adGroupCriteria/{ad_group_id}~{criterion_id}` |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/resource-names?hl=zh-cn
**最后更新：** 2026-02-11
