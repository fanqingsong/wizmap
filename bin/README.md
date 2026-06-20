# WizMap 管理脚本

这些脚本提供了方便的方式来管理 WizMap 的开发和生产环境。

## 🚀 快速开始

```bash
# 开发环境（推荐用于开发）
./bin/start_dev.sh

# 生产环境
./bin/start_prod.sh

# 停止所有服务
./bin/stop

# 查看服务状态
./bin/status

# 查看实时日志
./bin/logs

# 重启服务
./bin/restart
```

## 📋 脚本说明

### start_dev.sh
启动开发环境，启用热重载功能。

**特点：**
- ✅ 前端：Vite HMR（热模块替换）
- ✅ 后端：Uvicorn --reload
- ✅ Celery：watchfiles 自动重启
- ✅ 代码更改立即生效

**访问地址：**
- 前端（开发）: http://localhost:3002
- 前端（生产）: http://localhost:3001
- 后端 API: http://localhost:8080
- API 文档: http://localhost:8080/docs

### start_prod.sh
启动生产环境，使用优化的构建。

**特点：**
- ✅ 优化的前端构建
- ✅ 生产级后端配置
- ✅ 数据持久化
- ✅ 对象存储和缓存

**访问地址：**
- 前端: http://localhost:3001
- 后端 API: http://localhost:8080
- MinIO 控制台: http://localhost:9101

### stop
停止所有运行的服务。

**功能：**
- 优雅停止所有容器
- 保留数据卷
- 清理网络

### status
显示当前服务状态。

**信息包括：**
- 服务运行状态
- 端口映射
- 健康检查
- 访问地址

### logs
实时查看服务日志。

**功能：**
- 跟踪所有服务的日志输出
- 按 Ctrl+C 停止查看
- 自动检测开发/生产模式

### restart
重启所有运行的服务。

**功能：**
- 快速重启服务
- 保持当前模式（开发/生产）
- 应用代码更改

## 🔧 开发工作流

### 典型开发流程

1. **启动开发环境：**
   ```bash
   ./bin/start_dev.sh
   ```

2. **开发前端代码：**
   - 编辑 `frontend/` 目录下的文件
   - 浏览器自动刷新（HMR）
   - 无需手动重启

3. **开发后端代码：**
   - 编辑 `backend/` 目录下的文件
   - 服务器自动重启
   - 浏览器刷新即可

4. **查看日志：**
   ```bash
   ./bin/logs
   ```

5. **完成工作：**
   ```bash
   ./bin/stop
   ```

### 代码更改流程

**无需重启的场景（热加载）：**
- 前端：组件、样式、JavaScript 代码
- 后端：Python 代码、API 路由、业务逻辑

**需要重启的场景：**
- 依赖包更改（package.json, requirements.txt）
- Docker 配置更改
- 环境变量更改

## 🐛 故障排除

### 服务无法启动

```bash
# 检查 Docker 状态
docker ps

# 查看详细日志
docker compose logs

# 重启 Docker（如果需要）
# 然后重新启动服务
./bin/start_dev.sh
```

### 端口冲突

```bash
# 检查端口占用
netstat -tulpn | grep -E "3001|3002|8080"

# 停止服务
./bin/stop

# 再次启动
./bin/start_dev.sh
```

### 数据库问题

```bash
# 完全停止并清理
docker compose down -v

# 重新启动
./bin/start_dev.sh
```

## 📊 环境对比

| 特性 | 开发环境 | 生产环境 |
|------|----------|----------|
| 前端 | Vite HMR | Nginx |
| 端口 | 3002 | 3001 |
| 热重载 | ✅ 是 | ❌ 否 |
| 性能 | 调试优化 | 生产优化 |
| 用途 | 开发测试 | 部署运行 |

## 💡 提示

1. **开发时使用 start_dev.sh** - 热重载极大提高开发效率
2. **部署时使用 start_prod.sh** - 性能和稳定性更好
3. **定期查看 status** - 确保服务正常运行
4. **查看 logs 排错** - 实时监控服务状态
5. **修改代码后测试** - 利用热重载快速迭代

## 🔗 相关文档

- `../START-DEV-GUIDE.md` - 详细开发指南
- `../HOT-RELOAD-SETUP.md` - 热加载配置说明
- `../UPLOAD-FIX-GUIDE.md` - 上传功能指南
