# 日志记录

> Python 客户端库的日志记录配置

---

## 概述

该库可配置为记录与 Google Ads API 的互动。您可以记录详细的请求和响应，或者记录简洁的摘要消息。

---

## 日志配置方法

### 方法一：通过配置文件

日志配置通过客户端库配置指定。

### 方法二：以编程方式配置

```python
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s - %(levelname)s] %(message).5000s')
logging.getLogger('google.ads.googleads.client').setLevel(logging.INFO)
```

**重要提示：** 客户端日志记录器在客户端初始化时进行配置。对日志记录配置的后续更改将被忽略。请确保在客户端初始化之前调用上述代码行。

---

## 日志级别

| 级别 | 请求成功 | 失败的请求 |
|------|----------|-----------|
| `DEBUG` | 包含 JSON 格式的完整请求和响应对象 | 包含完整请求和异常对象（JSON 格式） |
| `INFO` | 包含特定请求和响应字段的简明摘要 | 包含完整请求和异常对象（JSON 格式） |
| `WARNING` | 无 | 简明摘要，包含具体请求信息、异常状态和消息 |

**说明：**
- 设置为 `WARNING`：只能看到与失败请求相关的简明消息
- 设置为 `DEBUG`：可以看到所有可能类型的日志

---

## 记录到文件

可以通过管道将日志消息发送到文件：

```bash
python get_campaigns.py -c $CLIENT_ID 2> example.log
```

---

## 日志记录拦截器

Python 客户端库使用 gRPC 拦截器来访问和记录请求和响应详细信息。

您可以创建具有自定义逻辑的 gRPC 拦截器来设置自己的自定义日志记录。详见日志记录指南。

---

## 日志配置示例

### YAML 配置

```yaml
logging:
  version: 1
  disable_existing_loggers: false
  formatters:
    default_fmt:
      format: '[%(asctime)s - %(levelname)s] %(message).5000s'
      datefmt: '%Y-%m-%d %H:%M:%S'
  handlers:
    default_handler:
      class: logging.StreamHandler
      formatter: default_fmt
  loggers:
    '':
      handlers: [default_handler]
      level: INFO
```

### 环境变量配置

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

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/logging?hl=zh-cn
**最后更新：** 2026-02-11
