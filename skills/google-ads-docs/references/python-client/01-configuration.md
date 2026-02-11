# 配置

> Google Ads Python 客户端库的配置方法

---

## 概述

您可以通过多种不同的方式配置 Python 客户端库。

---

## 使用 YAML 文件进行配置

您可以指定在初始化客户端时使用的 YAML 文件，该文件包含发出请求所需的必要身份验证信息。

### 基本用法

如果未提供路径，库将在 `$HOME` 目录中查找 `google-ads.yaml` 文件：

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage()
```

### 指定文件路径

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage("path/to/google-ads.yaml")
```

### 使用环境变量指定路径

```python
import os

os.environ["GOOGLE_ADS_CONFIGURATION_FILE_PATH"] = "path/to/google-ads.yaml"
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage()
```

**优先级：** 传递给方法的路径 > 环境变量

---

## 使用环境变量进行配置

环境变量应与 `google-ads.yaml` 文件中定义的变量同名，但全部大写并以 `GOOGLE_ADS_` 前缀开头。

### 在 .bashrc 中设置

```bash
# 将配置追加到 .bashrc 文件
$ echo "export GOOGLE_ADS_CLIENT_ID=1234567890" >> ~/.bashrc
# 更新 bash 环境
$ source ~/.bashrc
```

### 直接在终端设置

```bash
$ export GOOGLE_ADS_CLIENT_ID=1234567890
$ echo $GOOGLE_ADS_CLIENT_ID
1234567890
```

### 使用环境变量初始化

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_env()
```

### 配置日志记录（通过环境变量）

日志配置值必须是 JSON 对象：

```bash
export GOOGLE_ADS_LOGGING='{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "default_fmt": {
      "format": "[%(asctime)s - %(levelname)s] %(message).5000s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    }
  },
  "handlers": {
    "default_handler": {
      "class": "logging.StreamHandler",
      "formatter": "default_fmt"
    }
  },
  "loggers": {
    "": {
      "handlers": ["default_handler"],
      "level": "INFO"
    }
  }
}'
```

---

## 使用 YAML 字符串进行配置

如果已将 YAML 文件读入内存，可以直接提供给客户端：

```python
from google.ads.googleads.client import GoogleAdsClient

with open("/path/to/yaml", "rb") as handle:
    yaml = handle.read()

client = GoogleAdsClient.load_from_string(yaml)
```

---

## 使用 dict 进行配置

```python
from google.ads.googleads.client import GoogleAdsClient

credentials = {
    "developer_token": "abcdef123456",
    "refresh_token": "1//0abcdefghijklABCDEF",
    "client_id": "123456-abcdef.apps.googleusercontent.com",
    "client_secret": "aBcDeFgHiJkL"
}

client = GoogleAdsClient.load_from_dict(credentials)
```

---

## 配置字段

### 常规字段

| 字段 | 说明 |
|------|------|
| `refresh_token` | OAuth 刷新令牌 |
| `client_id` | OAuth 客户端 ID |
| `client_secret` | OAuth 客户端密钥 |
| `developer_token` | 用于访问 API 的开发者令牌 |
| `login_customer_id` | 登录客户 ID |
| `linked_customer_id` | 关联客户 ID |
| `json_key_file_path` | 本地私钥文件的路径（服务账号） |
| `impersonated_email` | 用作委托方的账号电子邮件（服务账号） |
| `logging` | 日志记录配置 |
| `http_proxy` | HTTP 代理配置 |
| `use_proto_plus` | 是否使用 proto-plus 消息 |

### 环境变量名称

| 字段 | 环境变量名称 |
|------|-------------|
| `developer_token` | `GOOGLE_ADS_DEVELOPER_TOKEN` |
| `refresh_token` | `GOOGLE_ADS_REFRESH_TOKEN` |
| `client_id` | `GOOGLE_ADS_CLIENT_ID` |
| `client_secret` | `GOOGLE_ADS_CLIENT_SECRET` |
| `login_customer_id` | `GOOGLE_ADS_LOGIN_CUSTOMER_ID` |
| `linked_customer_id` | `GOOGLE_ADS_LINKED_CUSTOMER_ID` |
| `json_key_file_path` | `GOOGLE_ADS_JSON_KEY_FILE_PATH` |
| `impersonated_email` | `GOOGLE_ADS_IMPERSONATED_EMAIL` |
| `logging` | `GOOGLE_ADS_LOGGING` |
| `http_proxy` | `GOOGLE_ADS_HTTP_PROXY` |
| `use_proto_plus` | `GOOGLE_ADS_USE_PROTO_PLUS` |

### 日志记录字段

日志记录配置字段直接派生自 Python 的 `logging.config` 模块：

| 字段 | 说明 |
|------|------|
| `version` | 架构版本的整数值 |
| `disable_existing_loggers` | 是否停用在应用其他位置配置的记录器 |
| `formatters` | 定义不同类型格式化程序的字典 |
| `handlers` | 定义不同处理程序的字典 |
| `loggers` | 定义不同类型日志记录器的字典 |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/configuration?hl=zh-cn
**最后更新：** 2026-02-11
