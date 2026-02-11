# 服务和类型 getter

> GoogleAdsClient 的 get_service 和 get_type 方法

---

## 概述

在 Python 中使用 API 时，需要获取对各种 proto 类的引用，这可能会非常冗长，并且需要您对 API 有深入的了解，或者经常切换上下文来引用 proto 或文档。

---

## 客户端的 `get_service` 和 `get_type` 方法

### get_service

检索服务客户端实例。服务客户端类在版本路径 `google/ads/googleads/v*/services/services/` 下定义。

```python
from google.ads.googleads.client import GoogleAdsClient

# 可选的 version 参数指定返回的 API 版本
client = GoogleAdsClient.load_from_storage(version="v22")
googleads_service = client.get_service("GoogleAdsService")
```

### get_type

检索任何其他对象（资源、枚举、错误等）。所有类型都在各种对象类别 `google/ads/googleads/v*/common|enums|errors|resources|services/types/` 下定义。

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage(version="v22")
campaign = client.get_type("Campaign")
```

**注意：** 版本目录下的所有代码都是生成的，因此最好使用这些方法，而不是直接导入对象，以防代码库的结构发生变化。

---

## 枚举

### 使用 enums 属性

每个 `GoogleAdsClient` 实例还具有一个 `enums` 属性，提供更简单易读的体验：

```python
client = GoogleAdsClient.load_from_storage(version="v22")

campaign = client.get_type("Campaign")
campaign.status = client.enums.CampaignStatusEnum.PAUSED
```

### 枚举值读取

```python
>>> print(campaign.status)
CampaignStatus.PAUSED
>>> type(campaign.status)
<enum 'CampaignStatus'>
>>> print(campaign.status.value)
3
```

### 枚举名称读取

```python
>>> print(campaign.status.name)
'PAUSED'
>>> type(campaign.status.name)
<class 'str'>
```

**注意：** 与枚举的互动方式因 `use_proto_plus` 配置设置而异。详见 [Protobuf 消息文档](./12-protobuf-messages.md)。

---

## 版本控制

同时维护 API 的多个版本。

### 初始化时指定版本

```python
client = GoogleAdsClient.load_from_storage(version="v22")
# Campaign 实例将来自 v22 版本
campaign = client.get_type("Campaign")
```

### 调用时指定版本（覆盖初始化版本）

```python
client = GoogleAdsClient.load_from_storage()
# 加载 v22 版本的 GoogleAdsService
googleads_service = client.get_service("GoogleAdsService", version="v22")

client = GoogleAdsClient.load_from_storage(version="v22")
# 加载 v20 版本的 Campaign
campaign = client.get_type("Campaign", version="v20")
```

**注意：** 如果未提供 `version` 参数，库将默认使用最新版本。

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/proto-getters?hl=zh-cn
**最后更新：** 2026-02-11
