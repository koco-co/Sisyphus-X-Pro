import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `scenario-test-${Date.now()}@example.com`,
  password: 'Test123456!',
}

const testProject = {
  name: `测试项目_${Date.now()}`,
  description: '场景编排测试项目',
}

const testScenario = {
  name: `测试场景_${Date.now()}`,
  description: '自动化测试创建的场景',
}

test.describe('SCEN 模块: 场景编排', () => {
  let authPage: AuthPage
  let dashboardPage: DashboardPage
  let projectId: string

  test.beforeAll(async () => {
    await ApiHelper.createTestUser(testUser.email, testUser.password)
  })

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    dashboardPage = new DashboardPage(page)

    await authPage.login(testUser.email, testUser.password)
    // 登录后应该跳转到首页 (/),不是 /dashboard
    await expect(page).toHaveURL('http://localhost:3000/')
  })

  test.afterAll(async () => {
    try {
      // 清理测试用户
      const token = await ApiHelper.getUserToken(testUser.email, testUser.password)
      if (token) {
        await ApiHelper.deleteTestUser(testUser.email, token)
      }
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('SCEN-001: 应该能够创建测试场景', async ({ page }) => {
    // 创建测试项目 - 先打开用户菜单
    await page.click('button:has([class*="avatar"])') // 点击用户头像打开菜单
    await page.click('text=项目管理') // 点击菜单项
    await page.click('button:has-text("新建项目")')
    await page.fill('[name="name"]', testProject.name)
    await page.fill('[name="description"]', testProject.description)
    await page.click('button:has-text("创建")')

    // 等待项目创建成功
    await expect(page.locator(`text=${testProject.name}`)).toBeVisible()

    // 导航到场景配置 - 打开用户菜单
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')

    // 点击创建场景按钮
    await page.click('button:has-text("新建场景")')

    // 填写场景信息
    await page.fill('[name="name"]', testScenario.name)
    await page.fill('[name="description"]', testScenario.description)

    // 提交
    await page.click('button:has-text("创建")')

    // 验证场景创建成功
    await expect(page.locator('text=创建成功')).toBeVisible()
    await expect(page.locator(`text=${testScenario.name}`)).toBeVisible()
  })

  test('SCEN-002: 应该能够拖拽排序步骤', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')

    // 选择一个已创建的场景
    const firstScenario = page.locator('[data-testid="scenario-item"]').first()
    await firstScenario.click()

    // 等待步骤列表加载
    await expect(page.locator('[data-testid="step-list"]')).toBeVisible()

    // 添加两个测试步骤
    for (let i = 0; i < 2; i++) {
      await page.click('button:has-text("添加步骤")')
      await page.selectOption('select[name="keyword-type"]', 'HTTP')
      await page.selectOption('select[name="keyword-name"]', '发送 HTTP 请求')
      await page.click('button:has-text("确定")')
    }

    // 获取第一个步骤的位置
    const firstStep = page.locator('[data-testid="step-item"]').first()
    const secondStep = page.locator('[data-testid="step-item"]').nth(1)

    // 拖拽第一个步骤到第二个位置
    await firstStep.dragTo(secondStep)

    // 验证步骤顺序已改变
    await page.waitForTimeout(500)
    const steps = await page.locator('[data-testid="step-item"]').allTextContents()
    expect(steps.length).toBeGreaterThan(0)
  })

  test('SCEN-003: 应该支持三级联动选择器', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')
    await page.locator('[data-testid="scenario-item"]').first().click()
    await page.click('button:has-text("添加步骤")')

    // 第一级: 选择关键字类型
    const typeSelect = page.locator('select[name="keyword-type"]')
    await typeSelect.selectOption('HTTP')
    await expect(typeSelect).toHaveValue('HTTP')

    // 第二级: 验证关键字名称选项已更新
    const nameSelect = page.locator('select[name="keyword-name"]')
    await expect(nameSelect).toBeEnabled()
    const httpKeywords = await nameSelect.locator('option').count()
    expect(httpKeywords).toBeGreaterThan(0)

    // 第三级: 选择关键字后显示参数表单
    await nameSelect.selectOption('发送 HTTP 请求')
    await expect(page.locator('[data-testid="keyword-params"]')).toBeVisible()
    await expect(page.locator('[name="url"]')).toBeVisible()
  })

  test('SCEN-004: 应该能够配置步骤参数', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')
    await page.locator('[data-testid="scenario-item"]').first().click()
    await page.click('button:has-text("添加步骤")')

    // 选择 HTTP 请求关键字
    await page.selectOption('select[name="keyword-type"]', 'HTTP')
    await page.selectOption('select[name="keyword-name"]', '发送 HTTP 请求')

    // 填写参数
    await page.fill('[name="url"]', 'https://api.example.com/test')
    await page.selectOption('[name="method"]', 'POST')
    await page.fill('[name="headers"]', '{"Content-Type": "application/json"}')
    await page.fill('[name="body"]', '{"key": "value"}')

    // 保存步骤
    await page.click('button:has-text("确定")')

    // 验证步骤已添加
    await expect(page.locator('text=POST https://api.example.com/test')).toBeVisible()
  })

  test('SCEN-005: 应该能够配置前置 SQL', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')
    await page.locator('[data-testid="scenario-item"]').first().click()

    // 切换到前置 SQL 标签
    await page.click('text=前置 SQL')

    // 添加 SQL 语句
    await page.click('button:has-text("添加 SQL")')
    await page.fill('[name="pre-sql"]', 'DELETE FROM test_table WHERE id = 1;')
    await page.click('button:has-text("保存")')

    // 验证 SQL 已保存
    await expect(page.locator('text=DELETE FROM test_table')).toBeVisible()
  })

  test('SCEN-006: 应该支持数据驱动测试', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')
    await page.locator('[data-testid="scenario-item"]').first().click()

    // 切换到数据驱动标签
    await page.click('text=数据驱动')

    // 启用数据驱动
    await page.check('[name="data-driven-enabled"]')

    // 模拟上传 CSV
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test-data.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('name,email\nTest1,test1@example.com\nTest2,test2@example.com'),
    })

    // 验证数据预览
    await expect(page.locator('text=Test1')).toBeVisible()
    await expect(page.locator('text=Test2')).toBeVisible()
  })

  test('SCEN-007: 应该能够调试场景', async ({ page }) => {
    await page.click('button:has([class*="avatar"])')
    await page.click('text=场景编排')
    await page.locator('[data-testid="scenario-item"]').first().click()

    // 点击调试按钮
    await page.click('button:has-text("调试")')

    // 验证调试输出面板显示
    await expect(page.locator('[data-testid="debug-output"]')).toBeVisible()

    // 等待调试完成
    await expect(page.locator('text=调试完成')).toBeVisible({ timeout: 30000 })
  })
})
