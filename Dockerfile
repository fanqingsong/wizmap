# Multi-stage build for WizMap

# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# 设置 npm 使用国内镜像源，提高下载速度
RUN npm config set registry https://registry.npmmirror.com

# 复制 frontend package 文件
COPY frontend/package.json ./

# 安装依赖，设置更长的超时时间
RUN npm install \
    --prefer-offline \
    --no-audit \
    --no-fund \
    --timeout=180000

# 复制前端源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# Stage 2: Production server with nginx
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口 80
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
