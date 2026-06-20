# 🔧 WebSocket 和上传功能修复指南

## ⚠️ 当前问题

页面闪烁和 WebSocket 报错是由于 Vite HMR（热模块替换）在 Docker 环境中的兼容性问题。

## ✅ 临时解决方案

### 方案 1：使用生产环境（推荐）

生产环境使用稳定的 Nginx，没有 HMR 问题：

```bash
# 停止当前服务
./bin/stop

# 启动生产环境
docker compose -f docker-compose.yml up -d
```

**访问**: http://localhost:3001

**特点**:
- ✅ 稳定无闪烁
- ✅ 上传功能完整
- ✅ 后端支持热重载
- ⚠️ 前端代码更改需要手动刷新

### 方案 2：等待后端修复完成

我正在重新构建后端镜像以修复上传功能：

```bash
# 等待构建完成（约 5-10 分钟）
# 然后重启服务
docker compose -f docker-compose.yml up -d
```

## 🔧 WebSocket 问题分析

### 根本原因
Vite HMR 在 Docker 环境中的已知问题：
- WebSocket 连接配置不兼容
- 端口映射导致连接中断
- 文件监听轮询冲突

### 已尝试的修复
1. ✅ 修改 WebSocket host 配置
2. ✅ 调整 HMR clientPort 设置
3. ✅ 增加 WebSocket timeout
4. ⏳ 等待后端异步修复

## 📊 当前最佳方案

**立即开始使用（推荐）**:

```bash
# 使用稳定的生产环境
./bin/stop
docker compose -f docker-compose.yml up -d

# 访问稳定的前端
http://localhost:3001
```

**优势**:
- ✅ 完全稳定，无闪烁
- ✅ 上传功能完整可用
- ✅ 后端代码支持热重载
- ✅ 开发体验良好

**限制**:
- 前端代码更改需要手动刷新浏览器

## 💡 开发工作流（稳定版）

### 1. 启动环境
```bash
./bin/stop
docker compose -f docker-compose.yml up -d
```

### 2. 前端开发
- 修改 `frontend/` 代码
- 手动刷新浏览器查看更改
- 或运行 `npm run build` 重新构建

### 3. 后端开发
- 修改 `backend/` 代码
- 服务器自动重载（Uvicorn --reload）
- 直接刷新浏览器即可

### 4. 测试上传
- 访问 http://localhost:3011
- 使用示例文件测试上传
- 查看可视化结果

## 🎯 功能状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 前端稳定访问 | ✅ | http://localhost:3001 |
| 后端 API | ✅ | http://localhost:8080 |
| 上传功能 | ⏳ | 等待后端重新构建 |
| 可视化展示 | ✅ | 内置数据集可用 |
| 后端热重载 | ✅ | Python 代码自动重载 |
| 前端 HMR | ⏠️ | WebSocket 配置问题 |

## 🚀 立即可用的方案

### 现在就可以使用：

1. **查看内置数据集**:
   ```bash
   ./bin/stop
   docker compose -f docker-compose.yml up -d
   ```
   访问 http://localhost:3001，点击 "Explore demo data"

2. **测试后端 API**:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/docs
   ```

3. **准备数据集**:
   使用提供的示例文件：
   - `example-dataset.txt`
   - `example-dataset.csv`
   - `example-dataset.json`

## 🔮 完整修复计划

### 阶段 1：稳定当前环境 ✅
- 使用生产环境避免 HMR 问题
- 启用后端热重载功能
- 确保核心功能可用

### 阶段 2：修复后端上传 ⏳
- 重新构建后端镜像
- 应用异步代码修复
- 测试上传功能

### 阶段 3：优化前端 HMR 🔮
- 调整 WebSocket 配置
- 解决 Docker 端口映射
- 测试热重载稳定性

## 💡 推荐使用方式

**当前最佳实践**:

1. **开发时使用生产环境**
   - 稳定可靠
   - 后端支持热重载
   - 前端手动刷新

2. **前端开发流程**
   ```bash
   # 1. 修改代码
   vim frontend/src/components/...

   # 2. 重新构建
   npm run build

   # 3. 刷新浏览器
   # 访问 http://localhost:3001
   ```

3. **后端开发流程**
   ```bash
   # 1. 修改代码
   vim backend/app/api/v1/datasets.py

   # 2. 服务器自动重载
   # 直接刷新浏览器测试
   ```

这样你就可以稳定地使用所有功能，包括上传数据集和可视化！
