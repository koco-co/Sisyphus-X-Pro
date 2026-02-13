import { Page, Locator } from '@playwright/test'

export class DashboardPage {
  readonly page: Page
  readonly welcomeMessage: Locator
  readonly userInfo: Locator

  constructor(page: Page) {
    this.page = page
    this.welcomeMessage = page.locator('h1:has-text("欢迎使用"), h1:has-text("欢迎"), .welcome')
    this.userInfo = page.locator('[data-testid="user-info"], .user-info, header')
  }

  async goto() {
    await this.page.goto('/')
  }

  async isLoaded(): Promise<boolean> {
    return await this.welcomeMessage.isVisible()
  }

  async getWelcomeText(): Promise<string> {
    return await this.welcomeMessage.textContent() as Promise<string>
  }

  async navigateToScenarios() {
    // 点击用户头像打开下拉菜单 - 使用 Button 的 variant 属性
    await this.page.click('button[class*="rounded-full"], button:has-text("S")')
    // 点击场景编排菜单项
    await this.page.click('text=场景编排')
    // 等待导航完成
    await this.page.waitForURL('**/scenarios', { timeout: 5000 })
  }

  async navigateToProjects() {
    // 点击用户头像打开下拉菜单
    await this.page.click('button[class*="rounded-full"], button:has-text("S")')
    // 如果项目管理在菜单中,点击它;否则直接导航
    const projectMenu = this.page.locator('text=项目管理').first()
    const isVisible = await projectMenu.isVisible().catch(() => false)
    if (isVisible) {
      await projectMenu.click()
    } else {
      await this.page.goto('/projects')
    }
    await this.page.waitForURL('**/projects', { timeout: 5000 })
  }

  async navigateToTestPlans() {
    // 点击用户头像打开下拉菜单
    await this.page.click('button[class*="rounded-full"], button:has-text("S")')
    // 点击测试计划菜单项
    await this.page.click('text=测试计划')
    await this.page.waitForURL('**/test-plans', { timeout: 5000 })
  }

  async navigateToGlobalFunctions() {
    // 点击用户头像打开下拉菜单
    await this.page.click('button[class*="rounded-full"], button:has-text("S")')
    // 点击全局函数菜单项
    await this.page.click('text=全局函数')
    await this.page.waitForURL('**/global-functions', { timeout: 5000 })
  }
}
