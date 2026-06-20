#!/bin/bash
# WizMap Docker 部署测试脚本

set -e

echo "🔍 WizMap Docker 部署测试"
echo "=========================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_step() {
    local name=$1
    local command=$2

    echo -n "测试 $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        return 1
    fi
}

# 1. 检查 Docker
echo -e "\n📦 检查环境"
test_step "Docker 安装" "docker --version"
test_step "Docker Compose 安装" "docker compose version"

# 2. 检查容器状态
echo -e "\n🐳 检查容器状态"
if docker compose ps | grep -q "wizmap-app"; then
    CONTAINER_STATUS=$(docker compose ps | grep wizmap-app | awk '{print $5, $6, $7}')
    echo -e "容器状态: ${GREEN}$CONTAINER_STATUS${NC}"

    # 检查健康状态
    if docker compose ps | grep -q "healthy"; then
        echo -e "健康检查: ${GREEN}✓ 健康${NC}"
    else
        echo -e "健康检查: ${YELLOW}⏳ 等待中${NC}"
    fi
else
    echo -e "${RED}✗ 容器未运行${NC}"
    echo "请先运行: docker compose up -d"
    exit 1
fi

# 3. 测试服务可访问性
echo -e "\n🌐 测试服务可访问性"
if test_step "HTTP 服务" "curl -s http://localhost:3001"; then
    # 检查响应内容
    HTTP_RESPONSE=$(curl -s http://localhost:3001)
    if echo "$HTTP_RESPONSE" | grep -q "WizMap"; then
        echo -e "内容验证: ${GREEN}✓ WizMap 页面正常${NC}"
    else
        echo -e "内容验证: ${RED}✗ 响应内容异常${NC}"
    fi
else
    echo -e "${RED}✗ 服务不可访问${NC}"
    echo "请检查容器日志: docker compose logs"
fi

# 4. 检查容器资源使用
echo -e "\n📊 容器资源使用"
docker stats wizmap-app --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 5. 显示访问信息
echo -e "\n🎉 访问信息"
echo -e "${GREEN}应用地址: http://localhost:3001${NC}"
echo -e "查看日志: ${YELLOW}docker compose logs -f${NC}"
echo -e "停止服务: ${YELLOW}docker compose down${NC}"

echo -e "\n✨ 测试完成！"
