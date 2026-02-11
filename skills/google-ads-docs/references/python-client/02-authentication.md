# 身份验证和授权

> Google Ads API 使用 OAuth 2.0 协议进行身份验证和授权

---

## 概述

与其他 Google API 一样，Google Ads API 使用 OAuth 2.0 协议进行身份验证和授权。借助 OAuth 2.0，您的 Google Ads API 客户端应用就能够访问用户的 Google Ads 账号，而无需处理或存储用户的登录信息。

---

## OAuth 工作流

使用 Google Ads API 时有三种常见的工作流程：

---

## 服务账号流程

如果您的工作流程不需要任何人工互动，建议采用此工作流程。

### 配置步骤

1. 用户将服务账号添加到其 Google Ads 账号
2. 应用使用服务账号的凭据来管理账号

### YAML 文件配置

```yaml
json_key_file_path: JSON_KEY_FILE_PATH
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage()
```

### dict 配置

```python
from google.ads.googleads.client import GoogleAdsClient

configuration = {
    # ...
    "json_key_file_path": JSON_KEY_FILE_PATH
    # ...
}

client = GoogleAdsClient.load_from_dict(configuration)
```

### 环境变量配置

```bash
export GOOGLE_ADS_JSON_KEY_FILE_PATH=JSON_KEY_FILE_PATH
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_env()
```

**注意：** 如果存在 `json_key_file_path` 且 `use_application_default_credentials` 为 `False`，库将自动使用服务账号流程。

---

## 单用户身份验证流程

如果您无法使用服务账号，则可以使用此工作流。

### 配置步骤

1. 向单个用户授予访问权限
2. 用户运行工具生成 OAuth 2.0 凭据

### 使用 gcloud CLI 工具（推荐）

1. 按照生成凭据文档设置应用默认凭据 (ADC)
2. 添加配置：

```yaml
use_application_default_credentials: true
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage()
```

### dict 配置

```python
from google.ads.googleads.client import GoogleAdsClient

configuration = {
    # ...
    "use_account_default_credentials": True
    # ...
}

client = GoogleAdsClient.load_from_dict(configuration)
```

### 环境变量配置

```bash
export GOOGLE_ADS_USE_ACCOUNT_DEFAULT_CREDENTIALS=true
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_env()
```

### 直接处理 OAuth 令牌

1. 设置控制台项目并下载包含客户端 ID 和密钥的 JSON 文件
2. 克隆 Python 客户端库：

```bash
$ git clone https://github.com/googleads/google-ads-python.git
$ cd google-ads-python
```

3. 执行示例生成刷新令牌：

```bash
$ python examples/authentication/generate_user_credentials.py -c PATH_TO_CREDENTIALS_JSON
```

4. 配置库：

```yaml
client_id: INSERT_OAUTH2_CLIENT_ID_HERE
client_secret: INSERT_OAUTH2_CLIENT_SECRET_HERE
refresh_token: INSERT_REFRESH_TOKEN_HERE
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage()
```

或使用 dict：

```python
from google.ads.googleads.client import GoogleAdsClient

configuration = {
    # ...
    "client_id": INSERT_OAUTH2_CLIENT_ID_HERE
    "client_secret": INSERT_OAUTH2_CLIENT_SECRET_HERE
    "refresh_token": INSERT_REFRESH_TOKEN_HERE
    # ...
}

client = GoogleAdsClient.load_from_dict(configuration)
```

---

## 多用户身份验证流程

如果您的应用允许用户登录并授权，建议采用此工作流程。

### 使用 dict 配置

`dict` 是在运行时获取凭据时的最简单配置机制：

```python
from google.ads.googleads.client import GoogleAdsClient

configuration = {
  # ...
  "client_id": client_id
  "client_secret": client_secret
  "refresh_token": refresh_token
  # ...
}

client = GoogleAdsClient.load_from_dict(configuration)
```

---

## 手动身份验证

您可以直接实例化客户端类并手动提供凭据：

```python
from google.ads.googleads.client import GoogleAdsClient
from google.auth import default

# 检索 ADC
credentials = default(scopes=["https://www.googleapis.com/auth/adwords"])

client = GoogleAdsClient(
  credentials=credentials,
  # ... 插入其余参数
)
```

---

## 多账号管理

用户通常会通过直接访问账号或通过 Google Ads 经理账号来管理多个 Google Ads 账号。

### 相关代码示例

1. `get_account_hierarchy` - 检索经理账号下的所有账号
2. `list_accessible_customers` - 检索用户有权直接访问的所有账号

这些账号可用作 `login_customer_id` 设置的有效值。

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/authentication?hl=zh-cn
**最后更新：** 2026-02-11
