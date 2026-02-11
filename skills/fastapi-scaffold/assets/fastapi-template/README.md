# FastAPI 项目

基于 FastAPI 框架模板创建的项目。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 开发环境
cp .env.example .env.development
# 编辑 .env.development
```

### 3. 运行应用

```bash
python -m app.main
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
├── app/
│   ├── main.py              # 应用入口
│   ├── config/              # 配置包
│   │   ├── settings.py      # 配置管理
│   │   ├── exceptions.py    # 异常处理
│   │   ├── schemas.py       # 响应模型
│   │   └── logger_config.py # 日志配置
│   ├── routers/             # API 路由
│   └── services/            # 业务逻辑层
├── storage/logs/            # 日志目录
└── requirements.txt
```

## 分层职责

- **路由层**：只处理参数校验，不处理 try/except
- **Service 层**：处理业务逻辑和异常捕获
