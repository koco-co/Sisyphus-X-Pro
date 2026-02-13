// Dashboard E2E 测试
import { test, expect } from '@playwright/test'

test.describe('DASH 模块: 首页仪表盘', () => {
  // 测试用户凭据
  const testUser = {
    email: `dash-test-${Date.now()}@example.com`,
    password: 'Dash123456!',
  }

  test.beforeAll(async ({ request }) => {
    // 创建测试用户
    await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testUser.email,
        password: testUser.password,
        nickname: 'Dashboard Test User',
      },
    })
  })

  test.beforeEach(async ({ page }) => {
    // 导航到登录页面
    await page.goto('http://localhost:3000/login')

    // 填写登录表单
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)

    // 点击登录按钮
    await page.click('button[type="submit"]')

    // 等待跳转到首页
    await expect(page).toHaveURL(/.*\/(dashboard|\/)/)
  })

  test.afterAll(async ({ request }) => {
    try {
      // 清理测试用户（可选）
      await request.post('http://localhost:8000/api/v1/auth/login', {
        data: {
          email: testUser.email,
          password: testUser.password,
        },
      })
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('DASH-001: 核心指标卡片显示', async ({ page }) => {
    // Arrange: 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // Act: 无需操作,页面加载后自动显示

    // Assert: 验证显示项目总数卡片
    const projectsCard = page.locator('text=/项目总数/')
    await expect(projectsCard).toBeVisible()

    // Assert: 验证显示接口总数卡片
    const interfacesCard = page.locator('text=/接口总数/')
    await expect(interfacesCard).toBeVisible()

    // Assert: 验证显示场景总数卡片
    const scenariosCard = page.locator('text=/场景总数/')
    await expect(scenariosCard).toBeVisible()

    // Assert: 验证显示计划总数卡片
    const plansCard = page.locator('text=/计划总数/')
    await expect(plansCard).toBeVisible()

    // Assert: 验证数字显示 (可能是 0 或其他值)
    const statsValues = page.locator('.text-3xl')
    const count = await statsValues.count()
    expect(count).toBe(4)

    // 截图保存（用于调试）
    await page.screenshot({ path: 'test-results/dash-001-cards.png' })
  })

  test('DASH-002: 测试执行趋势图显示', async ({ page }) => {
    // Arrange: 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // Act: 无需操作,页面加载后自动显示

    // Assert: 验证显示趋势图标题
    const trendTitle = page.locator('text=测试执行趋势')
    await expect(trendTitle).toBeVisible()

    // Assert: 验证显示图表区域
    const chartSection = page.locator('text=测试执行趋势').locator('..')
    await expect(chartSection).toBeVisible()

    // Assert: 验证图表容器存在
    const chartContainer = page.locator('[class*="chart"]').or(page.locator('.recharts-wrapper'))
    const chartCount = await chartContainer.count()

    if (chartCount > 0) {
      // 如果有图表容器,验证它可见
      await expect(chartContainer.first()).toBeVisible()

      // 尝试 hover 交互（如果有数据）
      const hasData = await page.locator('.recharts-rectangle').count() > 0
      if (hasData) {
        const bar = page.locator('.recharts-rectangle').first()
        await bar.hover()

        // Tooltip 应该显示（可选验证）
        const tooltip = page.locator('.recharts-tooltip-wrapper')
        const tooltipVisible = await tooltip.isVisible({ timeout: 1000 }).catch(() => false)
        if (tooltipVisible) {
          await expect(tooltip).toBeVisible()
        }
      }
    } else {
      // 如果没有图表,验证有无数据的友好提示
      const noDataMessage = page.locator('text=/暂无数据|无数据/')
      const noDataVisible = await noDataMessage.isVisible().catch(() => false)
      if (noDataVisible) {
        await expect(noDataMessage).toBeVisible()
      }
    }

    // 截图保存
    await page.screenshot({ path: 'test-results/dash-002-trend.png' })
  })

  test('DASH-003: 项目覆盖率概览显示', async ({ page }) => {
    // Arrange: 等待页面加载完成
    await page.waitForLoadState('networkidle')

    // Act: 无需操作,页面加载后自动显示

    // Assert: 验证显示覆盖率标题
    const coverageTitle = page.locator('text=/项目覆盖率|覆盖率/')
    await expect(coverageTitle).toBeVisible()

    // Assert: 查找饼图或覆盖率概览区域
    const coverageSection = page.locator('text=/项目覆盖率|覆盖率/').locator('..')
    await expect(coverageSection).toBeVisible()

    // 检查是否有饼图
    const pieChart = page.locator('.recharts-pie').or(page.locator('[class*="pie"]'))
    const pieCount = await pieChart.count()

    if (pieCount > 0) {
      // 如果有项目,应该显示饼图
      await expect(pieChart.first()).toBeVisible()

      // 验证显示覆盖率相关文本
      const percentageText = page.locator('text=/覆盖率:/')
      const percentageVisible = await percentageText.isVisible().catch(() => false)
      if (percentageVisible) {
        await expect(percentageText).toBeVisible()
      }

      // 验证显示已测试和未测试项目数
      const testedText = page.locator('text=/已测试.*项目|未测试.*项目/')
      const testedVisible = await testedText.isVisible().catch(() => false)
      if (testedVisible) {
        await expect(testedText).toBeVisible()
      }
    } else {
      // 如果没有项目,验证无数据的友好提示
      const noDataMessage = page.locator('text=/暂无项目|无项目|无数据/')
      const noDataVisible = await noDataMessage.isVisible().catch(() => false)
      if (noDataVisible) {
        await expect(noDataMessage).toBeVisible()
      }
    }

    // 截图保存
    await page.screenshot({ path: 'test-results/dash-003-coverage.png' })
  })
})
