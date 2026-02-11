# Protobuf 消息

> Proto-plus 与 Protobuf 消息类型详解

---

## 概述

借助 `use_proto_plus` 配置参数，您可以指定希望库返回 proto-plus 消息还是 protobuf 消息。

---

## Proto-plus 与 Protobuf 消息

### Proto-plus

- 接口更友好，行为更像原生 Python 对象
- 引入性能开销（类型封装）

### Protobuf

- 性能更优
- 接口不如 proto-plus 友好

---

## 性能分析

### 类型封装

Proto-plus 通过"类型封装"将 protobuf 消息和已知类型转换为原生 Python 类型。

```protobuf
syntax = "proto3";

message Dog {
  string name = 1;
}
```

### Proto-plus 类

```python
import proto

class Dog(proto.Message):
    name = proto.Field(proto.STRING, number=1)
```

### 使用示例

```python
dog = Dog()
dog.name = "Scruffy"
print(dog.name)
```

读取和设置 `name` 字段时，系统会将值从原生 Python `str` 类型转换为 `string` 类型。

---

## 用例建议

### Proto-plus 消息用例

- 编写可维护且可读的代码
- 日常开发工作
- 需要更好的开发体验

### Protobuf 消息用例

- 性能敏感的场景
- 处理大型报告
- 使用大量操作（如 `BatchJobService` 或 `OfflineUserDataJobService`）

---

## 动态切换消息类型

```python
from google.ads.googleads import util

# Proto-plus 消息类型
dog = Dog()

# 转换为 Protobuf 消息类型
dog = util.convert_proto_plus_to_protobuf(dog)

# 转换回 Proto-plus 消息类型
dog = util.convert_protobuf_to_proto_plus(dog)
```

---

## 接口差异

### 字节序列化

**Proto-plus：**
```python
serialized = type(campaign).serialize(campaign)
deserialized = type(campaign).deserialize(serialized)
```

**Protobuf：**
```python
serialized = campaign.SerializeToString()
deserialized = campaign.FromString(serialized)
```

### JSON 序列化

**Proto-plus：**
```python
serialized = type(campaign).to_json(campaign)
deserialized = type(campaign).from_json(serialized)
```

**Protobuf：**
```python
from google.protobuf.json_format import MessageToJson, Parse

serialized = MessageToJson(campaign)
deserialized = Parse(serialized, campaign)
```

### 字段掩码

**Proto-plus：**
```python
from google.api_core.protobuf_helpers import field_mask

campaign = client.get_type("Campaign")
protobuf_campaign = util.convert_proto_plus_to_protobuf(campaign)
mask = field_mask(None, protobuf_campaign)
```

**Protobuf：**
```python
from google.api_core.protobuf_helpers import field_mask

campaign = client.get_type("Campaign")
mask = field_mask(None, campaign)
```

### 枚举类型检索

**Proto-plus：**
```python
val = client.get_type("CampaignStatusEnum").CampaignStatus.PAUSED
```

**Protobuf：**
```python
val = client.get_type("CampaignStatusEnum").PAUSED
```

**统一接口（推荐）：**
```python
val = client.enums.CampaignStatusEnum.PAUSED
```

### 枚举值检索

**Proto-plus：**
```python
campaign = client.get_type("Campaign")
campaign.status = client.enums.CampaignStatusEnum.PAUSED
print(campaign.status.value)  # 3
```

**Protobuf：**
```python
campaign = client.get_type("Campaign")
status_enum = client.enums.CampaignStatusEnum
campaign.status = status_enum.PAUSED
print(status_enum.CampaignStatus.Value(campaign.status))
```

### 枚举名称检索

**Proto-plus：**
```python
campaign = client.get_type("Campaign")
campaign.status = client.enums.CampaignStatusEnum.PAUSED
print(campaign.status.name)  # 'PAUSED'
```

**Protobuf：**
```python
campaign = client.get_type("Campaign")
status_enum = client.enums.CampaignStatusEnum
campaign.status = status_enum.PAUSED
status_enum.CampaignStatus.Name(campaign.status)
```

### 重复字段

**附加标量值（两者相同）：**
```python
ad.final_urls.append("https://www.example.com")
```

**附加消息类型：**

**Proto-plus：**
```python
frequency_cap = client.get_type("FrequencyCapEntry")
frequency_cap.cap = 100
campaign.frequency_caps.append(frequency_cap)
```

**Protobuf：**
```python
frequency_cap = campaign.frequency_caps.add()
frequency_cap.cap = 100
```

**分配重复字段：**

**Proto-plus：**
```python
urls = ["https://www.example.com"]
ad.final_urls = urls
```

**Protobuf：**
```python
urls = ["https://www.example.com"]
ad.final_urls[:] = urls
```

### 空白消息检查

**Proto-plus：**
```python
is_empty = bool(campaign)
is_empty = not campaign
```

**Protobuf：**
```python
is_empty = campaign.ByteSize() == 0
```

### 字段存在检查

**Proto-plus：**
```python
has_field = "name" in campaign
```

**Protobuf：**
```python
campaign = client.get_type("Campaign")
campaign.HasField("name")
```

### Protobuf 消息方法

访问不属于 proto-plus 接口的便捷方法：

```python
# 访问 ListFields 方法
protobuf_campaign = util.convert_proto_plus_to_protobuf(campaign)
print(campaign.ListFields())

# 访问 Clear 方法
protobuf_campaign = util.convert_proto_plus_to_protobuf(campaign)
print(campaign.Clear())
```

---

## 保留字段名称

使用 proto-plus 消息时，如果字段名称也是 Python 中的保留字，则字段名称会自动带有尾随下划线。

```python
asset = client.get_type("Asset")
asset.type_ = client.enums.AssetTypeEnum.IMAGE
```

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/protobuf-messages?hl=zh-cn
**最后更新：** 2026-02-11
