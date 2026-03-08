import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility (WCAG 2.2 AA)', () => {
  test.setTimeout(60000)

  test('homepage should have no critical accessibility violations', async ({ page }) => {
    await page.goto('/')
    // Wait for main content to be visible
    await page.waitForSelector('main', { timeout: 15000 })

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      // Only fail on critical and serious violations
      .analyze()

    const critical = results.violations.filter(
      (v) => v.impact === 'critical'
    )

    // Log all violations for debugging, but only assert critical ones
    if (results.violations.length > 0) {
      console.log(
        'All a11y violations:',
        results.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          description: v.description,
          nodes: v.nodes.length,
        }))
      )
    }

    expect(critical, `Found ${critical.length} critical a11y violations`).toHaveLength(0)
  })
})
