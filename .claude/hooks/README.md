# Agent Teams Hooks 配置指南

这些hooks实现了Agent的自动生命周期管理和质量门禁检查。

## 安装

```bash
cd .claude/hooks
bash INSTALL.sh
```

## 配置

在 `~/.claude/settings.json` 中添加:

```json
{
  "hooks": {
    "TeammateIdle": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/teammate-idle.sh",
    "TaskCompleted": "/Users/poco/Documents/Projects/Sisyphus-X-Pro/.claude/hooks/task-completed.sh"
  }
}
```

**重要**: 使用绝对路径!

## Hook说明

### TeammateIdle Hook

**触发时机**: Agent即将变为idle时

**功能**:
1. 检查Agent是否所有任务都完成
2. 检查质量门禁是否通过
3. 如果通过 → 清理资源,允许关闭
4. 如果不通过 → 返回反馈,保持Agent工作

**退出码**:
- `0` - 允许Agent进入idle
- `2` - 拒绝idle,保持Agent工作,发送feedback

### TaskCompleted Hook

**触发时机**: 任务被标记为完成时

**功能**:
1. 识别Agent类型
2. 运行对应的质量检查
3. Backend/Frontend → 代码检查 + 覆盖率
4. E2E → 所有测试必须通过
5. Doc → 文档同步检查
6. 如果通过 → 允许完成
7. 如果不通过 → 阻止完成,发送反馈

**退出码**:
- `0` - 允许任务完成
- `2` - 阻止完成,发送feedback

## 工作流程

```
Agent完成任务
    ↓
标记任务为completed
    ↓
触发 TaskCompleted Hook
    ↓
运行质量检查
    ↓
    ├─ 通过 → ✅ 允许完成
    └─ 失败 → ❌ 阻止完成,要求修复
    ↓
Agent继续工作或尝试idle
    ↓
触发 TeammateIdle Hook
    ↓
检查是否所有任务完成
    ↓
    ├─ 是 → 清理资源,允许关闭
    └─ 否 → 发送反馈,保持工作
```

## 日志

查看hooks日志:

```bash
tail -f .claude/harness/hooks.log
```

## 调试

如果hooks不工作:

1. **检查路径**
   ```bash
   # 确认使用绝对路径
   ls -la .claude/hooks/teammate-idle.sh
   ```

2. **检查权限**
   ```bash
   chmod +x .claude/hooks/*.sh
   chmod +x .claude/hooks/*.py
   ```

3. **手动测试**
   ```bash
   # 测试TeammateIdle Hook
   export CLAUDE_TEAMMATE_NAME="backend-agent"
   export CLAUDE_PROJECT_ROOT="/Users/poco/Documents/Projects/Sisyphus-X-Pro"
   .claude/hooks/teammate-idle.sh
   ```

4. **查看日志**
   ```bash
   cat .claude/harness/hooks.log
   ```

## 环境变量

Hooks可以使用以下环境变量:

### TeammateIdle Hook
- `CLAUDE_TEAMMATE_NAME` - Agent名称
- `CLAUDE_TEAM_NAME` - Team名称
- `CLAUDE_PROJECT_ROOT` - 项目根目录

### TaskCompleted Hook
- `CLAUDE_TASK_AGENT_NAME` - 任务所属的Agent名称
- `CLAUDE_TASK_ID` - 任务ID
- `CLAUDE_PROJECT_ROOT` - 项目根目录

## 自定义

您可以根据项目需求修改hooks:

### 修改质量标准

编辑 `.claude/hooks/task-completed.sh`:

```bash
# 例如: 提高测试覆盖率要求
if coverage < 90; then  # 从80改为90
    ...
fi
```

### 添加额外检查

在 `task-completed.sh` 中添加:

```bash
# 例如: 添加安全检查
security_check=$(python3 "$PROJECT_ROOT/.claude/hooks/security_check.py")
if [ $? -ne 0 ]; then
    feedback="❌ 安全检查失败: $security_check"
    echo "$feedback"
    exit 2
fi
```

## 故障处理

### Hook不触发

1. 确认Agent Teams已启用
2. 确认hooks路径正确 (使用绝对路径)
3. 检查文件权限
4. 查看Claude Code日志

### Hook总是返回0

1. 手动运行hook测试
2. 查看hooks.log
3. 检查Python依赖

### Agent无法关闭

1. 检查任务是否真的完成
2. 检查质量门禁是否通过
3. 查看hooks.log中的反馈信息

## 相关文档

- [Agent Teams Hooks官方文档](https://code.claude.com/docs/en/agent-teams#enforce-quality-gates-with-hooks)
- [autonomous.md](../commands/autonomous.md) - 无人值守模式
- [agent_lifecycle.py](../harness/agent_lifecycle.py) - Agent生命周期管理
