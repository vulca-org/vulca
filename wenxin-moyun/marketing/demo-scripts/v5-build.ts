/**
 * Video 5: Build & Explore (~45s)
 *
 * Canvas Build/Explore Mode — demonstrates the tradition builder (YAML editor),
 * L1-L5 weight sliders, and the interactive explorer with 8 tradition cards
 * + weight comparison radar.
 *
 * Narration timestamps:
 * [0:00] VULCA doesn't hardcode culture. You define it.
 * [0:04] In Build mode, five sliders control the L1 through L5 evaluation weights.
 * [0:15] Switch to Explore. Eight tradition cards appear.
 * [0:24] Expand Chinese Xieyi. You'll see core terms, key techniques, and taboos.
 * [0:33] Select two traditions. A radar chart renders their profiles side by side.
 * [0:40] Culture isn't a label. It's a spectrum.
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v5-build.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
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
  const { browser, context, page } = await launchRecorder('v5-build');

  try {
    // ─────────────────────────────────────────────────────
    // 1. Navigate to Canvas, wait for load
    // [0:00] VULCA doesn't hardcode culture. You define it.
    // ─────────────────────────────────────────────────────
    console.log('[v5] Navigating to /canvas...');
    await page.goto(`${BASE_URL}/canvas`);
    await page.waitForSelector('[data-tour-modes]', { timeout: 15000 });
    await wait(PAUSE.normal);
    await waitForImages(page);

    // ─────────────────────────────────────────────────────
    // 2. Click "Build" mode button
    // [0:04] In Build mode...
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Switching to Build mode...');
      await showCursor(page);
      await clickWith(page, '[data-tour-modes] button:has-text("Build")');
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[v5] Section 2 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 3. Hold to show Build mode: Basic Info + L1-L5 weight sliders
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Showing Build mode — Basic Info + Weights...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v5] Section 3 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 3b. NEW: Hover over L1-L5 weight slider labels
    // [0:04] ...five sliders control the L1 through L5 evaluation weights.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Hovering L1-L5 slider labels...');
      await showCursor(page);

      const sliderLabels = [
        { code: 'L1', name: 'Cultural Authentication' },
        { code: 'L2', name: 'Technical Mastery' },
        { code: 'L3', name: 'Emotional Resonance' },
        { code: 'L4', name: 'Contextual Integrity' },
        { code: 'L5', name: 'Innovation' },
      ];

      for (const sl of sliderLabels) {
        // Try to find by code first, then by name
        let found = false;
        for (const searchText of [sl.code, sl.name]) {
          const el = page.locator(`text=${searchText}`).first();
          if (await el.isVisible({ timeout: 1500 }).catch(() => false)) {
            const box = await el.boundingBox();
            if (box) {
              await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
              await wait(PAUSE.normal); // 800ms per slider label
              found = true;
              break;
            }
          }
        }
        if (!found) {
          console.log(`[v5] Slider label "${sl.code}" not found, skipping...`);
        }
      }

      // Try to drag one slider to demonstrate interaction
      const sliderInput = page.locator('input[type="range"]').first();
      if (await sliderInput.isVisible({ timeout: 3000 }).catch(() => false)) {
        const sliderBox = await sliderInput.boundingBox();
        if (sliderBox) {
          // Move to slider thumb area (center), then drag right
          const startX = sliderBox.x + sliderBox.width * 0.5;
          const endX = sliderBox.x + sliderBox.width * 0.75;
          const y = sliderBox.y + sliderBox.height / 2;
          await moveTo(page, startX, y, 10);
          await wait(PAUSE.brief);
          await page.mouse.down();
          await moveTo(page, endX, y, 15);
          await page.mouse.up();
          await wait(PAUSE.normal);
        }
      }
    } catch (err) {
      console.warn('[v5] Section 3b (slider hover) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 4. Scroll down to YAML preview section
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Clicking Preview YAML...');
      await showCursor(page);
      await clickWith(page, 'button:has-text("Preview YAML")');
      await wait(PAUSE.normal);

      // Scroll the YAML preview into view
      await scrollToElement(page, 'pre');
      await wait(PAUSE.brief);
    } catch (err) {
      console.warn('[v5] Section 4 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 5. Hold on YAML preview
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Holding on YAML preview...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v5] Section 5 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 6. Click "Explore" mode button
    // [0:15] Switch to Explore. Eight tradition cards appear.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Switching to Explore mode...');
      // Scroll back to top to access mode buttons
      await page.evaluate('window.scrollTo({ top: 0, behavior: "smooth" })');
      await wait(800);

      await showCursor(page);
      await clickWith(page, '[data-tour-modes] button:has-text("Explore")');
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[v5] Section 6 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 7. Hold to show 8 tradition cards with L1-L5 weight bars
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Showing 8 tradition cards...');
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s to let viewer read the grid

      // Show cursor and hover over a few tradition card titles
      await showCursor(page);
      const cardTitles = ['Chinese Freehand Ink', 'Japanese', 'Persian', 'Islamic'];
      for (const title of cardTitles) {
        const cardEl = page.locator(`text=${title}`).first();
        if (await cardEl.isVisible({ timeout: 1500 }).catch(() => false)) {
          const box = await cardEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
            await wait(PAUSE.brief);
          }
        }
      }
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[v5] Section 7 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 8. Click on "Chinese Freehand Ink (Xieyi)" card to expand
    // [0:24] Expand Chinese Xieyi. Core terms, key techniques, and taboos.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Expanding Chinese Xieyi card...');
      await showCursor(page);
      await clickWith(page, 'text=Chinese Freehand Ink');
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[v5] Section 8 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 8b. NEW: Scroll within expanded card to show terms + taboos
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Exploring expanded Xieyi card — terms and taboos...');
      await showCursor(page);

      // Look for key terminology sections
      const termLabels = ['Core Terms', 'Terms', 'Taboos', 'Techniques', 'Key Techniques'];
      for (const label of termLabels) {
        const el = page.locator(`text=${label}`).first();
        if (await el.isVisible({ timeout: 2000 }).catch(() => false)) {
          await scrollToElement(page, `text=${label}`);
          const box = await el.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
            await wait(PAUSE.normal);
          }
        }
      }

      // Hover over specific Chinese art terms if visible
      const chineseTerms = ['\u62AB\u9EBB\u7699', '\u6C14\u97F5\u751F\u52A8', '\u7559\u767D'];
      for (const term of chineseTerms) {
        const termEl = page.locator(`text=${term}`).first();
        if (await termEl.isVisible({ timeout: 1000 }).catch(() => false)) {
          const box = await termEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 10);
            await wait(PAUSE.brief);
          }
        }
      }
    } catch (err) {
      console.warn('[v5] Section 8b (terms/taboos) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 9. Hold on expanded card
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Holding on expanded Xieyi card...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v5] Section 9 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 10. Select Chinese Xieyi + Japanese Traditional for radar comparison
    // [0:33] Select two traditions. A radar chart renders their profiles side by side.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Selecting traditions for radar comparison...');
      await showCursor(page);

      // Scroll back to see cards
      await page.evaluate('window.scrollTo({ top: 0, behavior: "smooth" })');
      await wait(800);

      // Click "Compare" button on Chinese Xieyi card (first card)
      const compareButtons = page.locator('button:has-text("Compare")');
      if (await compareButtons.count() > 0) {
        await clickWith(page, 'button:has-text("Compare") >> nth=0');
        await wait(PAUSE.normal);
      }

      // Click "Compare" on Japanese Traditional card
      if (await compareButtons.count() > 0) {
        await clickWith(page, 'button:has-text("Compare") >> nth=0');
        await wait(PAUSE.normal);
      }

      // Scroll to the Weight Comparison section (appears when 2+ selected)
      await scrollToElement(page, 'text=Weight Comparison');
      await wait(PAUSE.brief);
    } catch (err) {
      console.warn('[v5] Section 10 failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 11. Hold on radar chart — increased hold time + cursor guidance
    // [0:40] Culture isn't a label. It's a spectrum.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[v5] Holding on radar chart...');
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s hold

      // Show cursor and point at different radar dimensions
      await showCursor(page);

      // Try to find radar chart SVG points or labels
      const radarLabels = ['L1', 'L2', 'L3', 'L4', 'L5'];
      for (const label of radarLabels) {
        // Radar chart labels within the chart area
        const chartLabel = page.locator(`text=${label}`).last(); // last() to target chart, not form
        if (await chartLabel.isVisible({ timeout: 1000 }).catch(() => false)) {
          const box = await chartLabel.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 10);
            await wait(PAUSE.brief);
          }
        }
      }

      // Final hold on the complete comparison view
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v5] Section 11 failed, skipping:', err);
    }
  } catch (err) {
    console.error('[v5] Error during recording:', err);
  }

  // ─────────────────────────────────────────────────────
  // Done
  // ─────────────────────────────────────────────────────
  console.log('[v5] Finalizing...');
  await finalize(browser, context, page, 'v5-build');
}

main().catch(console.error);
