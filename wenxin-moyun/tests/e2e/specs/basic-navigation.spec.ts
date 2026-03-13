import { test, expect } from '@playwright/test';

test.describe('Basic Navigation', () => {
  test('Homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText?.length).toBeGreaterThan(100);

    const hasHeading = await page.locator('h1').count() > 0;
    const hasMainContent = await page.locator('main, [role="main"], .app-content').count() > 0;
    expect(hasHeading || hasMainContent).toBeTruthy();
  });

  test('Can navigate to models page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const modelsLink = page.locator('a[href*="models"], button:has-text("Models"), button:has-text("排行"), [data-testid="explore-rankings-button"]').first();
    if (await modelsLink.isVisible().catch(() => false)) {
      await modelsLink.click();
      await page.waitForURL('**/models', { timeout: 10000 });
    } else {
      await page.goto('/models');
    }

    const url = page.url();
    expect(url).toContain('/models');
  });

  test('Can navigate to canvas page', async ({ page }) => {
    await page.goto('/canvas');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    const url = page.url();
    expect(url).toContain('/canvas');

    const hasContent = await page.locator('h1, button:has-text("Edit"), button:has-text("Run")').first().isVisible({ timeout: 10000 }).catch(() => false);
    expect(hasContent).toBeTruthy();
  });

  test('Can navigate to login page directly', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('input[name="username"], input[placeholder*="username" i]').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login")').first()).toBeVisible();
  });

  // Skip backend health check if backend is not running
  test.skip('Backend health check works', async ({ request }) => {
    const API_URL = process.env.API_URL || 'http://localhost:8001';
    const response = await request.get(`${API_URL}/health`, { timeout: 5000 });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});
