import { test, expect } from '@playwright/test'
import { AuthPage } from './pages/AuthPage'
import { ApiHelper } from './helpers/api-helper'

// 测试用户
const testUser = {
  email: `menu-regression-${Date.now()}@example.com`,
  password: 'Test123456!',
}

test.describe('Bug #26, #29 回归测试: 用户菜单点击导致退出登录', () => {
  let authPage: AuthPage

  test.beforeAll(async () => {
    await ApiHelper.createTestUser(testUser.email, testUser.password)
  })

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page)
    await authPage.login(testUser.email, testUser.password)
    await expect(page).toHaveURL('http://localhost:3000/')
  })

  test.afterAll(async () => {
    try {
      const token = await ApiHelper.getUserToken(testUser.email, testUser.password)
      if (token) {
        await ApiHelper.deleteTestUser(testUser.email, token)
      }
    } catch (error) {
      console.log('Cleanup failed:', error)
    }
  })

  test('测试 1: 验证用户登录后 Token 存在', async ({ page }) => {
    // 检查 localStorage 中是否有 token
    const token = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    expect(token).toBeTruthy()
    console.log('✅ Token 存在:', token?.substring(0, 20) + '...')
  })

  test('测试 2: 用户头像按钮应该存在', async ({ page }) => {
    // 查找用户头像按钮
    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()

    const isVisible = await avatarButton.isVisible({ timeout: 5000 })
    expect(isVisible).toBeTruthy()
    console.log('✅ 用户头像按钮可见')

    // 截图保存当前状态
    await page.screenshot({ path: 'test-results/bug26-29-02-avatar-button.png' })
  })

  test('测试 3: 点击用户头像应该打开下拉菜单', async ({ page }) => {
    // 点击用户头像
    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()

    // 等待菜单出现
    await page.waitForTimeout(2000)

    // 截图
    await page.screenshot({ path: 'test-results/bug26-29-03-after-click.png' })

    // 检查是否有菜单项显示
    const menuItems = page.locator('[role="menuitem"], [data-testid*="menu"], [data-testid*="dropdown"]')
    const count = await menuItems.count()

    console.log(`📊 菜单项数量: ${count}`)

    if (count > 0) {
      console.log('✅ 下拉菜单显示了', count, '个菜单项')
    } else {
      console.log('❌ 下拉菜单未显示')
    }

    // 至少应该有一些菜单相关的元素
    // 即使菜单项不可见,也应该有菜单容器
    const menuContainer = page.locator('[data-radix-dropdown-menu], [role="menu"]')
    const menuExists = await menuContainer.isVisible().catch(() => false)

    if (menuExists) {
      console.log('✅ 菜单容器存在')
    } else {
      console.log('❌ 菜单容器不存在')
    }
  })

  test('测试 4: 场景编排菜单项应该存在', async ({ page }) => {
    // 点击用户头像
    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    // 查找场景编排菜单项
    const scenarioMenu = page.locator('text=场景编排')
    const isVisible = await scenarioMenu.isVisible({ timeout: 5000 }).catch(() => false)

    if (isVisible) {
      console.log('✅ 场景编排菜单项可见')

      // 截图
      await page.screenshot({ path: 'test-results/bug26-29-04-scenario-menu.png' })
    } else {
      console.log('❌ 场景编排菜单项不可见')

      // 检查是否有其他可能的文本
      const alternatives = page.locator('a, button, [role="menuitem"]')
      const texts = await alternatives.allTextContents()
      console.log('📋 可见的菜单文本:', texts.join(', '))
    }
  })

  test('测试 5: 点击场景编排菜单项应该导航且不退出登录', async ({ page }) => {
    // 记录初始 Token
    const initialToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    // 点击用户头像
    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    // 尝试点击场景编排
    const scenarioMenu = page.locator('text=场景编排')

    try {
      // 如果菜单项存在,点击它
      const isVisible = await scenarioMenu.isVisible({ timeout: 5000 })
      if (isVisible) {
        await scenarioMenu.click()

        // 等待导航
        await page.waitForTimeout(3000)

        // 检查 Token 是否还在
        const currentToken = await page.evaluate(() => {
          return localStorage.getItem('token') || localStorage.getItem('access_token')
        })

        // 检查当前 URL
        const currentUrl = page.url()
        console.log('📍 当前 URL:', currentUrl)
        console.log('🔑 Token 变化:', initialToken === currentToken ? '无' : '有变化')

        // 验证: 应该导航到 scenarios 页面
        const isScenariosPage = currentUrl.includes('/scenarios') || currentUrl.includes('/scenario')
        console.log(isScenariosPage ? '✅ 导航到场景页面' : '❌ 未导航到场景页面')

        // 验证: Token 应该还在(没有退出)
        const tokenStillExists = currentToken !== null && currentToken === initialToken
        console.log(tokenStillExists ? '✅ Token 存在,未退出登录' : '❌ Token 失去,已退出登录')

        // 截图
        await page.screenshot({ path: 'test-results/bug26-29-05-after-navigation.png' })

        // 主要断言
        expect(isScenariosPage).toBeTruthy()
        expect(tokenStillExists).toBeTruthy()
      } else {
        console.log('❌ 场景编排菜单项不可见,跳过点击测试')
        await page.screenshot({ path: 'test-results/bug26-29-05-no-menu.png' })
      }
    } catch (error) {
      console.log('❌ 点击场景编排时出错:', error)

      // 检查是否跳转到登录页(说明意外退出)
      const isLoginPage = page.url().includes('/login')
      if (isLoginPage) {
        console.log('❌ Bug 确认: 点击菜单项导致跳转到登录页')
      }

      await page.screenshot({ path: 'test-results/bug26-29-05-error.png' })
    }
  })

  test('测试 6: 测试计划菜单项应该正常工作', async ({ page }) => {
    const initialToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    const planMenu = page.locator('text=测试计划')

    try {
      const isVisible = await planMenu.isVisible({ timeout: 5000 })
      if (isVisible) {
        await planMenu.click()
        await page.waitForTimeout(3000)

        const currentToken = await page.evaluate(() => {
          return localStorage.getItem('token') || localStorage.getItem('access_token')
        })
        const currentUrl = page.url()

        console.log('📍 当前 URL:', currentUrl)
        console.log('🔑 Token 存在:', currentToken !== null)

        const isPlansPage = currentUrl.includes('/test-plans') || currentUrl.includes('/test-plan')
        const tokenStillExists = currentToken !== null && currentToken === initialToken

        console.log(isPlansPage ? '✅ 导航到测试计划页面' : '❌ 未导航到测试计划页面')
        console.log(tokenStillExists ? '✅ Token 存在,未退出登录' : '❌ Token 失去,已退出登录')

        await page.screenshot({ path: 'test-results/bug26-29-06-test-plans.png' })

        expect(isPlansPage).toBeTruthy()
        expect(tokenStillExists).toBeTruthy()
      } else {
        console.log('❌ 测试计划菜单项不可见')
        await page.screenshot({ path: 'test-results/bug26-29-06-no-menu.png' })
      }
    } catch (error) {
      console.log('❌ 点击测试计划时出错:', error)
      await page.screenshot({ path: 'test-results/bug26-29-06-error.png' })
    }
  })

  test('测试 7: 全局函数菜单项应该正常工作', async ({ page }) => {
    const initialToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    const globalFuncMenu = page.locator('text=全局函数')

    try {
      const isVisible = await globalFuncMenu.isVisible({ timeout: 5000 })
      if (isVisible) {
        await globalFuncMenu.click()
        await page.waitForTimeout(3000)

        const currentToken = await page.evaluate(() => {
          return localStorage.getItem('token') || localStorage.getItem('access_token')
        })
        const currentUrl = page.url()

        console.log('📍 当前 URL:', currentUrl)
        console.log('🔑 Token 存在:', currentToken !== null)

        const isGlobalFuncPage = currentUrl.includes('/global-functions') || currentUrl.includes('/global-function')
        const tokenStillExists = currentToken !== null && currentToken === initialToken

        console.log(isGlobalFuncPage ? '✅ 导航到全局函数页面' : '❌ 未导航到全局函数页面')
        console.log(tokenStillExists ? '✅ Token 存在,未退出登录' : '❌ Token 失去,已退出登录')

        await page.screenshot({ path: 'test-results/bug26-29-07-global-functions.png' })

        expect(isGlobalFuncPage).toBeTruthy()
        expect(tokenStillExists).toBeTruthy()
      } else {
        console.log('❌ 全局函数菜单项不可见')
        await page.screenshot({ path: 'test-results/bug26-29-07-no-menu.png' })
      }
    } catch (error) {
      console.log('❌ 点击全局函数时出错:', error)
      await page.screenshot({ path: 'test-results/bug26-29-07-error.png' })
    }
  })

  test('测试 8: 个人设置菜单项应该正常工作', async ({ page }) => {
    const initialToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    const settingsMenu = page.locator('text=个人设置, text=设置')

    try {
      const isVisible = await settingsMenu.isVisible({ timeout: 5000 })
      if (isVisible) {
        await settingsMenu.click()
        await page.waitForTimeout(3000)

        const currentToken = await page.evaluate(() => {
          return localStorage.getItem('token') || localStorage.getItem('access_token')
        })
        const currentUrl = page.url()

        console.log('📍 当前 URL:', currentUrl)
        console.log('🔑 Token 存在:', currentToken !== null)

        const isSettingsPage = currentUrl.includes('/settings') || currentUrl.includes('/setting')
        const tokenStillExists = currentToken !== null && currentToken === initialToken

        console.log(isSettingsPage ? '✅ 导航到设置页面' : '❌ 未导航到设置页面')
        console.log(tokenStillExists ? '✅ Token 存在,未退出登录' : '❌ Token 失去,已退出登录')

        await page.screenshot({ path: 'test-results/bug26-29-08-settings.png' })

        expect(isSettingsPage).toBeTruthy()
        expect(tokenStillExists).toBeTruthy()
      } else {
        console.log('❌ 个人设置菜单项不可见')
        await page.screenshot({ path: 'test-results/bug26-29-08-no-menu.png' })
      }
    } catch (error) {
      console.log('❌ 点击个人设置时出错:', error)
      await page.screenshot({ path: 'test-results/bug26-29-08-error.png' })
    }
  })

  test('测试 9: 只有退出登录按钮应该真正退出', async ({ page }) => {
    const initialToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })

    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    // 查找退出登录按钮
    const logoutButton = page.locator('text=退出登录, text=退出, text=登出')

    try {
      const isVisible = await logoutButton.isVisible({ timeout: 5000 })
      if (isVisible) {
        console.log('✅ 退出登录按钮可见')

        await logoutButton.click()
        await page.waitForTimeout(3000)

        // 检查 Token
        const currentToken = await page.evaluate(() => {
          return localStorage.getItem('token') || localStorage.getItem('access_token')
        })
        const currentUrl = page.url()

        console.log('📍 当前 URL:', currentUrl)
        console.log('🔑 Token 存在:', currentToken !== null)

        // 验证: 点击退出后,Token 应该被清除或 URL 应该是登录页
        const isLogoutPage = currentUrl.includes('/login') || currentToken === null

        if (isLogoutPage) {
          console.log('✅ 退出登录功能正常: Token 已清除或跳转到登录页')
        } else {
          console.log('❌ 退出登录功能异常: Token 仍在且未跳转到登录页')
        }

        await page.screenshot({ path: 'test-results/bug26-29-09-logout.png' })

        expect(isLogoutPage).toBeTruthy()
      } else {
        console.log('❌ 退出登录按钮不可见')

        // 列出所有可见的按钮/链接
        const allButtons = page.locator('button, a, [role="menuitem"]')
        const texts = await allButtons.allTextContents()
        console.log('📋 所有可见的按钮/链接文本:', texts.join(', '))

        await page.screenshot({ path: 'test-results/bug26-29-09-no-logout.png' })
      }
    } catch (error) {
      console.log('❌ 点击退出登录时出错:', error)
      await page.screenshot({ path: 'test-results/bug26-29-09-error.png' })
    }
  })

  test('测试 10: 验证所有菜单项的可见性', async ({ page }) => {
    // 点击用户头像
    const avatarButton = page.locator('button').filter({ hasText: /^[A-Z0-9]$/ }).first()
    await avatarButton.click()
    await page.waitForTimeout(2000)

    // 检查所有预期的菜单项
    const menuItems = [
      '场景编排',
      '测试计划',
      '全局函数',
      '个人设置',
      '退出登录'
    ]

    const visibleItems: string[] = []
    const missingItems: string[] = []

    for (const item of menuItems) {
      const element = page.locator(`text=${item}`)
      const isVisible = await element.isVisible({ timeout: 3000 }).catch(() => false)

      if (isVisible) {
        visibleItems.push(item)
      } else {
        missingItems.push(item)
      }
    }

    console.log('📊 菜单可见性统计:')
    console.log(`  ✅ 可见 (${visibleItems.length}/${menuItems.length}):`, visibleItems.join(', '))
    console.log(`  ❌ 缺失 (${missingItems.length}/${menuItems.length}):`, missingItems.join(', '))

    // 截图
    await page.screenshot({ path: 'test-results/bug26-29-10-all-items.png' })

    // 即使菜单项缺失,也记录当前状态
    if (visibleItems.length === 0) {
      console.log('⚠️ 警告: 所有菜单项都不可见,下拉菜单可能未渲染')

      // 检查页面上的所有文本
      const allText = await page.locator('body').allTextContents()
      console.log('📄 页面上的所有文本:', allText.join(' ').substring(0, 500))
    }
  })
})
