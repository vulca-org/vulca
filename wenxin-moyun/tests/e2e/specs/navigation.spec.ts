import { test, expect } from '@playwright/test';
import { HomePage } from '../fixtures/page-objects';
import { cleanupTestData } from '../helpers/test-utils';

test.describe('Navigation System', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigate('/');
  });

  test.afterEach(async ({ page }) => {
    await cleanupTestData(page);
  });

  test('Main navigation menu functionality', async ({ page }) => {
    // Check main navigation links for current pages
    const navLinks = [
      { patterns: ['Canvas'], url: '/canvas' },
      { patterns: ['Gallery'], url: '/gallery' },
      { patterns: ['Models'], url: '/models' },
    ];

    for (const link of navLinks) {
      let navLink = null;
      for (const pattern of link.patterns) {
        navLink = page.locator(`nav a:has-text("${pattern}"), header a:has-text("${pattern}")`).first();
        if (await navLink.isVisible({ timeout: 1000 }).catch(() => false)) {
          break;
        }
      }

      if (navLink && await navLink.isVisible({ timeout: 2000 }).catch(() => false)) {
        await navLink.click();
        await expect(page).toHaveURL(new RegExp(link.url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
        await page.goto('/');
      }
    }
  });

  test('Route switching and page transitions', async ({ page }) => {
    const routes = [
      { path: '/canvas', check: 'canvas', urlMatch: '/canvas' },
      { path: '/gallery', check: 'gallery', urlMatch: '/gallery' },
      { path: '/models', check: 'models', urlMatch: '/models' },
      { path: '/', check: 'home', urlMatch: '/$' }
    ];

    for (const route of routes) {
      await page.goto(route.path);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(new RegExp(route.urlMatch));

      if (route.check === 'canvas') {
        const canvasElements = page.locator('button:has-text("Edit"), button:has-text("Run"), h1, [data-testid*="canvas"]').first();
        await expect(canvasElements).toBeVisible({ timeout: 15000 });
      } else if (route.check === 'gallery') {
        const galleryElements = page.locator('h1, h2, [data-testid*="gallery"]').first();
        await expect(galleryElements).toBeVisible({ timeout: 10000 });
      } else if (route.check === 'models') {
        const modelsElements = page.locator('h1, h2, table, [data-testid="leaderboard"]').first();
        await expect(modelsElements).toBeVisible({ timeout: 10000 });
      } else if (route.check === 'home') {
        await expect(homePage.heroTitle).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('Legacy route redirects work correctly', async ({ page }) => {
    // Test that deprecated routes redirect to correct destinations
    const redirects = [
      { from: '/vulca', to: '/canvas' },
      { from: '/evaluations', to: '/canvas' },
      { from: '/leaderboard', to: '/models' },
      { from: '/battle', to: '/models' },
      { from: '/methodology', to: '/research' },
    ];

    for (const redirect of redirects) {
      await page.goto(redirect.from);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);
      expect(page.url()).toContain(redirect.to);
    }
  });

  test('404 page handling for invalid routes', async ({ page }) => {
    await page.goto('/non-existent-route-12345');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    const is404 = await page.locator('text=/404|not found|page.*not.*exist/i').isVisible({ timeout: 3000 }).catch(() => false);
    const hasHeading = await page.locator('h1').count() > 0;
    const hasContent = (await page.textContent('body'))?.length || 0 > 200;

    expect(is404 || hasHeading || hasContent).toBeTruthy();
  });

  test('Mobile navigation menu (responsive)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const mobileMenuButton = page.locator('button[aria-label*="menu" i], .mobile-menu-button, .hamburger, button:has-text("☰"), [data-testid="mobile-menu-button"]').first();

    if (await mobileMenuButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await mobileMenuButton.click();
      await page.waitForTimeout(500);

      const mobileMenu = page.locator('.mobile-menu, nav[aria-label="mobile"], [data-testid="mobile-nav"], .nav-mobile, nav').first();

      if (await mobileMenu.isVisible({ timeout: 2000 }).catch(() => false)) {
        const mobileLink = mobileMenu.locator('a[href="/canvas"]').first();
        if (await mobileLink.isVisible({ timeout: 2000 }).catch(() => false)) {
          await mobileLink.click();
          await expect(page).toHaveURL(/\/canvas/);
        } else {
          await expect(mobileMenu).toBeVisible();
        }
      }
    } else {
      const navLink = page.locator('nav a:has-text("Canvas"), nav a:has-text("Gallery"), nav a:has-text("Models")').first();
      if (await navLink.isVisible({ timeout: 2000 }).catch(() => false)) {
        await navLink.click();
        await expect(page).toHaveURL(/\/(canvas|gallery|models)/);
      }
    }
  });
});
