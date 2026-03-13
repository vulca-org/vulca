/**
 * Video 7: Self-Evolution Dashboard (~60s)
 *
 * Admin Page — stat cards, evolved context coverage, agent insights,
 * tradition insights, trajectory stats, feature space clusters,
 * prompt archetypes, feedback stats, skill ecosystem, evolution curve.
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v7-admin.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
 *   - Backend running on :8001 (for live data; page still renders with defaults)
 */

import {
  launchRecorder,
  finalize,
  wait,
  moveTo,
  clickWith,
  smoothScroll,
  scrollToElement,
  moveToElement,
  hideCursor,
  showCursor,
  adminLogin,
  waitForImages,
  PAUSE,
  BASE_URL,
} from './video-utils';

async function main() {
  const { browser, context, page } = await launchRecorder('v7-admin');

  try {
    // ─────────────────────────────────────────────────────
    // 1. Navigate to any page and perform admin login
    //    (sets access_token in localStorage)
    // ─────────────────────────────────────────────────────
    console.log('[v7] Logging in as admin...');
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('domcontentloaded');
    await adminLogin(page);
    await wait(PAUSE.brief);

    // ─────────────────────────────────────────────────────
    // 2. Navigate to /admin, wait for dashboard heading
    // ─────────────────────────────────────────────────────
    console.log('[v7] Navigating to /admin...');
    await page.goto(`${BASE_URL}/admin`);
    await page.waitForSelector('h1:has-text("Self-Evolution Dashboard")', { timeout: 15000 });
    await wait(PAUSE.normal);
    await waitForImages(page);

    // ─────────────────────────────────────────────────────
    // 3. Hold 3s on top: 4 stat cards
    //    (Sessions Learned, Traditions Active, Evolution Cycles, Emerged Concepts)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Showing top stat cards...');
      await hideCursor(page);
      await wait(PAUSE.hero);
    } catch (err) {
      console.warn(`[v7] Section 3 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 4. Scroll to "Evolved Context Coverage" section
    //    Shows Context Coverage + Pipeline Agents (AgentInsightsPanel)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Scrolling to Evolved Context Coverage...');
      await scrollToElement(page, 'h2:has-text("Evolved Context Coverage")');
      await wait(PAUSE.read);
    } catch (err) {
      console.warn(`[v7] Section 4 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 5. Click Scout agent card to expand its insights
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Expanding Scout agent insights...');
      await showCursor(page);

      // The AgentInsightsPanel has expandable agent cards; Scout is the first
      // Agent cards have the agent label text (Scout, Draft, Critic, Queen)
      const scoutCard = page.locator('text=Scout').first();
      if (await scoutCard.isVisible()) {
        await clickWith(page, 'text=Scout');
        await wait(PAUSE.brief);
      }
    } catch (err) {
      console.warn(`[v7] Section 5 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 6. Hold 2s on expanded Scout insights
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Holding on Scout insights...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v7] Section 6 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 7. Scroll to "Tradition Insights", click "Chinese Xieyi" to expand
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Expanding Chinese Xieyi tradition insights...');
      await showCursor(page);

      // Tradition insights section header
      const traditionHeader = page.locator('text=Tradition Insights').first();
      if (await traditionHeader.isVisible()) {
        await scrollToElement(page, 'text=Tradition Insights');
        await wait(PAUSE.normal);
      }

      // Click "Chinese Xieyi" or "chinese xieyi" tradition button to expand
      const xieyiButton = page.locator('button:has-text("Chinese Xieyi"), button:has-text("chinese xieyi")').first();
      if (await xieyiButton.isVisible()) {
        const box = await xieyiButton.boundingBox();
        if (box) {
          await moveTo(page, box.x + box.width / 2, box.y + box.height / 2);
          await wait(200);
          await xieyiButton.click();
          await wait(PAUSE.brief);
        }
      }
    } catch (err) {
      console.warn(`[v7] Section 7 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 8. Hold 2s on expanded tradition insight
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Holding on Chinese Xieyi insights...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v7] Section 8 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 9. Scroll to "Trajectory Stats"
    //    (total trajectories, avg rounds, repair rate)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Scrolling to Trajectory Stats...');
      // Trajectory stats are shown inside AgentInsightsPanel, look for "trajectories" text
      const trajectorySection = page.locator('text=trajectories').first();
      if (await trajectorySection.isVisible()) {
        await scrollToElement(page, 'text=trajectories');
      } else {
        // Fallback: scroll down to find trajectory data
        await smoothScroll(page, 400, 800);
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn(`[v7] Section 9 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 10. Scroll to "Feature Space Clusters" scatter plot
    //     (Avg Score vs Cultural Depth)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Scrolling to Feature Space Clusters...');
      const clusterSection = page.locator('text=Feature Space').first();
      if (await clusterSection.isVisible()) {
        await scrollToElement(page, 'text=Feature Space');
      } else {
        await smoothScroll(page, 500, 800);
      }
      await wait(PAUSE.brief);
    } catch (err) {
      console.warn(`[v7] Section 10 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 11. Hold 2s on scatter plot
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Holding on cluster scatter plot...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v7] Section 11 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 12. Scroll to "Prompt Archetypes" bar chart
    //     (Misty Mountain, Imperfect Object, Zen Garden, etc.)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Scrolling to Prompt Archetypes...');
      await showCursor(page);
      const archetypeSection = page.locator('h2:has-text("Prompt Archetypes")').first();
      if (await archetypeSection.isVisible()) {
        await scrollToElement(page, 'h2:has-text("Prompt Archetypes")');
      } else {
        await smoothScroll(page, 500, 800);
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn(`[v7] Section 12 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 13. Scroll to "Feedback Stats" + "Skill Ecosystem" + "Evolution Curve"
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Scrolling to Feedback + Skills + Evolution...');
      await hideCursor(page);

      // Feedback Stats section
      const feedbackCard = page.locator('text=Feedback Stats').first();
      if (await feedbackCard.isVisible()) {
        await scrollToElement(page, 'text=Feedback Stats');
      } else {
        await smoothScroll(page, 500, 800);
      }
      await wait(PAUSE.read);

      // Continue to Evolution Timeline
      const evolutionSection = page.locator('h2:has-text("Evolution Timeline")').first();
      if (await evolutionSection.isVisible()) {
        await scrollToElement(page, 'h2:has-text("Evolution Timeline")');
      } else {
        await smoothScroll(page, 500, 800);
      }
      await wait(PAUSE.brief);
    } catch (err) {
      console.warn(`[v7] Section 13 failed, skipping:`, err);
    }

    // ─────────────────────────────────────────────────────
    // 14. Hold 2s on Evolution Curve
    //     (dual line chart: Emerged Cultures + Evolution Cycles)
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v7] Holding on Evolution Curve...');
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v7] Section 14 failed, skipping:`, err);
    }
  } catch (err) {
    console.error('[v7] Error during recording:', err);
  }

  // ─────────────────────────────────────────────────────
  // Done
  // ─────────────────────────────────────────────────────
  console.log('[v7] Finalizing...');
  await finalize(browser, context, page, 'v7-admin');
}

main().catch(console.error);
