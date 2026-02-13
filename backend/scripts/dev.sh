#!/bin/bash
# 开发服务器启动脚本

cd "$(dirname "$0")/.."

echo "🚀 Starting Sisyphus-X-Pro Backend Development Server..."
echo "📍 API Documentation: http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
