---
name: task-plan
description: '生成任务规划.json 状态机文件。仅由架构师(@architect)在完成接口定义文档和数据库设计文档后调用。将需求拆分为最小粒度任务，预指派成员，生成符合禅道状态流转模型的 JSON 文件。'
---

# 任务规划 JSON 生成器（Task Plan Generator）

## 前置条件

> ⚠️ 调用此 skill 前，必须确保以下文档已就绪：

1. `docs/需求文档.md` — 由 `@pm` 产出
2. `docs/接口定义.md` — 由 `@architect` 产出
3. `docs/数据库设计.md` — 由 `@architect` 产出

## 输出

- **文件路径**：`docs/任务规划.json`
- **编码**：UTF-8

## 任务拆分原则

1. **最小粒度**：每个任务聚焦于单一功能点，预计开发时间 ≤ 2 小时
2. **可独立验证**：每个任务完成后可独立测试或验证
3. **依赖明确**：如有前后依赖关系，在 `dependencies` 字段中标注
4. **覆盖全面**：需求文档中的每个功能点必须拆分出对应的开发任务 + 测试任务

## 成员标识与工作目录

| 标识 | 角色 | 工作目录 |
|------|------|----------|
| `@frontend-dev` | 前端开发 | `frontend/` |
| `@backend-dev` | 后端开发 | `backend/` |
| `@blackbox-qa` | 黑盒测试 | `test_black/` |
| `@whitebox-qa` | 白盒测试 | `test_white/` |

> ⚠️ 每个任务必须通过 `workspace` 字段明确工作目录，成员只能在指定目录内操作。

## 状态枚举（status 可选值）

### 开发阶段

| 状态 | 说明 |
|------|------|
| `未开始` | 任务已创建，等待开发领取 |
| `进行中` | 开发已领取，正在实现 |
| `已完成` | 开发完成，等待测试 |

### 测试阶段

| 状态 | 说明 |
|------|------|
| `已激活` | 测试发现 Bug，退回开发修复 |
| `已解决` | 开发已修复 Bug，等待测试验证 |
| `已关闭` | 测试验证通过，任务关闭 |

### 状态流转规则

```
未开始 → 进行中 → 已完成 → 已关闭（无 Bug）
                          ↓
                       已激活（有 Bug）→ 已解决 → 已关闭
                          ↑                ↓
                          └────────────────┘（验证未通过）
```

## 任务分类（category）

| 类别 | 说明 | 指派对象 |
|------|------|----------|
| `api` | 后端接口实现 | `@backend-dev` |
| `ui` | 前端页面/组件 | `@frontend-dev` |
| `db` | 数据库模型/迁移 | `@backend-dev` |
| `functional` | 功能黑盒测试 | `@blackbox-qa` |
| `unit-test` | 单元测试 | `@whitebox-qa` |
| `api-test` | 接口自动化测试 | `@whitebox-qa` |
| `integration` | 前后端集成 | `@frontend-dev` / `@backend-dev` |

## JSON Schema

```json
{
  "project": "项目名称",
  "version": "版本号",
  "created_by": "@architect",
  "created_at": "YYYY-MM-DD",
  "tasks": [
    {
      "id": "TASK-001",
      "category": "api | ui | db | functional | unit-test | api-test | integration",
      "description": "简明任务描述",
      "steps": [
        "具体实现步骤1",
        "具体实现步骤2"
      ],
      "workspace": "backend/ | frontend/ | test_black/ | test_white/",
      "dependencies": ["TASK-000"],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@backend-dev | @frontend-dev | @blackbox-qa | @whitebox-qa",
      "reason": ""
    }
  ]
}
```

## 生成流程

### 1. 读取输入文档

```bash
# 读取需求文档
cat docs/需求文档.md

# 读取接口定义
cat docs/接口定义.md

# 读取数据库设计
cat docs/数据库设计.md
```

### 2. 任务拆分

按以下顺序从文档中提取并拆分任务：

