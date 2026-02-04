# RunPod Serverless Hello World Demo

## 概述
创建一个简单的 RunPod Serverless 部署 demo，实现 Hello World 功能。

## 文件变更

### 新增文件

| 文件路径 | 描述 |
|---------|------|
| `handler.py` | RunPod Serverless 处理函数，接收输入并返回结果 |
| `Dockerfile` | Docker 镜像构建配置 |
| `test_input.json` | 本地测试输入文件 |
| `requirements.txt` | Python 依赖列表 |
| `README.md` | 使用说明文档 |

### 修改文件
- `main.py` - 可以保留或删除（PyCharm 默认文件，与项目无关）

## 实现步骤

### 1. 创建 handler.py
- 实现符合 RunPod 规范的 handler 函数
- 处理 input 中的 prompt 参数
- 添加可选的 seconds 参数用于模拟处理时间
- 返回处理结果

### 2. 创建 Dockerfile
- 基于 python:3.10-slim 镜像
- 安装 runpod 依赖
- 复制 handler.py 到容器
- 设置启动命令

### 3. 创建测试文件
- test_input.json: 包含示例输入数据

### 4. 创建 requirements.txt
- 列出项目依赖

### 5. 创建 README.md
- 项目说明
- 本地测试步骤
- 构建和推送镜像步骤
- RunPod 控制台部署步骤
- 端点测试说明

## 后续步骤（用户需手动执行）

1. **本地测试**
   ```bash
   pip install -r requirements.txt
   python handler.py
   ```

2. **构建 Docker 镜像**
   ```bash
   docker build -t your-dockerhub-username/runpod-demo:latest .
   ```

3. **推送到 Docker Hub**
   ```bash
   docker login
   docker push your-dockerhub-username/runpod-demo:latest
   ```

4. **在 RunPod 控制台部署**
   - 进入 Serverless -> New Endpoint
   - Import from Docker Registry
   - 输入镜像 URL
   - 配置 GPU（可选）
   - 部署端点

5. **测试端点**
   - 在 RunPod 控制台的 Requests 标签页测试
