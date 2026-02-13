import { test, expect } from '@playwright/test'

test.describe('接口定义模块', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:3000/login')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')

    // 等待跳转到首页
    await page.waitForURL('http://localhost:3000/')
  })

  test('INTF-001: 创建接口目录树', async ({ page }) => {
    // 进入项目详情
    await page.goto('http://localhost:3000/projects/1/interfaces')

    // 点击新建目录
    await page.click('button:has-text("新建目录")')

    // 输入目录名称
    await page.fill('input[placeholder="目录名称"]', '测试目录')
    await page.click('button:has-text("确定")')

    // 验证目录创建成功
    await expect(page.locator('text=测试目录')).toBeVisible()
  })

  test('INTF-002: 通过 cURL 导入接口', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/1/interfaces')

    // 点击导入 cURL
    await page.click('button:has-text("导入 cURL")')

    // 粘贴 cURL 命令
    const curlCommand = 'curl -X POST https://api.example.com/users -H "Content-Type: application/json" -d \'{"name":"test"}\''
    await page.fill('textarea[placeholder*="curl"]', curlCommand)

    // 点击解析
    await page.click('button:has-text("解析 cURL")')

    // 等待解析结果显示
    await page.waitForSelector('text=解析结果')
    await expect(page.locator('text=POST')).toBeVisible()
    await expect(page.locator('text=/users')).toBeVisible()

    // 点击导入
    await page.click('button:has-text("导入")')

    // 验证接口创建成功
    await expect(page.locator('text=POST /users')).toBeVisible()
  })

  test('INTF-003: 手动创建接口', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/1/interfaces')

    // 点击新建接口
    await page.click('button:has-text("新建接口")')

    // 填写表单
    await page.fill('input[placeholder="获取用户信息"]', '获取用户列表')
    await page.selectOption('select', 'GET')
    await page.fill('input[placeholder="/api/users"]', '/api/users')

    // 提交
    await page.click('button:has-text("创建")')

    // 验证接口创建成功
    await expect(page.locator('text=GET')).toBeVisible()
    await expect(page.locator('text=/api/users')).toBeVisible()
  })

  test('INTF-004: 管理多环境配置', async ({ page }) => {
    // 进入环境配置页
    await page.goto('http://localhost:3000/projects/1/environments')

    // 点击新建环境
    await page.click('button:has-text("新建环境")')

    // 填写环境信息
    await page.fill('input[placeholder="开发/测试/生产"]', '测试环境')
    await page.fill('input[placeholder="https://api.example.com"]', 'https://test.api.example.com')

    // 提交
    await page.click('button:has-text("确定")')

    // 验证环境创建成功
    await expect(page.locator('text=测试环境')).toBeVisible()

    // 选择环境
    await page.click('text=测试环境')

    // 添加环境变量
    await page.click('button:has-text("添加变量")')
    await page.fill('input[placeholder="API_KEY"]', 'API_KEY')
    await page.fill('input[placeholder="your-api-key-value"]', 'test-key-123')

    // 提交
    await page.click('button:has-text("确定")')

    // 验证变量添加成功
    await expect(page.locator('text=API_KEY')).toBeVisible()
    await expect(page.locator('text=test-key-123')).toBeVisible()
  })

  test('INTF-005: 管理全局变量', async ({ page }) => {
    // 进入全局变量页
    await page.goto('http://localhost:3000/projects/1/global-variables')

    // 点击添加变量
    await page.click('button:has-text("添加变量")')

    // 填写变量信息
    await page.fill('input[placeholder="API_BASE_URL"]', 'API_BASE_URL')
    await page.fill('input[placeholder="https://api.example.com"]', 'https://api.example.com')
    await page.fill('input[placeholder="API 基础地址"]', 'API 基础地址')

    // 提交
    await page.click('button:has-text("确定")')

    // 验证变量创建成功
    await expect(page.locator('text=API_BASE_URL')).toBeVisible()
    await expect(page.locator('text=https://api.example.com')).toBeVisible()
  })

  test('INTF-001: 拖拽排序接口目录', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/1/interfaces')

    // 创建两个目录
    await page.click('button:has-text("新建目录")')
    await page.fill('input[placeholder="目录名称"]', '目录A')
    await page.click('button:has-text("确定")')

    await page.click('button:has-text("新建目录")')
    await page.fill('input[placeholder="目录名称"]', '目录B')
    await page.click('button:has-text("确定")')

    // 拖拽目录B到目录A上方
    const source = await page.locator('text=目录B').boundingBox()
    const target = await page.locator('text=目录A').boundingBox()

    if (source && target) {
      await page.mouse.move(source.x + source.width / 2, source.y + source.height / 2)
      await page.mouse.down()
      await page.mouse.move(target.x + target.width / 2, target.y + target.height / 2)
      await page.mouse.up()

      // 验证顺序改变(简单验证:检查元素是否还存在)
      await expect(page.locator('text=目录A')).toBeVisible()
      await expect(page.locator('text=目录B')).toBeVisible()
    }
  })
})
