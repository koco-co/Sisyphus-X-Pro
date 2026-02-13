import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `report-test-${Date.now()}@example.com`,
  password: 'Test123456!',
}

test.describe('REPT 模块: 测试报告', () => {
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

  test('REPT-001: 应该能够查看测试报告列表', async ({ page }) => {
    // 导航到测试报告页面
    await page.click('text=测试报告')

    // 验证报告列表显示
    await expect(page.locator('h1')).toContainText('测试报告')
    await expect(page.locator('[data-testid="report-list"]')).toBeVisible()

    // 验证列表包含必要的列
    await expect(page.locator('text=报告名称')).toBeVisible()
    await expect(page.locator('text=执行时间')).toBeVisible()
    await expect(page.locator('text=状态')).toBeVisible()
    await expect(page.locator('text=操作')).toBeVisible()
  })

  test('REPT-002: 应该能够查看平台报告详情', async ({ page }) => {
    await page.click('text=测试报告')

    // 选择第一个报告
    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      await firstReport.click()

      // 验证报告详情页面
      await expect(page.locator('[data-testid="report-detail"]')).toBeVisible()

      // 验证报告包含必要的信息
      await expect(page.locator('[data-testid="report-summary"]')).toBeVisible()
      await expect(page.locator('[data-testid="test-results"]')).toBeVisible()
      await expect(page.locator('[data-testid="execution-metrics"]')).toBeVisible()

      // 验证统计卡片
      await expect(page.locator('text=总用例数')).toBeVisible()
      await expect(page.locator('text=通过数')).toBeVisible()
      await expect(page.locator('text=失败数')).toBeVisible()
      await expect(page.locator('text=跳过数')).toBeVisible()
      await expect(page.locator('text=通过率')).toBeVisible()
    }
  })

  test('REPT-003: 应该能够查看 Allure 报告', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      await firstReport.click()

      // 点击查看 Allure 报告按钮
      const allureButton = page.locator('button:has-text("Allure 报告")')

      if ((await allureButton.count()) > 0) {
        await allureButton.click()

        // 验证 Allure 报告在新标签页打开
        const page1 = await context.waitForEvent('page')
        await page1.waitForLoadState()
        await expect(page1).toHaveURL(/allure/)

        // 验证 Allure 报告内容
        await expect(page1.locator('.chart')).toBeVisible()
      }
    }
  })

  test('REPT-004: 应该能够导出报告为 PDF', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      // 启动下载监听
      const downloadPromise = page.waitForEvent('download')

      // 点击导出按钮
      await firstReport.hover()
      await page.locator('button:has-text("导出 PDF")').click()

      // 等待下载完成
      const download = await downloadPromise

      // 验证文件名
      expect(download.suggestedFilename()).toMatch(/\.pdf$/)
    }
  })

  test('REPT-005: 应该能够导出报告为 HTML', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      // 启动下载监听
      const downloadPromise = page.waitForEvent('download')

      // 点击导出按钮
      await firstReport.hover()
      await page.locator('button:has-text("导出 HTML")').click()

      // 等待下载完成
      const download = await downloadPromise

      // 验证文件名
      expect(download.suggestedFilename()).toMatch(/\.html$/)
    }
  })

  test('REPT-006: 应该能够删除报告', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      // 获取报告名称
      const reportName = await firstReport.textContent()

      // 点击删除按钮
      await firstReport.hover()
      await page.locator('button:has-text("删除")').click()

      // 验证删除确认对话框
      await expect(page.locator('text=确认删除报告')).toBeVisible()
      await page.click('button:has-text("确认")')

      // 验证删除成功消息
      await expect(page.locator('text=删除成功')).toBeVisible()

      // 验证报告不再出现在列表中
      await expect(page.locator(`text=${reportName}`)).not.toBeVisible()
    }
  })

  test('REPT-007: 应该能够筛选报告列表', async ({ page }) => {
    await page.click('text=测试报告')

    // 使用状态筛选器
    await page.selectOption('select[name="status"]', 'passed')

    // 验证筛选结果
    const reportItems = page.locator('[data-testid="report-item"]')
    const count = await reportItems.count()

    if (count > 0) {
      // 验证所有显示的报告都是通过状态
      for (let i = 0; i < count; i++) {
        const status = await reportItems.nth(i).locator('[data-testid="report-status"]').textContent()
        expect(status).toContain('通过')
      }
    }
  })

  test('REPT-008: 应该能够搜索报告', async ({ page }) => {
    await page.click('text=测试报告')

    // 在搜索框输入关键词
    await page.fill('input[name="search"]', '测试')

    // 等待搜索结果
    await page.waitForTimeout(500)

    // 验证搜索结果
    const reportItems = page.locator('[data-testid="report-item"]')
    const count = await reportItems.count()

    if (count > 0) {
      // 验证所有结果都包含搜索关键词
      for (let i = 0; i < Math.min(count, 5); i++) {
        const text = await reportItems.nth(i).textContent()
        expect(text).toMatch(/测试/)
      }
    }
  })

  test('REPT-009: 应该能够查看测试用例详情', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      await firstReport.click()

      // 等待报告详情加载
      await expect(page.locator('[data-testid="report-detail"]')).toBeVisible()

      // 点击第一个测试用例
      const firstTestCase = page.locator('[data-testid="test-case"]').first()

      if ((await firstTestCase.count()) > 0) {
        await firstTestCase.click()

        // 验证用例详情面板显示
        await expect(page.locator('[data-testid="test-case-detail"]')).toBeVisible()

        // 验证用例详情包含必要信息
        await expect(page.locator('[data-testid="case-name"]')).toBeVisible()
        await expect(page.locator('[data-testid="case-status"]')).toBeVisible()
        await expect(page.locator('[data-testid="case-duration"]')).toBeVisible()
        await expect(page.locator('[data-testid="case-logs"]')).toBeVisible()
      }
    }
  })

  test('REPT-010: 应该能够查看执行日志', async ({ page }) => {
    await page.click('text=测试报告')

    const firstReport = page.locator('[data-testid="report-item"]').first()

    if ((await firstReport.count()) > 0) {
      await firstReport.click()

      // 点击执行日志标签
      await page.click('text=执行日志')

      // 验证日志显示
      await expect(page.locator('[data-testid="execution-logs"]')).toBeVisible()

      // 验证日志内容
      const logs = page.locator('[data-testid="log-entry"]')
      const logCount = await logs.count()

      if (logCount > 0) {
        // 验证日志包含时间戳和消息
        await expect(logs.first().locator('[data-testid="log-time"]')).toBeVisible()
        await expect(logs.first().locator('[data-testid="log-message"]')).toBeVisible()
      }
    }
  })
})
