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
}
