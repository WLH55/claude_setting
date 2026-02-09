# 通用 FastAPI 项目结构文档生成计划

## 任务概述
基于当前项目的优秀架构实践，整理一份通用的 FastAPI 项目结构文档，供其他项目快速构建时参考。

## 交付物
- **文件路径**: `PROJECT_STRUCTURE.md`
- **位置**: 项目根目录
- **受众**: 有经验的开发者

## 文档结构设计

### 1. 项目概述
- 快速介绍项目定位（FastAPI 微服务/网关）
- 核心技术栈
- 架构设计理念（原子化架构、分层设计）

### 2. 目录结构树
```
project-name/
├── app/                        # 核心应用代码
│   ├── routers/                # API 路由模块
│   ├── internal/               # 内部客户端/工具
│   ├── templates/              # 模板文件
│   └── ...
├── tests/                      # 测试代码
├── docs/                       # 项目文档
├── storage/                    # 运行时数据（不提交）
├── .env.example                # 环境变量模板
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 构建
└── ...
```

### 3. 核心目录详解
- **app/**: 按功能模块组织
  - `main.py`: 应用入口、生命周期管理
  - `config.py`: 统一配置管理
  - `dependencies.py`: 依赖注入
  - `exceptions.py`: 异常定义
  - `schemas.py`: 响应模型
  - `logger_config.py`: 日志配置
  - `middleware.py`: 中间件
- **app/routers/**: 按业务/平台划分的子目录
- **app/internal/**: 第三方客户端、工具函数

### 4. 分层架构设计
```
Router Layer (路由层)
    ↓ 参数验证、拼装、响应封装
Client Layer (客户端层)
    ↓ 业务方法封装、认证处理
HttpClient Base (基类层)
    ↓ HTTP 请求、连接池、异常处理
```

### 5. 关键设计模式
- 依赖注入模式
- 连接池复用
- 统一响应格式
- 异常统一处理
- 签名验证机制

### 6. 代码模板示例
- HttpClient 基类模板
- 客户端实现模板（Bearer Token / 签名认证）
- 路由接口模板
- 依赖注入模板

### 7. 配置管理
- Pydantic Settings 配置模式
- python-dotenv 最佳实践
- 环境变量优先级

### 8. 新增模块步骤清单
- 1. 配置 → 2. 客户端 → 3. 依赖注入 → 4. 路由 → 5. 生命周期 → 6. 注册

### 9. Docker 容器化
- 多阶段构建优化
- docker-compose 编排

### 10. 最佳实践
- 代码规范
- 测试策略
- 日志管理
- 安全考虑

## 执行步骤
1. 创建 `PROJECT_STRUCTURE.md` 文件
2. 按照上述结构编写完整文档
3. 确保内容简洁专业，适合有经验的开发者快速参考
