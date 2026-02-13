import { test, expect } from '@playwright/test'

test.describe('Header 下拉菜单测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问登录页面
    await page.goto('http://localhost:3000/login')

    // 使用测试账号登录
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'test123456')
    await page.click('button[type="submit"]')

    // 等待登录成功并跳转到首页
    await page.waitForURL('http://localhost:3000/')
    await page.waitForLoadState('networkidle')
  })

  test('应该显示用户头像按钮', async ({ page }) => {
    // 验证用户头像按钮存在
    const avatarButton = page.locator('button[aria-label="User menu"]')
    await expect(avatarButton).toBeVisible()
  })

  test('点击头像后应该显示下拉菜单', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 验证下拉菜单中的关键菜单项
    await expect(page.locator('text=场景编排')).toBeVisible()
    await expect(page.locator('text=测试计划')).toBeVisible()
    await expect(page.locator('text=全局函数')).toBeVisible()
    await expect(page.locator('text=个人设置')).toBeVisible()
    await expect(page.locator('text=退出登录')).toBeVisible()
  })

  test('点击场景编排菜单项应该导航到场景编排页面', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 点击场景编排菜单项
    await page.click('text=场景编排')

    // 验证导航到场景编排页面
    await page.waitForURL('http://localhost:3000/scenarios')
    expect(page.url()).toContain('/scenarios')
  })

  test('点击测试计划菜单项应该导航到测试计划页面', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 点击测试计划菜单项
    await page.click('text=测试计划')

    // 验证导航到测试计划页面
    await page.waitForURL('http://localhost:3000/test-plans')
    expect(page.url()).toContain('/test-plans')
  })

  test('点击全局函数菜单项应该导航到全局函数页面', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 点击全局函数菜单项
    await page.click('text=全局函数')

    // 验证导航到全局函数页面
    await page.waitForURL('http://localhost:3000/global-functions')
    expect(page.url()).toContain('/global-functions')
  })

  test('点击个人设置菜单项应该导航到设置页面', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 点击个人设置菜单项
    await page.click('text=个人设置')

    // 验证导航到设置页面
    await page.waitForURL('http://localhost:3000/settings')
    expect(page.url()).toContain('/settings')
  })

  test('点击退出登录菜单项应该退出登录', async ({ page }) => {
    // 点击用户头像按钮
    const avatarButton = page.locator('button:has(.avatar)')
    await avatarButton.click()

    // 等待下拉菜单出现
    await page.waitForTimeout(300)

    // 点击退出登录菜单项
    await page.click('text=退出登录')

    // 验证退出登录并跳转到登录页面
    await page.waitForURL('http://localhost:3000/login')
    expect(page.url()).toContain('/login')
  })
})
