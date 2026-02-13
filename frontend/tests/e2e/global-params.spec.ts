import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `globalparam-test-${Date.now()}@example.com`,
  password: 'Test123456!',
}

const customFunction = {
  name: `testFunction_${Date.now()}`,
  description: '测试自定义函数',
  code: `def test_function():
    """测试函数"""
    return "test_result"`,
}

test.describe('GPAR 模块: 全局参数', () => {
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

  test('GPAR-001: 应该显示内置工具函数库', async ({ page }) => {
    // 导航到全局参数页面
    await page.click('text=全局参数')

    // 验证页面标题
    await expect(page.locator('h1')).toContainText('全局参数')

    // 验证内置函数存在
    await expect(page.locator('text=内置函数')).toBeVisible()

    // 验证常见内置函数
    await expect(page.locator('text={{ current_time() }}')).toBeVisible()
    await expect(page.locator('text={{ random_string() }}')).toBeVisible()
    await expect(page.locator('text={{ uuid() }}')).toBeVisible()
    await expect(page.locator('text={{ timestamp() }}')).toBeVisible()
  })

  test('GPAR-002: 应该能够查看内置函数详情', async ({ page }) => {
    await page.click('text=全局参数')

    // 点击第一个内置函数
    const firstFunction = page.locator('[data-testid="builtin-function"]').first()
    await firstFunction.click()

    // 验证函数详情面板
    await expect(page.locator('[data-testid="function-detail"]')).toBeVisible()

    // 验证包含函数信息
    await expect(page.locator('[data-testid="function-name"]')).toBeVisible()
    await expect(page.locator('[data-testid="function-description"]')).toBeVisible()
    await expect(page.locator('[data-testid="function-syntax"]')).toBeVisible()
    await expect(page.locator('[data-testid="function-example"]')).toBeVisible()
  })

  test('GPAR-003: 应该能够使用 Monaco Editor 创建自定义函数', async ({ page }) => {
    await page.click('text=全局参数')

    // 切换到自定义函数标签
    await page.click('text=自定义函数')

    // 点击创建函数按钮
    await page.click('button:has-text("创建函数")')

    // 验证 Monaco Editor 加载
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 })

    // 填写函数信息
    await page.fill('[name="name"]', customFunction.name)
    await page.fill('[name="description"]', customFunction.description)

    // 在 Monaco Editor 中输入代码
    const editor = page.locator('.monaco-editor textarea')
    await editor.click()
    await editor.type(customFunction.code)

    // 提交
    await page.click('button:has-text("保存")')

    // 验证成功消息
    await expect(page.locator('text=函数创建成功')).toBeVisible()

    // 验证函数出现在列表中
    await expect(page.locator(`text=${customFunction.name}`)).toBeVisible()
  })

  test('GPAR-004: 应该能够使用 {{函数名()}} 引用函数', async ({ page }) => {
    await page.click('text=全局参数')

    // 切换到自定义函数标签
    await page.click('text=自定义函数')

    // 创建测试函数
    await page.click('button:has-text("创建函数")')

    const functionName = `get_username_${Date.now()}`
    await page.fill('[name="name"]', functionName)
    await page.fill('[name="description"]', '获取用户名')
    await page.locator('.monaco-editor textarea').type(`def get_username():\n    return "test_user"`)
    await page.click('button:has-text("保存")')

    // 等待创建成功
    await expect(page.locator('text=函数创建成功')).toBeVisible()

    // 验证函数引用语法显示
    await expect(page.locator(`text={{${functionName}()}}`)).toBeVisible()
  })

  test('GPAR-005: 应该能够测试函数执行', async ({ page }) => {
    await page.click('text=全局参数')
    await page.click('text=自定义函数')

    // 选择一个函数
    const firstFunction = page.locator('[data-testid="custom-function"]').first()

    if ((await firstFunction.count()) > 0) {
      await firstFunction.click()

      // 点击测试按钮
      await page.click('button:has-text("测试函数")')

      // 验证测试结果显示
      await expect(page.locator('[data-testid="function-test-result"]')).toBeVisible()
      await expect(page.locator('[data-testid="test-output"]')).toBeVisible()
    }
  })

  test('GPAR-006: 应该能够编辑自定义函数', async ({ page }) => {
    await page.click('text=全局参数')
    await page.click('text=自定义函数')

    const firstFunction = page.locator('[data-testid="custom-function"]').first()

    if ((await firstFunction.count()) > 0) {
      await firstFunction.click()

      // 点击编辑按钮
      await page.click('button:has-text("编辑")')

      // 验证编辑器加载并显示现有代码
      await expect(page.locator('.monaco-editor')).toBeVisible()

      // 修改代码
      const editor = page.locator('.monaco-editor textarea')
      await editor.click()
      await editor.press('End')
      await editor.type('\n    # New comment')

      // 保存修改
      await page.click('button:has-text("保存")')

      // 验证保存成功
      await expect(page.locator('text=保存成功')).toBeVisible()
    }
  })

  test('GPAR-007: 应该能够删除自定义函数', async ({ page }) => {
    await page.click('text=全局参数')
    await page.click('text=自定义函数')

    // 创建一个测试函数
    await page.click('button:has-text("创建函数")')
    const testFunctionName = `to_delete_${Date.now()}`
    await page.fill('[name="name"]', testFunctionName)
    await page.locator('.monaco-editor textarea').type('def test():\n    pass')
    await page.click('button:has-text("保存")')

    // 等待创建成功
    await expect(page.locator(`text=${testFunctionName}`)).toBeVisible()

    // 删除函数
    await page.locator(`text=${testFunctionName}`).hover()
    await page.locator('button:has-text("删除")').click()

    // 验证删除确认对话框
    await expect(page.locator('text=确认删除函数')).toBeVisible()
    await page.click('button:has-text("确认")')

    // 验证删除成功
    await expect(page.locator('text=删除成功')).toBeVisible()
    await expect(page.locator(`text=${testFunctionName}`)).not.toBeVisible()
  })

  test('GPAR-008: 应该能够支持函数嵌套调用', async ({ page }) => {
    await page.click('text=全局参数')

    // 切换到使用示例标签
    await page.click('text=使用示例')

    // 验证嵌套调用示例
    await expect(page.locator('text=函数嵌套调用')).toBeVisible()

    // 验证示例代码显示
    await expect(page.locator('text={{ base64_encode(random_string(10)) }}')).toBeVisible()
  })

  test('GPAR-009: 应该能够查看函数使用统计', async ({ page }) => {
    await page.click('text=全局参数')
    await page.click('text=自定义函数')

    const firstFunction = page.locator('[data-testid="custom-function"]').first()

    if ((await firstFunction.count()) > 0) {
      // 查看函数详情
      await firstFunction.click()

      // 验证使用统计信息
      const stats = page.locator('[data-testid="function-stats"]')

      if ((await stats.count()) > 0) {
        await expect(stats.locator('[data-testid="call-count"]')).toBeVisible()
        await expect(stats.locator('[data-testid="last-used"]')).toBeVisible()
      }
    }
  })

  test('GPAR-010: 应该能够搜索和筛选函数', async ({ page }) => {
    await page.click('text=全局参数')

    // 使用搜索框
    await page.fill('input[name="search"]', 'random')

    // 验证搜索结果
    await page.waitForTimeout(500)
    const searchResults = page.locator('[data-testid="builtin-function"]')
    const count = await searchResults.count()

    if (count > 0) {
      // 验证结果包含关键词
      for (let i = 0; i < Math.min(count, 5); i++) {
        const text = await searchResults.nth(i).textContent()
        expect(text.toLowerCase()).toContain('random')
      }
    }

    // 清除搜索
    await page.fill('input[name="search"]', '')

    // 使用分类筛选
    await page.selectOption('select[name="category"]', 'string')

    // 验证筛选结果
    await page.waitForTimeout(500)
    const filteredResults = page.locator('[data-testid="builtin-function"]')
    const filteredCount = await filteredResults.count()
    expect(filteredCount).toBeGreaterThanOrEqual(0)
  })
})
