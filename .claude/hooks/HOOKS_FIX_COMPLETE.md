# Hooks配置完整修复记录

## 问题历程

### 问题1: Hooks格式错误
**错误信息**: `matcher: Expected string, but received object`

**原因**: 使用了旧格式的matcher对象

**解决方案**:
- TeammateIdle, TaskCompleted, Stop: 省略matcher字段(不支持)
- PreToolUse, PostToolUse: 使用字符串matcher `""`匹配所有工具

### 问题2: 路径找不到
**错误信息**: `bash: .claude/hooks/stop_gate.sh: No such file or directory`

**原因**: 命令缺少 `bash` 前缀

**解决方案**: 所有命令添加 `bash` 前缀

### 问题3: 路径重复错误
**错误信息**: `/.../.claude/hooks/.claude/harness/hooks.log: No such file or directory`

**原因**: 使用了错误的环境变量 `CLAUDE_PROJECT_ROOT`

**解决方案**: 使用正确的环境变量 `CLAUDE_PROJECT_DIR`

## 最终正确配置

### settings.json格式

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/poco/.../.claude/hooks/teammate-idle.sh"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/poco/.../.claude/hooks/task-completed.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/poco/.../.claude/hooks/stop_gate.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/poco/.../.claude/hooks/pre-tool-use.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/poco/.../.claude/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

### 脚本中的环境变量

**正确用法**:
```bash
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
```

**错误用法**:
```bash
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
```

## 官方文档参考

根据 [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks):

### Matcher支持情况

| Hook | 支持Matcher? | 说明 |
|------|--------------|------|
| TeammateIdle | ❌ 否 | 总是触发 |
| TaskCompleted | ❌ 否 | 总是触发 |
| Stop | ❌ 否 | 总是触发 |
| PreToolUse | ✅ 是 | 匹配工具名称 |
| PostToolUse | ✅ 是 | 匹配工具名称 |

### Matcher值

- 空字符串 `""` 或省略: 匹配所有
- 工具名称: `"Bash"`, `"Edit"`, `"Write"` 等
- 正则表达式: `"Edit|Write"` 匹配多个工具

### 环境变量

Claude Code提供以下环境变量给hooks:

- `CLAUDE_PROJECT_DIR`: 项目根目录 (正确) ✅
- `CLAUDE_PLUGIN_ROOT`: 插件根目录 (插件hooks)
- `CLAUDE_ENV_FILE`: 环境变量持久化文件

## 测试命令

```bash
# 测试Stop Hook
export CLAUDE_PROJECT_DIR="/Users/poco/Documents/Projects/Sisyphus-X-Pro"
bash /Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/stop_gate.sh

# 查看hooks日志
tail -f /Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/harness/hooks.log

# 查看会话总结
ls -la /Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/harness/session_summary_*.txt
```

## 配置更新脚本

最新的配置脚本: `.claude/hooks/UPDATE_v4.py`

运行方式:
```bash
python3 .claude/hooks/UPDATE_v4.py
```

## 验证清单

- [x] TeammateIdle - 正确格式,无matcher
- [x] TaskCompleted - 正确格式,无matcher
- [x] Stop - 正确格式,无matcher
- [x] PreToolUse - matcher="",使用bash前缀
- [x] PostToolUse - matcher="",使用bash前缀
- [x] 所有脚本使用CLAUDE_PROJECT_DIR
- [x] Stop Hook测试通过

## 下一步

1. ✅ 所有hooks已正确配置
2. ✅ 所有脚本已修复环境变量
3. ✅ Stop Hook测试通过
4. 🔄 重启Claude Code使hooks生效

重启后可以测试无人值守模式:
```bash
/autonomous
```
