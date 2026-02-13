import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
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

const lockoutUser = {
  email: `lockout-test-${Date.now()}@example.com`,
  password: 'LockoutTest123!',
}

test.describe('AUTH-002: 邮箱密码登录', () => {
  let authPage: AuthPage
  let dashboardPage: DashboardPage

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    dashboardPage = new DashboardPage(page)

    // 创建测试用户
    await ApiHelper.createTestUser(testUsers.valid.email, testUsers.valid.password)
  })

  test.afterEach(async ({ page }) => {
    // 清理: 登出并删除用户
    try {
      const token = await authPage.getToken()
      if (token) {
        await ApiHelper.deleteTestUser(testUsers.valid.email, token)
      }
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('应该成功登录并跳转到首页', async ({ page }) => {
    await authPage.login(testUsers.valid.email, testUsers.valid.password)

    // 验证跳转到首页
    await authPage.waitForDashboard()
    expect(await authPage.isOnDashboard()).toBeTruthy()

    // 验证显示用户信息
    await expect(authPage.userEmail).toBeVisible()
    const displayedEmail = await authPage.getUserEmail()
    expect(displayedEmail).toContain(testUsers.valid.email)

    // 验证 token 存入 localStorage
    const token = await authPage.getToken()
    expect(token).toBeTruthy()
    expect(token?.length).toBeGreaterThan(0)
  })

  test('应该拒绝错误密码登录', async ({ page }) => {
    await authPage.login(testUsers.valid.email, testUsers.invalid.password)

    // 验证显示错误消息
    await authPage.waitForErrorMessage()
    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toContain('密码')

    // 验证仍然在登录页
    expect(await authPage.isOnLoginPage()).toBeTruthy()

    // 验证没有 token
    const token = await authPage.getToken()
    expect(token).toBeNull()
  })

  test('应该拒绝未注册邮箱登录', async ({ page }) => {
    await authPage.login(testUsers.invalid.email, testUsers.invalid.password)

    // 验证显示错误消息
    await authPage.waitForErrorMessage()
    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toMatch(/邮箱|用户|不存在|未注册/)

    // 验证仍然在登录页
    expect(await authPage.isOnLoginPage()).toBeTruthy()

    // 验证没有 token
    const token = await authPage.getToken()
    expect(token).toBeNull()
  })

  test('应该显示验证错误（空字段）', async ({ page }) => {
    await authPage.goto()
    await authPage.clickSubmit()

    // 验证显示验证错误
    await expect(authPage.errorMessage).toBeVisible()
  })
})

test.describe('AUTH-005: 退出登录', () => {
  let authPage: AuthPage

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    await ApiHelper.createTestUser(testUsers.valid.email, testUsers.valid.password)
  })

  test.afterEach(async ({ page }) => {
    try {
      await ApiHelper.deleteTestUser(testUsers.valid.email, 'cleanup-token')
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('应该成功退出并清除 token', async ({ page }) => {
    // 先登录
    await authPage.login(testUsers.valid.email, testUsers.valid.password)
    await authPage.waitForDashboard()

    // 验证已登录
    let token = await authPage.getToken()
    expect(token).toBeTruthy()

    // 点击退出
    await authPage.logout()

    // 验证跳转到登录页
    await page.waitForURL('**/login', { timeout: 5000 })
    expect(await authPage.isOnLoginPage()).toBeTruthy()

    // 验证 token 已清除
    token = await authPage.getToken()
    expect(token).toBeNull()
  })

  test('退出后不应该能访问受保护页面', async ({ page }) => {
    // 登录
    await authPage.login(testUsers.valid.email, testUsers.valid.password)
    await authPage.waitForDashboard()

    // 退出
    await authPage.logout()
    await page.waitForURL('**/login')

    // 尝试直接访问首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 应该被重定向到登录页
    expect(await authPage.isOnLoginPage()).toBeTruthy()
  })
})

test.describe('AUTH-007: 密码加密（数据库验证）', () => {
  test('注册后密码应该是 bcrypt 哈希', async ({ page }) => {
    // 这个测试需要数据库访问权限
    // 在真实环境中，我们需要:
    // 1. 注册用户
    // 2. 直接查询数据库
    // 3. 验证密码字段不是明文
    // 4. 验证包含 bcrypt 标识符 ($2a$, $2b$, $2y$)

    // 由于 E2E 测试不能直接访问数据库，
    // 我们通过 API 响应验证密码不会以明文返回
    const authPage = new AuthPage(page)

    // 注册新用户
    const email = `bcrypt-test-${Date.now()}@example.com`
    await authPage.register(email, testUsers.valid.password)

    // 验证注册成功后响应中不包含密码
    // 通过检查网络请求
    const [response] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/register')),
      authPage.clickSubmit(),
    ])

    const responseData = await response.json()
    expect(responseData).not.toHaveProperty('password')
    expect(responseData.user).not.toHaveProperty('password')

    // 清理
    const token = await authPage.getToken()
    if (token) {
      await ApiHelper.deleteTestUser(email, token)
    }
  })
})

