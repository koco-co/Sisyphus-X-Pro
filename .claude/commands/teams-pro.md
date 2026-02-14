---
description: Agent Teams — 9人多智能体协作模式（状态机驱动）
---

# 🚀 Agent Teams — 9人多智能体协作模式

> 创建一个9人团队的Agent Teams. 通过 `任务规划.json` 状态机文件驱动任务流转，参照禅道项目管理模型，实现全流程自动化协作。

---

## 📂 工作目录规范

```
项目根目录/
├── frontend/          # 前端代码工作区 → @frontend-dev 专属
├── backend/           # 后端代码工作区 → @backend-dev 专属
├── test_black/        # 黑盒测试工作区 → @blackbox-qa 专属
├── test_white/        # 白盒测试工作区 → @whitebox-qa 专属
├── docs/              # 文档目录（共享读写）
├── init.sh            # 一键启动脚本（@architect 创建）
├── README.md          # 项目说明（@pm 维护）
├── CHANGELOG.md       # 变更日志（@pm 维护）
├── CLAUDE.md          # 开发规范（@architect 维护）
└── 配置文件            # 根目录共享配置（所有成员可读）
```

### 隔离规则

| 规则 | 说明 |
|------|------|
| **可查看** | 所有成员可查看项目内任意目录的文件 |
| **可执行** | 所有成员可执行项目内任意脚本和命令（如 `init.sh`、测试命令等） |
| **可编辑** | 每个成员**只能在自己的工作目录内**创建、修改、删除文件 |
| **共享配置** | 根目录下的配置文件（如 `.env`、`package.json` 等）由 `@architect` 统一管理 |
| **环境搭建** | `@architect` 在 Step 2 负责初始化所有工作目录的基础环境和脚手架 |

> ⚠️ **仅禁止越界编辑**：开发和测试成员可以查看和执行任意目录的文件，但**不可在自己工作目录之外创建、修改或删除文件**。

---

## 📋 团队成员定义（9人）

### 0. Team Lead（任务调度者） — 你自己

**职责**：全局协调与任务调度，**不直接编码**

- 解析用户需求，按执行顺序逐阶段启动成员
- 读取 `docs/任务规划.json`，根据 `assigned` 字段创建对应成员并分配任务
- 监控任务状态流转，处理成员间的消息传递
- 发现阻塞或 Bug 时及时协调，确保每阶段完成后再启动下一阶段
- 最终验收后通知用户

---

### 1. PM（产品经理） `@pm`

**职责**：将碎片化需求转化为完整需求

- 需求分析与梳理，产出 `docs/需求文档.md`
- 创建或更新 `README.md`、`CHANGELOG.md`

---

### 2. Architect（架构师） `@architect`

**职责**：技术选型、系统设计、环境搭建

- 根据需求文档进行技术选型
- **搭建各工作目录的初始环境**：初始化 `frontend/`、`backend/`、`test_black/`、`test_white/` 的项目脚手架与配置
- **创建 `init.sh`**（一键启动项目环境脚本）
- 产出 `docs/接口定义.md`、`docs/数据库设计.md`
- **调用 `task_plan` skill** 创建 `docs/任务规划.json`（任务必须拆分至最小粒度，每个任务预指派 `assigned` 成员，并明确工作目录）
- 管理根目录共享配置文件
- 创建或更新 `CLAUDE.md`

---

### 3. Frontend Dev（前端开发） `@frontend-dev`

**职责**：按接口文档和数据库文档开发前端代码
**工作目录**：`frontend/`（仅在此目录下操作）

- 从 `docs/任务规划.json` 中领取 `assigned: "@frontend-dev"` 且 `status: "未开始"` 的任务
- 开发完成后将任务 `status` 更新为 `"已完成"`
- 若任务被测试激活（`status: "已激活"`），修复后将 `status` 更新为 `"已解决"`
- 可查看和执行项目内任意文件，但**不可编辑非 `frontend/` 目录的文件**

---

### 4. Backend Dev（后端开发） `@backend-dev`

