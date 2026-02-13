import { test as base } from '@playwright/test'

export const test = base.extend<{
  authenticatedPage: any
}>({
  authenticatedPage: async ({ page }, use) => {
    // 可以在这里设置认证状态
    // 例如: 自动登录、设置 token 等
    await use(page)
  },
})

export { expect } from '@playwright/test'
