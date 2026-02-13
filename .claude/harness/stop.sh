#!/bin/bash

# Sisyphus-X-Pro 停止开发服务脚本

echo "🛑 停止 Sisyphus-X-Pro 开发服务"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 停止前端服务
echo -e "${YELLOW}🛑 停止前端服务...${NC}"
if [ -f "logs/frontend.pid" ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo -e "${GREEN}✅ 前端服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
    fi
    rm logs/frontend.pid
else
    # 通过进程名查找并停止
    pkill -f "vite.*3000" && echo -e "${GREEN}✅ 前端服务已停止${NC}" || echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
fi

# 2. 停止后端服务
echo -e "${YELLOW}🛑 停止后端服务...${NC}"
if [ -f "logs/backend.pid" ]; then
    PID=$(cat logs/backend.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo -e "${GREEN}✅ 后端服务已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    fi
    rm logs/backend.pid
else
    # 通过进程名查找并停止
    pkill -f "uvicorn app.main:app" && echo -e "${GREEN}✅ 后端服务已停止${NC}" || echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
fi

# 3. 询问是否停止 Docker 服务
echo ""
read -p "是否停止 Docker 服务 (PostgreSQL/MinIO/Redis)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🛑 停止 Docker 服务...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Docker 服务已停止${NC}"
else
    echo -e "${YELLOW}ℹ️  Docker 服务保持运行${NC}"
fi

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}✅ 开发服务已停止${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "📋 日志文件保留在:"
echo "  - logs/backend.log"
echo "  - logs/frontend.log"
echo ""
echo "🚀 重新启动: source .claude/harness/init.sh"
echo ""
