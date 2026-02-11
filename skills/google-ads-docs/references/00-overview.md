# Google Ads API 概览

> **重要提示**：本指南适用于已熟悉 Google Ads 的用户。其他用户可能需要先查看有关帐号组织方式的帮助中心文章，以了解帐号的关键组成部分及其组织方式。

## API 定位

本系列中的指南概述了 Google Ads API 中提供的对象、方法和服务。阅读这些指南后，您将了解以下重要概念：

### 1. Google Ads API 的结构
- API 的整体架构设计
- 各组件之间的关系

### 2. 用于修改对象的 API 服务
- 创建、更新、删除广告对象的方法
- 管理广告系列、广告组、广告等实体的服务

### 3. 用于检索对象及其效果统计信息的 API 服务
- 获取广告对象数据
- 查询性能指标和统计数据

### 4. 用于检索 API 元数据的 API 服务
- 获取 API 结构信息
- 了解可用的字段和资源

### 5. 如何使用 cURL 调用 API
- 使用命令行工具进行 API 调用的示例

---

## 导航结构

该文档还包含了完整的导航结构，涵盖了以下主要主题领域：

### 快速入门
- 概览
- 开发者令牌
- 客户端库
- OAuth 云项目
- OAuth 客户端库
- 刷新令牌
- 首次调用

### 核心概念
- API 结构
- 更改并检查对象
- 检索对象
- 资源元数据
- 调用结构
- API 调用示例

### OAuth 认证
- 概览
- 云项目
- 客户端库
- 优化请求
- 服务帐号
- 内部
- Playground

### 报告功能
- 概览
- 示例
- 条件指标
- 零展示

### 查询语言（Google Ads Query Language - GAQL）
- 概览
- 查询语法
- 查询结构
- 日期范围
- 排序和限制结果
- 互动式查询构建工具

### 转变
- 概览
- 资源转变
- 批量转变
- 最佳做法

### 广告管理
- 广告系列管理
- 定位设置
- 结算设置
- 帐号管理
- 转化跟踪

### 特定广告类型
- 购物广告
- 酒店广告
- 应用广告系列

### 最佳实践
- API 限制和配额
- 速率限制
- 问题排查
- 常见错误

---

## API 类型

Google Ads API 是一个带有 REST 绑定的 gRPC API：

| 方式 | 说明 | 推荐度 |
|------|------|--------|
| **gRPC** | Protocol Buffers + HTTP/2 | ⭐ 首选 |
| **REST** | JSON + HTTP 1.1 | ⚠️ 可选 |

---

## 文档主题映射

| 主题 | 文档 | 说明 |
|------|------|------|
| API 结构 | [01-api-structure.md](./01-api-structure.md) | 资源、服务、对象层次结构 |
| 调用结构 | [02-call-structure.md](./02-call-structure.md) | 请求头、授权、调用方式 |
| 更改对象 | [03-changing-objects.md](./03-changing-objects.md) | Mutate 操作、批量操作 |
| 检索对象 | [04-retrieving-objects.md](./04-retrieving-objects.md) | GAQL、Search/SearchStream |
| 字段服务 | [05-field-service.md](./05-field-service.md) | GoogleAdsFieldService 元数据 |

---

**文档来源：** https://developers.google.com/google-ads/api/docs/concepts/overview?hl=zh-cn
**最后更新：** 2026-02-11
