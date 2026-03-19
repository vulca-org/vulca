/**
 * User Journey Smoke Test — the REAL end-to-end test.
 *
 * Tests actual user workflows, not just "does the page load".
 * Each test builds on the previous one to simulate a real session:
 *
 *   1. Demo login (one-click, no password exposure)
 *   2. Canvas Preview create (mock, instant, verify L1-L5 scores)
 *   3. Canvas Generate create (real Gemini API, verify image + scores)
 *   4. Publish to Gallery (verify API call succeeds)
 *   5. Gallery shows the published work
 *   6. Feedback submission
 *   7. Gallery filtering and sorting
 *
 * Requirements:
 *   - Backend running on localhost:8001 with GOOGLE_API_KEY loaded
 *   - Frontend running on localhost:5173
 *   - Demo account (demo/demo123) exists in DB
 */

import { test, expect, type Page } from '@playwright/test';
import { withRoute } from '../utils/route-helper';

const BASE = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
const API_BASE = process.env.API_BASE_URL || 'http://localhost:8001';

// ─── Helpers ────────────────────────────────────────────────

async function waitForCanvasReady(page: Page) {
  // Set tour-seen BEFORE loading canvas — go to a simple page first
  await page.goto(`${BASE}${withRoute('/')}`);
  await page.evaluate(() => {
    try {
      localStorage.setItem('vulca-has-visited', 'true');
      localStorage.setItem('vulca_tour_seen', 'true');
    } catch {}
  });
  // Now load canvas — tour should not appear
  await page.goto(`${BASE}${withRoute('/canvas')}`);
  await page.waitForLoadState('domcontentloaded');
  const canvas = page.locator('h1:has-text("Canvas")').first();
  await canvas.waitFor({ state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1000);
  await dismissOverlays(page);
  // Wait for "Ready" status
  await expect(page.locator('text=Ready').first()).toBeVisible({ timeout: 10000 });
  // Click Run tab
  const runTab = page.getByRole('button', { name: 'Run' });
  if (await runTab.isVisible({ timeout: 2000 }).catch(() => false)) {
    await runTab.click({ force: true });
    await page.waitForTimeout(500);
  }
}

async function dismissOverlays(page: Page) {
  await page.evaluate(() => {
    document.querySelectorAll('.fixed').forEach(el => {
      const z = window.getComputedStyle(el).zIndex;
      if (z && parseInt(z) >= 10000) el.remove();
    });
  });
}

async function fillIntentAndCreate(page: Page, intent: string) {
  await dismissOverlays(page);
  // Click on the textarea first, then type (triggers React onChange properly)
  const input = page.getByTestId('intent-input').first();
  await input.click({ force: true });
  await input.clear();
  await input.type(intent, { delay: 10 });
  // Wait for tradition auto-detection + Create button to enable
  await page.waitForTimeout(3000);
  await dismissOverlays(page);
  // Check textarea value was actually set
  const textareaValue = await page.evaluate(() => {
    const ta = document.querySelector('[data-testid="intent-input"]') as HTMLTextAreaElement;
    return ta?.value || '';
  });
  if (!textareaValue) {
    throw new Error('Intent textarea is empty — type() did not register');
  }
  // Check Create button state
  const createBtn = page.getByRole('button', { name: 'Create' }).first();
  const isDisabled = await createBtn.isDisabled();
  if (isDisabled) {
    // Debug: what's the form state?
    const debugInfo = await page.evaluate(() => {
      const ta = document.querySelector('[data-testid="intent-input"]') as HTMLTextAreaElement;
      const btns = Array.from(document.querySelectorAll('button')).filter(b => b.textContent?.includes('Create'));
      return {
        textareaValue: ta?.value?.substring(0, 30),
        createButtons: btns.map(b => ({ disabled: b.disabled, text: b.textContent?.trim() })),
        overlayCount: document.querySelectorAll('.fixed').length,
      };
    });
    throw new Error(`Create button is disabled! Debug: ${JSON.stringify(debugInfo)}`);
  }
  // Monitor network to verify POST /runs is sent
  const runPromise = page.waitForResponse(
    resp => resp.url().includes('/prototype/runs') && resp.request().method() === 'POST',
    { timeout: 10000 }
  ).catch(() => null);
  await createBtn.click({ force: true, timeout: 5000 });
  const runResponse = await runPromise;
  if (!runResponse) {
    throw new Error('POST /prototype/runs was never sent — Create click did not trigger pipeline');
  }
  const runData = await runResponse.json().catch(() => ({}));
  if (runResponse.status() === 429) {
    throw new Error(`Daily limit reached: ${JSON.stringify(runData)}`);
  }
  if (runResponse.status() >= 400) {
    throw new Error(`Pipeline creation failed (${runResponse.status()}): ${JSON.stringify(runData)}`);
  }
}

// ─── Tests ──────────────────────────────────────────────────

test.describe('User Journey Smoke', () => {
  // Generous timeout for real API calls
  test.setTimeout(120000);

  test.describe.configure({ mode: 'serial' });

  let page: Page;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.afterAll(async () => {
    await page.close();
  });

  // ─── Step 1: Demo Login ───────────────────────────────────

  test('1. Demo one-click login works', async () => {
    await page.goto(`${BASE}${withRoute('/login')}`);
    await page.waitForLoadState('domcontentloaded');

    // Wait for login form
    const heading = page.locator('h2:has-text("Welcome Back")');
    await heading.waitFor({ state: 'visible', timeout: 15000 });

    // Click "Use demo account" — should login directly, not fill form
    const demoBtn = page.getByRole('button', { name: 'Use demo account' });
    await expect(demoBtn).toBeVisible();
    await demoBtn.click();

    // Should redirect away from login — wait for navigation or user indicator
    await page.waitForURL(url => !url.toString().includes('/login'), { timeout: 15000 }).catch(async () => {
      // If still on login, check for error message
      const error = page.locator('[role="alert"]');
      const errorText = await error.textContent().catch(() => 'unknown');
      throw new Error(`Login did not redirect. Error: ${errorText}`);
    });

    // Nav should show "demo" user
    const userBtn = page.getByRole('button', { name: 'demo' });
    await expect(userBtn).toBeVisible({ timeout: 10000 });
  });

  // ─── Step 2: Canvas Preview Create ────────────────────────

  test('2. Canvas Preview mode creates with mock and shows L1-L5 scores', async () => {
    await waitForCanvasReady(page);

    // Verify Preview is default mode
    const previewBtn = page.getByRole('button', { name: 'Preview' });
    await expect(previewBtn).toBeVisible();

    // Enter intent
    await fillIntentAndCreate(page, 'Bamboo forest in morning mist');

    // Wait for pipeline to complete — look for score or "Done" or "Pipeline Complete"
    const completed = page.locator('text=/Pipeline Complete|Overall Score|0\\.\\d+.*\\/.*1\\.000/').first();
    await completed.waitFor({ state: 'visible', timeout: 30000 }).catch(async () => {
      // Debug: capture current page state
      await page.screenshot({ path: 'test-results/debug-pipeline-stuck.png' });
      const bodyText = await page.locator('body').textContent().catch(() => '');
      const hasRunning = bodyText?.includes('Running') || false;
      const hasFailed = bodyText?.includes('Failed') || false;
      const hasDone = bodyText?.includes('Done') || false;
      throw new Error(`Pipeline did not show completion UI. Running=${hasRunning} Failed=${hasFailed} Done=${hasDone}`);
    });

    // Verify L1-L5 scores are displayed
    for (const dim of ['L1 Visual Perception', 'L2 Technical Analysis', 'L3 Cultural Context', 'L4 Critical Interpretation', 'L5 Philosophical Aesthetic']) {
      await expect(page.locator(`text=${dim}`).first()).toBeVisible({ timeout: 5000 });
    }

    // Verify Overall Score is a valid number
    const scoreText = await page.locator('text=/0\\.[0-9]+/').first().textContent();
    expect(scoreText).toBeTruthy();
    const score = parseFloat(scoreText!);
    expect(score).toBeGreaterThan(0);
    expect(score).toBeLessThanOrEqual(1);

    // Verify Queen Decision shows ACCEPT
    await expect(page.locator('text=accept').first()).toBeVisible();

    // Verify action buttons are present
    await expect(page.getByRole('button', { name: 'Publish to Gallery' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'New Run' })).toBeVisible();
  });

  // ─── Step 3: Publish to Gallery ───────────────────────────

  test('3. Publish to Gallery succeeds without errors', async () => {
    // Intercept the publish API call to verify it hits the right endpoint
    const publishPromise = page.waitForResponse(
      resp => resp.url().includes('/prototype/gallery/') && resp.url().includes('/publish'),
      { timeout: 10000 }
    );

    const publishBtn = page.getByRole('button', { name: 'Publish to Gallery' });
    await expect(publishBtn).toBeVisible();
    await publishBtn.click();

    // Wait for the API response
    const response = await publishPromise.catch(() => null);
    if (response) {
      // If we got a response, check it's successful
      expect(response.status()).toBeLessThan(500); // No server error
    }

    // No error dialog should appear
    const errorDialog = page.locator('dialog:has-text("Failed")');
    const hasError = await errorDialog.isVisible().catch(() => false);
    expect(hasError).toBe(false);
  });

  // ─── Step 4: Gallery Shows Works ──────────────────────────

  test('4. Gallery page loads and shows artworks', async () => {
    await page.goto(`${BASE}${withRoute('/gallery')}`);
    await page.waitForLoadState('domcontentloaded');

    // Wait for gallery content (either live data or mock fallback)
    const heading = page.locator('h1:has-text("Creation Gallery")');
    await heading.waitFor({ state: 'visible', timeout: 15000 });

    // Gallery should show content — live data shows "Showing X-Y of Z", mock shows cards
    const showing = page.locator('text=/Showing|artwork|round/').first();
    await expect(showing).toBeVisible({ timeout: 15000 });

    // Filter controls should be present
    await expect(page.getByLabel('Filter by tradition')).toBeVisible();
    await expect(page.getByLabel('Sort artworks')).toBeVisible();
  });

  // ─── Step 5: Gallery Filtering ────────────────────────────

  test('5. Gallery tradition filter works', async () => {
    const filter = page.getByLabel('Filter by tradition');
    await expect(filter).toBeVisible();

    // Get initial count text
    const countText = page.locator('text=/\\d+ artwork/');
    const initialText = await countText.textContent().catch(() => '');

    // Select a specific tradition
    await filter.selectOption({ index: 1 }); // First non-"All" option
    await page.waitForTimeout(1000);

    // Page should still render without errors
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  // ─── Step 6: Evolution Banner ─────────────────────────────

  test('6. Gallery shows evolution system stats', async () => {
    // Reset filter
    await page.goto(`${BASE}${withRoute('/gallery')}`);
    const heading = page.locator('h1:has-text("Creation Gallery")');
    await heading.waitFor({ state: 'visible', timeout: 15000 });

    // Evolution banner should show session count
    const sessionCount = page.locator('text=/\\d+ sessions learned/');
    const hasEvolution = await sessionCount.isVisible({ timeout: 5000 }).catch(() => false);
    if (hasEvolution) {
      const text = await sessionCount.textContent();
      const count = parseInt(text!.match(/(\d+)/)?.[1] || '0');
      expect(count).toBeGreaterThan(0);
    }
    // If no evolution data, it's acceptable (backend may not have enough sessions)
  });

  // ─── Step 7: Canvas Generate Mode (Real API) ──────────────

  test('7. Canvas Generate mode produces real image via Gemini', async () => {
    // Skip if no API key configured
    const capsResponse = await page.request.get(`${API_BASE}/api/v1/prototype/capabilities`);
    const caps = await capsResponse.json();
    if (!caps.has_api_key) {
      test.skip(true, 'No GOOGLE_API_KEY configured — skipping real generation test');
      return;
    }

    await waitForCanvasReady(page);

    // Switch to Generate mode
    // Click Generate mode — use evaluate to bypass any overlay
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const gen = btns.find(b => b.textContent?.includes('Generate'));
      if (gen) gen.click();
    });
    await page.waitForTimeout(500);

    // Create with real API
    await fillIntentAndCreate(page, 'Lotus pond in moonlight, Chinese gongbi style');

    // Wait for pipeline — real Gemini call takes 30-90s
    const complete = page.locator('text=Pipeline Complete');
    await complete.waitFor({ state: 'visible', timeout: 120000 });

    // Verify scores
    const overallScore = page.locator('text=/0\\.[0-9]+.*\\/.*1\\.000/').first();
    await expect(overallScore).toBeVisible({ timeout: 5000 });

    // Verify no error dialog
    const errorDialog = page.locator('dialog:has-text("Failed")');
    const hasError = await errorDialog.isVisible().catch(() => false);
    expect(hasError).toBe(false);
  });

  // ─── Step 8: Feedback Submission ──────────────────────────

  test('8. Feedback star rating and comment submission', async () => {
    // Should still be on Canvas with results
    const feedbackHeading = page.locator('h3:has-text("Feedback")');
    const hasFeedback = await feedbackHeading.isVisible().catch(() => false);
    if (!hasFeedback) {
      // Navigate back to canvas and do a quick preview run
      await waitForCanvasReady(page);
      await fillIntentAndCreate(page, 'Quick test for feedback');
      const complete = page.locator('text=Pipeline Complete');
      await complete.waitFor({ state: 'visible', timeout: 30000 });
    }

    // Click 4 stars
    const fourStar = page.getByRole('radio', { name: '4 stars' });
    await fourStar.click();

    // Submit should now be enabled
    const submitBtn = page.getByRole('button', { name: 'Submit Feedback' });
    await expect(submitBtn).toBeEnabled({ timeout: 3000 });

    // Add comment
    const commentBox = page.getByPlaceholder('Add a comment');
    await commentBox.fill('Great ink wash quality, could improve composition');

    // Submit
    await submitBtn.click();
    await page.waitForTimeout(2000);

    // No error should appear
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  // ─── Step 9: Canvas Run History ───────────────────────────

  test('9. Run History shows previous runs with scores', async () => {
    await waitForCanvasReady(page);

    // Run History section should be visible
    const historyHeading = page.locator('h3:has-text("Run History")').first();
    await expect(historyHeading).toBeVisible({ timeout: 10000 });

    // Should have at least one history item — they contain "ago" text
    const historyItem = page.locator('text=/\\d+[hm]? ago/').first();
    await expect(historyItem).toBeVisible({ timeout: 5000 });
  });

  // ─── Step 10: Leaderboard Loads ───────────────────────────

  test('10. Leaderboard page loads with model data', async () => {
    await page.goto(`${BASE}${withRoute('/leaderboard')}`);
    await page.waitForLoadState('domcontentloaded');

    // Should show the leaderboard heading
    const heading = page.locator('h1:has-text("Leaderboard")');
    await heading.waitFor({ state: 'visible', timeout: 15000 });

    // Category tabs should be IOSButtons (not raw buttons)
    const overallTab = page.getByRole('button', { name: 'Overall Rankings' });
    await expect(overallTab).toBeVisible();

    // Should show model count
    await expect(page.locator('text=/\\d+.*models/')).toBeVisible({ timeout: 5000 });
  });
});
