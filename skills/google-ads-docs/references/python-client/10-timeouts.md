# 超时

> Python 客户端库的超时配置

---

## 概述

Python 客户端库未指定任何默认超时，gRPC 传输层也没有指定任何默认值。这意味着，默认情况下，Python 版客户端库会将超时行为完全委托给服务器。

---

## 超时限制

您可以将超时设置为 2 小时或更长时间，但 API 可能仍会超时处理运行时间极长的请求，并返回 `DEADLINE_EXCEEDED` 错误。

**建议：** 如果长时间运行的请求成为一个问题，可以拆分查询并并行执行这些分块。

---

## 流式调用超时

唯一使用此类调用的 Google Ads API 服务方法是 `GoogleAdsService.SearchStream`。

```python
def make_server_streaming_call(
    client: GoogleAdsClient, customer_id: str
) -> None:
    """使用自定义客户端超时进行服务器流式调用"""
    ga_service: GoogleAdsServiceClient = client.get_service("GoogleAdsService")
    campaign_ids: List[str] = []

    try:
        search_request: SearchGoogleAdsStreamRequest = client.get_type(
            "SearchGoogleAdsStreamRequest"
        )
        search_request.customer_id = customer_id
        search_request.query = _QUERY
        stream: Iterator[SearchGoogleAdsStreamResponse] = (
            ga_service.search_stream(
                request=search_request,
                # 可选的 timeout 参数指定客户端响应截止时间（秒）
                timeout=_CLIENT_TIMEOUT_SECONDS,
            )
        )

        batch: SearchGoogleAdsStreamResponse
        for batch in stream:
            row: GoogleAdsRow
            for row in batch.results:
                campaign_ids.append(row.campaign.id)

        print("The server streaming call completed before the timeout.")
    except DeadlineExceeded:
        print("The server streaming call did not complete before the timeout.")
        sys.exit(1)
    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed")
        sys.exit(1)

    print(f"Total # of campaign IDs retrieved: {len(campaign_ids)}")
```

---

## 一元调用超时

大多数 Google Ads API 服务方法都使用一元调用，例如 `GoogleAdsService.Search` 和 `GoogleAdsService.Mutate`。

```python
def make_unary_call(client: GoogleAdsClient, customer_id: str) -> None:
    """使用自定义客户端超时进行一元调用"""
    ga_service: GoogleAdsServiceClient = client.get_service("GoogleAdsService")
    campaign_ids: List[str] = []

    try:
        search_request: SearchGoogleAdsRequest = client.get_type(
            "SearchGoogleAdsRequest"
        )
        search_request.customer_id = customer_id
        search_request.query = _QUERY
        results: Iterator[GoogleAdsRow] = ga_service.search(
            request=search_request,
            # 可选的 retry 参数指定重试行为
            retry=Retry(
                # 设置调用的最大累积超时（包括所有重试）
                deadline=_CLIENT_TIMEOUT_SECONDS,
                # 设置首次尝试的超时（最大累积超时的 1/10）
                initial=_CLIENT_TIMEOUT_SECONDS / 10,
                # 设置任何给定尝试的最大超时（最大累积超时的 1/5）
                maximum=_CLIENT_TIMEOUT_SECONDS / 5,
            ),
        )

        row: GoogleAdsRow
        for row in results:
            campaign_ids.append(row.campaign.id)

        print("The unary call completed before the timeout.")
    except DeadlineExceeded:
        print("The unary call did not complete before the timeout.")
        sys.exit(1)
    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed")
        sys.exit(1)

    print(f"Total # of campaign IDs retrieved: {len(campaign_ids)}")
```

---

## 超时参数说明

### timeout 参数（流式调用）

- **类型：** 浮点数（秒）
- **说明：** 如果未设置，客户端不会强制执行超时，通道将保持打开直到响应完成或断开

### retry 参数（一元调用）

- **deadline：** 调用的最大累积超时（包括所有重试）
- **initial：** 首次尝试的超时时间
- **maximum：** 任何给定尝试的最大超时时间

---

**文档来源：** https://developers.google.com/google-ads/api/docs/client-libs/python/timeouts?hl=zh-cn
**最后更新：** 2026-02-11
