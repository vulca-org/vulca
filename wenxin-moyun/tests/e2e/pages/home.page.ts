import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class HomePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  get exploreRankingsButton() {
    return this.page.locator('[data-testid="explore-rankings-button"]').first();
  }

  get tryCanvasButton() {
    return this.page.locator('[data-testid="hero-try-demo"], a[href="/canvas"]').first();
  }

  get modelsLink() {
    return this.page.locator('a[href*="models"], [data-testid="explore-rankings-button"]').first();
  }

  get userAvatar() {
    return this.page.locator('[data-testid="user-avatar"], .user-avatar').first();
  }

  // Actions
  async goto() {
    await this.navigateTo('/');
  }

  async navigateToLogin() {
    await this.navigateTo('/login');
  }

  async navigateToModels() {
    await this.modelsLink.click();
    await this.waitForNavigation('/models');
  }

  async clickExploreRankings() {
    await this.exploreRankingsButton.click();
    await this.waitForNavigation('/models');
  }

  async clickTryCanvas() {
    await this.tryCanvasButton.click();
    await this.waitForNavigation('/canvas');
  }

  async setGuestMode() {
    await this.page.evaluate(() => {
      const guestId = `guest-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('guest_session_id', guestId);
      localStorage.setItem('is_guest', 'true');
    });
  }

  // Assertions
  async assertOnHomePage() {
    await this.assertCurrentPath('/');
  }

  async assertUserLoggedIn() {
    await expect(this.userAvatar).toBeVisible();
  }
}
