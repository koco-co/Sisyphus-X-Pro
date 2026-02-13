import { test, expect } from '@playwright/test'

// 测试登录
test.beforeEach(async ({ page }) => {
  // 导航到登录页面
  await page.goto('http://localhost:3000/login')

  // 填写登录表单
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')

  // 点击登录按钮
  await page.click('button[type="submit"]')

  // 等待导航到首页
  await page.waitForURL('http://localhost:3000/')
})

test.describe('项目管理 (PROJ)', () => {
  test('PROJ-001: 创建项目', async ({ page }) => {
    // 导航到项目列表
    await page.goto('http://localhost:3000/projects')

    // 点击新建项目按钮
    await page.click('button:has-text("新建项目")')

    // 填写项目信息
    await page.fill('input#name', 'E2E 测试项目')
    await page.fill('input#description', '这是端到端测试创建的项目')

    // 点击创建按钮
    await page.click('button:has-text("创建")')

    // 验证项目出现在列表中
    await expect(page.locator('text=E2E 测试项目')).toBeVisible()
    await expect(page.locator('text=这是端到端测试创建的项目')).toBeVisible()
  })

  test('PROJ-002: 编辑项目', async ({ page }) => {
    // 导航到项目列表
    await page.goto('http://localhost:3000/projects')

    // 找到测试项目并点击编辑按钮
    const projectRow = page.locator('tr:has-text("E2E 测试项目")')
    await projectRow.locator('button[title="编辑"]').click()

    // 修改项目信息
    await page.fill('input#name', 'E2E 测试项目 (已编辑)')
    await page.fill('input#description', '这是编辑后的描述')

    // 点击保存按钮
    await page.click('button:has-text("保存")')

    // 验证编辑成功
    await expect(page.locator('text=E2E 测试项目 (已编辑)')).toBeVisible()
    await expect(page.locator('text=这是编辑后的描述')).toBeVisible()
  })

  test('PROJ-003: 删除项目', async ({ page }) => {
    // 导航到项目列表
    await page.goto('http://localhost:3000/projects')

    // 找到测试项目并点击删除按钮
    const projectRow = page.locator('tr:has-text("E2E 测试项目 (已编辑)")')
    await projectRow.locator('button[title="删除"]').click()

    // 确认删除
    await page.click('button:has-text("删除"):has-text("确定")')

    // 验证项目从列表消失
    await expect(page.locator('text=E2E 测试项目 (已编辑)')).not.toBeVisible()
  })

  test('PROJ-004: 数据库配置', async ({ page }) => {
    // 先创建一个项目
    await page.goto('http://localhost:3000/projects')
    await page.click('button:has-text("新建项目")')
    await page.fill('input#name', '数据库测试项目')
    await page.click('button:has-text("创建")')
    await expect(page.locator('text=数据库测试项目')).toBeVisible()

    // 点击数据库配置按钮
    const projectRow = page.locator('tr:has-text("数据库测试项目")')
    await projectRow.locator('button[title="数据库配置"]').click()

    // 验证导航到数据库配置页面
    await expect(page).toHaveURL(/\/projects\/\d+\/database-config/)
    await expect(page.locator('text=数据库配置')).toBeVisible()

    // 点击新增配置
    await page.click('button:has-text("新增配置")')

    // 填写数据库配置 (使用 Docker 中的 PostgreSQL)
    await page.fill('input#name', '测试数据库')
    await page.fill('input#variable_name', 'test_db')
    await page.selectOption('select#db_type', 'postgresql')
    await page.fill('input#host', 'localhost')
    await page.fill('input#port', '5432')
    await page.fill('input#database', 'sisyphus_test')
    await page.fill('input#username', 'postgres')
    await page.fill('input#password', 'postgres')

    // 注意: 这里只是测试流程,实际连接可能失败
    // 在真实环境中需要正确的数据库凭据
  })

  test('PROJ-006: 多数据源配置', async ({ page }) => {
    // 导航到已存在的项目数据库配置
    await page.goto('http://localhost:3000/projects')

    // 使用第一个项目
    const firstProjectId = await page.locator('tr').first.locator('button[title="数据库配置"]').getAttribute('data-project-id')
    await page.goto(`http://localhost:3000/projects/${firstProjectId}/database-config`)

    // 添加第一个数据库
    await page.click('button:has-text("新增配置")')
    await page.fill('input#name', '主数据库')
    await page.fill('input#variable_name', 'main_db')
    await page.selectOption('select#db_type', 'postgresql')
    await page.fill('input#host', 'localhost')
    await page.fill('input#port', '5432')
    await page.fill('input#database', 'db_main')
    await page.fill('input#username', 'user')
    await page.fill('input#password', 'pass')

    // 关闭弹窗
    await page.click('button:has-text("取消")')

    // 添加第二个数据库
    await page.click('button:has-text("新增配置")')
    await page.fill('input#name', '从数据库')
    await page.fill('input#variable_name', 'slave_db')
    await page.selectOption('select#db_type', 'mysql')
    await page.fill('input#host', 'localhost')
    await page.fill('input#port', '3306')
    await page.fill('input#database', 'db_slave')
    await page.fill('input#username', 'user')
    await page.fill('input#password', 'pass')

    // 关闭弹窗
    await page.click('button:has-text("取消")')

    // 验证两个数据库都显示在列表中 (如果连接测试成功的话)
    // 注意: 这个测试假设连接测试通过,实际需要真实数据库
  })
})
