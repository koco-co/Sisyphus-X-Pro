#!/bin/bash
# 运行测试脚本

cd "$(dirname "$0")/.."

echo "🧪 Running tests..."
uv run pytest -v
