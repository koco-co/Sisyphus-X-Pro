import { test, expect } from '@playwright/test'

/**
 * 示例 E2E 测试
 * 用于演示基本的 Playwright 测试模式
 */

test.describe('示例测试组', () => {
  test('基本页面加载测试', async ({ page }) => {
    // 导航到页面
    await page.goto('/')

    // 验证标题
    await expect(page).toHaveTitle(/Sisyphus/)

    // 验证某个元素存在
    await expect(page.locator('h1')).toBeVisible()
  })

  test('表单交互示例', async ({ page }) => {
    await page.goto('/login')

    // 填写表单
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')

    // 点击按钮
    await page.click('button[type="submit"]')

    // 等待导航
    await page.waitForURL('**/')

    // 验证结果
    await expect(page).toHaveURL('/')
  })

  test('API 拦截示例', async ({ page }) => {
    await page.goto('/login')

    // 拦截 API 请求
    const [response] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/auth/login')),
      page.fill('input[type="email"]', 'test@example.com'),
      page.fill('input[type="password"]', 'password123'),
      page.click('button[type="submit"]'),
    ])

    // 验证响应
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data).toHaveProperty('access_token')
  })

  test('localStorage 验证示例', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')

    // 等待登录成功
    await page.waitForURL('**/')

    // 验证 localStorage
    const token = await page.evaluate(() => {
      return localStorage.getItem('token')
    })

    expect(token).toBeTruthy()
    expect(token?.length).toBeGreaterThan(0)
  })

  test('错误处理示例', async ({ page }) => {
    await page.goto('/login')

    // 使用错误凭据
    await page.fill('input[type="email"]', 'wrong@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // 验证错误消息
    await expect(page.locator('.error, [role="alert"]')).toBeVisible()

    const errorMessage = await page.textContent('.error, [role="alert"]')
    expect(errorMessage).toMatch(/邮箱|密码|不存在/)
  })

  test('截图示例', async ({ page }) => {
    await page.goto('/')

    // 截图保存到 test-results/
    await page.screenshot({ path: 'homepage.png' })

    // 只截图某个元素
    const header = page.locator('header')
    await header.screenshot({ path: 'header.png' })
  })

  test('多步骤工作流示例', async ({ page }) => {
    // 步骤 1: 导航到登录页
    await page.goto('/login')
    await expect(page).toHaveURL('/login')

    // 步骤 2: 填写表单
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')

    // 步骤 3: 提交
    await page.click('button[type="submit"]')

    // 步骤 4: 验证跳转
    await page.waitForURL('**/')
    await expect(page).toHaveURL('/')

    // 步骤 5: 验证登录状态
    const userEmail = await page.textContent('[data-testid="user-email"]')
    expect(userEmail).toContain('test@example.com')

    // 步骤 6: 退出
    await page.click('button:has-text("退出")')
    await page.waitForURL('**/login')
  })
})

/**
 * 使用 test.beforeEach 和 test.afterEach
 */
test.describe('测试钩子示例', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前执行
    console.log('Before each test')
    await page.goto('/login')
  })

  test.afterEach(async ({ page }) => {
    // 每个测试后执行
    console.log('After each test')
  })

  test('测试 1', async ({ page }) => {
    await expect(page).toHaveURL('/login')
  })

  test('测试 2', async ({ page }) => {
    await expect(page).toHaveURL('/login')
  })
})

/**
 * 使用 Page Object 模式示例
 */
class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login')
  }

  async login(email: string, password: string) {
    await this.page.fill('input[type="email"]', email)
    await this.page.fill('input[type="password"]', password)
    await this.page.click('button[type="submit"]')
  }

  async getErrorMessage() {
    return await this.page.textContent('.error, [role="alert"]')
  }
}

test('Page Object 模式示例', async ({ page }) => {
  const loginPage = new LoginPage(page)

  await loginPage.goto()
  await loginPage.login('wrong@example.com', 'wrongpassword')

  const errorMessage = await loginPage.getErrorMessage()
  expect(errorMessage).toBeTruthy()
})