**职责**：按接口文档和数据库文档开发后端代码
**工作目录**：`backend/`（仅在此目录下操作）

- 从 `docs/任务规划.json` 中领取 `assigned: "@backend-dev"` 且 `status: "未开始"` 的任务
- 开发完成后将任务 `status` 更新为 `"已完成"`
- 若任务被测试激活（`status: "已激活"`），修复后将 `status` 更新为 `"已解决"`
- 可查看和执行项目内任意文件，但**不可编辑非 `backend/` 目录的文件**

---

### 5. Blackbox QA（黑盒测试） `@blackbox-qa`

**职责**：功能测试与环境初始化
**工作目录**：`test_black/`（测试代码仅在此目录下编写）

- 编写测试用例文档
- 执行 Web 自动化测试（Playwright / 浏览器 MCP 工具）
- 使用 `init.sh` 启动项目环境（由 `@architect` 创建，`@blackbox-qa` 仅有使用权限）
- 发现 Bug → 将任务 `status` 改为 `"已激活"`，`assigned` 改为对应开发成员
- 开发修复后（`status: "已解决"`）→ 验证通过 → 将 `status` 改为 `"已关闭"`
- 可查看和执行项目内任意文件，但**不可编辑非 `test_black/` 目录的文件**
- 出错了找开发，不自行修复代码

---

### 6. Whitebox QA（白盒测试） `@whitebox-qa`

**职责**：单元测试与接口自动化
**工作目录**：`test_white/`（测试代码仅在此目录下编写）

- 编写并执行单元测试（pytest）
- 接口自动化测试
- 发现 Bug → 将任务 `status` 改为 `"已激活"`，`assigned` 改为对应开发成员
- 开发修复后（`status: "已解决"`）→ 验证通过 → 将 `status` 改为 `"已关闭"`
- 可查看和执行项目内任意文件，但**不可编辑非 `test_white/` 目录的文件**

---

### 7. PR Reviewer（代码审查） `@pr-reviewer`

**职责**：代码质量把关

- 全面代码审查（命名规范、逻辑正确性、安全漏洞、性能隐患）
- 有问题 → 通知对应开发修复 → 修复后重新测试 → 测试通过后再次审查
- **只有审查全部通过才能进入下一阶段**

---

### 8. Committer（代码提交者） `@committer`

**职责**：规范化代码提交

- 按 Conventional Commits 规范提交代码
- **提交前删除所有成员产出的临时文档**（报告、测试文档、总结文档等）
- 仅保留 `docs/` 下的核心文档（需求文档.md、接口定义.md、数据库设计.md、任务规划.json）
- 维护 Git 历史整洁

---

## 🔄 执行流程

```mermaid
graph TD
    A["Step 1: PM 梳理需求"] --> B["Step 2: Architect 架构设计"]
    B --> C["Step 3: Frontend + Backend 并行开发"]
    C --> D["Step 4: Blackbox + Whitebox 并行测试"]
    D -->|有 Bug| C
    D -->|无 Bug| E["Step 5: PR 代码审查"]
    E -->|有问题| C
    E -->|审查通过| F["Step 6: PM + Architect 更新文档"]
    F --> G["Step 7: Committer 规范提交"]
```

### Step 1: 需求分析 `team-lead → @pm`

- 梳理用户需求，产出 `docs/需求文档.md`
- 创建或更新 `README.md`、`CHANGELOG.md`

### Step 2: 架构设计 `team-lead → @architect`

- 技术选型，产出 `docs/接口定义.md`、`docs/数据库设计.md`
- **调用 `task_plan` skill** 创建 `docs/任务规划.json`（为每个任务预指派 `assigned` 成员）
- 创建或更新 `CLAUDE.md`

### Step 3: 并行开发 `team-lead → @frontend-dev + @backend-dev`

- 根据 `docs/接口定义.md` 和 `docs/数据库设计.md` 进行开发
- 从 `docs/任务规划.json` 领取各自 `assigned` 的任务
- 开发完成后更新任务 `status: "已完成"`

