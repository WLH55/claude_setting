# 代理

> 配置 Google Ads API 的代理设置

---

## 概述

如果您需要通过代理连接到 Google Ads API，可以通过在 `google-ads.yaml` 文件中设置 `http_proxy` 配置来实现。

---

## YAML 配置

```yaml
# Proxy configuration
###############################################################################
# Below you can specify an optional proxy configuration to be used by         #
# requests. If you don't have username and password, just specify host and    #
# port.                                                                       #
###############################################################################
http_proxy: INSERT_PROXY_HERE
```

### 示例

```yaml
http_proxy: http://user:pass@localhost:8082
```

或（无认证）：

```yaml
http_proxy: http://localhost:8082
```

---

## 编程方式配置

### 使用 dict 配置

```python
config = {
  ...
  "http_proxy": "INSERT_PROXY_HERE",
}
googleads_client = GoogleAdsClient.load_from_dict(config)
```

### 使用环境变量

```bash
export GOOGLE_ADS_HTTP_PROXY=http://user:pass@localhost:8082
```

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_env()
```

---

## 配置方法对比

| 方法 | 配置位置 |
|------|---------|
| YAML 文件 | `http_proxy: INSERT_PROXY_HERE` |
| dict | `{"http_proxy": "INSERT_PROXY_HERE"}` |
| 环境变量 | `GOOGLE_ADS_HTTP_PROXY` |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/proxy?hl=zh-cn
**最后更新：** 2026-02-11
