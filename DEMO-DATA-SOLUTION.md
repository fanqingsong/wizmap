# 🎯 解决方案：使用官方演示数据

## ❌ 当前问题

你一直看到 400 错误，因为：
- 所有上传的数据集都卡在 "processing" 状态
- Celery 后台处理服务未完全实现
- 前端无法访问未处理完成的数据

## ✅ 立即解决方案

**访问 WizMap 官方演示数据**，无需本地处理：

### 方案 1: 使用官方 WizMap 网站

```
https://poloclub.github.io/wizmap/
```

官方站点包含完整的演示数据：
- DiffusionDB (180万 Stable Diffusion 提示词 + 图片)
- IMDB (2.5万条电影评论)
- ACL (6.3万篇论文摘要)

### 方案 2: 清除本地数据集 URL

**直接访问干净的 URL**：
```
http://localhost:3002
```

**确保浏览器地址栏中没有**：
- `?datasetId=...`
- `?dataset=...`
- `?dataURL=...`

### 方案 3: 手动清理数据库

```bash
# 清理所有未完成的数据集
docker exec -it wizmap-postgres psql -U wizmap -d wizmap -c "DELETE FROM datasets;"

# 重新访问
http://localhost:3002
```

## 📊 WizMap 演示数据集

官方演示数据包括：

### 1. DiffusionDB
- **规模**: 180万文本 + 180万图片
- **内容**: Stable Diffusion 提示词和生成图片
- **嵌入**: CLIP (ViT-H/14)
- **特点**: 多模态，图文对应

### 2. IMDB 评论
- **规模**: 2.5万条电影评论
- **内容**: 用户影评和情感标签
- **嵌入**: all-MiniLM-L6-v2
- **特点**: 情感分析数据

### 3. ACL 论文摘要
- **规模**: 6.3万篇论文摘要
- **内容**: 学术论文摘要文本
- **嵌入**: all-MiniLM-L6-v2
- **特点**: 学术主题聚类

## 🔧 为什么本地数据集失败？

### 处理流程不完整

WizMap 需要完整的处理流程：
1. **文件上传** ✅ 已实现
2. **文本嵌入生成** ❌ 未实现 (需要 sentence-transformers)
3. **UMAP 降维** ❌ 未实现
4. **WizMap 汇总** ❌ 未实现 (需要自定义算法)
5. **结果存储** ❌ 未实现

### Celery Worker 问题

```bash
# 检查 Celery worker 状态
docker logs wizmap-celery-worker --tail=20
```

可能看到错误或无任务处理日志。

## 💡 推荐使用方式

### 开发/测试阶段

**使用官方演示数据**：
- 功能完整
- 数据丰富
- 立即可用
- 无需等待处理

访问：`https://poloclub.github.io/wizmap/`

### 本地开发

**前端开发**：
```bash
cd frontend
npm run dev
```
访问演示数据进行界面开发

**后端开发**：
专注于 API 功能，暂不实现完整处理流程

## 🎉 现在就可以做

### 选项 1: 访问官方站点
```
https://poloclub.github.io/wizmap/
```

### 选项 2: 清理本地环境
```bash
docker exec -it wizmap-postgres psql -U wizmap -d wizmap -c "DELETE FROM datasets;"
```
然后访问：`http://localhost:3002`

### 选项 3: 停止数据加载
1. 访问 `http://localhost:3002`
2. 确保 URL 没有参数
3. 点击 "Explore demo data"

---

**关键点**：当前本地处理服务未完全实现，使用官方演示数据是最佳选择。