import { test, expect } from '@playwright/test';

test.describe('Canvas Simple Tests', () => {
  test('should navigate to canvas page', async ({ page }) => {
    await page.goto('/canvas');
    await page.waitForTimeout(3000);

    expect(page.url()).toMatch(/\/canvas/);

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should show loading or content', async ({ page }) => {
    await page.goto('/canvas');
    await page.waitForTimeout(3000);

    const hasCanvasTitle = await page.locator('text=/VULCA|Canvas|Playground/i').count() > 0;
    const hasModeButtons = await page.locator('button:has-text("Edit")').count() > 0;
    const hasContent = await page.locator('text=/Edit|Run|Traditions/').count() > 0;

    expect(hasCanvasTitle || hasModeButtons || hasContent).toBeTruthy();
  });

  test('should eventually show main content', async ({ page }) => {
    await page.goto('/canvas');

    const mainContent = await page.waitForSelector(
      'text=/VULCA|Playground|Edit|Run|Traditions|Pipeline|Canvas/i',
      { timeout: 30000, state: 'visible' }
    ).catch(() => null);

    expect(mainContent).toBeTruthy();
  });

  test('legacy /vulca route redirects to /canvas', async ({ page }) => {
    await page.goto('/vulca');
    await page.waitForTimeout(2000);

    expect(page.url()).toContain('/canvas');
  });
});

test.describe('Canvas API Tests', () => {
  // Skip API tests - they require running backend on localhost:8001
  test.skip(true, 'Canvas API tests require running backend');

  test('should have working prototype API', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/prototype/gallery');
    expect(response.ok()).toBeTruthy();
  });

  test('should get traditions list', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/prototype/traditions');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.length).toBeGreaterThan(0);
  });
});
