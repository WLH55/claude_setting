---
name: fastapi-scaffold
description: FastAPI 项目脚手架生成器。根据 FASTAPI_FRAMEWORK_TEMPLATE.md 模板快速创建完整的 FastAPI 项目框架。包含：Pydantic V2 配置管理（多环境支持）、全局异常处理（_log_exception + register_exception_handlers）、日志系统（gzip 压缩轮转）、路由层和 Service 层分离架构（路由层只处理参数校验，Service 层处理异常）。触发条件：用户请求创建/初始化/搭建 FastAPI 项目时使用，如"创建一个 FastAPI 项目"、"帮我搭建 FastAPI 框架"、"初始化 FastAPI 项目"、"生成 FastAPI 项目结构"等。
---

# FastAPI 项目脚手架

根据 FASTAPI_FRAMEWORK_TEMPLATE.md 模板快速创建完整的 FastAPI 项目框架。

## 使用方式

当用户需要创建新的 FastAPI 项目时触发：
- "创建一个 FastAPI 项目"
- "帮我搭建 FastAPI 框架"
- "初始化 FastAPI 项目"
- "生成 FastAPI 项目结构"

## 工作流程

1. 询问项目名称和目录位置
2. 创建完整的项目目录结构
3. 从 `assets/` 复制所有模板文件到目标目录
4. 根据用户输入替换项目名称等占位符

## 项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                   # 应用入口（create_app 模式）
│   ├── config/                   # 配置包
│   │   ├── __init__.py
│   │   ├── settings.py           # Pydantic V2 配置管理
│   │   ├── dependencies.py       # 依赖注入
│   │   ├── exceptions.py         # 异常类 + 全局处理器
│   │   ├── schemas.py            # ApiResponse + ResponseCode
│   │   └── logger_config.py      # 日志配置（gzip 压缩轮转）
│   ├── routers/                  # API 路由
│   │   ├── __init__.py
│   │   └── example.py            # 示例路由（CRUD）
│   └── services/                 # 业务逻辑层
│       ├── __init__.py
│       └── example_service.py    # 示例 Service（带异常处理）
├── storage/
│   └── logs/                     # 日志目录
├── .env.development              # 开发环境
├── .env.production               # 生产环境
├── .env.example                  # 环境变量模板
├── .gitignore
├── requirements.txt
└── README.md
```

## 核心特性

### 分层职责规范
- **路由层**：只处理参数校验，不处理 try/except
- **Service 层**：处理业务逻辑和异常捕获，抛出 BusinessValidationException

### 配置管理
- Pydantic V2 `model_config`
- 多环境支持（development/production/test）
- 通过 `ENVIRONMENT` 环境变量切换

### 异常处理
- `_log_exception` 记录请求信息（IP、方法、路径、查询参数、请求体）
- `register_exception_handlers(app)` 注册全局处理器
- BusinessValidationException → 400
- Exception → 500

### 日志系统
- 格式：`[%(asctime)s] %(levelname)s: %(message)s`
- 按日期轮转（每天午夜）
- gzip 压缩旧日志
- 自动清理过期日志

## 模板文件

所有模板文件位于 `assets/fastapi-template/` 目录。创建项目时直接复制整个目录。
