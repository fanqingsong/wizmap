# WizMap Docker 部署指南

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 使用 Docker Compose 启动

```bash
# 构建并启动容器
docker compose up -d

# 查看日志
docker compose logs -f

# 停止容器
docker compose down
```

### 访问应用

启动后，在浏览器中访问：**http://localhost:3001**

> **注意**：默认端口为 3001，如需修改请编辑 `docker-compose.yml` 文件中的端口映射

## Docker 命令参考

### 构建镜像
```bash
docker compose build
```

### 启动服务
```bash
# 后台启动
docker compose up -d

# 前台启动（查看日志）
docker compose up
```

### 查看状态
```bash
docker compose ps
```

### 查看日志
```bash
# 查看所有日志
docker compose logs

# 实时查看日志
docker compose logs -f

# 查看特定服务的日志
docker compose logs -f wizmap
```

### 停止服务
```bash
# 停止容器
docker compose stop

# 停止并删除容器
docker compose down

# 停止并删除容器及网络
docker compose down --remove-orphans
```

### 重新构建
```bash
# 强制重新构建
docker compose build --no-cache

# 重新构建并启动
docker compose up -d --build
```

## 配置说明

### 修改端口

编辑 `docker-compose.yml` 文件中的端口映射：

```yaml
ports:
  - "8080:80"  # 将主机的 8080 端口映射到容器的 80 端口
```

### 环境变量

可以在 `docker-compose.yml` 中添加环境变量：

```yaml
environment:
  - NODE_ENV=production
  - CUSTOM_VAR=value
```

## 生产环境部署

### 使用外部 Nginx

如果已有 Nginx 服务器，可以只构建镜像：

```bash
# 构建镜像
docker build -t wizmap:latest .

# 运行容器
docker run -d -p 3000:80 --name wizmap wizmap:latest
```

### 使用 Docker Swarm

```yaml
# stack.yml
version: '3.8'
services:
  wizmap:
    image: wizmap:latest
    deploy:
      replicas: 2
    ports:
      - "3000:80"
```

```bash
docker stack deploy -c stack.yml wizmap
```

## 故障排查

### 容器启动失败
```bash
# 查看详细日志
docker compose logs

# 检查容器状态
docker compose ps
```

### 端口被占用
修改 `docker-compose.yml` 中的端口映射

### 清理和重建
```bash
# 完全清理
docker compose down -v
docker system prune -a

# 重新构建
docker compose up -d --build
```

## 镜像信息

- 基础镜像：node:18-alpine (构建阶段), nginx:alpine (运行阶段)
- 镜像大小：约 50-100 MB
- 暴露端口：80
- 工作目录：/usr/share/nginx/html
