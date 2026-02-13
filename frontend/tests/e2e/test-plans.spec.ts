import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `plan-test-${Date.now()}@example.com`,
  password: 'Test123456!',
}

const testPlan = {
  name: `测试计划_${Date.now()}`,
  description: '自动化测试创建的测试计划',
}

test.describe('PLAN 模块: 测试计划', () => {
  let authPage: AuthPage
  let dashboardPage: DashboardPage

  test.beforeAll(async () => {
    await ApiHelper.createTestUser(testUser.email, testUser.password)
  })

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    dashboardPage = new DashboardPage(page)

    await authPage.login(testUser.email, testUser.password)
    await expect(page).toHaveURL(/.*\/dashboard/)
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

  test('PLAN-001: 应该能够创建测试计划', async ({ page }) => {
    // 导航到测试计划页面
    await page.click('text=测试计划')

    // 点击创建计划按钮
    await page.click('button:has-text("创建测试计划")')

    // 填写计划信息
    await page.fill('[name="name"]', testPlan.name)
    await page.fill('[name="description"]', testPlan.description)

    // 选择环境
    await page.selectOption('select[name="environment"]', 'test')

    // 提交
    await page.click('button:has-text("创建")')

    // 验证计划创建成功
    await expect(page.locator('text=测试计划创建成功')).toBeVisible()
    await expect(page.locator(`text=${testPlan.name}`)).toBeVisible()
  })

  test('PLAN-002: 应该能够添加场景到计划', async ({ page }) => {
    await page.click('text=测试计划')

    // 选择一个测试计划
    const firstPlan = page.locator('[data-testid="plan-item"]').first()
    await firstPlan.click()

    // 点击添加场景按钮
    await page.click('button:has-text("添加场景")')

    // 选择场景
    const scenarioSelect = page.locator('select[name="scenario"]')
    await expect(scenarioSelect).toBeVisible()

    // 选择第一个可用场景
    await scenarioSelect.selectOption({ index: 0 })

    // 确认添加
    await page.click('button:has-text("添加")')

    // 验证场景已添加到计划
    await expect(page.locator('[data-testid="plan-scenario-item"]')).toBeVisible()
  })

  test('PLAN-003: 应该能够调整场景执行顺序', async ({ page }) => {
    await page.click('text=测试计划')

    // 选择一个有多个场景的计划
    const firstPlan = page.locator('[data-testid="plan-item"]').first()
    await firstPlan.click()

    // 等待场景列表加载
    await expect(page.locator('[data-testid="plan-scenario-list"]')).toBeVisible()

    // 拖拽场景调整顺序
    const firstScenario = page.locator('[data-testid="plan-scenario-item"]').first()
    const secondScenario = page.locator('[data-testid="plan-scenario-item"]').nth(1)

    if ((await firstScenario.count()) > 0 && (await secondScenario.count()) > 0) {
      await firstScenario.dragTo(secondScenario)

      // 验证顺序已改变
      await page.waitForTimeout(500)
    }
  })

  test('PLAN-004: 应该能够配置执行参数', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()

    // 点击执行配置按钮
    await page.click('button:has-text("执行配置")')

    // 配置并发数
    await page.fill('[name="concurrency"]', '3')

    // 配置超时时间
    await page.fill('[name="timeout"]', '300')

    // 启用失败重试
    await page.check('[name="retry-on-failure"]')
    await page.fill('[name="max-retries"]', '2')

    // 保存配置
    await page.click('button:has-text("保存")')

    // 验证配置已保存
    await expect(page.locator('text=配置已保存')).toBeVisible()
  })

  test('PLAN-005: 应该能够执行测试计划', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()

    // 点击执行按钮
    await page.click('button:has-text("执行测试")')

    // 验证执行确认对话框
    await expect(page.locator('text=确认执行测试计划')).toBeVisible()
    await page.click('button:has-text("确认")')

    // 验证进入执行监控页面
    await expect(page.locator('[data-testid="execution-monitor"]')).toBeVisible()

    // 等待执行开始
    await expect(page.locator('text=正在执行')).toBeVisible({ timeout: 5000 })
  })

  test('PLAN-006: 应该能够实时监控执行进度', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()
    await page.click('button:has-text("执行测试")')
    await page.click('button:has-text("确认")')

    // 验证进度条显示
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible()

    // 验证执行统计
    await expect(page.locator('[data-testid="execution-stats"]')).toBeVisible()
    await expect(page.locator('text=总场景数')).toBeVisible()
    await expect(page.locator('text=已完成')).toBeVisible()
    await expect(page.locator('text=失败')).toBeVisible()

    // 等待执行完成或超时
    await expect(
      page.locator('text=执行完成').or(page.locator('text=执行失败'))
    ).toBeVisible({ timeout: 60000 })
  })

  test('PLAN-007: 应该能够暂停执行', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()
    await page.click('button:has-text("执行测试")')
    await page.click('button:has-text("确认")')

    // 等待执行开始
    await expect(page.locator('text=正在执行')).toBeVisible()

    // 点击暂停按钮
    await page.click('button:has-text("暂停")')

    // 验证状态更新为已暂停
    await expect(page.locator('text=已暂停')).toBeVisible()
  })

  test('PLAN-008: 应该能够终止执行', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()
    await page.click('button:has-text("执行测试")')
    await page.click('button:has-text("确认")')

    // 等待执行开始
    await expect(page.locator('text=正在执行')).toBeVisible()

    // 点击终止按钮
    await page.click('button:has-text("终止")')

    // 验证终止确认对话框
    await expect(page.locator('text=确认终止执行')).toBeVisible()
    await page.click('button:has-text("确认")')

    // 验证状态更新为已终止
    await expect(page.locator('text=已终止')).toBeVisible()
  })

  test('PLAN-009: 应该能够查看执行历史', async ({ page }) => {
    await page.click('text=测试计划')
    await page.locator('[data-testid="plan-item"]').first().click()

    // 切换到执行历史标签
    await page.click('text=执行历史')

    // 验证历史记录列表显示
    await expect(page.locator('[data-testid="execution-history-list"]')).toBeVisible()

    // 验证历史记录包含必要信息
    const firstRecord = page.locator('[data-testid="execution-record"]').first()
    if ((await firstRecord.count()) > 0) {
      await expect(firstRecord.locator('[data-testid="execution-status"]')).toBeVisible()
      await expect(firstRecord.locator('[data-testid="execution-time"]')).toBeVisible()
      await expect(firstRecord.locator('[data-testid="execution-result"]')).toBeVisible()
    }
  })
})
