import { test as base } from '@playwright/test'

// 扩展 Playwright test 以包含自定义 fixtures
export const test = base.extend<{
  authenticatedPage: any
}>({
  authenticatedPage: async ({ page }, use) => {
    // 在测试前自动登录
    await page.goto('http://localhost:3000/login')

    // 创建测试用户
    const testEmail = `auth-${Date.now()}@example.com`
    const testPassword = 'Test123456!'

    // 注册用户
    await page.fill('input[name="email"]', testEmail)
    await page.fill('input[name="password"]', testPassword)
    await page.click('button[type="submit"]')

    // 等待跳转到首页
    await page.waitForURL(/.*\/dashboard/, { timeout: 5000 })

    // 使用已认证的页面
    await use(page)

    // 测试后清理
    await page.context().clearCookies()
  },
})

export { expect } from '@playwright/test'
