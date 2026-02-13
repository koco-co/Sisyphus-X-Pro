# Hooks快速配置指南

## 一键安装配置

```bash
cd .claude/hooks
python3 UPDATE_v2.py
```

这个脚本会:
1. ✅ 备份现有配置
2. ✅ 自动添加所有hooks到 `~/.claude/settings.json`
3. ✅ 使用新的数组格式配置hooks
4. ✅ 使用绝对路径

## 手动配置

如果自动配置失败,可以手动配置:

### 步骤1: 编辑 `~/.claude/settings.json`

**重要**: Claude Code新版hooks需要使用数组格式!

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/teammate-idle.sh"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/task-completed.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/stop_gate.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/pre-tool-use.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

### 步骤2: 更新路径

将路径中的 `Users/poco/Documents/Projects/Sisyphus-X-Pro` 替换为您的实际项目路径:

```bash
# 获取当前项目路径
pwd

# 输出: /Users/poco/Documents/Projects/Sisyphus-X-Pro
```

### 步骤3: 重启Claude Code

关闭并重新启动Claude Code使hooks生效。

## 验证配置

### 方法1: 检查配置文件

```bash
cat ~/.claude/settings.json | jq '.hooks'
```

### 方法2: 测试hooks

```bash
# 测试Stop hook
export CLAUDE_PROJECT_ROOT="/Users/poco/Documents/Projects/Sisyphus-X-Pro"
.claude/hooks/stop_gate.sh

# 应该输出: ✅ 会话结束检查全部通过
```

### 方法3: 查看hooks日志

```bash
tail -f .claude/harness/hooks.log
```

## Hooks说明

| Hook | 触发时机 | 功能 |
|------|---------|------|
| **TeammateIdle** | Agent即将idle时 | 检查任务完成度,自动清理资源 |
| **TaskCompleted** | 任务标记完成时 | 运行质量门禁检查 |
| **Stop** | 会话结束时 | 最终检查,生成会话总结 |
| **PreToolUse** | 工具使用前 | 阻止危险操作 |
| **PostToolUse** | 工具使用后 | 自动格式化代码 |

## 故障处理

### Hook不触发

**症状**: Agent完成任务后没有自动检查

**解决**:
1. 确认使用绝对路径
2. 检查文件权限: `chmod +x .claude/hooks/*.sh`
3. 重启Claude Code

### Stop Hook报错

**症状**: 会话结束时显示 "Failed with non-blocking status code"

**解决**:
```bash
# 检查文件是否存在
ls -la .claude/hooks/stop_gate.sh

# 检查权限
chmod +x .claude/hooks/stop_gate.sh

# 手动测试
export CLAUDE_PROJECT_ROOT="$(pwd)"
.claude/hooks/stop_gate.sh
```

### Hook执行失败

**症状**: Hook返回错误码

**解决**:
```bash
# 查看详细日志
tail -50 .claude/harness/hooks.log

# 手动运行查看错误
bash -x .claude/hooks/stop_gate.sh
```

### 路径问题

**症状**: "No such file or directory"

**解决**:
```bash
# 使用绝对路径,不要用 ~ 或 $HOME
# 错误:
"Stop": "~/.claude/hooks/stop_gate.sh"

# 正确:
"Stop": "/Users/用户名/.claude/hooks/stop_gate.sh"
```

## 配置示例

### 完整的 `~/.claude/settings.json`

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/teammate-idle.sh"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/task-completed.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/stop_gate.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/pre-tool-use.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  },
  "teammateMode": "auto",
  "autonomous": {
    "enabled": true
  }
}
```

## 卸载Hooks

```bash
# 编辑 ~/.claude/settings.json
# 删除或注释掉 "hooks" 部分

# 或者
jq 'del(.hooks)' ~/.claude/settings.json > ~/.claude/settings.json.tmp
mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

## 下一步

配置完成后,可以:

1. **启动无人值守模式**: `/autonomous`
2. **查看hooks日志**: `tail -f .claude/harness/hooks.log`
3. **阅读完整文档**: `.claude/hooks/README.md`
