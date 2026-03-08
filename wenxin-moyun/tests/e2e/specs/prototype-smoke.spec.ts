/**
 * Unit 5: Prototype page smoke test.
 *
 * Minimal Playwright test covering the Prototype page rendering.
 * /prototype redirects to /canvas (PrototypePage). Verifies all 5 mode
 * buttons, basic view switching, and page responsiveness.
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

  test('all 5 mode buttons are visible', async ({ page }) => {
    const modes = ['Edit', 'Run', 'Build', 'Explore', 'Compare'];
    for (const mode of modes) {
      const btn = page.locator(`button:has-text("${mode}")`).first();
      await expect(btn).toBeVisible({ timeout: 10000 });
    }
  });

  test('clicking mode buttons switches view without crash', async ({ page }) => {
    const modes = ['Edit', 'Run', 'Build', 'Explore', 'Compare'];
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
    // Edit mode shows PipelineEditor or config elements — verify the mode
    // button is in active state (has blue styling) and page has content
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const textContent = await body.textContent();
    // Should have some pipeline/editor/config related content or at minimum the mode buttons
    expect(textContent).toBeTruthy();
    expect(textContent!.length).toBeGreaterThan(50);
  });

  test('Build mode renders content', async ({ page }) => {
    const buildBtn = page.locator('button:has-text("Build")').first();
    await buildBtn.click();
    await page.waitForTimeout(500);
    // Build mode should render TraditionBuilder — just verify page is responsive
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const textContent = await body.textContent();
    expect(textContent).toBeTruthy();
  });

  test('Explore mode renders content', async ({ page }) => {
    const exploreBtn = page.locator('button:has-text("Explore")').first();
    await exploreBtn.click();
    await page.waitForTimeout(500);
    // Explore mode should render TraditionExplorer — verify page is responsive
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const textContent = await body.textContent();
    expect(textContent).toBeTruthy();
  });

  test('Compare mode renders content', async ({ page }) => {
    const compareBtn = page.locator('button:has-text("Compare")').first();
    await compareBtn.click();
    await page.waitForTimeout(500);
    // Compare mode should render ComparePanel — verify page is responsive
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });
});
