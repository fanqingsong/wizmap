# WizMap 部署和使用指南

## 🚀 快速开始

### 1. 启动完整系统

```bash
# 构建并启动所有容器
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

### 2. 访问服务

- **前端界面**: http://localhost:3001
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **MinIO控制台**: http://localhost:9001 (admin/password123)

---

## 📊 完整使用流程

### 方式1: 通过后端API上传数据

#### 1.1 上传文本文件

```bash
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -F "file=@your_texts.txt" \
  -F "name=My Dataset"
```

**响应示例**:
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Dataset",
  "status": "processing",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### 1.2 检查处理状态

```bash
curl "http://localhost:8000/api/v1/datasets/{dataset_id}/status"
```

**状态响应**:
```json
{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "error": null
}
```

#### 1.3 在前端查看结果

```
访问: http://localhost:3001/?datasetId={dataset_id}
```

### 方式2: 使用前端上传界面

#### 2.1 访问前端上传页面

```
访问: http://localhost:3001/upload
```

#### 2.2 上传文件

1. **选择文件**: 点击上传区域或拖拽文件
2. **设置名称**: 为数据集命名
3. **上传处理**: 点击"Upload & Process"按钮
4. **等待处理**: 后台自动处理文本数据
5. **查看结果**: 处理完成后点击"View Visualization"

#### 2.3 支持的文件格式

- **.txt**: 纯文本文件（每行一个文档）
- **.csv**: CSV文件（第一列为文本）
- **.json**: JSON数组或对象

---

## 🔧 后端API端点

### 数据集管理

#### 创建数据集
```http
POST /api/v1/datasets
Content-Type: multipart/form-data

file: <文件>
name: <数据集名称>
```

#### 列出所有数据集
```http
GET /api/v1/datasets
```

#### 获取数据集详情
```http
GET /api/v1/datasets/{dataset_id}
```

#### 获取处理状态
```http
GET /api/v1/datasets/{dataset_id}/status
```

#### 获取可视化数据
```http
GET /api/v1/datasets/{dataset_id}/data  # 点数据
GET /api/v1/datasets/{dataset_id}/grid  # 网格数据
```

#### 删除数据集
```http
DELETE /api/v1/datasets/{dataset_id}
```

---

## 🧪 测试后端功能

### 运行测试脚本

```bash
# 确保后端正在运行
python test_backend.py
```

**测试内容**:
- ✅ 健康检查
- ✅ 文件上传
- ✅ 状态查询
- ✅ 数据列表
- ✅ 处理等待
- ✅ 数据获取

### 手动测试步骤

```bash
# 1. 测试健康检查
curl http://localhost:8000/health

# 2. 创建测试文件
echo -e "Text 1\nText 2\nText 3" > test.txt

# 3. 上传测试文件
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -F "file=@test.txt" \
  -F "name=Test Dataset"

# 4. 检查状态（替换{dataset_id}）
curl "http://localhost:8000/api/v1/datasets/{dataset_id}/status"

# 5. 获取数据
curl "http://localhost:8000/api/v1/datasets/{dataset_id}/data"
curl "http://localhost:8000/api/v1/datasets/{dataset_id}/grid"
```

---

## 🛠️ 容器管理

### 启动服务
```bash
docker compose up -d
```

### 停止服务
```bash
docker compose down
```

### 重启特定服务
```bash
# 重启后端
docker compose restart backend

# 重启Celery Worker
docker compose restart celery_worker

# 重启前端
docker compose restart frontend
```

### 查看日志
```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f celery_worker
docker compose logs -f frontend
```

### 进入容器调试
```bash
# 进入后端容器
docker compose exec backend bash

# 进入PostgreSQL容器
docker compose exec postgres psql -U wizmap

# 进入Redis容器
docker compose exec redis redis-cli
```

---

## 📁 项目结构

```
/home/fqs/workspace/self/wizmap/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 配置和数据库
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── services/          # 业务逻辑
│   │   ├── workers/           # Celery任务
│   │   └── main.py            # FastAPI应用
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── src/                        # 前端代码
│   └── components/
│       ├── dataset-upload/    # 上传组件
│       ├── mapview/           # 地图视图
│       ├── embedding/         # 嵌入可视化
│       └── ...
├── docker-compose.yml         # 容器编排
├── test_backend.py            # 后端测试脚本
├── BACKEND-IMPLEMENTATION-SUMMARY.md
└── DEPLOYMENT-GUIDE.md
```

---

## 🔍 系统架构

### 数据流程

```
用户上传文件 → MinIO存储 → 数据库记录 → Celery异步处理 → 
生成嵌入向量 → UMAP降维 → WizMap格式 → API提供 → 前端展示
```

### 技术栈

- **前端**: Svelte + Vite + D3.js + WebGL
- **后端**: FastAPI + Python 3.11
- **数据库**: PostgreSQL + pgvector
- **存储**: MinIO (S3兼容)
- **任务队列**: Celery + Redis
- **ML处理**: sentence-transformers + UMAP + scikit-learn
- **容器化**: Docker + Docker Compose

---

## ⚡ 性能优化建议

### 1. 大文件处理

```python
# 在backend/app/core/config.py中调整
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
PROCESSING_TIMEOUT = 1800  # 30分钟
```

### 2. 数据库优化

```sql
-- 在PostgreSQL中创建索引
CREATE INDEX ON embeddings USING ivfflat (vector vector_cosine_ops);
CREATE INDEX ON datasets(created_at DESC);
CREATE INDEX ON processing_jobs(status, created_at);
```

### 3. Celery配置

```python
# 在backend/app/workers/celery_worker.py中调整
CELERY_TASK_PREFETCH_LIMIT = 1
CELERY worker -c 4  # 使用4个worker进程
```

---

## 🐛 故障排除

### 问题1: 后端无法启动

```bash
# 检查后端日志
docker compose logs backend

