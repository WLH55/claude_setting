# IDE 代码补全

> Python 客户端库的 IDE 代码补全功能

---

## 概述

VS Code 和 PyCharm 等 IDE 为 Python 语言提供内置的代码补全功能。

`google-ads-python` 库在运行时使用 `GoogleAdsClient` 类上的 getter 方法动态生成 protobuf 消息类，这可能会抑制依赖于源代码静态分析的 IDE 代码补全功能。

---

## 两种导入方式

### 1. 使用动态导入（不推荐用于代码补全）

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage()

# Campaign 类是动态导入的，IDE 无法读取类定义
campaign = client.get_type("Campaign")
```

**缺点：** IDE 无法读取类定义，代码补全功能受限。

### 2. 使用直接导入（推荐用于代码补全）

```python
from google.ads.googleads.v23.resources import Campaign

# Campaign 类直接导入，IDE 可以读取类定义并提供代码补全
campaign = Campaign()
```

**优点：** IDE 可以读取类定义并提供代码补全建议。

---

## 直接导入的优缺点

### 优点

- IDE 代码补全功能正常工作
- 开发体验更好

### 缺点

1. **难以找到导入路径**：给定类所在的模块并不总是显而易见
2. **版本升级可能中断代码**：生成类的目录结构可能随新版本变化
3. **需要手动初始化服务**：`get_service` 方法会在返回服务之前初始化，直接导入需要手动初始化

---

## 选择建议

| 场景 | 推荐方式 |
|------|---------|
| 日常开发、调试 | 直接导入（代码补全） |
| 生产环境、稳定版本 | 动态导入（版本兼容） |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/code-completion?hl=zh-cn
**最后更新：** 2026-02-11
