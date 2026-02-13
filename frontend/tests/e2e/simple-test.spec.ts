import { test, expect } from '@playwright/test'

test('simple test', async ({ page }) => {
  await page.goto('/')
  await page.waitForTimeout(1000)
  expect(true).toBe(true)
})