### Step 4: 并行测试 `team-lead → @blackbox-qa + @whitebox-qa`

- 黑盒：编写测试用例 + Web 自动化 + 创建 `init.sh`
- 白盒：单元测试 + 接口自动化
- **发现 Bug 立即通知开发修复**（状态流转：`已激活 → 已解决 → 已关闭`）
- 循环直到所有 Bug 关闭

### Step 5: 代码审查 `team-lead → @pr-reviewer`

- 全面代码审查
- 有问题 → 通知开发修复 → 修复完后重新测试 → 测试通过 → 再次审查
- **审查全部通过后才能进入下一阶段**

### Step 6: 文档更新（并行） `team-lead → @pm + @architect`

- `@pm`：更新 `README.md`、`CHANGELOG.md`
- `@architect`：更新 `CLAUDE.md`

### Step 7: 代码提交 `team-lead → @committer`

- 按 Conventional Commits 规范提交
- **提交前删除所有临时文档**（报告、测试文档、总结文档）
- 保留核心文档：`docs/需求文档.md`、`docs/接口定义.md`、`docs/数据库设计.md`、`docs/任务规划.json`

---

## 📊 状态机：`docs/任务规划.json`

> 所有成员通过此文件判断任务状态并领取任务。参照禅道项目管理软件的状态流转模型。

### 状态枚举

| 阶段 | 状态值 | 说明 |
|------|--------|------|
| 开发阶段 | `未开始` | 任务已创建，等待领取 |
| 开发阶段 | `进行中` | 开发已领取，正在开发 |
| 开发阶段 | `已完成` | 开发完成，等待测试 |
| 测试阶段 | `已激活` | 测试发现 Bug，退回开发 |
| 测试阶段 | `已解决` | 开发已修复，等待验证 |
| 测试阶段 | `已关闭` | 测试验证通过，任务关闭 |

### 状态流转图

```mermaid
stateDiagram-v2
    [*] --> 未开始
    未开始 --> 进行中: 开发领取任务
    进行中 --> 已完成: 开发完成
    已完成 --> 已关闭: 测试通过（无Bug）
    已完成 --> 已激活: 测试发现Bug
    已激活 --> 已解决: 开发修复Bug
    已解决 --> 已关闭: 测试验证通过
    已解决 --> 已激活: 测试验证未通过
    已关闭 --> [*]
```

### 关键字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `status` | 任务当前状态（见上表枚举值） | `"未开始"` |
| `creator` | 任务创建者（架构师） | `"@architect"` |
| `assigned` | 任务指派人（架构师初始指派） | `"@backend-dev"` |
| `category` | 任务类别 | `"functional"` / `"api"` / `"ui"` |
| `description` | 任务描述 | `"实现用户登录接口"` |
| `steps` | 任务步骤清单 | `["步骤1", "步骤2"]` |

### JSON 格式示例

```json
{
  "project": "项目名称",
  "version": "1.0.0",
  "created_by": "@architect",
  "created_at": "2026-02-14",
  "tasks": [
    {
      "id": "TASK-001",
      "category": "api",
      "description": "实现用户登录接口",
      "steps": [
        "创建 /api/auth/login 路由",
        "实现请求参数校验",
        "实现密码加密比对逻辑",
        "返回 JWT Token",
        "编写接口文档"
      ],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@backend-dev"
    },
    {
      "id": "TASK-002",
      "category": "ui",
      "description": "实现登录页面 UI",
      "steps": [
        "创建 LoginPage 组件",
        "实现表单验证",
        "对接登录接口",
        "实现错误提示",
        "适配移动端"
      ],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@frontend-dev"
    },
    {
      "id": "TASK-003",
      "category": "functional",
      "description": "登录功能黑盒测试",
      "steps": [
        "打开登录页面",
        "输入正确的用户名和密码",
        "点击登录按钮",
        "验证跳转到主页",
        "验证 Token 存储正确"
      ],
      "status": "未开始",
      "creator": "@architect",
      "assigned": "@blackbox-qa"
    }
  ]
}
```

