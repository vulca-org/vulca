import { test, expect } from '@playwright/test';
import { HomePage, LeaderboardPage } from '../e2e/fixtures/page-objects';
import { setGuestSession, cleanupTestData } from '../e2e/helpers/test-utils';

test.describe('Visual Regression Tests', () => {
  // Skip all visual tests until baseline screenshots are generated
  // To generate baselines, run: npx playwright test tests/visual --update-snapshots
  test.skip(true, 'Baseline screenshots not yet generated - run with --update-snapshots to create them');

  test.beforeEach(async ({ page }) => {
    // Set up consistent state for visual tests
    await setGuestSession(page, 'visual-test-guest');
  });

  test.afterEach(async ({ page }) => {
    await cleanupTestData(page);
  });

  test('Homepage visual consistency', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.navigate('/');

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot('homepage-full.png', {
      fullPage: true,
      maxDiffPixels: 100,
      animations: 'disabled'
    });

    await expect(page).toHaveScreenshot('homepage-viewport.png', {
      fullPage: false,
      maxDiffPixels: 50
    });
  });

  test('Models page visual consistency', async ({ page }) => {
    const leaderboardPage = new LeaderboardPage(page);
    await page.goto('/models');

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('main')).toHaveScreenshot('models-main.png', {
      maxDiffPixels: 100
    });
  });

  test('Canvas page visual consistency', async ({ page }) => {
    await page.goto('/canvas');

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('main')).toHaveScreenshot('canvas-main.png', {
      maxDiffPixels: 100
    });
  });

  test('Gallery page visual consistency', async ({ page }) => {
    await page.goto('/gallery');

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('main')).toHaveScreenshot('gallery-main.png', {
      maxDiffPixels: 100
    });
  });

  test('Dark mode visual consistency', async ({ page }) => {
    await page.goto('/');

    const darkModeButton = page.locator('button[aria-label*="dark"], button[aria-label*="深色"]');
    if (await darkModeButton.isVisible()) {
      await darkModeButton.click();
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('homepage-dark.png', {
        fullPage: true,
        maxDiffPixels: 100
      });
    }
  });

  test('Mobile responsive visual consistency', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot('homepage-mobile.png', {
      fullPage: true,
      maxDiffPixels: 100
    });

    const mobileMenuButton = page.locator('button[aria-label*="menu"], .mobile-menu-button');
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click();
      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('mobile-menu-open.png', {
        fullPage: false,
        maxDiffPixels: 50
      });
    }
  });

  test('Component animations disabled for consistency', async ({ page }) => {
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `
    });

    await page.goto('/');
    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('homepage-no-animations.png', {
      fullPage: true,
      maxDiffPixels: 50
    });
  });

  test('Chart components visual consistency', async ({ page }) => {
    await page.goto('/canvas');

    await page.waitForTimeout(2000);

    const chartContainer = page.locator('.chart-container, .recharts-wrapper, canvas');
    const chartCount = await chartContainer.count();

    if (chartCount > 0) {
      for (let i = 0; i < Math.min(chartCount, 3); i++) {
        await expect(chartContainer.nth(i)).toHaveScreenshot(`chart-${i}.png`, {
          maxDiffPixels: 200
        });
      }
    }
  });

  test('Loading states visual consistency', async ({ page }) => {
    await page.route('**/*', route => {
      setTimeout(() => route.continue(), 2000);
    });

    await page.goto('/canvas');

    await page.waitForTimeout(100);
    const loadingIndicator = page.locator('.loading, .spinner, [aria-label*="loading"]');

    if (await loadingIndicator.isVisible()) {
      await expect(loadingIndicator).toHaveScreenshot('loading-state.png', {
        maxDiffPixels: 50
      });
    }
  });
});
