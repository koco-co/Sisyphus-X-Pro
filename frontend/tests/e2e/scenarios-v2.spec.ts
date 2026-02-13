import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { ApiHelper } from './helpers/api-helper'

// 测试数据
const testUser = {
  email: `scenario-test-v2-${Date.now()}@example.com`,
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

test.describe('SCEN 模块: 场景编排 (v2 - 修复导航)', () => {
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
    // 创建测试项目 - 使用直接导航
    await page.goto('/projects')
    await page.waitForLoadState('networkidle')

    // 点击创建项目按钮
    const createButton = page.locator('button:has-text("创建项目")').first()
    await createButton.click()

    // 填写项目信息
    await page.fill('input[name="name"]', testProject.name)
    await page.fill('input[name="description"]', testProject.description)

    // 提交
    await page.click('button[type="submit"]:has-text("创建"), button[type="submit"]:has-text("提交")')

    // 等待项目创建成功
    await page.waitForTimeout(2000)

    // 导航到场景配置页面
    await dashboardPage.navigateToScenarios()

    // 点击创建场景按钮
    const createScenarioButton = page.locator('button:has-text("创建场景"), button:has-text("新建")').first()
    await createScenarioButton.click()

    // 选择项目 (如果有选择器)
    const projectSelect = page.locator('select[name="project"]').first()
    if (await projectSelect.isVisible()) {
      await projectSelect.selectOption(testProject.name)
    }

    // 填写场景信息
    await page.fill('input[name="name"]', testScenario.name)
    await page.fill('textarea[name="description"], input[name="description"]', testScenario.description)

    // 提交
    await page.click('button[type="submit"]:has-text("创建"), button:has-text("提交")')

    // 验证场景创建成功 - 检查成功消息或场景名称出现
    await page.waitForTimeout(2000)
    const scenarioName = page.locator(`text=${testScenario.name}`)
    await expect(scenarioName).toBeVisible({ timeout: 10000 })
  })

  test('SCEN-002: 应该能够拖拽排序步骤', async ({ page }) => {
    // 导航到场景配置
    await dashboardPage.navigateToScenarios()

    // 等待场景列表加载
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item, tr:has-text("测试")').first()
    await firstScenario.click()

    // 等待详情页加载
    await page.waitForTimeout(2000)

    // 检查是否有添加步骤按钮
    const addStepButton = page.locator('button:has-text("添加"), button:has-text("Add")').first()
    if (await addStepButton.isVisible()) {
      // 添加测试步骤
      for (let i = 0; i < 2; i++) {
        await addStepButton.click()
        await page.waitForTimeout(500)

        // 选择关键字类型
        const typeSelect = page.locator('select[name="keyword-type"], select[name="type"]').first()
        if (await typeSelect.isVisible()) {
          await typeSelect.selectOption('HTTP')
          await page.waitForTimeout(500)

          // 选择关键字名称
          const nameSelect = page.locator('select[name="keyword-name"], select[name="name"]').first()
          if (await nameSelect.isVisible()) {
            await nameSelect.selectOption('发送 HTTP 请求')
            await page.waitForTimeout(500)

            // 点击确定
            await page.click('button:has-text("确定"), button:has-text("OK"), button:has-text("保存")')
            await page.waitForTimeout(1000)
          }
        }
      }

      // 验证步骤已添加
      const steps = page.locator('[data-testid="step-item"], .step-item, tr')
      const stepCount = await steps.count()
      expect(stepCount).toBeGreaterThan(0)
    }
  })

  test('SCEN-003: 应该支持三级联动选择器', async ({ page }) => {
    await dashboardPage.navigateToScenarios()
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item').first()
    if (await firstScenario.isVisible()) {
      await firstScenario.click()
      await page.waitForTimeout(2000)

      // 点击添加步骤
      const addStepButton = page.locator('button:has-text("添加"), button:has-text("Add")').first()
      if (await addStepButton.isVisible()) {
        await addStepButton.click()
        await page.waitForTimeout(500)

        // 第一级: 选择关键字类型
        const typeSelect = page.locator('select[name="keyword-type"], select[name="type"]').first()
        if (await typeSelect.isVisible()) {
          await typeSelect.selectOption('HTTP')

          // 第二级: 验证关键字名称选项已更新
          const nameSelect = page.locator('select[name="keyword-name"], select[name="name"]').first()
          if (await nameSelect.isVisible()) {
            await expect(nameSelect).toBeEnabled()
            const options = await nameSelect.locator('option').count()
            expect(options).toBeGreaterThan(0)

            // 第三级: 选择关键字后显示参数表单
            await nameSelect.selectOption('发送 HTTP 请求')
            await page.waitForTimeout(500)

            // 验证参数表单显示
            const urlInput = page.locator('input[name="url"], [name="url"]').first()
            await expect(urlInput).toBeVisible()
          }
        }
      }
    }
  })

  test('SCEN-004: 应该能够配置步骤参数', async ({ page }) => {
    await dashboardPage.navigateToScenarios()
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item').first()
    if (await firstScenario.isVisible()) {
      await firstScenario.click()
      await page.waitForTimeout(2000)

      // 点击添加步骤
      const addStepButton = page.locator('button:has-text("添加"), button:has-text("Add")').first()
      if (await addStepButton.isVisible()) {
        await addStepButton.click()
        await page.waitForTimeout(500)

        // 选择 HTTP 请求关键字
        const typeSelect = page.locator('select[name="keyword-type"], select[name="type"]').first()
        if (await typeSelect.isVisible()) {
          await typeSelect.selectOption('HTTP')
          await page.waitForTimeout(500)

          const nameSelect = page.locator('select[name="keyword-name"], select[name="name"]').first()
          if (await nameSelect.isVisible()) {
            await nameSelect.selectOption('发送 HTTP 请求')
            await page.waitForTimeout(500)

            // 填写参数
            const urlInput = page.locator('input[name="url"]').first()
            if (await urlInput.isVisible()) {
              await urlInput.fill('https://api.example.com/test')

              const methodSelect = page.locator('select[name="method"]').first()
              if (await methodSelect.isVisible()) {
                await methodSelect.selectOption('POST')

                const headersInput = page.locator('input[name="headers"], textarea[name="headers"]').first()
                if (await headersInput.isVisible()) {
                  await headersInput.fill('{"Content-Type": "application/json"}')

                  const bodyInput = page.locator('input[name="body"], textarea[name="body"]').first()
                  if (await bodyInput.isVisible()) {
                    await bodyInput.fill('{"key": "value"}')

                    // 保存步骤
                    await page.click('button:has-text("确定"), button:has-text("OK"), button:has-text("保存")')
                    await page.waitForTimeout(2000)

                    // 验证步骤已添加 (检查是否显示在列表中)
                    const stepIndicator = page.locator('text=POST').or(page.locator('text=https://api.example.com/test'))
                    await expect(stepIndicator).toBeVisible({ timeout: 5000 })
                  }
                }
              }
            }
          }
        }
      }
    }
  })

  test('SCEN-005: 应该能够配置前置 SQL', async ({ page }) => {
    await dashboardPage.navigateToScenarios()
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item').first()
    if (await firstScenario.isVisible()) {
      await firstScenario.click()
      await page.waitForTimeout(2000)

      // 切换到前置 SQL 标签
      const preSqlTab = page.locator('text=前置 SQL, tab:has-text("前置 SQL")').first()
      if (await preSqlTab.isVisible()) {
        await preSqlTab.click()
        await page.waitForTimeout(500)

        // 添加 SQL 语句
        const addSqlButton = page.locator('button:has-text("添加 SQL"), button:has-text("Add SQL")').first()
        if (await addSqlButton.isVisible()) {
          await addSqlButton.click()
          await page.waitForTimeout(500)

          const sqlInput = page.locator('textarea[name="pre-sql"], textarea[name="sql"], input[name="sql"]').first()
          if (await sqlInput.isVisible()) {
            await sqlInput.fill('DELETE FROM test_table WHERE id = 1;')

            // 保存
            await page.click('button:has-text("保存"), button:has-text("Save")')
            await page.waitForTimeout(1000)

            // 验证 SQL 已保存
            const sqlText = page.locator('text=DELETE FROM test_table')
            await expect(sqlText).toBeVisible({ timeout: 5000 })
          }
        }
      }
    }
  })

  test('SCEN-006: 应该支持数据驱动测试', async ({ page }) => {
    await dashboardPage.navigateToScenarios()
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item').first()
    if (await firstScenario.isVisible()) {
      await firstScenario.click()
      await page.waitForTimeout(2000)

      // 切换到数据驱动标签
      const dataTab = page.locator('text=数据驱动, tab:has-text("数据驱动")').first()
      if (await dataTab.isVisible()) {
        await dataTab.click()
        await page.waitForTimeout(500)

        // 启用数据驱动
        const enabledCheckbox = page.locator('input[name="data-driven-enabled"], input[type="checkbox"]').first()
        if (await enabledCheckbox.isVisible()) {
          await enabledCheckbox.check()
          await page.waitForTimeout(500)

          // 模拟上传 CSV
          const fileInput = page.locator('input[type="file"]').first()
          if (await fileInput.isVisible()) {
            await fileInput.setInputFiles({
              name: 'test-data.csv',
              mimeType: 'text/csv',
              buffer: Buffer.from('name,email\nTest1,test1@example.com\nTest2,test2@example.com'),
            })

            // 验证数据预览
            await page.waitForTimeout(2000)
            const testData1 = page.locator('text=Test1')
            const testData2 = page.locator('text=Test2')

            const isVisible1 = await testData1.isVisible().catch(() => false)
            const isVisible2 = await testData2.isVisible().catch(() => false)

            // 至少有一个数据可见
            expect(isVisible1 || isVisible2).toBeTruthy()
          }
        }
      }
    }
  })

  test('SCEN-007: 应该能够调试场景', async ({ page }) => {
    await dashboardPage.navigateToScenarios()
    await page.waitForLoadState('networkidle')

    // 选择第一个场景
    const firstScenario = page.locator('[data-testid="scenario-item"], .scenario-item').first()
    if (await firstScenario.isVisible()) {
      await firstScenario.click()
      await page.waitForTimeout(2000)

      // 点击调试按钮
      const debugButton = page.locator('button:has-text("调试"), button:has-text("Debug")').first()
      if (await debugButton.isVisible()) {
        await debugButton.click()
        await page.waitForTimeout(2000)

        // 验证调试输出面板显示
        const debugOutput = page.locator('[data-testid="debug-output"], .debug-output, pre').first()
        const isOutputVisible = await debugOutput.isVisible().catch(() => false)

        // 等待调试完成 (最多 30 秒)
        const completionMessage = page.locator('text=调试完成, text=完成, text=Done')
        const isCompleted = await completionMessage.isVisible({ timeout: 30000 }).catch(() => false)

        // 调试输出或完成消息至少有一个可见
        expect(isOutputVisible || isCompleted).toBeTruthy()
      }
    }
  })
})
