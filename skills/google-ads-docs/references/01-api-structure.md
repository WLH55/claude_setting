# Google Ads API 结构

> 本指南介绍了 Google Ads API 的主要构成组件。Google Ads API 由多个资源和服务组成。资源表示 Google Ads 实体，而服务用于检索和处理 Google Ads 实体。

## 一、对象层次结构

Google Ads 账号可以视为对象的层次结构：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Customer (客户/账号)                         │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────────┐                       │
│              │    Campaign (广告系列)   │                       │
│              └─────────────┬───────────┘                       │
│                            │                                   │
│              ┌─────────────┴───────────┐                       │
│              │    AdGroup (广告组)      │                       │
│              └─────────────┬───────────┘                       │
│                            │                                   │
│              ┌─────────────┴───────────┐                       │
│              │  AdGroupAd (广告组广告) │                       │
│              └─────────────────────────┘                       │
│                                                                 │
│   Criteria (条件) - 关键字、年龄段、地理位置                      │
│   Extensions (扩展信息) - 电话号码、地址、促销信息                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 层次结构说明

- **账号的顶级资源是 `customer`**
- **每个客户都包含一个或多个有效广告系列**
- **每个广告系列都包含一个或多个广告组**，用于将广告分组为逻辑集合
- **广告组广告表示您正在投放的广告**。除了应用广告系列（每个广告组只能包含一个广告组广告）之外，每个广告组都包含一个或多个广告组广告

### 条件 (Criteria)

您可以向广告组或广告系列添加一个或多个 `AdGroupCriterion` 或 `CampaignCriterion`。这些表示用于定义广告触发方式的条件。

**条件类型示例：**
- 关键字
- 年龄段
- 地理位置

在广告系列一级定义的条件会影响广告系列中的所有其他资源。您还可以指定整个广告系列的预算和日期。

### 扩展信息 (Extensions)

最后，您可以在**账号、广告系列或广告组一级附加扩展信息**。借助附加信息，您可以向广告添加额外信息，例如：
- 电话号码
- 街道地址
- 促销信息

---

## 二、资源 (Resources)

资源表示 Google Ads 账号中的实体。`Campaign` 和 `AdGroup` 是两个资源示例。

### 2.1 对象 ID

Google Ads 中的每个对象都由其自己的 ID 标识。其中一些 ID 在所有 Google Ads 账号中都是全局唯一的，而另一些 ID 仅在限定范围内是唯一的。

| 对象 ID | 唯一性范围 | 是否全局唯一？ |
|---------|-----------|---------------|
| 预算 ID | 全局 | 是 |
| 广告系列 ID | 全局 | 是 |
| AdGroup ID | 全局 | 是 |
| 广告 ID | 广告组 | 否，但 (`AdGroupId`, `AdId`) 对是全局唯一的 |
| AdGroupCriterion ID | 广告组 | 否，但 (`AdGroupId`, `CriterionId`) 对是全局唯一的 |
| CampaignCriterion ID | 广告系列 | 否，但 (`CampaignId`, `CriterionId`) 对是全局唯一的 |
| 广告附加信息 | 广告系列 | 否，但 (`CampaignId`, `AdExtensionId`) 对是全局唯一的 |
| 标签 ID | 全局 | 是 |
| UserList ID | 全球 | 是 |
| 资产 ID | 全球 | 是 |

> 在为 Google Ads 对象设计本地存储时，这些 ID 规则可能会很有用。

### 多类型对象

某些对象可用于多种实体类型。在这种情况下，对象包含一个描述其内容的 `type` 字段。

**示例：** `AdGroupAd` 可以指文字广告、酒店广告或本地广告等对象。此值可通过 `AdGroupAd.ad.type` 字段访问，并返回 `AdType` 枚举中的值。

### 2.2 资源名称 (resource_name)

每个资源都由一个 `resource_name` 字符串进行了唯一标识，该字符串会将相应资源及其父项连接到路径中。

**广告系列资源名称格式：**
```
customers/customer_id/campaigns/campaign_id
```

**示例：** 在客户 ID 为 `1234567` 的 Google Ads 账号中，对于 ID 为 `987654` 的广告系列，`resource_name` 将是：
```
customers/1234567/campaigns/987654
```

---

## 三、服务 (Services)

服务可让您检索和修改 Google Ads 实体。服务分为三种类型：

| 服务类型 | 说明 | 主要服务 |
|---------|------|---------|
| **修改服务** | 修改对象 | CustomerService, CampaignService, AdGroupService |
| **检索服务** | 获取对象和统计信息 | GoogleAdsService |
| **元数据服务** | 获取 API 元数据 | GoogleAdsFieldService |

### 3.1 修改对象 (Mutate)

此类服务使用 `mutate` 请求修改关联资源类型的实例。此外，它们还提供用于检索单个资源实例的 `get` 请求。

**服务示例：**
- `CustomerService` - 用于修改客户
- `CampaignService` - 用于修改广告系列
- `AdGroupService` - 用于修改广告组

每个 `mutate` 请求都必须包含相应的 `operation` 对象。例如，`CampaignService.MutateCampaigns` 方法需要一个或多个 `CampaignOperation` 实例。

#### 并发转变

**不能同时由多个来源并行修改 Google Ads 对象。**

如果您有多个用户使用您的应用更新同一对象，或者您使用多个线程并行更改 Google Ads 对象，则可能会导致出现错误。

这包括：
- 从同一应用中的多个线程更新对象
- 从不同应用更新对象（例如，您的应用和同时进行的 Google Ads 界面会话）