test.describe('AUTH-008: 账户锁定机制', () => {
  let authPage: AuthPage

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    // 创建将被锁定的账户
    await ApiHelper.createTestUser(lockoutUser.email, lockoutUser.password)
  })

  test.afterEach(async ({ page }) => {
    try {
      // 用正确密码登录以获取 token
      const token = await ApiHelper.getUserToken(lockoutUser.email, lockoutUser.password)
      await ApiHelper.deleteTestUser(lockoutUser.email, token)
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('5次错误密码后应该锁定账户', async ({ page }) => {
    // 尝试5次错误密码
    for (let i = 1; i <= 5; i++) {
      await authPage.login(lockoutUser.email, testUsers.invalid.password)
      await authPage.waitForErrorMessage()
      await page.waitForTimeout(500) // 短暂等待
    }

    // 第6次尝试应该显示账户锁定错误
    await authPage.login(lockoutUser.email, testUsers.invalid.password)
    await authPage.waitForErrorMessage()
    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toMatch(/锁定|lock|锁定|尝试次数/)

    // 即使使用正确密码也应该被锁定
    await authPage.clearToken()
    await authPage.login(lockoutUser.email, lockoutUser.password)
    await authPage.waitForErrorMessage()
    const lockedMessage = await authPage.getErrorMessageText()
    expect(lockedMessage.toLowerCase()).toMatch(/锁定|lock/)
  })

  test('正确登录应该重置失败计数', async ({ page }) => {
    // 3次错误登录
    for (let i = 1; i <= 3; i++) {
      await authPage.login(lockoutUser.email, testUsers.invalid.password)
      await authPage.waitForErrorMessage()
      await page.waitForTimeout(500)
    }

    // 用正确密码登录（应该重置计数）
    await authPage.clearToken()
    await authPage.login(lockoutUser.email, lockoutUser.password)
    await authPage.waitForDashboard()

    // 验证登录成功
    expect(await authPage.isOnDashboard()).toBeTruthy()

    // 退出后再次尝试5次错误密码（应该再次被锁定）
    await authPage.logout()
    await page.waitForURL('**/login')

    for (let i = 1; i <= 5; i++) {
      await authPage.login(lockoutUser.email, testUsers.invalid.password)
      await authPage.waitForErrorMessage()
      await page.waitForTimeout(500)
    }

    // 第6次应该被锁定
    await authPage.clearToken()
    await authPage.login(lockoutUser.email, lockoutUser.password)
    await authPage.waitForErrorMessage()
    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toMatch(/锁定|lock/)
  })
})

test.describe('AUTH-003 & AUTH-004: OAuth 登录', () => {
  let authPage: AuthPage

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
  })

  test('GitHub OAuth 按钮应该存在并可点击', async ({ page }) => {
    await authPage.goto()

    await expect(authPage.githubButton).toBeVisible()
    await expect(authPage.githubButton).toBeEnabled()

    // 点击按钮（不完成整个 OAuth 流程，因为需要真实的 GitHub 账户）
    await authPage.clickGitHubLogin()

    // 验证跳转到 GitHub OAuth 页面
    await page.waitForURL(/github\.com/, { timeout: 5000 })
    expect(page.url()).toContain('github.com')
  })

  test('Google OAuth 按钮应该存在并可点击', async ({ page }) => {
    await authPage.goto()

    await expect(authPage.googleButton).toBeVisible()
    await expect(authPage.googleButton).toBeEnabled()

    // 点击按钮（不完成整个 OAuth 流程，因为需要真实的 Google 账户）
    await authPage.clickGoogleLogin()

    // 验证跳转到 Google OAuth 页面
    await page.waitForURL(/accounts\.google\.com|google\.com/, { timeout: 5000 })
    expect(page.url()).toMatch(/google\.com|accounts\.google\.com/)
  })

  // 注意: 完整的 OAuth 流程测试需要:
  // 1. 真实的 GitHub/Google 测试账户
  // 2. OAuth 应用配置（localhost 回调）
  // 3. 可能使用 mock OAuth 服务器
  //
  // 在真实环境中，你可能会使用测试专用的 OAuth 配置
  // 或者 mock OAuth provider 的响应

  test.describe('OAuth 完整流程（需要真实配置）', () => {
    test.skip('应该完成 GitHub OAuth 登录', async ({ page }) => {
      // 这个测试需要:
      // 1. 配置真实的 GitHub OAuth 应用
      // 2. 使用测试账户授权
      // 3. 验证自动创建账户
      // 4. 验证跳转到首页
      // 5. 验证显示 GitHub 用户信息

      await authPage.goto()
      await authPage.clickGitHubLogin()

      // 这里需要实际的 GitHub 授权流程
      // 通常在 CI/CD 中会使用 mock OAuth 服务器
    })

    test.skip('应该完成 Google OAuth 登录', async ({ page }) => {
      // 类似 GitHub OAuth 测试
    })
  })
})

