import { Page, Locator } from '@playwright/test'

export class AuthPage {
  readonly page: Page
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator
  readonly githubButton: Locator
  readonly googleButton: Locator
  readonly logoutButton: Locator
  readonly errorMessage: Locator
  readonly successMessage: Locator
  readonly userEmail: Locator

  constructor(page: Page) {
    this.page = page
    this.emailInput = page.locator('input[type="email"], input[name="email"], input#email')
    this.passwordInput = page.locator('input[type="password"], input[name="password"], input#password')
    this.submitButton = page.locator('button[type="submit"], button:has-text("登录"), button:has-text("注册")')
    this.githubButton = page.locator('button:has-text("GitHub"), a:has-text("GitHub")')
    this.googleButton = page.locator('button:has-text("Google"), a:has-text("Google")')
    this.logoutButton = page.locator('button:has-text("退出"), button:has-text("登出")')
    this.errorMessage = page.locator('.error, .alert-error, [role="alert"]')
    this.successMessage = page.locator('.success, .alert-success')
    this.userEmail = page.locator('[data-testid="user-email"], .user-email, .user-info')
  }

  async goto() {
    await this.page.goto('/login')
  }

  async gotoRegister() {
    await this.page.goto('/register')
  }

  async fillCredentials(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
  }

  async clickSubmit() {
    await this.submitButton.click()
  }

  async login(email: string, password: string) {
    await this.goto()
    await this.fillCredentials(email, password)
    await this.clickSubmit()
  }

  async register(email: string, password: string) {
    await this.gotoRegister()
    await this.fillCredentials(email, password)
    await this.clickSubmit()
  }

  async clickGitHubLogin() {
    await this.githubButton.click()
  }

  async clickGoogleLogin() {
    await this.googleButton.click()
  }

  async logout() {
    if (await this.logoutButton.isVisible()) {
      await this.logoutButton.click()
    }
  }

  async getToken(): Promise<string | null> {
    return await this.page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token')
    })
  }

  async clearToken() {
    await this.page.evaluate(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
    })
  }

  async waitForDashboard() {
    await this.page.waitForURL('**/', { timeout: 5000 })
  }

  async waitForErrorMessage() {
    await this.errorMessage.waitFor({ state: 'visible' })
  }

  getErrorMessageText(): Promise<string> {
    return this.errorMessage.textContent() as Promise<string>
  }

  getUserEmail(): Promise<string> {
    return this.userEmail.textContent() as Promise<string>
  }

  async isOnLoginPage(): Promise<boolean> {
    return await this.page.url().includes('/login')
  }

  async isOnDashboard(): Promise<boolean> {
    return await this.page.url() === 'http://localhost:3000/' || await this.page.url() === 'http://localhost:3000'
  }
}
