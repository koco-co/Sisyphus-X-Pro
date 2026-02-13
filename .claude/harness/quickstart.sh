#!/bin/bash

# Sisyphus-X-Pro AI Agent 快速启动脚本
# 用于 Claude Code 或其他 AI Agent 快速开始开发会话

set -e

echo "🤖 Sisyphus-X-Pro AI Agent 快速启动"
echo "=================================="
echo ""
echo "📍 当前目录: $(pwd)"
echo ""

# 检查是否在项目根目录
if [ ! -f ".claude/harness/feature_list.json" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   当前目录应包含 .claude/harness/ 目录"
    exit 1
fi

echo "📋 检查会话清单..."
echo "-----------------------------------"
cat .claude/harness/session_checklist.md | grep -A 50 "## 会话开始清单"
echo ""

echo "🚀 启动开发环境..."
echo "-----------------------------------"
source .claude/harness/init.sh
echo ""

echo "📊 当前项目状态..."
echo "-----------------------------------"
python .claude/harness/test_helper.py
echo ""

echo "📝 下一步操作建议:"
echo "-----------------------------------"
echo "1. 阅读: cat .claude/harness/claude-progress.txt"
echo "2. 查看功能: cat .claude/harness/feature_list.json"
echo "3. 查看提交: git log --oneline -10"
echo "4. 选择一个功能开始实现"
echo ""

echo "✅ 环境就绪! 可以开始开发了"
echo "=================================="
