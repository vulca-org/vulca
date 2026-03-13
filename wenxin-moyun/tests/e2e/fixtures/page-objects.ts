import { Page, Locator } from '@playwright/test';
import { withRoute, urlMatcher } from '../utils/route-helper';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigate(path: string) {
    const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
    const fullURL = path.startsWith('http') ? path : `${baseURL}${withRoute(path)}`;
    await this.page.goto(fullURL);
  }

  async expectURL(path: string) {
    await this.page.waitForURL(urlMatcher(path));
  }

  async waitForLoadComplete() {
    await this.page.waitForLoadState('networkidle');
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `tests/visual/baseline/${name}.png`, fullPage: true });
  }
}

export class HomePage extends BasePage {
  readonly heroTitle: Locator;
  readonly navMenu: Locator;
  readonly canvasLink: Locator;
  readonly modelsLink: Locator;
  readonly loginButton: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.heroTitle = page.locator('main h1').first();
    this.navMenu = page.locator('nav');
    this.canvasLink = page.locator('[data-testid="nav-canvas"], a[href="/canvas"]').first();
    this.modelsLink = page.locator('a[href="/models"], nav a:has-text("Models")').first();
    this.loginButton = page.locator('a[href*="login"], button:has-text("Login")').first();
    this.logoutButton = page.locator('[data-testid="logout-btn"], button:has-text("Logout")').first();
  }

  // Kept for backward compatibility with existing tests
  get leaderboardLink(): Locator { return this.modelsLink; }
  get battleLink(): Locator { return this.canvasLink; }

  async clickExploreRankings() {
    if (await this.modelsLink.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.modelsLink.click();
      return;
    }
    await this.navigate('/models');
  }

  async clickModelBattle() {
    if (await this.canvasLink.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.canvasLink.click();
      return;
    }
    await this.navigate('/canvas');
  }

  async navigateToLogin() {
    if (await this.loginButton.isVisible({ timeout: 2000 })) {
      await this.loginButton.click();
    } else {
      await this.navigate('/login');
    }
    await this.page.waitForURL(urlMatcher('/login'));
  }

  async clickStartExperience() {
    const btn = this.page.locator('button:has-text("Start Experience"), button:has-text("Guest Mode")');
    if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await btn.click();
    } else {
      // Fallback: set guest session via JavaScript
      await this.page.evaluate(() => {
        const session = { id: 'test-guest-manual', dailyUsage: 0, lastReset: new Date().toDateString(), evaluations: [] };
        try { localStorage?.setItem('guest_session', JSON.stringify(session)); } catch { /* expected */ }
        (window as any).__TEST_GUEST_SESSION__ = session;
      });
    }
  }
}

export class LoginPage extends BasePage {
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly loginForm: Locator;

  constructor(page: Page) {
    super(page);
    this.usernameInput = page.locator('input[id="username"], input[name="username"]').first();
    this.passwordInput = page.locator('input[id="password"], input[type="password"]').first();
    this.submitButton = page.locator('[data-testid="login-submit"], button[type="submit"]').first();
    this.errorMessage = page.locator('[role="alert"]').first();
    this.loginForm = page.locator('form').first();
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}

export class CanvasPage extends BasePage {
  readonly intentInput: Locator;
  readonly intentSubmit: Locator;
  readonly pipelineStatus: Locator;
  readonly modeButtons: Locator;

  constructor(page: Page) {
    super(page);
    this.intentInput = page.locator('[data-testid="intent-input"]');
    this.intentSubmit = page.locator('[data-testid="intent-submit"]');
    this.pipelineStatus = page.locator('[data-testid="pipeline-status"]');
    this.modeButtons = page.locator('[data-tour-modes] button');
  }

  async submitIntent(text: string) {
    await this.intentInput.fill(text);
    await this.intentSubmit.click();
  }
}

export class ModelsPage extends BasePage {
  readonly searchInput: Locator;
  readonly rankingTable: Locator;
  readonly modelCards: Locator;

  constructor(page: Page) {
    super(page);
    this.searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    this.rankingTable = page.locator('table').first();
    this.modelCards = page.locator('.model-card, .ranking-item').first();
  }

  async searchModel(query: string) {
    await this.searchInput.fill(query);
  }
}

// Legacy aliases for backward compatibility
export { ModelsPage as LeaderboardPage };
export { CanvasPage as EvaluationPage };