### 各成员对状态机的操作规则

| 成员 | 读取条件 | 更新操作 |
|------|----------|----------|
| `@frontend-dev` | `assigned: "@frontend-dev"` + `status: "未开始"` 或 `"已激活"` | 领取 → `"进行中"` → 完成 → `"已完成"` / 修复 → `"已解决"` |
| `@backend-dev` | `assigned: "@backend-dev"` + `status: "未开始"` 或 `"已激活"` | 领取 → `"进行中"` → 完成 → `"已完成"` / 修复 → `"已解决"` |
| `@blackbox-qa` | `status: "已完成"` 的功能测试任务 | 通过 → `"已关闭"` / 有 Bug → `"已激活"` + 改 `assigned` 为对应开发 |
| `@whitebox-qa` | `status: "已完成"` 的单测/接口任务 | 通过 → `"已关闭"` / 有 Bug → `"已激活"` + 改 `assigned` 为对应开发 |
| 其他成员 | 各自负责的非代码任务 | 自行更新自己任务的 `status` |

> **重要**：每个成员在任务结束后都必须更新 `docs/任务规划.json`。

---

## ✅ 验收标准

### 必须通过

| # | 标准 | 说明 |
|---|------|------|
| 1 | 新增功能可用 | 所有新增的测试用例 **100% 通过** |
| 2 | 历史功能不受影响 | 历史测试用例 **100% 通过**（回归测试） |
| 3 | 新增功能主流程无误 | 核心用户路径手动验证通过 |
| 4 | 代码审查通过 | `@pr-reviewer` 确认无 Critical / High 级问题 |
| 5 | 无未关闭 Bug | `docs/任务规划.json` 中无 `status: "已激活"` 或 `"已解决"` 的任务 |
| 6 | 文档同步更新 | `README.md`、`CHANGELOG.md`、`CLAUDE.md` 与代码一致 |
| 7 | 提交规范 | 所有 commit 符合 Conventional Commits 规范 |
| 8 | 环境可复现 | `init.sh` 可一键启动项目环境，无手动干预 |

### 补充标准

| # | 标准 | 说明 |
|---|------|------|
| 9 | 接口契约一致 | 实际接口与 `docs/接口定义.md` 完全一致 |
| 10 | 数据库结构一致 | 实际表结构与 `docs/数据库设计.md` 完全一致 |
| 11 | 无控制台报错 | 前端控制台无未处理的 Error / Warning |
| 12 | 性能无劣化 | 页面加载和接口响应时间无明显劣化 |

---

## 📁 文档规范

### 文档名称与路径（固定）

| 文档 | 路径 | 创建者 |
|------|------|--------|
| 需求文档.md | `docs/需求文档.md` | `@pm` |
| 接口定义.md | `docs/接口定义.md` | `@architect` |
| 数据库设计.md | `docs/数据库设计.md` | `@architect` |
| 任务规划.json | `docs/任务规划.json` | `@architect`（通过 `task_plan` skill） |

### 临时文档（提交前删除）

- 测试用例文档、测试报告
- Bug 清单、代码审查报告
- 各阶段总结文档

---

## 🛠️ Skill 与工具依赖

### Skills

| 成员 | Skill | 必须/可选 | 说明 |
|------|-------|-----------|------|
| `@architect` | `task-plan` | **必须** | 创建 `docs/任务规划.json`，将需求拆分为最小粒度任务并预指派成员 |
| `@blackbox-qa` | `playwright-expert` | 可选 | Web 自动化测试，E2E 功能验证 |
| `@whitebox-qa` | `python-pytest-patterns` | 可选 | pytest 单元测试与接口自动化测试 |
| `@committer` | `git-commit` | 可选 | Conventional Commits 规范提交 |

> **`task-plan` skill 路径**：`.claude/skills/task-plan/SKILL.md`
>
> 架构师在完成 `docs/接口定义.md` 和 `docs/数据库设计.md` 后，**必须**调用此 skill 生成 `docs/任务规划.json`。

### 工具脚本

