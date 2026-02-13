// Dashboard E2E 测试
import { test, expect } from '@playwright/test'

test.describe('Dashboard 仪表盘', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到登录页面
    await page.goto('http://localhost:3000/login')

    // 填写登录表单 (使用测试账户)
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'test123456')

    // 点击登录按钮
    await page.click('button[type="submit"]')

    // 等待跳转到首页
    await page.waitForURL('http://localhost:3000/')
  })

  test('DASH-001: 核心指标卡片显示', async ({ page }) => {
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // 验证显示项目总数卡片
    const projectsCard = page.locator('text=/项目总数/')
    await expect(projectsCard).toBeVisible()

    // 验证显示接口总数卡片
    const interfacesCard = page.locator('text=/接口总数/')
    await expect(interfacesCard).toBeVisible()

    // 验证显示场景总数卡片
    const scenariosCard = page.locator('text=/场景总数/')
    await expect(scenariosCard).toBeVisible()

    // 验证显示计划总数卡片
    const plansCard = page.locator('text=/计划总数/')
    await expect(plansCard).toBeVisible()

    // 验证数字显示 (可能是 0 或其他值)
    const statsValues = page.locator('.text-3xl')
    const count = await statsValues.count()
    expect(count).toBe(4)
  })

  test('DASH-002: 测试执行趋势图显示', async ({ page }) => {
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // 验证显示趋势图标题
    const trendTitle = page.locator('text=测试执行趋势')
    await expect(trendTitle).toBeVisible()

    // 验证显示图表区域
    const chartContainer = page.locator('text=测试执行趋势').locator('..').locator('.recharts-wrapper')
    await expect(chartContainer).toBeVisible()

    // 如果有数据,验证 hover 交互
    const hasData = await page.locator('.recharts-bar-rectangle').count() > 0
    if (hasData) {
      // 验证图表可以交互
      const bar = page.locator('.recharts-bar-rectangle').first()
      await bar.hover()
      // Tooltip 应该显示
      const tooltip = page.locator('.recharts-tooltip-wrapper')
      await expect(tooltip).toBeVisible()
    }
  })

  test('DASH-003: 项目覆盖率概览显示', async ({ page }) => {
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // 验证显示覆盖率标题
    const coverageTitle = page.locator('text=项目覆盖率概览')
    await expect(coverageTitle).toBeVisible()

    // 验证显示饼图
    const pieChart = page.locator('.recharts-pie')
    const pieCount = await pieChart.count()

    // 如果有项目,应该显示饼图
    if (pieCount > 0) {
      await expect(pieChart.first()).toBeVisible()

      // 验证显示覆盖率百分比
      const percentageText = page.locator('text=/覆盖率:/')
      await expect(percentageText).toBeVisible()

      // 验证显示已测试和未测试项目数
      const testedText = page.locator('text=/已测试项目:/')
      await expect(testedText).toBeVisible()
    }
  })
})