# 检查数据库连接
docker compose exec backend python -c "from app.core.database import test_connection; test_connection()"
```

### 问题2: 数据处理失败

```bash
# 检查Celery worker日志
docker compose logs celery_worker

# 查看处理任务状态
docker compose exec backend python -c "from app.core.celery import app; print(app.control.inspect().active())"
```

### 问题3: 前端无法连接后端

```bash
# 检查网络连接
docker compose ps

# 测试后端API
curl http://localhost:8000/health

# 检查CORS配置
docker compose logs backend | grep -i cors
```

### 问题4: MinIO连接问题

```bash
# 检查MinIO状态
docker compose logs minio

# 进入MinIO容器测试
docker compose exec minio mc ls local/data
```

---

## 🔐 生产环境配置

### 1. 环境变量

创建`.env`文件:
```bash
# 数据库配置
DATABASE_URL=postgresql://wizmap:your_password@postgres:5432/wizmap
POSTGRES_PASSWORD=your_secure_password

# MinIO配置
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your_secure_password
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# Redis配置
REDIS_URL=redis://redis:6379/0

# 应用配置
SECRET_KEY=your_secret_key
ALGORITHM=hs256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. 反向代理配置

使用Nginx:
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 监控和日志

```bash
# 使用Docker日志驱动
docker compose config | grep logging

# 配置日志轮转
# 在docker-compose.yml中添加:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📚 相关文档

- [BACKEND-IMPLEMENTATION-SUMMARY.md](BACKEND-IMPLEMENTATION-SUMMARY.md) - 后端实现详细说明
- [DOCKER.md](DOCKER.md) - Docker配置说明
- [原WizMap文档](https://github.com/vis-net-design/wizmap) - 原始项目文档

---

## 🎯 下一步功能

### 待实现功能

1. **用户认证系统**
   - 用户注册/登录
   - 数据集权限管理
   - API密钥管理

2. **实时进度监控**
   - WebSocket连接
   - 处理进度实时显示
   - 错误状态实时推送

3. **高级数据处理**
   - 自定义参数配置
   - 多语言支持
   - 增量数据更新

4. **数据集管理界面**
   - 数据集列表页面
   - 删除/重命名功能
   - 数据集分享功能

---

## 💡 使用技巧

### 1. 数据集命名规范

- 使用描述性名称
- 包含数据来源信息
- 添加时间戳便于管理

```
good_names = [
  "news_articles_2024_01",
  "product_reviews_amazon",
  "scientific_papers_arxiv"
]
```

### 2. 批量数据处理

```python
# 使用脚本批量上传
import requests
import os

for filename in os.listdir('data/'):
    with open(f'data/{filename}', 'rb') as f:
        requests.post('http://localhost:8000/api/v1/datasets',
                     files={'file': f},
                     data={'name': filename.replace('.txt', '')})
```

### 3. API集成示例

```python
import requests

class WizMapClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
    
    def upload_dataset(self, file_path, name):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/api/v1/datasets',
                files={'file': f},
                data={'name': name}
            )
        return response.json()
    
    def get_status(self, dataset_id):
        response = requests.get(
            f'{self.base_url}/api/v1/datasets/{dataset_id}/status'
        )
        return response.json()
    
    def wait_for_completion(self, dataset_id, timeout=300):
        import time
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_status(dataset_id)
            if status['status'] == 'completed':
                return True
            elif status['status'] == 'failed':
                return False
            time.sleep(5)
        return False

# 使用示例
client = WizMapClient()
result = client.upload_dataset('data.txt', 'My Data')
if client.wait_for_completion(result['dataset_id']):
    print(f"✅ Ready: http://localhost:3001/?datasetId={result['dataset_id']}")
```

---

## 🌟 最佳实践

### 1. 数据准备

- **文本清洗**: 移除特殊字符和格式
- **编码统一**: 确保UTF-8编码
- **数据量控制**: 单次建议<10MB

### 2. 系统监控

```bash
# 监控容器资源使用
docker stats

# 监控数据库性能
docker compose exec postgres psql -U wizmap -c "SELECT * FROM pg_stat_activity;"
```

### 3. 备份策略

```bash
# 备份数据库
docker compose exec postgres pg_dump -U wizmap wizmap > backup.sql

# 备份MinIO数据
docker cp minio:/data ./minio_backup
```

---

这个系统现在是一个完整的全栈应用，提供了从数据上传到可视化的完整流程！🎉