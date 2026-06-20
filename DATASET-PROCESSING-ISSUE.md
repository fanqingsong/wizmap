# 📊 数据集处理问题分析

## ⚠️ 当前问题

前端尝试访问数据集数据，但收到 400 错误：
```
GET http://localhost:8080/api/v1/datasets/1c84043b-503e-4f81-b063-3942a4f992ac/grid 400 (Bad Request)
```

**错误原因**: 数据集尚未处理完成，当前状态为 "processing"

## 🔍 数据集状态分析

当前数据库中的数据集状态：
- **处理中**: 4 个数据集 (状态卡在 processing)
- **失败**: 7 个数据集 (之前的 MinIO 异步问题)

### 失败的数据集错误信息
```
"a bytes-like object is required, not 'coroutine'"
```
这是之前的 MinIO 服务异步问题，已经修复。

### 处理中的数据集
这些数据集卡在 "processing" 状态是因为：
1. Celery 后台任务处理服务未正常运行
2. 嵌入生成和 WizMap 处理流程未执行
3. grid 和 data 文件未生成

## 🎯 解决方案

### 方案 1: 使用演示数据 (推荐)

WizMap 支持查看内置演示数据，无需上传自定义文件：

```bash
# 访问开发环境
http://localhost:3002

# 点击界面上的 "Explore demo data" 按钮
# 或者确保 URL 中没有 datasetId 参数
```

### 方案 2: 完成处理服务设置

需要完成以下组件：

1. **Celery Worker 正常运行**
   ```bash
   docker logs wizmap-celery-worker --tail=20
   ```

2. **处理服务完整实现**
   - `backend/app/services/processing_service.py`
   - 嵌入生成 (sentence-transformers)
   - WizMap 汇总生成
   - UMAP 降维

3. **MinIO 对象存储**
   - 文件上传成功 ✅
   - 处理结果存储

### 方案 3: 手动清理数据集

清理失败的数据集，重新开始：

```bash
# 连接到数据库
docker exec -it wizmap-postgres psql -U wizmap -d wizmap

# 删除所有数据集
DELETE FROM datasets;

# 退出
\q
```

## 📊 WizMap 数据要求

### 前端期望的数据格式

WizMap 前端需要两个文件：

1. **grid.json** - 多分辨率汇总数据
   ```json
   {
     "grid": [[...]], // 2D 网格数据
     "x_range": [...],
     "y_range": [...],
     "sample_size": 1000,
     "total_point_size": 10000
   }
   ```

2. **data.ndjson** - 原始嵌入数据
   ```json
   {"x": 0.1, "y": 0.2, "text": "..."}
   {"x": 0.3, "y": 0.4, "text": "..."}
   ...
   ```

### API 端点要求

前端调用的端点：
- `GET /api/v1/datasets/{id}/data` - 返回 data.ndjson
- `GET /api/v1/datasets/{id}/grid` - 返回 grid.json

## 💡 临时解决方案

### 使用演示数据

最简单的方式是使用 WizMap 内置的演示数据：

1. **访问**: http://localhost:3002
2. **确保 URL 为**: `http://localhost:3002` (不带 datasetId 参数)
3. **点击**: "Explore demo data" 按钮
4. **查看**: 完整的 WizMap 可视化功能

演示数据包括：
- DiffusionDB 提示词 + 图片
- IMDB 评论
- ACL 论文摘要

### 上传新数据集 (开发测试)

如果需要测试上传功能：

1. **确保处理服务运行**
2. **上传小文件测试**
3. **等待处理完成**
4. **查看可视化结果**

## 🔧 处理服务状态检查

### 检查 Celery Worker

```bash
# 检查 Celery worker 状态
docker logs wizmap-celery-worker --tail=20

# 检查 Celery worker 健康
docker inspect wizmap-celery-worker | jq '.[0].State.Health'
```

### 检查处理服务日志

```bash
# 查看处理相关日志
docker logs wizmap-backend | grep -i processing
docker logs wizmap-celery-worker | grep -i task
```

## 🎉 推荐做法

**当前阶段建议**:

1. **使用演示数据** - 最稳定，功能完整
2. **测试前端功能** - 界面、交互、可视化
3. **测试后端 API** - 上传、状态查询
4. **等待处理服务完善** - 后续再测试自定义数据集

WizMap 的核心价值在于可视化和交互，使用内置演示数据可以充分体验所有功能。

---

**问题原因**: 数据集处理服务未完全实现  
**临时方案**: 使用演示数据  
**访问地址**: http://localhost:3002  
**推荐操作**: 点击 "Explore demo data" 按钮