# WizMap 开发环境启动指南

## 问题解决方案

如果你遇到页面无限刷新的问题，这是因为 Vite HMR 在某些环境下的兼容性问题。我们提供了几种解决方案：

## 🔥 推荐方案：Docker 开发环境（无 HMR）

这是最稳定的开发方式，前端使用生产构建，后端支持热重载。

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f

# 修改前端代码后重新构建
docker compose restart frontend

# 修改后端代码会自动重载
```

### 端口说明
- **前端**: http://localhost:3001 (生产构建)
- **后端**: http://localhost:8080 (支持热重载)
- **API文档**: http://localhost:8080/docs

## 🎨 替代方案：本地开发（前端生产构建）

如果你更喜欢本地开发：

### 1. 启动后端（支持热重载）
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2. 构建并启动前端
```bash
cd frontend

# 首次构建
npm install
npm run build

# 启动简单HTTP服务器
cd dist
python3 -m http.server 3002
```

### 访问地址
- 前端: http://localhost:3002
- 后端: http://localhost:8080

## 🔧 开发工作流

### 前端开发
1. 修改 `frontend/src/` 下的代码
2. 运行 `npm run build` 重新构建
3. 刷新浏览器查看更改
4. 或者在 Docker 中运行 `docker compose restart frontend`

### 后端开发  
1. 修改 `backend/app/` 下的代码
2. 后端会自动重载（uvicorn --reload）
3. 直接刷新浏览器即可

## 🐛 故障排除

### 页面无限刷新问题
这是 Vite HMR 的已知问题，解决方法：
- ✅ 使用生产构建代替开发服务器
- ✅ 确保前端代码没有无限循环的 JavaScript
- ✅ 清理浏览器缓存

### Docker 相关问题
```bash
# 清理所有容器
docker compose down

# 重新构建镜像
docker compose build --no-cache

# 重新启动
docker compose up -d
```

### 前端构建问题
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

## 📋 快速命令参考

```bash
# Docker 方式（推荐）
docker compose up -d                    # 启动所有服务
docker compose logs -f                   # 查看日志
docker compose restart frontend         # 重启前端
docker compose down                      # 停止所有服务

# 本地开发方式
npm run build                           # 构建前端
cd dist && python3 -m http.server 3002  # 启动前端服务器
cd ../backend && python -m uvicorn app.main:app --reload --port 8080  # 启动后端
```

## 💡 推荐开发习惯

1. **使用 Docker**: 最稳定的环境一致性
2. **前端使用生产构建**: 避免 HMR 问题
3. **后端使用热重载**: 提高开发效率
4. **定期清理**: 避免缓存问题

选择最适合你的开发方式！
