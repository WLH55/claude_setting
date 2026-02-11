# Google Ads API 调用结构

> 本指南介绍了所有 API 调用的常见结构。如果您使用客户端库与 API 进行互动，则无需了解底层请求的详细信息。

## API 调用方式

Google Ads API 是一个带有 REST 绑定的 gRPC API。这意味着有两种方法可以调用此 API：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Ads API 调用方式                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐         ┌────────────────────┐        │
│  │     gRPC (首选)     │         │     REST (可选)    │        │
│  └────────────────────┘         └────────────────────┘        │
│                                                                 │
│  1. Protocol Buffers            1. JSON                        │
│  2. HTTP/2                      2. HTTP 1.1                    │
│  3. 高性能                      3. 易用                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 资源名称

API 中的大多数对象都通过其**资源名称字符串**进行标识。使用 REST 接口时，这些字符串也可用作网址。

### 资源名称格式

```
customers/{customer_id}/{resource_type}/{resource_id}
```

**示例：**
```
customers/1234567890/campaigns/987654
```

---

## 复合 ID

如果对象的 ID 不具有全局唯一性，则在构建该对象的复合 ID 时，要在前面加上其父级的 ID 和波浪号 (`~`)。

### 复合 ID 构成

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ParentID   +   "~"   +   ChildID                         │
│   (父级ID)           (子级ID)                              │
│                                                             │
│   示例: 123~45678                                          │
│         │    │                                              │
│         │    └── AdGroupAdId (广告组广告ID)                │
│         └── AdGroupId (广告组ID)                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ID 唯一性范围

| 对象 | ID 类型 | 唯一性范围 |
|------|---------|-----------|
| Customer | 单一ID | 全局 |
| Campaign | 单一ID | 全局 |
| AdGroup | 单一ID | 全局 |
| Ad | 复合ID | 广告组内 |
| AdGroupCriterion | 复合ID | 广告组内 |

---

## 请求标头

### 1. Authorization（授权）

**格式：**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**说明：**
- 必须添加 OAuth2 访问令牌
- 用于标识代表客户操作的经理账号或直接管理自己账号的广告客户
- 访问令牌在获得后一小时之内有效
- 客户端库会自动刷新过期令牌

**错误处理：**
- `USER_PERMISSION_DENIED` - 用户无权访问指定客户账号

### 2. developer-token（开发者令牌）

**格式：**
```
developer-token: ABcdeFGH93KL-NOPQ_STUv
```

**说明：**
- 由 22 个字符组成的字符串
- 用于唯一标识 Google Ads API 开发者

### 3. login-customer-id（登录客户 ID）

**格式：**
```
login-customer-id: 1234567890
```

**说明：**
- 在请求中使用的授权客户的客户 ID，不带连字符 (`-`)
- 如果您通过经理账号访问客户账号，则此标头是**必填字段**
- 必须设置为经理账号的客户 ID
- 如果未添加此标头，则默认为**执行操作的客户**

**关键概念：**

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Ads 账号结构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   经理账号 (Manager Account)                                │
│        ID: 3555775829                                        │
│        │                                                     │
│        ├─── 子账号 A: 5454107876                            │
│        ├─── 子账号 B: 7073039329                            │
│        └─── 子账号 C: 5531273254                            │
│                                                             │
│   login-customer-id = 3555775829 (经理账号ID)                │
│   customer-id = 5454107876 (要操作的目标账号)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. linked-customer-id（关联客户 ID）

**说明：**
- 此标头仅供**第三方应用分析工具提供商**使用
- 用于上传转化数据到关联的 Google Ads 账号

---

## 响应标头

### request-id（请求 ID）

对相应请求进行唯一标识的字符串，用于调试和问题排查。

**建议：** 出于调试目的考虑，建议记录此值。

---

## 完整请求示例

### 使用 cURL 调用 API

```bash
curl -X POST "https://googleads.googleapis.com/v18/customers/1234567890/campaigns:mutate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "developer-token: ABcdeFGH93KL-NOPQ_STUv" \
  -H "login-customer-id: 9876543210" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [
      {
        "create": {
          "name": "新广告系列",
          "status": "PAUSED",
          "advertising_channel_type": "SEARCH"
        }
      }
    ]
  }'
```

---

## Python 客户端库使用

### 初始化客户端

```python
from google.ads.googleads.client import GoogleAdsClient

# 方式 1: 从字典加载
config_dict = {
    "developer_token": "ABcdeFGH93KL-NOPQ_STUv",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "login_customer_id": "3555775829",  # 经理账号ID
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config_dict)

# 方式 2: 从 YAML 文件加载
# client = GoogleAdsClient.load_from_storage("google-ads.yaml")
```

### 发起 API 请求

```python
# 获取服务
campaign_service = client.get_service("CampaignService")

# 构造 mutate 请求
mutate_operation = client.get_type("CampaignOperation")
mutate_operation.create = client.get_type("Campaign")
mutate_operation.create.name = "新广告系列"
mutate_operation.create.status = "PAUSED"
mutate_operation.create.advertising_channel_type = "SEARCH"

# 发送请求
response = campaign_service.mutate_campaigns(
    customer_id="1234567890",
    operations=[mutate_operation]
)
```

---

## FastAPI 集成注意事项

### 在 FastAPI 中的调用方式

```
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI + Google Ads API                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   async def route():                def route():             │
│       │                            │                        │
│       ▼                            ▼                        │
│   await ...                  Google Ads API 调用               │
│   (非阻塞)                    (同步阻塞)                     │
│       │                            │                        │
│       ▼                            ▼                        │
│   继续处理                      线程池中执行               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 推荐做法

| 场景 | 路由层类型 | 说明 |
|------|-----------|------|
| **少量请求** | `def` | FastAPI 自动放线程池 |
| **高并发** | `async def` + `run_in_executor` | 显式控制线程池 |

**示例：**

```python
# 方案 1: 使用 def（简单）
def get_campaigns(client: GoogleAdsClientDep) -> ApiResponse:
    campaigns = get_account_campaigns(client, account_id)
    return ApiResponse.success(data=campaigns)

# 方案 2: 使用 async + run_in_executor（灵活）
async def get_campaigns(client: GoogleAdsClientDep) -> ApiResponse:
    loop = asyncio.get_event_loop()
    campaigns = await loop.run_in_executor(
        None, get_account_campaigns, client, account_id
    )
    return ApiResponse.success(data=campaigns)
```

---

## 相关文档

- [API 结构](./01-api-structure.md)
- [更改对象](./03-changing-objects.md)
- [检索对象](./04-retrieving-objects.md)

---

**文档来源：** https://developers.google.com/google-ads/api/docs/concepts/call-structure?hl=zh-cn
**最后更新：** 2025-12-11 (UTC)
