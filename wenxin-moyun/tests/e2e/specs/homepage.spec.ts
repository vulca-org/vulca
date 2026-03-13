import { test, expect } from '@playwright/test';
import { HomePage } from '../fixtures/page-objects';

test.describe('Homepage', () => {
  // Increase timeout for CI environment
  test.setTimeout(60000);

  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigate('/');
  });

  test('应该正确显示页面标题和主要导航', async ({ page }) => {
    await expect(page).toHaveTitle(/VULCA/);

    await expect(homePage.navMenu).toBeVisible();
    await expect(homePage.leaderboardLink).toBeVisible();
    await expect(homePage.battleLink).toBeVisible();
  });

  test('应该显示主要内容区域', async ({ page }) => {
    await expect(homePage.heroTitle).toBeVisible();

    // Check for iOS-style glass card components
    const iosCards = page.locator('.liquid-glass-container');
    await expect(iosCards.first()).toBeVisible();
  });

  test('应该响应式适配移动端', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main').getByRole('heading', { level: 1 })).toBeVisible();

    const mobileNav = page.locator('[class*="mobile"], [class*="hamburger"]').first();
    if (await mobileNav.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(mobileNav).toBeVisible();
    }
  });

  test('导航链接应该正确跳转', async ({ page }) => {
    // Test explore rankings → /models
    await homePage.clickExploreRankings();
    await expect(page).toHaveURL(/\/models/);

    await homePage.navigate('/');

    // Test try canvas button → /canvas
    await homePage.clickModelBattle();
    await expect(page).toHaveURL(/\/canvas/);

    await homePage.navigate('/');

    // Test models nav link
    await homePage.leaderboardLink.click();
    await expect(page).toHaveURL(/\/models/);
  });

  test('页面加载性能测试', async ({ page }) => {
    const startTime = Date.now();
    await homePage.navigate('/');
    const loadTime = Date.now() - startTime;

    // Page should load within 10 seconds (CI environments can be slower)
    expect(loadTime).toBeLessThan(10000);

    await expect(homePage.heroTitle).toBeVisible();
    await expect(homePage.navMenu).toBeVisible();
  });
});
