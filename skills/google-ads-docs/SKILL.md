---
name: google-ads-docs
description: Google Ads API 文档知识库。当用户询问 Google Ads API 及Google Ads Python客户端 相关问题时使用，包括：API 结构、身份验证、Mutate 操作、GAQL 查询、配额限制、错误处理、问题排查和最佳实践。自动搜索并读取相关文档提供基于官方文档的准确答案。
---

# Google Ads API 文档查询

查询 Google Ads API 文档知识库以回答用户问题。

## 文档索引

查看 [references/README.md](references/README.md) 获取完整的文档目录、搜索关键词和内容摘要。

## 核心文档

| 文档 | 主题 |
|------|------|
| [00-overview.md](references/00-overview.md) | API 概览、导航结构 |
| [01-api-structure.md](references/01-api-structure.md) | 资源、服务、对象层次结构 |
| [02-call-structure.md](references/02-call-structure.md) | 身份验证、请求头 |
| [03-changing-objects.md](references/03-changing-objects.md) | Mutate 操作、批量操作 |
| [04-retrieving-objects.md](references/04-retrieving-objects.md) | GAQL、Search/SearchStream |
| [06-best-practices-overview.md](references/06-best-practices-overview.md) | 最佳实践、性能优化 |
| [07-quotas-limits.md](references/07-quotas-limits.md) | API 配额、速率限制 |
| [08-system-limits.md](references/08-system-limits.md) | 账号限制、资源限制 |
| [09-troubleshooting.md](references/09-troubleshooting.md) | 问题排查流程 |
| [10-error-types.md](references/10-error-types.md) | 错误分类 |
| [11-understand-api-errors.md](references/11-understand-api-errors.md) | 错误模型详解 |

### Python 客户端库文档

| 文档 | 主题 |
|------|------|
| [python-client/01-configuration.md](references/python-client/01-configuration.md) | 配置 - YAML、环境变量、dict |
| [python-client/02-authentication.md](references/python-client/02-authentication.md) | 身份验证 - OAuth2、服务账号 |
| [python-client/03-code-completion.md](references/python-client/03-code-completion.md) | IDE 代码补全 |
| [python-client/04-proto-getters.md](references/python-client/04-proto-getters.md) | 服务和类型 getter |
| [python-client/05-field-masks.md](references/python-client/05-field-masks.md) | 字段掩码 |
| [python-client/06-logging.md](references/python-client/06-logging.md) | 日志记录 |
| [python-client/07-resource-names.md](references/python-client/07-resource-names.md) | 资源名称 |
| [python-client/08-empty-message-fields.md](references/python-client/08-empty-message-fields.md) | 空消息字段 |
| [python-client/09-protobuf-messages.md](references/python-client/09-protobuf-messages.md) | Protobuf 消息 |
| [python-client/10-timeouts.md](references/python-client/10-timeouts.md) | 超时 |
| [python-client/11-dependencies.md](references/python-client/11-dependencies.md) | 依赖项 |
| [python-client/12-streaming-iterators.md](references/python-client/12-streaming-iterators.md) | 流式迭代器 |
| [python-client/13-proxy.md](references/python-client/13-proxy.md) | 代理 |
| [python-client/14-optional-request-headers.md](references/python-client/14-optional-request-headers.md) | 可选请求标头 |

## 工作流程

1. **识别主题** - 确定相关文档
2. **读取文档** - 使用索引或直接读取相关文件
3. **提供答案** - 基于文档内容回答

## 快速主题映射

| 问题类型 | 相关文档 |
|---------|---------|
| 身份验证、令牌 | 02-call-structure.md, python-client/02-authentication.md |
| 创建/更新/删除 | 03-changing-objects.md |
| 查询、GAQL、Search | 04-retrieving-objects.md |
| 配额、限制 | 07-quotas-limits.md |
| 错误、异常 | 10-error-types.md, 11-understand-api-errors.md |
| 最佳实践 | 06-best-practices-overview.md |
| Python 客户端配置 | python-client/01-configuration.md |
| Python 日志 | python-client/06-logging.md |
| Python 超时 | python-client/10-timeouts.md |
