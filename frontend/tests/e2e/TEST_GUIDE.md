# AUTH 模块 E2E 测试指南

## 快速开始

### 1. 启动后端服务

```bash
cd backend

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证后端运行: 访问 http://localhost:8000/docs

### 2. 运行 E2E 测试

```bash
cd frontend

# 运行所有测试
npm run test:e2e

# 运行特定测试文件
npx playwright test auth.spec

# 运行特定测试用例
npx playwright test -g "应该成功登录"

# UI 模式（推荐）
npm run test:e2e:ui
```

## 测试用例列表

### AUTH-001: 用户注册 (4 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| 成功注册 | 创建新用户 | 跳转到首页/登录页,token 存在 |
| 重复注册 | 相同邮箱再次注册 | 显示"已存在"错误 |
| 密码强度 | 弱密码注册 | 显示密码强度错误 |
| 邮箱格式 | 无效邮箱格式 | 显示邮箱格式错误 |

### AUTH-002: 邮箱密码登录 (4 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| 成功登录 | 正确凭据登录 | 跳转首页,显示用户信息,token 存在 |
| 错误密码 | 错误密码登录 | 显示密码错误,无 token |
| 未注册邮箱 | 不存在邮箱登录 | 显示"不存在"错误,无 token |
| 空字段 | 提交空表单 | 显示验证错误 |

### AUTH-005: 退出登录 (2 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| 退出清除 token | 点击退出 | 跳转登录页,localStorage 清空 |
| 无法访问保护页 | 退出后访问首页 | 重定向到登录页 |

### AUTH-007: 密码加密 (1 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| bcrypt 哈希 | 注册新用户 | API 响应不包含密码字段 |

### AUTH-008: 账户锁定 (2 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| 5次失败锁定 | 连续5次错误密码 | 第6次显示"锁定"错误 |
| 正确登录重置 | 3次失败后正确登录 | 失败计数重置 |

### AUTH-003/004: OAuth (2 个测试)

| 测试用例 | 描述 | 验证点 |
|---------|------|--------|
| GitHub 按钮 | 点击 GitHub 登录 | 跳转到 GitHub OAuth 页面 |
| Google 按钮 | 点击 Google 登录 | 跳转到 Google OAuth 页面 |

## 测试数据

所有测试使用动态生成的邮箱,避免冲突:

```typescript
const testUsers = {
  valid: {
    email: `test-${Date.now()}@example.com`,
    password: 'Test123456!',
  },
  invalid: {
    email: 'nonexistent@example.com',
    password: 'WrongPassword123!',
  },
}
```

## 调试测试

### 1. 使用 UI 模式

```bash
npm run test:e2e:ui
```

UI 模式提供:
- 可视化测试执行
- 时间旅行调试
- 网络请求查看
- DOM 快照

### 2. 使用调试模式

```bash
npm run test:e2e:debug
```

调试模式特点:
- 慢动作执行
- 浏览器开发者工具
- 断点调试

### 3. 查看测试报告

```bash
npm run test:e2e
npm run test:e2e:report
```

### 4. 查看失败截图

失败测试会自动保存截图:
```
test-results/
├── auth-spec-should-login-successfully-1.png
├── auth-spec-should-login-successfully-1-video.webm
└── ...
```

## Page Object 模式

### AuthPage 示例

```typescript
import { AuthPage } from './pages/AuthPage'

test('示例测试', async ({ page }) => {
  const authPage = new AuthPage(page)

  // 导航到登录页
  await authPage.goto()

  // 填写表单
  await authPage.fillCredentials('test@example.com', 'password123')

  // 提交
  await authPage.clickSubmit()

  // 验证
  await expect(page).toHaveURL('/')
})
```

## 常见问题

### Q: 测试失败 "Backend connection refused"

**A**: 确保后端服务运行在 http://localhost:8000

```bash
cd backend
uvicorn app.main:app --reload
```

### Q: 测试失败 "Email already exists"

**A**: 删除数据库中的测试用户

```bash
psql -U postgres -d sisyphus
DELETE FROM users WHERE email LIKE '%@example.com';
```

### Q: OAuth 测试被跳过

**A**: OAuth 完整流程测试需要:
1. 真实的 GitHub/Google OAuth 应用配置
2. 测试账户授权
3. 或使用 mock OAuth 服务器

当前只测试按钮存在性和跳转。

### Q: 测试很慢

**A**: 可以:
1. 使用 `--workers=N` 并行运行
2. 只运行特定测试: `npx playwright test -g "登录"`
3. 使用 `--headed=false` 无头模式

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: sisyphus_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Install Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          uvicorn app.main:app &
          sleep 10

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload test report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## 扩展测试

添加新测试用例:

1. **创建 Page Object** (如果需要)

```typescript
// tests/e2e/pages/ProjectPage.ts
export class ProjectPage {
  readonly page: Page
  readonly createButton: Locator

  constructor(page: Page) {
    this.page = page
    this.createButton = page.locator('button:has-text("创建项目")')
  }

  async createProject(name: string) {
    await this.createButton.click()
    await this.page.fill('input[name="name"]', name)
    await this.page.click('button[type="submit"]')
  }
}
```

2. **添加测试用例**

```typescript
test('应该创建项目', async ({ page }) => {
  const projectPage = new ProjectPage(page)
  await projectPage.goto()
  await projectPage.createProject('测试项目')
  await expect(page.locator('.project-list')).toContainText('测试项目')
})
```

3. **运行验证**

```bash
npx playwright test -g "应该创建项目"
```

## 测试覆盖率

当前 AUTH 模块 E2E 测试覆盖:

- ✅ 成功路径 (注册/登录/退出)
- ✅ 失败路径 (错误密码/未注册邮箱)
- ✅ 边界情况 (空字段/弱密码/重复注册)
- ✅ 安全性 (密码加密/账户锁定)
- ✅ 状态管理 (localStorage/UI 状态)

## 下一步

需要添加的 E2E 测试:

- [ ] PROJ 模块 (项目管理)
- [ ] KEYW 模块 (关键字配置)
- [ ] INTF 模块 (接口定义)
- [ ] SCEN 模块 (场景编排)
- [ ] PLAN 模块 (测试计划)
- [ ] REPT 模块 (测试报告)

参考 `auth.spec.ts` 作为模板创建其他模块的测试。
