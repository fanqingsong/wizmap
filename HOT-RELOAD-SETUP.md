# WizMap 热加载开发环境

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 启动所有服务（包含热重载）
npm run docker:dev

# 查看日志
npm run docker:logs

# 停止服务
npm run docker:stop
```

### 本地开发

```bash
# 前端（需要占用端口 3002）
npm run dev:frontend

# 后端（需要占用端口 8080）
npm run dev:backend
```

## 🔥 热加载功能

### 前端热加载（Vite HMR）
- **访问地址**: http://localhost:3002
- **功能**: 文件修改后自动刷新浏览器
- **支持**: Svelte 组件热重载、CSS 热重载、JavaScript 热重载

### 后端热加载（Uvicorn --reload）
- **访问地址**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs
- **功能**: Python 代码修改后自动重启服务器

## 🐳 Docker 服务架构

```
┌─────────────────────────────────────────────┐
│           Docker Development Stack           │
├─────────────────────────────────────────────┤
│ Frontend (Vite HMR)   →  localhost:3002     │
│ Backend (Uvicorn)      →  localhost:8080     │
│ PostgreSQL             →  :5432              │
│ Redis                  →  :6379              │
│ MinIO                  →  :9100, :9101       │
│ Celery Worker          →  (auto-restart)     │
└─────────────────────────────────────────────┘
```

## ⚙️ 配置说明

### 热加载优化配置

1. **文件监听轮询**: 启用以支持 Docker/WSL2 环境
2. **忽略目录**: node_modules, dist, .vite, git
3. **HMR 配置**: WebSocket 连接，确保热更新稳定
4. **卷挂载优化**: 保持容器内 node_modules 不被覆盖

### 解决无限刷新问题

如果遇到页面无限刷新：

```bash
# 1. 清理 Vite 缓存
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend rm -rf /app/.vite

# 2. 重启前端服务
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart frontend

# 3. 如果问题持续，完全重启
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 🔍 故障排除

### 前端问题

**问题**: 页面无限刷新
- **解决**: 检查浏览器控制台错误，清理 Vite 缓存

**问题**: HMR 不工作
- **解决**: 确认 WebSocket 连接，检查防火墙设置

**问题**: 样式不更新
- **解决**: 清理浏览器缓存，重启开发服务器

### 后端问题

**问题**: 自动重载不工作
- **解决**: 检查文件监听权限，确认 uvicorn --reload 参数

**问题**: 数据库连接失败
- **解决**: 等待 PostgreSQL 容器完全启动，检查连接字符串

### Docker 问题

**问题**: 容器无法启动
- **解决**: 检查端口冲突，清理旧容器 `docker system prune`

**问题**: 性能缓慢
- **解决**: 增加 Docker 资源限制，使用轮询模式

## 📝 开发工作流

1. **启动服务**: `npm run docker:dev`
2. **开发前端**: 修改 `frontend/` 目录文件，自动热重载
3. **开发后端**: 修改 `backend/` 目录文件，自动重启
4. **查看日志**: `npm run docker:logs`
5. **停止服务**: `npm run docker:stop`

## 🎯 端口分配

| 服务 | 容器端口 | 宿主端口 | 用途 |
|------|----------|----------|------|
| Frontend Dev | 3000 | 3002 | Vite 开发服务器 |
| Backend API | 8000 | 8080 | FastAPI 后端 |
| PostgreSQL | 5432 | - | 数据库 |
| Redis | 6379 | - | 缓存/队列 |
| MinIO API | 9000 | 9100 | 对象存储 |
| MinIO Console | 9001 | 9101 | 存储管理界面 |

## 🔗 相关链接

- **前端**: http://localhost:3002
- **后端 API**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs
- **健康检查**: http://localhost:8080/health
