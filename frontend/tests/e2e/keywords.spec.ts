import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `keyword-test-${Date.now()}@example.com`,
  password: 'Test123456!',
}

const customKeyword = {
  name: `测试关键字_${Date.now()}`,
  description: '自动化测试创建的关键字',
  code: 'def test_keyword():\n    return "success"',
}

test.describe('KEYW 模块: 关键字配置', () => {
  let authPage: AuthPage
  let dashboardPage: DashboardPage

  test.beforeAll(async () => {
    // 创建测试用户
    await ApiHelper.createTestUser(testUser.email, testUser.password)
  })

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    dashboardPage = new DashboardPage(page)

    // 登录
    await authPage.login(testUser.email, testUser.password)
    await expect(page).toHaveURL(/.*\/(dashboard|\/)/)
  })

  test.afterAll(async ({ page }) => {
    try {
      const token = await authPage.getToken()
      if (token) {
        await ApiHelper.deleteTestUser(testUser.email, token)
      }
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('KEYW-001: 应该显示内置关键字列表', async ({ page }) => {
    // 导航到关键字配置页面
    await page.click('text=关键字配置')

    // 等待页面加载
    await expect(page.locator('h1')).toContainText('关键字配置')

    // 验证内置关键字存在
    await expect(page.locator('text=发送 HTTP 请求')).toBeVisible()
    await expect(page.locator('text=JSON 路径提取')).toBeVisible()
    await expect(page.locator('text=断言响应状态码')).toBeVisible()
    await expect(page.locator('text=数据库查询')).toBeVisible()
  })

  test('KEYW-002: 应该加载 Monaco Editor', async ({ page }) => {
    await page.click('text=关键字配置')

    // 点击创建自定义关键字按钮
    await page.click('button:has-text("创建关键字")')

    // 验证 Monaco Editor 加载
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 })

    // 验证编辑器功能
    const editor = page.locator('.monaco-editor textarea')
    await expect(editor).toBeVisible()
  })

  test('KEYW-003: 应该能够启用/禁用关键字', async ({ page }) => {
    await page.click('text=关键字配置')

    // 找到第一个关键字
    const firstKeyword = page.locator('[data-testid="keyword-item"]').first()

    // 获取初始状态
    const initialStatus = await firstKeyword
      .locator('[data-testid="keyword-status"]')
      .textContent()

    // 点击切换按钮
    await firstKeyword.click()

    // 等待状态更新
    await page.waitForTimeout(500)

    // 验证状态已改变
    const newStatus = await firstKeyword
      .locator('[data-testid="keyword-status"]')
      .textContent()
    expect(newStatus).not.toBe(initialStatus)
  })

  test('KEYW-004: 应该能够创建自定义关键字', async ({ page }) => {
    await page.click('text=关键字配置')
    await page.click('button:has-text("创建关键字")')

    // 填写关键字信息
    await page.fill('[name="name"]', customKeyword.name)
    await page.fill('[name="description"]', customKeyword.description)

    // 在 Monaco Editor 中输入代码
    const editor = page.locator('.monaco-editor textarea')
    await editor.click()
    await editor.type(customKeyword.code)

    // 提交
    await page.click('button:has-text("保存")')

    // 验证成功消息
    await expect(page.locator('text=创建成功')).toBeVisible()

    // 验证关键字出现在列表中
    await expect(page.locator(`text=${customKeyword.name}`)).toBeVisible()
  })

  test('KEYW-005: 应该能够编辑关键字参数', async ({ page }) => {
    await page.click('text=关键字配置')

    // 点击第一个关键字
    await page.locator('[data-testid="keyword-item"]').first().click()

    // 验证参数配置面板
    await expect(page.locator('text=参数配置')).toBeVisible()

    // 添加新参数
    await page.click('button:has-text("添加参数")')
    await page.fill('[name="param-name"]', 'test_param')
    await page.selectOption('[name="param-type"]', 'string')
    await page.fill('[name="param-default"]', 'default_value')

    // 保存参数
    await page.click('button:has-text("保存参数")')

    // 验证参数已添加
    await expect(page.locator('text=test_param')).toBeVisible()
  })
})
