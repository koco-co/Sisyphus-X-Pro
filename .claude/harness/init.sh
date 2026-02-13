#!/bin/bash

# Sisyphus-X-Pro 自动化开发环境初始化脚本
# 此脚本由 Initializer Agent 创建,Coding Agent 在每次会话开始时运行

set -e  # 遇到错误立即退出

echo "🚀 Sisyphus-X-Pro 开发环境初始化"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查Docker服务是否运行
echo -e "${YELLOW}📦 检查 Docker 服务...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行,请先启动 Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 服务正常${NC}"

# 2. 启动中间件 (PostgreSQL/MinIO/Redis)
echo -e "${YELLOW}📦 启动中间件服务...${NC}"
if ! docker-compose ps | grep -q "sisyphus-postgres.*Up"; then
    docker-compose up -d
    echo "等待服务启动..."
    sleep 10
else
    echo -e "${GREEN}✅ 中间件服务已运行${NC}"
fi

# 3. 检查后端环境变量
echo -e "${YELLOW}🔧 检查后端配置...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件,从 .env.example 复制...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  请编辑 backend/.env 配置数据库连接等信息${NC}"
fi

# 4. 安装后端依赖
echo -e "${YELLOW}📦 检查后端依赖...${NC}"
cd backend
if [ ! -d ".venv" ]; then
    echo "安装后端依赖 (uv)..."
    uv sync
else
    echo -e "${GREEN}✅ 后端依赖已安装${NC}"
fi

# 5. 检查数据库是否已初始化
echo -e "${YELLOW}🗄️  检查数据库...${NC}"
if ! python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())" 2>/dev/null; then
    echo "初始化数据库..."
    python -m app.init_db
fi
cd ..
echo -e "${GREEN}✅ 数据库连接正常${NC}"

# 6. 安装前端依赖
echo -e "${YELLOW}📦 检查前端依赖...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖 (npm)..."
    npm install
else
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
fi
cd ..

# 7. 启动后端服务器 (后台运行)
echo -e "${YELLOW}🚀 启动后端开发服务器...${NC}"
pkill -f "uvicorn app.main:app" || true
cd backend
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
echo $! > ../logs/backend.pid
cd ..

# 等待后端启动
echo "等待后端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ 后端服务已启动 (http://localhost:8000)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        tail -n 50 logs/backend.log
        exit 1
    fi
    sleep 1
done

# 8. 启动前端服务器 (后台运行)
echo -e "${YELLOW}🚀 启动前端开发服务器...${NC}"
pkill -f "vite" || true
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo $! > ../logs/frontend.pid
cd ..

# 等待前端启动
echo "等待前端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ 前端服务已启动 (http://localhost:3000)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 前端服务启动失败${NC}"
        tail -n 50 logs/frontend.log
        exit 1
    fi
    sleep 1
done

# 9. 运行基础健康检查
echo -e "${YELLOW}🔍 运行基础健康检查...${NC}"
python .claude/harness/health_check.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 所有健康检查通过${NC}"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}✅ 开发环境初始化完成!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "📝 服务地址:"
echo "  - 前端: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "📋 日志文件:"
echo "  - 后端: logs/backend.log"
echo "  - 前端: logs/frontend.log"
echo ""
echo "🛑 停止服务: ./stop.sh"
echo ""
