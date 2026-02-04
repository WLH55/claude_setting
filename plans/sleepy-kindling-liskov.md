# 去掉依赖注入，在 utils.py 中直接实例化 HttpClient

## 方案确认

在 `utils.py` 中直接创建全局 `HttpClient` 实例，工具函数内部直接使用，不需要参数传递。

## 调用链示意图

```
utils.py（模块加载时）
    ↓ 创建全局实例
_http_client = HttpClient()

工具函数内部直接使用
    ↓ 获取底层 client
client = await _http_client.get_client() → httpx.AsyncClient
    ↓ 直接使用
await client.get(url)
```

## 修改文件

### 1. `app/internal/utils.py`

在模块顶部创建全局 HttpClient 实例：

```python
# ========== 全局 HttpClient 实例（用于图片下载等场景）==========
_http_client = HttpClient()

async def close_http_client():
    """关闭全局 HttpClient 连接池"""
    await _http_client.close()
```

修改工具函数，去掉 `http_client` 参数：

#### `download_image`
```python
async def download_image(url: str, filepath: str) -> bool:
    if Path(filepath).exists():
        return True
    try:
        client = await _http_client.get_client()
        response = await client.get(url)
        ...
```

#### `save_images_by_task_id`, `save_images_with_unique_name`
- 去掉 `http_client` 参数
- 内部调用 `download_image(url, filepath)` 不传参

#### `process_sync_gen_image`, `process_image_download`
- 去掉 `http_client` 参数
- 内部调用 `save_images_*()` 不传参

#### `detect_faces_from_url`
```python
async def detect_faces_from_url(image_url: str) -> Dict[str, Any]:
    client = await _http_client.get_client()
    response = await client.get(image_url)
    ...
```

### 2. `app/routers/unified_genimage.py`

去掉 `http_client` 参数和导入：

```python
# 去掉导入: HttpxClientDep

@router.post("/genImage", summary="统一生图接口")
async def gen_image(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    liblib_client: LiblibClientDep,
    doubao_client: DoubaoClientDep,
    # 去掉 http_client 参数
) -> Dict[str, Any]:
    ...
    # 后台任务不传 http_client
    background_tasks.add_task(process_sync_gen_image, "doubao", request, response)
```

### 3. `app/routers/face_recognition/detection.py`

去掉 `http_client` 参数：

```python
# 去掉导入: HttpxClientDep

@router.post("/detect", summary="检测图片中的人脸")
async def detect_faces(
    request: FaceDetectRequest,
    # 去掉 http_client 参数
) -> ApiResponse:
    result = await detect_faces_from_url(request.image_url)
    ...
```

### 4. `app/dependencies.py`

去掉 `HttpxClientDep` 相关代码：

```python
# 去掉这些:
# from app.internal.httpclient import HttpClient
# async def get_httpx_client(request: Request) -> HttpClient: ...
# HttpxClientDep = Annotated[HttpClient, Depends(get_httpx_client)]
```

### 5. `app/main.py`

去掉 `http_client` 的初始化和清理：

```python
# 去掉导入: from app.internal.httpclient import HttpClient

lifespan 中:
    # 去掉: http_client = HttpClient()
    # 去掉: app.state.http_client = http_client
    # 去掉: await http_client.close()

# 添加导入: from app.internal import utils
# 清理时调用: await utils.close_http_client()
```

## 关键点

1. **utils.py**：创建全局 `_http_client = HttpClient()`，提供 `close_http_client()` 清理函数
2. **工具函数**：去掉 `http_client` 参数，内部直接使用 `_http_client`
3. **路由层**：去掉 `HttpxClientDep` 参数
4. **main.py**：lifespan 中调用 `utils.close_http_client()` 清理连接池
