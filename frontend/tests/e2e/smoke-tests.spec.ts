import { test, expect } from '@playwright/test'

/**
 * 冒烟测试 - 快速验证核心功能
 *
 * 这些测试覆盖所有 9 个模块的核心流程,
 * 用于快速验证系统基本功能是否正常。
 */

test.describe('冒烟测试: 核心功能验证', () => {
  // 测试用户凭据
  const testUser = {
    email: `smoke-${Date.now()}@example.com`,
    password: 'Smoke123456!',
  }

  test.beforeAll(async ({ request }) => {
    // 创建测试用户
    await request.post('http://localhost:8000/api/auth/register', {
      data: { email: testUser.email, password: testUser.password },
    })
  })

  test('SMOKE-001: 用户登录', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 验证跳转到首页
    await expect(page).toHaveURL(/.*\/dashboard/)
  })

  test('SMOKE-002: 首页加载', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 验证首页元素
    await expect(page.locator('h1')).toBeVisible()
    await expect(page.locator('text=欢迎')).toBeVisible()
  })

  test('SMOKE-003: 项目管理可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到项目管理
    await page.click('text=项目管理')
    await expect(page.locator('h1')).toContainText('项目')
  })

  test('SMOKE-004: 关键字配置可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到关键字配置
    await page.click('text=关键字配置')
    await expect(page.locator('h1')).toContainText('关键字')
  })

  test('SMOKE-005: 接口定义可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到接口定义
    await page.click('text=接口定义')
    await expect(page.locator('h1')).toContainText('接口')
  })

  test('SMOKE-006: 场景配置可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到场景配置
    await page.click('text=场景配置')
    await expect(page.locator('h1')).toContainText('场景')
  })

  test('SMOKE-007: 测试计划可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到测试计划
    await page.click('text=测试计划')
    await expect(page.locator('h1')).toContainText('测试计划')
  })

  test('SMOKE-008: 测试报告可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到测试报告
    await page.click('text=测试报告')
    await expect(page.locator('h1')).toContainText('测试报告')
  })

  test('SMOKE-009: 全局参数可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到全局参数
    await page.click('text=全局参数')
    await expect(page.locator('h1')).toContainText('全局参数')
  })

  test('SMOKE-010: 环境配置可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到环境配置
    await page.click('text=环境配置')
    await expect(page.locator('h1')).toContainText('环境')
  })

  test('SMOKE-011: 全局变量可访问', async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // 导航到全局变量
    await page.click('text=全局变量')
    await expect(page.locator('h1')).toContainText('全局变量')
  })

  test.afterAll(async ({ request }) => {
    // 清理测试用户
    const loginResponse = await request.post('http://localhost:8000/api/auth/login', {
      data: { email: testUser.email, password: testUser.password },
    })
    const loginData = await loginResponse.json()

    await request.delete('http://localhost:8000/api/users/profile', {
      headers: {
        Authorization: `Bearer ${loginData.access_token || loginData.token}`,
      },
    })
  })
})
