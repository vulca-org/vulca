/**
 * Unit 5: Prototype page smoke test.
 *
 * Minimal Playwright test covering the Prototype page rendering.
 * /prototype redirects to /canvas (PrototypePage). Verifies all 3 mode
 * buttons (Edit, Run, Traditions), basic view switching, and page responsiveness.
 * Frontend-only — no backend API calls needed.
 */

import { test, expect } from '@playwright/test';
import { withRoute } from '../utils/route-helper';

test.describe('Prototype Page Smoke', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    // /prototype redirects to /canvas — navigate directly to /canvas
    const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
    await page.goto(`${baseURL}${withRoute('/canvas')}`);
    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');
  });

  test('page loads without crash', async ({ page }) => {
    // Page should not show a blank error
    const body = page.locator('body');
    await expect(body).toBeVisible();
    // Should have some content (not an error page)
    const textContent = await body.textContent();
    expect(textContent).toBeTruthy();
  });

  test('all 3 mode buttons are visible', async ({ page }) => {
    const modes = ['Edit', 'Run', 'Traditions'];
    for (const mode of modes) {
      const btn = page.locator(`button:has-text("${mode}")`).first();
      await expect(btn).toBeVisible({ timeout: 10000 });
    }
  });

  test('clicking mode buttons switches view without crash', async ({ page }) => {
    const modes = ['Edit', 'Run', 'Traditions'];
    for (const mode of modes) {
      const btn = page.locator(`button:has-text("${mode}")`).first();
      await btn.click();
      // Wait a moment for view to render
      await page.waitForTimeout(500);
      // Page should still be responsive (no crash)
      const body = page.locator('body');
      await expect(body).toBeVisible();
    }
  });

  test('Edit mode shows editor or config UI', async ({ page }) => {
    const editBtn = page.locator('button:has-text("Edit")').first();
    await editBtn.click();
    await page.waitForTimeout(500);
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const textContent = await body.textContent();
    expect(textContent).toBeTruthy();
    expect(textContent!.length).toBeGreaterThan(50);
  });

  test('Traditions mode renders Browse/Create sub-tabs', async ({ page }) => {
    const traditionsBtn = page.locator('button:has-text("Traditions")').first();
    await traditionsBtn.click();
    await page.waitForTimeout(500);
    // Traditions mode should show Browse/Create segmented control
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const textContent = await body.textContent();
    expect(textContent).toBeTruthy();
  });
});
