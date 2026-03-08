import { test, expect } from '@playwright/test'

test.describe('Mobile viewport (375x812)', () => {
  test.setTimeout(60000)

  test.use({
    viewport: { width: 375, height: 812 },
  })

  test('homepage should render without horizontal overflow', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('main', { timeout: 15000 })

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })

    expect(hasOverflow, 'Page has horizontal overflow at 375px width').toBe(false)
  })

  test('models page should render without horizontal overflow', async ({ page }) => {
    await page.goto('/models')
    // Wait for content to load; use a generous timeout since the page may redirect
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {})
    await page.waitForTimeout(1000) // Allow any client-side rendering

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })

    expect(hasOverflow, 'Models page has horizontal overflow at 375px width').toBe(false)
  })

  test('homepage should show navigation at mobile width', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('nav', { timeout: 15000 })

    // The nav should be visible (header navigation)
    const nav = page.locator('nav')
    await expect(nav.first()).toBeVisible()
  })

  test('main heading should be visible on mobile', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('main', { timeout: 15000 })

    // The h1 heading should be visible
    const heading = page.locator('main h1').first()
    await expect(heading).toBeVisible()
  })
})