test.describe('AUTH-001: 用户注册', () => {
  let authPage: AuthPage

  test.afterEach(async ({ page }) => {
    // 清理测试用户
    try {
      const token = await authPage.getToken()
      if (token) {
        await ApiHelper.deleteTestUser(testUsers.valid.email, token)
      }
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('应该成功注册新用户', async ({ page }) => {
    authPage = new AuthPage(page)
    const email = `new-user-${Date.now()}@example.com`
    const password = 'NewUser123!'

    await authPage.register(email, password)

    // 验证跳转到首页或登录页
    await page.waitForTimeout(2000)
    const url = page.url()
    expect(url).toMatch(/\/$|\/login/)

    // 如果自动登录，验证 token 存在
    const token = await authPage.getToken()
    if (token) {
      expect(token).toBeTruthy()
      await authPage.logout()
    }
  })

  test('应该拒绝重复注册相同邮箱', async ({ page }) => {
    authPage = new AuthPage(page)
    const email = `duplicate-${Date.now()}@example.com`
    const password = 'Duplicate123!'

    // 第一次注册
    await authPage.register(email, password)
    await page.waitForTimeout(1000)

    // 退出
    const token = await authPage.getToken()
    if (token) {
      await authPage.logout()
    }

    // 尝试再次注册
    await authPage.register(email, password)
    await authPage.waitForErrorMessage()

    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toMatch(/已存在|已注册|邮箱/)

    // 清理
    if (token) {
      await ApiHelper.deleteTestUser(email, token)
    }
  })

  test('应该验证密码强度', async ({ page }) => {
    authPage = new AuthPage(page)
    const email = `weak-pass-${Date.now()}@example.com`

    await authPage.gotoRegister()
    await authPage.fillCredentials(email, '123') // 太弱的密码
    await authPage.clickSubmit()

    // 应该显示密码强度错误
    await expect(authPage.errorMessage).toBeVisible()
    const errorMessage = await authPage.getErrorMessageText()
    expect(errorMessage.toLowerCase()).toMatch(/密码|强度|长度/)
  })

  test('应该验证邮箱格式', async ({ page }) => {
    authPage = new AuthPage(page)

    await authPage.gotoRegister()
    await authPage.fillCredentials('invalid-email', 'ValidPass123!')
    await authPage.clickSubmit()

    // 应该显示邮箱格式错误
    await expect(authPage.errorMessage).toBeVisible()
  })
})
