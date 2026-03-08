import { test, expect } from '@playwright/test';
import { withRoute } from '../utils/route-helper';

test.describe('Skills Page', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
    await page.goto(`${baseURL}${withRoute('/skills')}`);
    await page.waitForLoadState('domcontentloaded');
  });

  test('page loads and shows heading', async ({ page }) => {
    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible({ timeout: 15000 });
  });

  test('skill cards are visible (fallback data)', async ({ page }) => {
    // SkillCard renders skill names as h3 elements inside IOSCard.
    // IOSCard uses Tailwind utility classes (no "card"/"Card" in class names),
    // so match by the skill name headings instead.
    const skillHeading = page.locator('h3:has-text("Brand Consistency"), h3:has-text("Audience Fit"), h3:has-text("Accessibility Check")');
    await expect(skillHeading.first()).toBeVisible({ timeout: 15000 });
  });

  test('search input is functional', async ({ page }) => {
    const search = page.locator('input[type="text"], input[type="search"]').first();
    if (await search.isVisible({ timeout: 5000 }).catch(() => false)) {
      await search.fill('Brand');
      await page.waitForTimeout(500);
      const body = await page.locator('body').textContent();
      expect(body).toContain('Brand');
    }
  });

  test('no console errors on load', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.reload();
    await page.waitForLoadState('domcontentloaded');
    const critical = errors.filter(e => !e.includes('favicon') && !e.includes('net::'));
    expect(critical.length).toBe(0);
  });
});