该 API 不提供在更新之前锁定对象的方法；如果两个来源尝试同时更改某个对象，该 API 会引发 `DatabaseError.CONCURRENT_MODIFICATION_ERROR`。

#### 异步与同步突变

Google Ads API mutate 方法是**同步的**：

| 特性 | 同步 | 异步 |
|------|------|------|
| **执行方式** | 调用后立即执行 | 提交后后台执行 |
| **返回时机** | 等待完成后返回 | 立即返回 |
| **编码复杂度** | 相对简单 | 需要轮询状态 |
| **资源利用** | 可能浪费 | 更高效 |

**异步处理方案：** 使用 `BatchJobService`
- 可对多个服务执行批量操作
- 无需等待操作完成
- 提交后 Google Ads API 服务器会异步执行操作
- 释放进程以执行其他操作
- 可以定期检查作业状态

#### 转变验证

大多数 mutate 请求都可以进行验证，而无需实际针对真实数据执行调用。

**使用方法：** 将请求的可选 `validate_only` 布尔值字段设置为 `true`

**功能：**
- 全面验证请求
- 跳过最终执行
- 如果未发现错误，返回空响应
- 如果验证失败，错误消息会指明失败点

**应用场景：**
- 测试缺少参数和字段值不正确的请求
- 测试广告是否存在常见违规问题
- 发现违反相关政策的问题（字词、标点符号、大写字母或长度）

### 3.2 获取对象和效果统计信息

`GoogleAdsService` 是一项统一的服务，用于同时检索对象和效果统计信息。

**请求类型：**
- `Search` - 标准搜索
- `SearchStream` - 流式搜索（推荐用于大数据量）

**查询要求：**
- 指定要查询的资源
- 要检索的资源属性和效果指标
- 用于过滤请求的谓词
- 用于进一步细分效果统计信息的细分

> 详细信息请参阅 Google Ads 查询语言指南（GAQL）。

### 3.3 检索元数据

`GoogleAdsFieldService` 用于检索有关 Google Ads API 中资源的元数据。

**提供的信息：**
- 资源的可用属性
- 属性的数据类型

此服务提供了构建 `GoogleAdsService` 查询所需的信息。为方便起见，字段参考文档中也提供了 `GoogleAdsFieldService` 返回的信息。

---

## 四、Python 客户端库使用

### 服务调用方式

Google Ads Python 客户端库是**同步**的：

```python
from google.ads.googleads.client import GoogleAdsClient

# 加载客户端
client = GoogleAdsClient.load_from_dict(config_dict)

# 获取服务
ga_service = client.get_service("GoogleAdsService")

# 执行查询（同步阻塞）
stream = ga_service.search_stream(
    customer_id=customer_id,
    query=query
)

# 处理结果
for batch in stream:
    for row in batch.results:
        # 处理每一行
        pass
```

### 在 FastAPI 中的注意事项

```
┌─────────────────────────────────────────────────────────────┐
│              FastAPI 异步 vs Google Ads 同步                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   async def route():                                       │
│       │                                                    │
│       ▼                                                    │
│   def service():           同步阻塞调用                      │
│       │                 GoogleAdsClient.search_stream()     │
│       ▼                                                    │
│   ┌─────────────────┐                                       │
│   │ 阻塞事件循环!    │                                       │
│   │ 其他请求等待    │                                       │
│   └─────────────────┘                                       │
│                                                             │
│   解决方案:                                                 │
│   1. 路由层用 def 而非 async def (FastAPI 自动放线程池)      │
│   2. 或用 run_in_executor 包装同步调用                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**推荐做法：**

```python
# 方案 1: 路由层使用 def（简单）
def get_accounts(client: GoogleAdsClientDep) -> ApiResponse:
    accounts = list_child_accounts(client, ...)
    return ApiResponse.success(data=accounts)

# 方案 2: 使用 run_in_executor（灵活）
async def get_accounts(client: GoogleAdsClientDep) -> ApiResponse:
    loop = asyncio.get_event_loop()
    accounts = await loop.run_in_executor(
        None, list_child_accounts, client, ...
    )
    return ApiResponse.success(data=accounts)
```

---

## 五、关键概念速查

| 概念 | 说明 |
|------|------|
| **Resource** | 表示 Google Ads 实体（如 Campaign、AdGroup） |
| **Service** | 用于检索和修改实体的接口 |
| **Mutate** | 修改对象的操作（同步） |
| **Search/SearchStream** | 查询对象和统计数据 |
| **resource_name** | 资源的路径格式唯一标识符 |
| **validate_only** | 验证请求而不实际执行 |
| **login-customer-id** | 经理账号 ID（必填请求头） |
| **developer-token** | 开发者令牌（22 个字符） |

---

## 六、服务类型对照表

| 服务类型 | 主要服务 | 主要方法 | 用途 |
|---------|---------|---------|------|
| 修改服务 | CustomerService | mutate, get | 修改客户 |
| 修改服务 | CampaignService | mutate, get | 修改广告系列 |
| 修改服务 | AdGroupService | mutate, get | 修改广告组 |
| 检索服务 | GoogleAdsService | search, search_stream | 检索对象和统计 |
| 元数据服务 | GoogleAdsFieldService | - | 获取 API 元数据 |
| 批量服务 | BatchJobService | mutate, query | 批量异步操作 |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/concepts/api-structure?hl=zh-cn
**整理时间：** 2026-02-11
**版本：** Google Ads API v22+