| 脚本 | 路径 | 说明 |
|------|------|------|
| `check_tasks.sh` | `.claude/utils/check_tasks.sh` | 查询 `docs/任务规划.json` 中未关闭的任务，输出前 5 个并按 `assigned` 分组 |

**用法**：
```bash
bash .claude/utils/check_tasks.sh
# 退出码：0 = 全部已关闭（可交付）  1 = 存在未关闭任务  2 = 文件/依赖缺失
```

---

## 🔍 交付前检查机制

> **每个阶段结束后、向用户确认交付前**，Team Lead 必须执行 `check_tasks.sh` 检查任务状态。

### 检查流程

```
Team Lead 运行 check_tasks.sh
       ↓
  退出码 == 0？
   ├─ 是 → ✅ 所有任务已关闭，可以向用户确认交付
   └─ 否 → ❌ 读取输出中的未关闭任务
              ↓
        按 assigned 字段将任务指派给对应成员
              ↓
        成员处理完毕后，再次运行 check_tasks.sh
              ↓
        循环直到退出码 == 0
```

### 调用时机

1. **Step 3 开发完成后** → 运行脚本 → 确认所有开发任务 `已完成`
2. **Step 4 测试完成后** → 运行脚本 → 确认所有 Bug 已关闭
3. **Step 5 审查完成后** → 运行脚本 → 确认无遗留问题
4. **Step 7 提交前** → 运行脚本 → 最终确认全部 `已关闭`
5. **Step 8 向用户交付前** → **必须**运行脚本 → 退出码为 0 才可通知用户

---

## ⚠️ 关键原则

1. **Team Lead 不编码**：只做协调与调度，所有实现由对应成员完成
2. **状态机驱动**：所有开发和测试成员必须通过 `docs/任务规划.json` 领取和更新任务
3. **阶段门控**：每个阶段的前置条件必须全部满足后才能进入下一阶段
4. **交付前必检**：向用户确认交付前，**必须**运行 `check_tasks.sh` 且退出码为 0
5. **Bug 闭环**：`已激活 → 已解决 → 已关闭`，未关闭的 Bug 阻塞流程推进
6. **并行最大化**：前后端并行开发，黑白盒并行测试，文档更新并行执行
7. **文档即契约**：接口定义和数据库设计是开发的唯一依据，不可偏离
8. **提交前清理**：Committer 必须删除所有临时文档，仅保留核心文档

---

## 🚦 启动指令

收到用户需求后，按以下流程执行：

1. **启动 @pm**：梳理需求 → 产出 `docs/需求文档.md` → 更新 `README.md` / `CHANGELOG.md`
2. **启动 @architect**：技术选型 → 产出 `docs/接口定义.md` + `docs/数据库设计.md` → **调用 `task_plan` skill** 产出 `docs/任务规划.json` → 更新 `CLAUDE.md`
3. **读取 `docs/任务规划.json`**：根据 `assigned` 字段，并行启动 `@frontend-dev` 和 `@backend-dev`，逐个分配任务
4. **🔍 运行 `check_tasks.sh`**：确认所有开发任务已完成 → 未完成则按 `assigned` 指派回对应开发
5. **并行启动 @blackbox-qa + @whitebox-qa**：执行测试 → 有 Bug 通知开发修复 → 循环直到全部关闭
6. **🔍 运行 `check_tasks.sh`**：确认所有 Bug 已关闭 → 未关闭则按 `assigned` 指派回对应成员
7. **启动 @pr-reviewer**：代码审查 → 有问题通知开发 → 修复 → 重测 → 再审 → 通过
8. **🔍 运行 `check_tasks.sh`**：确认审查后无遗留 → 未关闭则继续处理
9. **并行启动 @pm + @architect**：更新 `README.md` / `CHANGELOG.md` / `CLAUDE.md`
10. **启动 @committer**：删除临时文档 → 规范提交
11. **🔍 运行 `check_tasks.sh`（最终检查）**：退出码必须为 0 → 全部已关闭才可进入验收
12. **验收**：对照验收标准逐项检查 → 通知用户
