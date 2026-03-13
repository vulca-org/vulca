/**
 * VULCA Demo Video 1: Product Overview (~45s)
 *
 * Scrolls through the Home page showcasing all major sections:
 *   Hero → Why Cultural Evaluation Matters → VULCA Platform pillars →
 *   How It Works → See VULCA in Action → Get Started → Solutions →
 *   Built on Real Data → Sample Report → Trust → Final CTA → Footer
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v1-home.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
 */

import {
  launchRecorder,
  finalize,
  wait,
  moveTo,
  smoothScroll,
  scrollToElement,
  moveToElement,
  hideCursor,
  showCursor,
  waitForImages,
  PAUSE,
  BASE_URL,
} from './video-utils';

async function main() {
  const { browser, context, page } = await launchRecorder('v1-home');

  try {
    // ─── 1. Navigate to Home ───
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await wait(PAUSE.normal);
    await waitForImages(page);

    // ─── 2. Hero section hold (3s) — trust badges, headline, CTA, pip install ───
    try {
      await showCursor(page);
      // Hover over trust badges
      await moveToElement(page, 'text=Reproducible');
      await wait(PAUSE.brief);
      await moveToElement(page, 'text=Decision-grade');
      await wait(PAUSE.brief);
      await moveToElement(page, 'text=Enterprise-ready');
      await wait(PAUSE.brief);

      // Hover the main headline
      await moveToElement(page, 'h1');
      await wait(PAUSE.normal);

      // Hover "Try It Now" CTA
      await moveToElement(page, '[data-testid="hero-try-now"]');
      await wait(PAUSE.brief);

      // Hover pip install command
      await moveToElement(page, 'code:has-text("pip install vulca")');
      await wait(PAUSE.read);

      // Hold on hero for the full 3s experience
      await hideCursor(page);
      await wait(PAUSE.hero);
    } catch (err) {
      console.warn(`[v1] Section 2 failed, skipping:`, err);
    }

    // ─── 3. "Why Cultural Evaluation Matters" — 3 problem cards ───
    try {
      await scrollToElement(page, 'text=Why Cultural Evaluation Matters');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover each of the 3 cards
      await moveToElement(page, 'text=Hidden Cultural Risks');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Single Metric Fails');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Reproducibility Required');
      await wait(PAUSE.read);
    } catch (err) {
      console.warn(`[v1] Section 3 failed, skipping:`, err);
    }

    // ─── 4. "The VULCA Platform" 3 pillars + "How It Works" + "See VULCA in Action" ───
    try {
      await hideCursor(page);
      await scrollToElement(page, 'text=The VULCA Platform');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover pillar cards
      await moveToElement(page, 'text=Benchmark Library');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Evaluation Engine');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Explainable Diagnostics');
      await wait(PAUSE.read);

      // Scroll to "How It Works"
      await hideCursor(page);
      await scrollToElement(page, 'text=How It Works');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover the 3 steps
      await moveToElement(page, 'text=Describe Your Intent');
      await wait(PAUSE.normal);
      await moveToElement(page, 'text=Auto-Route to Pipeline');
      await wait(PAUSE.normal);
      await moveToElement(page, 'text=Get Scores & Recommendations');
      await wait(PAUSE.normal);

      // Scroll to "See VULCA in Action"
      await hideCursor(page);
      await scrollToElement(page, 'text=See VULCA in Action');
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v1] Section 4 failed, skipping:`, err);
    }

    // ─── 5. 6 scenario cards + "Get Started" terminal block ───
    try {
      await showCursor(page);
      // Hover a couple of scenario cards
      await moveToElement(page, 'text=Culture Fail');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Self-Evolution');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=API Integration');
      await wait(PAUSE.normal);

      // Scroll down to remaining scenario cards
      await hideCursor(page);
      await smoothScroll(page, 400);
      await wait(PAUSE.normal);

      // Scroll to "Get Started in Seconds" terminal block
      await scrollToElement(page, 'text=Get Started in Seconds');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover the terminal card with pip install
      await moveToElement(page, '.font-mono:has-text("pip install vulca")');
      await wait(PAUSE.read);

      // Hover "Try It Now" button in this section
      await moveToElement(page, 'text=View on GitHub');
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn(`[v1] Section 5 failed, skipping:`, err);
    }

    // ─── 6. "Solutions for Every Team" (3 cards) + "Built on Real Data" (stats) ───
    try {
      await hideCursor(page);
      await scrollToElement(page, 'text=Solutions for Every Team');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover solution cards
      await moveToElement(page, 'text=AI Labs & Companies');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Research Institutions');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Museums & Galleries');
      await wait(PAUSE.read);

      // Scroll to "Built on Real Data" stats
      await hideCursor(page);
      await scrollToElement(page, 'text=Built on Real Data');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover each stat number (42/47/8/130)
      await moveToElement(page, 'text=Models Evaluated');
      await wait(PAUSE.normal);
      await moveToElement(page, 'text=Dimensions');
      await wait(PAUSE.normal);
      await moveToElement(page, 'text=Cultural Perspectives');
      await wait(PAUSE.normal);
      await moveToElement(page, 'text=Artworks');
      await wait(PAUSE.read);
    } catch (err) {
      console.warn(`[v1] Section 6 failed, skipping:`, err);
    }

    // ─── 7. "Sample Report Preview" + "Trust by Default" + Final CTA + Footer ───
    try {
      await hideCursor(page);
      await scrollToElement(page, 'text=What You Get: Sample Report Preview');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover the 3 report preview cards
      await moveToElement(page, 'text=Executive Summary');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=47D Radar Analysis');
      await wait(PAUSE.read);
      await moveToElement(page, 'text=Cultural Bias Analysis');
      await wait(PAUSE.read);

      // Hover "Download Sample Report (PDF)" button
      await moveToElement(page, 'text=Download Sample Report (PDF)');
      await wait(PAUSE.normal);

      // Scroll to "Trust by Default"
      await hideCursor(page);
      await scrollToElement(page, 'text=Trust by Default');
      await wait(PAUSE.section);

      // Final CTA section
      await scrollToElement(page, 'text=Make Cultural Evaluation Part of Your Model Release Workflow');
      await wait(PAUSE.normal);
      await showCursor(page);

      // Hover "Book a Demo" CTA
      await moveToElement(page, 'text=Book a Demo');
      await wait(PAUSE.read);

      // Scroll to footer
      await hideCursor(page);
      await smoothScroll(page, 600);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn(`[v1] Section 7 failed, skipping:`, err);
    }
  } catch (err) {
    console.error('[v1] Error during recording:', err);
  }

  // ─── Finalize ───
  await finalize(browser, context, page, 'v1-home');
  console.log('v1-home recording complete.');
}

main().catch(console.error);