1. **数据库层**（`db`）：从数据库设计文档提取每个表/模型 → 一个任务
2. **接口层**（`api`）：从接口定义文档提取每个 API 端点 → 一个任务
3. **页面层**（`ui`）：从需求文档提取每个页面/组件 → 一个任务
4. **集成层**（`integration`）：前后端对接 → 按功能模块拆分
5. **黑盒测试**（`functional`）：每个用户场景 → 一个测试任务
6. **单元测试**（`unit-test`）：每个核心模块 → 一个测试任务
7. **接口测试**（`api-test`）：每组相关 API → 一个测试任务

### 3. 指派成员

根据 `category` 自动指派 `assigned`：
- `api` / `db` → `@backend-dev`
- `ui` → `@frontend-dev`
- `integration` → 根据具体内容指派
- `functional` → `@blackbox-qa`
- `unit-test` / `api-test` → `@whitebox-qa`

### 4. 设置依赖

- `api` 任务依赖对应的 `db` 任务
- `ui` 的接口对接部分依赖对应的 `api` 任务
- `functional` 测试依赖对应的 `ui` + `api` 任务
- `unit-test` 依赖对应的 `api` 任务

### 5. 写入文件

将生成的 JSON 写入 `docs/任务规划.json`，确保：
- UTF-8 编码
- 2 空格缩进
- `id` 按 `TASK-001`、`TASK-002` 递增
- 所有任务初始 `status` 为 `"未开始"`

## 示例输出

```json
{
  "project": "Sisyphus-X-Pro",
  "version": "1.0.0",
  "created_by": "@architect",
  "created_at": "2026-02-14",
  "tasks": [
    {
      "id": "TASK-001",
      "category": "db",
      "description": "创建用户表模型（User Model）",
      "steps": [
        "定义 User SQLModel 类",
        "添加字段：id, username, email, password_hash, created_at",
        "配置索引和约束",
        "创建数据库迁移脚本"
      ],
      "workspace": "backend/",
      "dependencies": [],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@backend-dev",
      "reason": ""
    },
    {
      "id": "TASK-002",
      "category": "api",
      "description": "实现用户注册接口 POST /api/auth/register",
      "steps": [
        "创建注册请求/响应 Schema",
        "实现注册路由处理函数",
        "添加邮箱唯一性校验",
        "实现密码加密存储",
        "返回创建成功响应"
      ],
      "workspace": "backend/",
      "dependencies": ["TASK-001"],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@backend-dev",
      "reason": ""
    },
    {
      "id": "TASK-003",
      "category": "ui",
      "description": "实现注册页面组件",
      "steps": [
        "创建 RegisterPage 组件",
        "实现表单（用户名、邮箱、密码、确认密码）",
        "添加前端表单验证",
        "对接注册 API",
        "实现成功/失败提示"
      ],
      "workspace": "frontend/",
      "dependencies": [],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@frontend-dev",
      "reason": ""
    },
    {
      "id": "TASK-004",
      "category": "functional",
      "description": "用户注册功能黑盒测试",
      "steps": [
        "打开注册页面",
        "填写有效注册信息",
        "提交表单",
        "验证注册成功提示",
        "验证可使用新账号登录"
      ],
      "workspace": "test_black/",
      "dependencies": ["TASK-002", "TASK-003"],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@blackbox-qa",
      "reason": ""
    },
    {
      "id": "TASK-005",
      "category": "unit-test",
      "description": "用户注册接口单元测试",
      "steps": [
        "测试正常注册流程",
        "测试重复邮箱注册",
        "测试无效参数校验",
        "测试密码加密正确性"
      ],
      "workspace": "test_white/",
      "dependencies": ["TASK-002"],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@whitebox-qa",
      "reason": ""
    }
  ]
}
```

## 注意事项

1. **不要遗漏任务**：需求文档中的每个功能点都必须有对应的开发 + 测试任务
2. **粒度把控**：太大的任务必须拆分，太小的任务可以合并（如同一模块的 CRUD 可以合为 2-3 个任务）
3. **ID 连续性**：任务 ID 必须从 `TASK-001` 开始连续递增
4. **初始状态**：所有任务的初始 `status` 必须为 `"未开始"`
5. **creator 统一**：所有任务的 `creator` 均为 `"@architect"`
6. **reason 字段**：初始为空字符串 `""`，仅在测试或审查阶段将 `status` 改为 `"已激活"` 时必须填写具体原因
