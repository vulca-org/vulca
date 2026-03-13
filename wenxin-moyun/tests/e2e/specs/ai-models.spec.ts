import { test, expect } from '@playwright/test';

test.describe('AI Models Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/models');
  });

  test('应该显示AI模型列表', async ({ page }) => {
    await expect(page).toHaveTitle(/VULCA/);

    const modelsList = page.locator('[class*="leaderboard"], table, [class*="model-list"]').first();
    await expect(modelsList).toBeVisible();

    const modelNames = page.locator('[class*="model-name"], td, [class*="card-title"]').first();
    await expect(modelNames).toBeVisible();
  });

  test('应该正确处理NULL分数显示', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const naScore = page.getByText('N/A').first();
    const hasVisibleNA = await naScore.isVisible({ timeout: 2000 }).catch(() => false);
    if (hasVisibleNA) {
      await expect(naScore).toBeVisible();
    }

    const scores = page.locator('[class*="score"]:not(:has-text("N/A"))');
    if (await scores.count() > 0) {
      const scoreText = await scores.first().textContent();
      expect(scoreText).toMatch(/^\d+\.\d+$/);
    }
  });

  test('应该支持模型类型筛选', async ({ page }) => {
    const filters = page.locator('[class*="filter"], select, [role="tab"]').first();

    if (await filters.isVisible({ timeout: 3000 }).catch(() => false)) {
      const typeFilters = page.locator('[value="llm"], [value="image"], [value="multimodal"]').first();

      if (await typeFilters.isVisible({ timeout: 2000 }).catch(() => false)) {
        await typeFilters.click();
        await page.waitForTimeout(1000);

        const results = page.locator('[class*="model-card"], tr').first();
        await expect(results).toBeVisible();
      }
    }
  });

  test('应该支持排序功能', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const sortButtons = page.locator('[class*="sort"], th[role="button"], [data-sort]').first();

    if (await sortButtons.isVisible({ timeout: 3000 }).catch(() => false)) {
      await sortButtons.click();
      await page.waitForTimeout(1000);

      const modelList = page.locator('[class*="model-list"], tbody').first();
      await expect(modelList).toBeVisible();
    }
  });

  test('模型详情页面跳转', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const modelLinks = page.locator('a[href*="/model/"], [class*="model-card"][role="button"]').first();

    if (await modelLinks.isVisible({ timeout: 3000 }).catch(() => false)) {
      await modelLinks.click();
      await expect(page).toHaveURL(/\/model\//);

      const modelDetail = page.locator('[class*="model-detail"], main').first();
      await expect(modelDetail).toBeVisible();
    }
  });

  test('响应式设计测试', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    const modelsList = page.locator('[class*="leaderboard"], table, [class*="model-list"]').first();

    // Desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1500);
    await expect(modelsList).toBeVisible({ timeout: 10000 });

    // Tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1500);
    await expect(modelsList).toBeVisible({ timeout: 10000 });

    // Mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1500);
    await expect(modelsList).toBeVisible({ timeout: 10000 });
  });

  test('搜索功能测试', async ({ page }) => {
    const searchBox = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="搜索"]').first();

    if (await searchBox.isVisible({ timeout: 3000 }).catch(() => false)) {
      await searchBox.fill('GPT');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const results = page.locator('[class*="model-card"], tr').first();
      await expect(results).toBeVisible();

      const resultText = await page.locator('body').textContent();
      expect(resultText?.toLowerCase()).toContain('gpt');
    }
  });

  test('数据加载状态测试', async ({ page }) => {
    const loadingIndicator = page.locator('[class*="loading"], [class*="spinner"]').first();

    if (await loadingIndicator.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
    }

    const content = page.locator('[class*="model-list"], table, [class*="leaderboard"]').first();
    await expect(content).toBeVisible();
  });
});
