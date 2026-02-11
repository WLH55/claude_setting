# 流式迭代器

> GoogleAdsService.search_stream 的作用域管理

---

## 概述

调用 `GoogleAdsService.search_stream` 时，系统会返回一个流式响应迭代器。使用此迭代器时，它应保持与 `GoogleAdsService` 客户端相同的作用域，以避免数据流中断或分段错误。

---

## 原理说明

当打开的 `GoogleAdsService` 对象超出范围时，gRPC `Channel` 对象会被垃圾回收。如果在对 `search_stream` 的结果进行迭代时，`GoogleAdsService` 对象已不在作用域内，则 `Channel` 对象可能已被销毁，从而导致迭代器尝试检索下一个值时出现未定义的行为。

---

## 错误用法

```python
def stream_response(client, customer_id, query):
    return client.get_service("GoogleAdsService", version="v23").search_stream(customer_id, query=query)

def main(client, customer_id):
    query = "SELECT campaign.name FROM campaign LIMIT 10"
    response = stream_response(client, customer_id, query=query)
    # 在与创建服务对象不同的作用域中访问迭代器
    try:
        for batch in response:
            # 遍历响应，会出现未定义行为
```

**问题：** `GoogleAdsService` 对象是在访问迭代器的范围之外创建的。在迭代器使用完整个响应之前，`Channel` 对象可能会被销毁。

---

## 正确用法

```python
def main(client, customer_id):
    ga_service = client.get_service("GoogleAdsService", version="v23")
    query = "SELECT campaign.name FROM campaign LIMIT 10"
    response = ga_service.search_stream(customer_id=customer_id, query=query)
    # 在与创建服务对象相同的作用域中访问迭代器
    try:
        for batch in response:
            # 成功遍历响应
```

**关键：** 在使用期间，流式迭代器应保持与 `GoogleAdsService` 客户端相同的范围。

---

## 最佳实践

| 做法 | 说明 |
|------|------|
| **保持服务对象在作用域内** | 确保在遍历流式响应时，服务对象未被垃圾回收 |
| **使用函数级作用域** | 在同一个函数内创建服务对象和遍历响应 |
| **避免返回迭代器** | 不要跨函数边界返回流式迭代器 |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/streaming-iterators?hl=zh-cn
**最后更新：** 2026-02-11
