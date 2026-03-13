/**
 * Video 6: Gallery & Community (~45s)
 *
 * Gallery Page — hero section with Evolution Banner, artwork cards with
 * L1-L5 score bars, Like/Fork social actions, and fork-to-canvas flow.
 *
 * Narration timestamps:
 * [0:00] Every creation lives in the Gallery. And every creation feeds the system.
 * [0:05] The Evolution Banner shows it in real time — sessions, traditions, evolutions.
 * [0:13] Each artwork card displays L1 through L5 score bars.
 * [0:21] Like a piece that resonates.
 * [0:27] See something you want to build on? Fork it. One click carries the intent into Canvas.
 * [0:35] This isn't a static portfolio. It's a living gallery.
 * [0:42] Now let's look under the hood.
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v6-gallery.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
 *   - Backend running on :8001 (optional, falls back to mock data)
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
  waitForImages,
  PAUSE,
  BASE_URL,
} from './video-utils';

async function main() {
  const { browser, context, page } = await launchRecorder('v6-gallery');

  try {
    // ─────────────────────────────────────────────────────
    // 1. Navigate to /gallery, wait for load
    // [0:00] Every creation lives in the Gallery. And every creation feeds the system.
    // ─────────────────────────────────────────────────────
    console.log('[v6] Navigating to /gallery...');
    await page.goto(`${BASE_URL}/gallery`);

    // Wait for the page to render
    await page.waitForSelector('h1', { timeout: 15000 });
    await wait(PAUSE.normal);
    await waitForImages(page);

    // ─────────────────────────────────────────────────────
    // 2. Evolution Banner — hover each statistic
    // [0:05] The Evolution Banner shows it in real time — sessions, traditions, evolutions.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Showing Evolution Banner with cursor guidance...');

      // Brief hold to show the full banner
      await hideCursor(page);
      await wait(PAUSE.read);

      // Show cursor and hover over each stat
      await showCursor(page);

      // The banner typically shows 3 stat counters: sessions, traditions, evolutions
      // Try finding them by text patterns or stat-like elements
      const statTexts = ['session', 'tradition', 'evolution'];
      for (const statText of statTexts) {
        const statEl = page.locator(`text=/${statText}/i`).first();
        if (await statEl.isVisible({ timeout: 2000 }).catch(() => false)) {
          const box = await statEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
            await wait(PAUSE.normal); // 800ms per stat
          }
        }
      }

      // Also try finding numeric stat values (large numbers in the banner)
      // They may be in spans with large font sizes
      const statNumbers = page.locator('h1 + div span, [class*="banner"] span, [class*="stat"] span').all();
      const numbers = await statNumbers;
      if (numbers.length >= 3) {
        for (let i = 0; i < Math.min(numbers.length, 3); i++) {
          const box = await numbers[i].boundingBox();
          if (box && box.y < 400) { // Only in top area (banner)
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 10);
            await wait(PAUSE.normal);
          }
        }
      }

      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[v6] Section 2 (evolution banner) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 3. Smooth scroll down through artwork cards
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Scrolling through artwork cards...');
      await smoothScroll(page, 500, 1200);
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[v6] Section 3 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 4. Hover over artwork cards — point at L1-L5 score bars
    // [0:13] Each artwork card displays L1 through L5 score bars.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Hovering over artwork cards with score bar guidance...');
      await showCursor(page);

      // Find artwork cards
      const cards = page.locator('.ios-card, [class*="IOSCard"], [class*="card"]').filter({
        has: page.locator('h3, h4'),
      });

      const cardCount = await cards.count();
      if (cardCount > 0) {
        // Hover card 1 — center
        const box1 = await cards.nth(0).boundingBox();
        if (box1) {
          await moveTo(page, box1.x + box1.width / 2, box1.y + box1.height / 2, 20);
          await wait(PAUSE.normal);

          // Now try to point at L1-L5 score bars within the card
          const scoreBars = cards.nth(0).locator('[class*="score"], [class*="bar"], [class*="progress"]');
          const barCount = await scoreBars.count();
          if (barCount > 0) {
            for (let i = 0; i < Math.min(barCount, 3); i++) {
              const barBox = await scoreBars.nth(i).boundingBox();
              if (barBox) {
                await moveTo(page, barBox.x + barBox.width / 2, barBox.y + barBox.height / 2, 8);
                await wait(PAUSE.brief);
              }
            }
          }

          await wait(PAUSE.read);
        }

        // Hover card 2
        if (cardCount > 1) {
          const box2 = await cards.nth(1).boundingBox();
          if (box2) {
            await moveTo(page, box2.x + box2.width / 2, box2.y + box2.height / 2, 20);
            await wait(PAUSE.read);
          }
        }

        // Hover card 3
        if (cardCount > 2) {
          const box3 = await cards.nth(2).boundingBox();
          if (box3) {
            await moveTo(page, box3.x + box3.width / 2, box3.y + box3.height / 2, 20);
            await wait(PAUSE.normal);
          }
        }
      }
    } catch (err) {
      console.warn('[v6] Section 4 (card hover) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 5. Click a "Like" button on one card (heart icon)
    // [0:21] Like a piece that resonates.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Clicking Like on first card...');

      const likeButtons = page.locator('button[aria-label="Like this artwork"]');
      if (await likeButtons.count() > 0) {
        await moveToElement(page, 'button[aria-label="Like this artwork"] >> nth=0');
        await wait(PAUSE.brief);
        await clickWith(page, 'button[aria-label="Like this artwork"] >> nth=0');
        await wait(PAUSE.read);
      } else {
        // Fallback: try heart icon buttons
        const heartBtns = page.locator('button:has(svg[class*="heart" i]), button:has(svg path[d*="M12 21"])');
        if (await heartBtns.count() > 0) {
          await clickWith(page, 'button:has(svg[class*="heart" i]), button:has(svg path[d*="M12 21"])');
          await wait(PAUSE.read);
        }
      }
    } catch (err) {
      console.warn('[v6] Section 5 (like) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 6. Click a "Fork" button on another card
    // [0:27] Fork it. One click carries the intent into Canvas.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Clicking Fork on a card...');

      const forkButtons = page.locator('button:has-text("Fork")');
      const forkCount = await forkButtons.count();

      if (forkCount > 1) {
        // Click Fork on the second card (different from the liked card)
        await moveToElement(page, 'button:has-text("Fork") >> nth=1');
        await wait(PAUSE.brief);
        await clickWith(page, 'button:has-text("Fork") >> nth=1');
      } else if (forkCount > 0) {
        await moveToElement(page, 'button:has-text("Fork") >> nth=0');
        await wait(PAUSE.brief);
        await clickWith(page, 'button:has-text("Fork") >> nth=0');
      }

      // Wait for navigation to /canvas
      console.log('[v6] Waiting for navigation to Canvas...');
      try {
        await page.waitForURL('**/canvas**', { timeout: 8000 });
        console.log('[v6] Navigated to Canvas!');
      } catch {
        console.log('[v6] Navigation not detected, continuing...');
        await wait(PAUSE.read);
      }
    } catch (err) {
      console.warn('[v6] Section 6 (fork) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 7. Show Canvas pre-filled state after fork
    // [0:35] This isn't a static portfolio. It's a living gallery.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Showing Canvas with pre-filled fork data...');

      // Wait for Canvas to load with the pre-filled intent
      try {
        await page.waitForSelector('[data-tour-intent], textarea', { timeout: 10000 });
      } catch {
        // Canvas may take a moment to render
      }

      await wait(PAUSE.normal);

      // Show cursor and hover over the IntentBar to show pre-filled subject
      await showCursor(page);

      // Hover the textarea to highlight the pre-filled subject text
      const textarea = page.locator('textarea').first();
      if (await textarea.isVisible({ timeout: 5000 }).catch(() => false)) {
        const taBox = await textarea.boundingBox();
        if (taBox) {
          await moveTo(page, taBox.x + taBox.width / 2, taBox.y + taBox.height / 2, 15);
          await wait(PAUSE.read);
        }
      }

      // Check for tradition selector or other pre-filled fields
      const traditionEl = page.locator('[data-tour-intent] select, [data-tour-intent] [class*="tradition"]').first();
      if (await traditionEl.isVisible({ timeout: 3000 }).catch(() => false)) {
        const tBox = await traditionEl.boundingBox();
        if (tBox) {
          await moveTo(page, tBox.x + tBox.width / 2, tBox.y + tBox.height / 2, 12);
          await wait(PAUSE.normal);
        }
      }

      // Final hold on the pre-filled Canvas
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s hold
    } catch (err) {
      console.warn('[v6] Section 7 (canvas prefill) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 8. Final hold
    // [0:42] Now let's look under the hood.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v6] Final hold...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v6] Section 8 (final) failed, skipping:', err);
    }
  } catch (err) {
    console.error('[v6] Error during recording:', err);
  }

  // ─────────────────────────────────────────────────────
  // Done
  // ─────────────────────────────────────────────────────
  console.log('[v6] Finalizing...');
  await finalize(browser, context, page, 'v6-gallery');
}

main().catch(console.error);
