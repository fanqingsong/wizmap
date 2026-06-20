# 🔧 白屏问题修复指南

## ⚠️ 问题原因

访问白屏是因为访问了错误的端口。当前运行的是**开发环境**，需要访问正确的端口。

## ✅ 解决方案

### 正确的访问地址

**开发环境 (当前运行)**:
- **前端**: http://localhost:3002 ⬅️ **使用这个地址**
- **后端**: http://localhost:8080

**生产环境**:
- **前端**: http://localhost:3001
- **后端**: http://localhost:8080

### 🚀 立即测试

```bash
# 开发环境 (推荐 - 支持热重载)
# 浏览器访问: http://localhost:3002

# 生产环境 (稳定 - 无热重载)
# 浏览器访问: http://localhost:3001
```

## 📊 当前状态

**运行中的服务**:
- ✅ 前端开发服务器 (Vite HMR)
- ✅ 后端 API (FastAPI + Uvicorn --reload)
- ✅ PostgreSQL 数据库
- ✅ Redis 缓存
- ✅ MinIO 对象存储
- ✅ Celery 后台任务

**端口映射**:
```
开发环境:
- 3002 → 3000 (Vite 开发服务器) ⬅️ 使用这个
- 3001 → 80 (未使用 - 白屏原因)

生产环境:
- 3001 → 80 (Nginx) ⬅️ 生产环境使用
```

## 🔍 为什么会白屏？

1. **开发环境配置**: 使用 Vite 开发服务器运行在容器内端口 3000
2. **端口映射**: Docker 将外部端口 3002 映射到容器内端口 3000
3. **错误访问**: 如果访问 http://localhost:3001，会连接到容器内端口 80，但开发容器中没有运行 Nginx

## 💡 开发环境优势

**开发环境 (推荐)**:
- ✅ 前端热重载 (Vite HMR) - 代码修改立即生效
- ✅ 后端热重载 (Uvicorn --reload) - Python 代码自动重启
- ✅ 实时错误反馈
- ✅ 更快的开发迭代

**生产环境**:
- ✅ 稳定的 Nginx 服务
- ✅ 优化的构建
- ⚠️ 需要手动重启查看前端更改

## 🎯 快速切换环境

### 切换到开发环境 (当前)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```
**访问**: http://localhost:3002

### 切换到生产环境
```bash
docker compose -f docker-compose.yml up -d
```
**访问**: http://localhost:3001

### 停止所有服务
```bash
docker compose down
```

## 📝 重要提示

1. **开发环境**: 总是使用端口 **3002**
2. **生产环境**: 总是使用端口 **3001**
3. **后端 API**: 两个环境都使用端口 **8080**

## 🔥 热重载测试

在开发环境中，你可以测试热重载功能:

1. **前端热重载**:
   ```bash
   # 修改 frontend/src/ 下的任何文件
   # 浏览器会自动刷新
   # 例如: vim frontend/src/App.svelte
   ```

2. **后端热重载**:
   ```bash
   # 修改 backend/app/ 下的任何 Python 文件
   # 服务器会自动重启
   # 例如: vim backend/app/main.py
   ```

## 🎉 现在就可以使用

打开浏览器访问 **http://localhost:3002**，你应该能看到 WizMap 的完整界面！

如果还有问题，请检查:
1. 浏览器控制台是否有错误
2. 确认访问的是正确的端口 (3002)
3. 查看服务日志: `docker logs wizmap-frontend-dev`

---

**更新时间**: 2026-06-20 00:15:00  
**环境**: 开发环境运行中  
**正确访问地址**: http://localhost:3002