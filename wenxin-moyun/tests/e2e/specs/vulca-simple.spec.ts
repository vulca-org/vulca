import { test, expect } from '@playwright/test';

test.describe('VULCA Simple Tests', () => {
  test('should navigate to VULCA page (redirects to canvas)', async ({ page }) => {
    // /vulca redirects to /canvas — navigate and verify
    await page.goto('/vulca');

    // Wait for redirect and page load
    await page.waitForTimeout(3000);

    // /vulca → /canvas redirect; accept either
    expect(page.url()).toMatch(/\/(vulca|canvas)/);

    // Check that page has some content (not blank)
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should show loading or content', async ({ page }) => {
    await page.goto('/canvas');
    await page.waitForTimeout(3000);

    // Check if either VULCA/Canvas content or mode buttons are visible
    const hasVULCATitle = await page.locator('text=/VULCA|Canvas|Playground/i').count() > 0;
    const hasModeButtons = await page.locator('button:has-text("Edit")').count() > 0;
    const hasContent = await page.locator('text=/Edit|Run|Build|Explore|Compare/').count() > 0;

    // At least one should be true
    expect(hasVULCATitle || hasModeButtons || hasContent).toBeTruthy();
  });

  test('should eventually show main content', async ({ page }) => {
    await page.goto('/canvas');

    // Wait up to 30 seconds for main content — look for mode buttons or playground text
    const mainContent = await page.waitForSelector(
      'text=/VULCA|Playground|Edit|Run|Build|Explore|Compare|Pipeline|Canvas/i',
      { timeout: 30000, state: 'visible' }
    ).catch(() => null);

    // Should have found something
    expect(mainContent).toBeTruthy();
  });
});

test.describe('VULCA API Tests', () => {
  // Skip API tests - they require running backend on localhost:8001
  test.skip(true, 'VULCA API tests require running backend');

  test('should have working VULCA API', async ({ request }) => {
    // Test the VULCA info endpoint
    const response = await request.get('http://localhost:8001/api/v1/vulca/info');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.name).toContain('VULCA');
    expect(data.dimensions).toBeDefined();
  });

  test('should get cultural perspectives', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/vulca/cultural-perspectives');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.length).toBeGreaterThan(0);
  });

  test('should get dimensions', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/vulca/dimensions');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.length).toBe(47); // Should have 47 dimensions
  });
});
