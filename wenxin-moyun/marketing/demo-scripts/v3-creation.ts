/**
 * VULCA Demo Video 3: Creation Flow (~60s)
 *
 * Shows the complete creation journey — from intent to pipeline execution to results:
 *   [0:00]  Switch to Run mode
 *   [0:05]  Open Run History → L1-L5 scores in IOSSheet
 *   [0:16]  Type creative intent → tradition auto-detect
 *   [0:22]  Show tradition badge
 *   [0:32]  Hover Provider switch (Mock vs NB2)
 *   [0:40]  Click Create → pipeline starts (Scout→Draft→Critic→Queen)
 *   [0:49]  Watch pipeline execute, candidates appear, scores populate
 *   [0:55]  Hold on final results
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v3-creation.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
 *   - Backend running on :8001
 */

import {
  launchRecorder,
  finalize,
  wait,
  moveTo,
  clickWith,
  typeText,
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
  const { browser, context, page } = await launchRecorder('v3-creation');

  try {
    // ─────────────────────────────────────────────────────
    // 1. [0:00-0:05] Navigate to Canvas → Switch to Run mode
    //    "Creation starts with intent. Switch to Run mode —
    //     the canvas transforms."
    // ─────────────────────────────────────────────────────
    console.log('[V3] Navigating to Canvas...');
    await page.goto(`${BASE_URL}/canvas`, { waitUntil: 'networkidle' });
    await page.waitForSelector('textarea', { timeout: 15000 });
    await wait(PAUSE.normal);
    await waitForImages(page);

    try {
      console.log('[V3] Switching to Run mode...');
      const runBtn = page.locator('[data-tour-modes] button').filter({ hasText: 'Run' });
      if (await runBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await clickWith(page, '[data-tour-modes] button:has-text("Run")');
      } else {
        // Fallback: try generic button
        await clickWith(page, 'button:has-text("Run")');
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[V3] Section 1 (Run mode) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 2. [0:05-0:16] Open Run History item → Show IOSSheet with L1-L5 scores
    //    "Before we begin, let's look at history. Open a previous
    //     run and you'll see L1 through L5 scores."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Opening Run History detail...');
      // Run History items are <li> > <button> inside the RunHistoryPanel
      // Each item is: button.w-full.flex with tradition color block + subject text
      const historyButtons = page.locator('ul.space-y-1 li button.w-full');
      const firstHistory = historyButtons.first();

      if (await firstHistory.isVisible({ timeout: 4000 }).catch(() => false)) {
        // Move cursor to the first history item and click
        const box = await firstHistory.boundingBox();
        if (box) {
          await moveTo(page, box.x + box.width / 2, box.y + box.height / 2);
          await wait(PAUSE.brief);
          await firstHistory.click();
          await wait(PAUSE.normal);
        }

        // Wait for the IOSSheet to appear (it renders via portal into document.body)
        console.log('[V3] Waiting for detail sheet...');
        try {
          // The sheet has "Dimension Scores" heading and L1-L5 labels
          await page.waitForSelector('text=Dimension Scores', { timeout: 4000 });
          console.log('[V3] Detail sheet visible with L1-L5 scores');
        } catch {
          console.log('[V3] Sheet text not found, checking for Overall score...');
          try {
            await page.waitForSelector('text=Overall', { timeout: 2000 });
          } catch {
            console.log('[V3] Sheet content not detected, continuing...');
          }
        }

        // Hold to let viewer read the L1-L5 scores
        await wait(PAUSE.hero);

        // Scroll down inside the sheet to show more scores if needed
        const sheetContent = page.locator('.overflow-y-auto.px-4').first();
        if (await sheetContent.isVisible({ timeout: 1000 }).catch(() => false)) {
          const sheetBox = await sheetContent.boundingBox();
          if (sheetBox) {
            await moveTo(page, sheetBox.x + sheetBox.width / 2, sheetBox.y + sheetBox.height / 2);
            await page.mouse.wheel(0, 150);
            await wait(PAUSE.read);
          }
        }

        // Close the sheet by pressing Escape
        console.log('[V3] Closing detail sheet...');
        await page.keyboard.press('Escape');
        await wait(PAUSE.normal);
      } else {
        console.log('[V3] No history items found, skipping...');
        await wait(PAUSE.normal);
      }
    } catch (err) {
      console.warn('[V3] Section 2 (Run History) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 3. [0:16-0:22] Type creative intent
    //    "Now, type your intent. 'Lotus pond with morning mist
    //     in traditional ink wash style.'"
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Typing creative intent...');
      // Clear any existing text first
      const textarea = page.locator('textarea').first();
      await textarea.click();
      await wait(200);
      await textarea.fill('');
      await wait(200);

      await typeText(
        page,
        'textarea',
        'Lotus pond with morning mist in traditional ink wash style',
        45,
      );
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[V3] Section 3 (type intent) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 4. [0:22-0:32] Show tradition auto-detect badge
    //    "Watch what happens. VULCA auto-detects the tradition —
    //     Chinese Ink Wash."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Waiting for tradition auto-detect...');
      // The tradition indicator is inside [data-tour-tradition]
      // It shows: "Tradition: chinese xieyi" (with the tradition name in #C87F4A)
      const traditionContainer = page.locator('[data-tour-tradition]');

      try {
        // Wait for the tradition text to appear (case-insensitive match)
        await page.waitForSelector('[data-tour-tradition] span.font-medium', { timeout: 6000 });
        console.log('[V3] Tradition detected!');
      } catch {
        console.log('[V3] Tradition label slow to appear, continuing...');
      }

      // Move cursor to highlight the tradition badge
      if (await traditionContainer.isVisible({ timeout: 2000 }).catch(() => false)) {
        await moveToElement(page, '[data-tour-tradition]');
        await wait(PAUSE.brief);
      }

      // Check for the classifying spinner (spinning border element)
      try {
        await page.waitForSelector('[data-tour-tradition] .animate-spin', { timeout: 2000, state: 'hidden' });
      } catch {
        // Spinner may have already disappeared
      }

      // Hold on the tradition result
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V3] Section 4 (tradition detect) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 5. [0:32-0:40] Hover over Provider switch
    //    "Choose your provider. Mock mode for fast iteration.
    //     NB2 for production-quality."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Hovering over provider switch...');
      // ProviderQuickSwitch uses IOSSegmentedControl with Mock/NB2 segments
      // The segments are rendered inside a container with class "px-1 space-y-1.5"
      const mockSegment = page.locator('button:has-text("Mock"), [class*="segment"]:has-text("Mock")').first();
      const nb2Segment = page.locator('button:has-text("NB2"), [class*="segment"]:has-text("NB2")').first();

      if (await mockSegment.isVisible({ timeout: 3000 }).catch(() => false)) {
        // Hover Mock
        await moveToElement(page, 'button:has-text("Mock")');
        await wait(PAUSE.normal);

        // Hover NB2
        if (await nb2Segment.isVisible({ timeout: 2000 }).catch(() => false)) {
          await moveToElement(page, 'button:has-text("NB2")');
          await wait(PAUSE.normal);
        }

        // Move back to Mock (we stay on Mock for fast demo)
        await moveToElement(page, 'button:has-text("Mock")');
        await wait(PAUSE.brief);
      } else {
        console.log('[V3] Provider switch not found, skipping hover...');
      }

      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[V3] Section 5 (provider switch) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 6. [0:40-0:42] Click "Create" button → Pipeline starts
    //    "One intent. One click. The pipeline takes over —
    //     Scout, Draft, Critic, Queen."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Clicking Create to start pipeline...');
      // The Create button is inside IntentBar — IOSButton with text "Create"
      // It might also say "Run Pipeline" depending on mode
      const createBtn = page.locator('button:has-text("Create")').first();
      const runPipelineBtn = page.locator('button:has-text("Run Pipeline")').first();

      if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await clickWith(page, 'button:has-text("Create")');
      } else if (await runPipelineBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await clickWith(page, 'button:has-text("Run Pipeline")');
      } else {
        console.warn('[V3] Neither Create nor Run Pipeline button found');
      }

      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[V3] Section 6 (click Create) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 7. [0:42-0:55] Watch pipeline execution
    //    Scout → Draft → Critic → Queen
    //    "You described what you wanted. VULCA handled the rest."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Watching pipeline execution...');

      // --- 7a. Wait for Scout stage to appear ---
      try {
        console.log('[V3]   Waiting for Scout...');
        // PipelineProgress shows stage circles; Scout is the first
        // Look for the Progress card to appear (indicates pipeline started)
        await page.waitForSelector('text=Progress', { timeout: 8000 });
        await wait(PAUSE.brief);

        // Scout analyzing indicator: pulsing circle with magnifying glass emoji
        try {
          await page.waitForSelector('text=Scout analyzing', { timeout: 3000 });
        } catch {
          // May have already passed Scout
        }

        // Move cursor to the progress area to draw attention
        const progressCard = page.locator('text=Progress').first();
        if (await progressCard.isVisible({ timeout: 1000 }).catch(() => false)) {
          await moveToElement(page, 'text=Progress');
        }
        await wait(PAUSE.read);
      } catch {
        console.log('[V3]   Scout stage not detected, continuing...');
      }

      // --- 7b. Wait for Scout completion (checkmark on first stage) ---
      try {
        console.log('[V3]   Waiting for Scout completion...');
        // Completed stages get bg-[#5F8A50] and show checkmark
        // Wait for the first stage circle to show checkmark text
        await page.waitForSelector('.bg-\\[\\#5F8A50\\]', { timeout: 10000 });
        console.log('[V3]   Scout completed (green checkmark visible)');
        await wait(PAUSE.normal);
      } catch {
        console.log('[V3]   Scout completion indicator not found, continuing...');
        await wait(PAUSE.read);
      }

      // --- 7c. Wait for Draft candidates to appear ---
      try {
        console.log('[V3]   Waiting for Draft candidates...');
        // CandidateGallery shows images in a grid
        // Look for "Candidates" heading or actual image elements
        await page.waitForSelector('text=Candidates', { timeout: 12000 });
        console.log('[V3]   Candidates section appeared');

        // Wait a moment for images to start loading
        await wait(PAUSE.normal);

        // Try to wait for actual candidate images
        try {
          await page.waitForSelector('img.w-full.h-full.object-cover, .aspect-square img', { timeout: 8000 });
          console.log('[V3]   Candidate images loaded');
          await waitForImages(page);
        } catch {
          console.log('[V3]   No candidate images found (mock mode may use emoji placeholders)');
        }

        // Move cursor across the candidate gallery to show the images
        const candidateGrid = page.locator('.grid.grid-cols-2').first();
        if (await candidateGrid.isVisible({ timeout: 2000 }).catch(() => false)) {
          const gridBox = await candidateGrid.boundingBox();
          if (gridBox) {
            // Hover over first candidate
            await moveTo(page, gridBox.x + gridBox.width * 0.25, gridBox.y + gridBox.height * 0.25);
            await wait(PAUSE.brief);
            // Hover over second candidate
            await moveTo(page, gridBox.x + gridBox.width * 0.75, gridBox.y + gridBox.height * 0.25);
            await wait(PAUSE.brief);
          }
        }

        await wait(PAUSE.read);
      } catch {
        console.log('[V3]   Candidates section not found, continuing...');
        await wait(PAUSE.read);
      }

      // --- 7d. Wait for Critic scores to appear ---
      try {
        console.log('[V3]   Waiting for Critic scores...');
        // CriticScoreTable shows "Critic L1-L5" heading
        await page.waitForSelector('text=Critic L1-L5', { timeout: 12000 });
        console.log('[V3]   Critic scores visible');

        // Scroll to make the score table visible if needed
        const criticHeader = page.locator('text=Critic L1-L5').first();
        if (await criticHeader.isVisible({ timeout: 1000 }).catch(() => false)) {
          await criticHeader.scrollIntoViewIfNeeded();
          await wait(PAUSE.brief);
          await moveToElement(page, 'text=Critic L1-L5');
        }

        // Wait for score bars to render
        try {
          await page.waitForSelector('.bg-\\[\\#5F8A50\\].rounded-full, .bg-yellow-500.rounded-full, .bg-red-500.rounded-full', { timeout: 5000 });
          console.log('[V3]   Score bars rendered');
        } catch {
          console.log('[V3]   Score bar selectors not matched');
        }

        // Hold to let viewer read the L1-L5 scores
        await wait(PAUSE.section);
      } catch {
        console.log('[V3]   Critic scores not found, continuing...');
        await wait(PAUSE.read);
      }

      // --- 7e. Wait for pipeline completion (Done badge or FinalResultPanel) ---
      try {
        console.log('[V3]   Waiting for pipeline completion...');
        // The "Done" badge appears when status === 'completed'
        // Or FinalResultPanel shows with the winning candidate
        await page.waitForSelector('text=Done, text=Pipeline Complete', { timeout: 15000 });
        console.log('[V3]   Pipeline completed!');
        await wait(PAUSE.normal);
      } catch {
        console.log('[V3]   Done badge not found, pipeline may still be running...');
        // Give extra time for slow pipelines
        await wait(PAUSE.section);
      }
    } catch (err) {
      console.warn('[V3] Section 7 (pipeline execution) error:', err);
    }

    // ─────────────────────────────────────────────────────
    // 8. [0:50-0:55] Hold on final results
    //    Show candidates + L1-L5 scores + final decision
    //    "That's where Human-in-the-Loop comes in."
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Holding on final results...');

      // Scroll to show the FinalResultPanel if it exists
      const finalPanel = page.locator('text=Final Result, text=Pipeline Complete').first();
      if (await finalPanel.isVisible({ timeout: 3000 }).catch(() => false)) {
        await finalPanel.scrollIntoViewIfNeeded();
        await wait(PAUSE.brief);
      }

      // Look for the best candidate image
      const bestBadge = page.locator('text=Best').first();
      if (await bestBadge.isVisible({ timeout: 2000 }).catch(() => false)) {
        await moveToElement(page, 'text=Best');
        await wait(PAUSE.read);
      }

      // Look for PASS/FAIL gate badges
      const passBadge = page.locator('text=PASS').first();
      if (await passBadge.isVisible({ timeout: 2000 }).catch(() => false)) {
        await moveToElement(page, 'text=PASS');
        await wait(PAUSE.normal);
      }

      // Scroll back up to show the full picture: candidates + scores
      await page.evaluate('window.scrollTo({ top: 0, behavior: "smooth" })');
      await wait(PAUSE.read);

      // Final panoramic hold
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V3] Section 8 (final results) skipped:', err);
    }

    // ─────────────────────────────────────────────────────
    // 9. [0:55-0:60] Final hold with cursor hidden
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V3] Final hold...');
      await hideCursor(page);
      await wait(PAUSE.hero);
      await showCursor(page);
    } catch (err) {
      console.warn('[V3] Section 9 (final hold) skipped:', err);
    }

    console.log('[V3] Recording complete!');
  } catch (err) {
    console.error('[V3] Fatal error during recording:', err);
  }

  // ─────────────────────────────────────────────────────
  // Finalize: close browser, save video
  // ─────────────────────────────────────────────────────
  await finalize(browser, context, page, 'v3-creation');
}

main().catch(console.error);
