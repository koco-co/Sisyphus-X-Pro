# E2E 测试快速参考

## 🚀 快速命令

```bash
# 安装依赖
npm install

# 运行所有测试
npm run test:e2e

# 运行 AUTH 测试
npx playwright test auth.spec

# UI 模式
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 列出所有测试
npx playwright test --list

# 查看报告
npm run test:e2e:report
```

## 📂 目录结构

```
tests/e2e/
├── auth.spec.ts          # AUTH 模块测试
├── pages/
│   ├── AuthPage.ts       # 登录/注册页面对象
│   └── DashboardPage.ts  # 首页面对象
├── helpers/
│   ├── api-helper.ts     # API 辅助函数
│   ├── test-setup.ts     # 测试设置
│   └── health-check.ts   # 健康检查
├── fixtures/
│   └── test-data.ts      # 测试数据
└── README.md             # 文档
```

## 🎯 测试清单

### AUTH-001: 用户注册 (4)
- ✅ 成功注册
- ✅ 重复注册
- ✅ 密码强度
- ✅ 邮箱格式

### AUTH-002: 邮箱登录 (4)
- ✅ 成功登录
- ✅ 错误密码
- ✅ 未注册邮箱
- ✅ 空字段验证

### AUTH-005: 退出登录 (2)
- ✅ 退出清除 token
- ✅ 退出后无法访问保护页

### AUTH-007: 密码加密 (1)
- ✅ bcrypt 哈希验证

### AUTH-008: 账户锁定 (2)
- ✅ 5 次失败锁定
- ✅ 正确登录重置计数

### AUTH-003/004: OAuth (2)
- ✅ GitHub 按钮
- ✅ Google 按钮

## 📝 Page Object 示例

```typescript
import { AuthPage } from './pages/AuthPage'

test('示例', async ({ page }) => {
  const authPage = new AuthPage(page)

  await authPage.login('test@example.com', 'password123')
  await authPage.waitForDashboard()

  expect(await authPage.getToken()).toBeTruthy()
})
```

## 🔍 选择器模式

```typescript
// 按文本
page.locator('button:has-text("登录")')

// 按类型
page.locator('input[type="email"]')

// 按属性
page.locator('[data-testid="user-email"]')

// 按 CSS class
page.locator('.error, .alert-error')
```

## ⚙️ 配置选项

```typescript
// playwright.config.ts
{
  baseURL: 'http://localhost:3000',
  workers: 1,              // 串行执行
  retries: 0,
  timeout: 30000,
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  }
}
```

## 🛠️ 调试技巧

### 1. 使用 UI 模式
```bash
npm run test:e2e:ui
```

### 2. 慢动作执行
```bash
npx playwright test --slow-mo=1000
```

### 3. 只运行失败测试
```bash
npx playwright test --last-failed
```

### 4. 显示浏览器
```bash
npx playwright test --headed
```

### 5. 截图调试
```typescript
await page.screenshot({ path: 'debug.png' })
```

## 🧪 测试数据

```typescript
// 动态邮箱
`test-${Date.now()}@example.com`

// 测试用户
{
  email: 'test@example.com',
  password: 'Test123456!'
}

// 错误凭据
{
  email: 'wrong@example.com',
  password: 'WrongPassword123!'
}
```

## 🔐 Token 验证

```typescript
// 获取 token
const token = await page.evaluate(() => {
  return localStorage.getItem('token')
})

// 验证 token
expect(token).toBeTruthy()
expect(token?.length).toBeGreaterThan(0)

// 清除 token
await page.evaluate(() => {
  localStorage.clear()
})
```

## 🌐 API 测试

```typescript
// 拦截请求
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes('/api/auth/login')),
  page.click('button[type="submit"]')
])

// 验证响应
expect(response.status()).toBe(200)
const data = await response.json()
expect(data).toHaveProperty('access_token')
```

## 📦 清理策略

```typescript
test.afterEach(async ({ page }) => {
  // 清理测试数据
  const token = await authPage.getToken()
  if (token) {
    await ApiHelper.deleteTestUser(email, token)
  }
})
```

## ❗ 常见错误

### "Connection refused"
确保后端运行在 http://localhost:8000

### "Element not found"
使用 UI 模式检查选择器是否正确

### "Timeout"
增加超时时间或检查网络延迟

### "Email already exists"
清理数据库中的测试用户

## 📚 更多资源

- 详细指南: `TEST_GUIDE.md`
- 实施总结: `TEST_SUMMARY.md`
- Playwright 文档: https://playwright.dev
