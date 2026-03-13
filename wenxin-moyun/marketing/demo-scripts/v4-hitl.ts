/**
 * VULCA Demo Video 4: HITL & Advanced (~45s)
 *
 * Shows the Canvas Human-in-the-Loop workflow:
 * - Enable HITL toggle on Canvas
 * - Start Mock pipeline with creative intent
 * - Review Scout evidence panel (hold for reading)
 * - Add cultural terms and approve
 * - Review Draft candidates (hold for reading)
 * - Review Critic L1-L5 scores (hold for reading)
 * - Queen decision panel (ACCEPT/RERUN)
 *
 * Narration timestamps:
 * [0:00] AI creates. You guide. That's Human-in-the-Loop.
 * [0:04] Enable the HITL toggle and type your intent. Start the pipeline.
 * [0:11] Scout presents its cultural evidence. You review — and add your own terms.
 * [0:21] Approve the evidence and Draft generates a candidate. Review the composition.
 * [0:28] Now Critic scores across five layers — L1 through L5.
 * [0:37] Approve the final result. Every decision you made — the system remembers.
 * [0:42] Full automation when you want speed. Full control when it matters.
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v4-hitl.ts
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
  const { browser, context, page } = await launchRecorder('v4-hitl');

  try {
    // ─────────────────────────────────────────────────────
    // 1. Navigate to Canvas, wait for load, click Run mode
    // [0:00] AI creates. You guide. That's Human-in-the-Loop.
    // ─────────────────────────────────────────────────────
    console.log('[V4] Navigating to Canvas...');
    await page.goto(`${BASE_URL}/canvas`, { waitUntil: 'networkidle' });
    await page.waitForSelector('textarea', { timeout: 15000 });
    await wait(PAUSE.section);

    console.log('[V4] Switching to Run mode...');
    await clickWith(page, 'button:has-text("Run")');
    await wait(PAUSE.normal);

    // ─────────────────────────────────────────────────────
    // 2. Enable HITL toggle
    // [0:04] Enable the HITL toggle and type your intent.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Enabling Human-in-the-Loop toggle...');

      // Move cursor to the HITL area for visual effect
      const hitlArea = page.locator('[data-tour-hitl]').first();
      if (await hitlArea.isVisible({ timeout: 5000 }).catch(() => false)) {
        await moveToElement(page, '[data-tour-hitl]');
        await wait(PAUSE.brief);
      } else {
        // Fallback: find label text
        const hitlLabel = page.locator('label:has-text("Human-in-the-Loop")').first();
        if (await hitlLabel.isVisible({ timeout: 3000 }).catch(() => false)) {
          const labelBox = await hitlLabel.boundingBox();
          if (labelBox) {
            await moveTo(page, labelBox.x + labelBox.width / 2, labelBox.y + labelBox.height / 2);
            await wait(PAUSE.brief);
          }
        }
      }

      // Click the toggle using stable selectors
      const toggleClicked = await page.locator('[data-tour-hitl] div[tabindex="0"]').first()
        .click({ timeout: 3000 }).then(() => true).catch(() => false);

      if (!toggleClicked) {
        // Fallback: role="switch"
        const switchClicked = await page.locator('[data-tour-hitl] [role="switch"]').first()
          .click({ timeout: 3000 }).then(() => true).catch(() => false);

        if (!switchClicked) {
          // Last fallback: evaluate
          console.log('[V4] Toggle selectors failed, using evaluate fallback...');
          await page.evaluate(`
            (function() {
              var toggle = document.querySelector('[data-tour-hitl] div[tabindex="0"]')
                || document.querySelector('[data-tour-hitl] [role="switch"]');
              if (toggle) toggle.click();
              else {
                var labels = document.querySelectorAll('label');
                for (var i = 0; i < labels.length; i++) {
                  if (labels[i].textContent && labels[i].textContent.indexOf('Human-in-the-Loop') !== -1) {
                    var gp = labels[i].parentElement && labels[i].parentElement.parentElement;
                    var t = gp && gp.querySelector('div[tabindex="0"]');
                    if (t) t.click();
                    break;
                  }
                }
              }
            })()
          `);
        }
      }

      await wait(PAUSE.normal);
      console.log('[V4] HITL toggle enabled.');
    } catch (err) {
      console.warn('[V4] Section 2 (HITL toggle) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 3. Type creative intent
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Typing creative intent...');
      await typeText(
        page,
        'textarea',
        'Ancient temple courtyard with pine trees in ink wash style',
        50,
      );
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[V4] Section 3 (type intent) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 4. Click "Create" button to start Mock pipeline
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Starting Mock pipeline...');
      await clickWith(page, 'button:has-text("Create"), button:has-text("Run Pipeline")');
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[V4] Section 4 (start pipeline) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 5. Wait for HITL modal to appear ("Human Input Required")
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Waiting for Scout HITL modal...');
      try {
        await page.waitForSelector('text=/Human Input Required|human.input/i', { timeout: 15000 });
        console.log('[V4] HITL modal appeared!');
      } catch {
        console.log('[V4] HITL modal not found by text, trying alternative...');
        await page.waitForSelector('[class*="modal"], [class*="Modal"], [role="dialog"]', { timeout: 8000 }).catch(() => {});
      }
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[V4] Section 5 (wait scout modal) failed, continuing:', err);
    }

    // ─────────────────────────────────────────────────────
    // 6. Show Scout review panel — hold longer for reading
    // [0:11] Scout presents its cultural evidence. You review.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Showing Scout review panel...');
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s hold for reading evidence
      await showCursor(page);

      // Hover over evidence items if visible
      const evidenceItems = page.locator('[class*="evidence"], [class*="Evidence"], li');
      const evidenceCount = await evidenceItems.count();
      if (evidenceCount > 0) {
        for (let i = 0; i < Math.min(evidenceCount, 3); i++) {
          const box = await evidenceItems.nth(i).boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
            await wait(PAUSE.normal);
          }
        }
      }
    } catch (err) {
      console.warn('[V4] Section 6 (scout panel) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 7. Fill "Add Terms" input with cultural terms
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Adding cultural terms...');
      const termsInput = page.locator('input[placeholder*="term" i], input[placeholder*="Term" i], input[placeholder*="add" i]').first();
      if (await termsInput.isVisible({ timeout: 5000 }).catch(() => false)) {
        await typeText(
          page,
          'input[placeholder*="term" i], input[placeholder*="Term" i], input[placeholder*="add" i]',
          '\u7559\u767D, \u58A8\u5206\u4E94\u8272, \u6C14\u97F5\u751F\u52A8',
          50,
        );
      } else {
        // Fallback: try any visible input inside the modal
        console.log('[V4] Terms input not found by placeholder, trying fallback...');
        const modalInput = page.locator('[class*="modal"] input, [class*="Modal"] input, [role="dialog"] input').first();
        if (await modalInput.isVisible({ timeout: 3000 }).catch(() => false)) {
          const inputBox = await modalInput.boundingBox();
          if (inputBox) {
            await moveTo(page, inputBox.x + inputBox.width / 2, inputBox.y + inputBox.height / 2);
            await wait(PAUSE.brief);
            await modalInput.click();
            await modalInput.type('\u7559\u767D, \u58A8\u5206\u4E94\u8272, \u6C14\u97F5\u751F\u52A8', { delay: 50 });
          }
        }
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[V4] Section 7 (add terms) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 8. Click "Approve Evidence"
    // [0:21] Approve the evidence.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Approving Scout evidence...');
      const approveBtn = page.locator('button:has-text("Approve")').first();
      if (await approveBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
        await moveToElement(page, 'button:has-text("Approve")');
        await wait(PAUSE.brief);
        await approveBtn.click({ timeout: 5000 });
      } else {
        console.log('[V4] Approve button not visible, clicking via evaluate...');
        await page.evaluate(`
          (function() {
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
              if (btns[i].textContent && btns[i].textContent.indexOf('Approve') !== -1) {
                btns[i].click(); break;
              }
            }
          })()
        `);
      }
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V4] Section 8 (approve scout) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 9. Wait for Draft HITL, hold longer for candidate review
    // [0:21] Draft generates a candidate. Review the composition.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Waiting for Draft HITL modal...');
      try {
        await page.waitForSelector('text=/Human Input Required|Draft|candidate/i', { timeout: 15000 });
        console.log('[V4] Draft HITL appeared!');
      } catch {
        console.log('[V4] Draft HITL not detected by text, waiting...');
        await wait(3000);
      }

      await waitForImages(page);
      console.log('[V4] Showing Draft candidate selection...');
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s hold for reading draft
      await showCursor(page);

      // Hover over candidate images if visible
      const candidateImgs = page.locator('img[alt*="candidate" i], img[alt*="draft" i], [class*="candidate"] img').first();
      if (await candidateImgs.isVisible({ timeout: 3000 }).catch(() => false)) {
        const imgBox = await candidateImgs.boundingBox();
        if (imgBox) {
          await moveTo(page, imgBox.x + imgBox.width / 2, imgBox.y + imgBox.height / 2, 15);
          await wait(PAUSE.read);
        }
      }
    } catch (err) {
      console.warn('[V4] Section 9 (draft modal) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 10. Click "Proceed to Critic"
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Clicking "Proceed to Critic"...');
      const proceedBtn = page.locator('button:has-text("Proceed")').first();
      if (await proceedBtn.isVisible({ timeout: 8000 }).catch(() => false)) {
        await scrollToElement(page, 'button:has-text("Proceed")');
        await moveToElement(page, 'button:has-text("Proceed")');
        await wait(PAUSE.brief);
        await proceedBtn.click({ timeout: 5000 });
      } else {
        // Fallback via evaluate
        await page.evaluate(`
          (function() {
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
              if (btns[i].textContent && btns[i].textContent.indexOf('Proceed') !== -1) {
                btns[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(function() { btns[i].click(); }, 500);
                break;
              }
            }
          })()
        `);
        await wait(1000);
      }
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V4] Section 10 (proceed to critic) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 11. Wait for Critic HITL, hold longer for L1-L5 scores
    // [0:28] Now Critic scores across five layers — L1 through L5.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Waiting for Critic HITL modal...');
      try {
        await page.waitForSelector('text=/Human Input Required|Critic|L1|Score/i', { timeout: 15000 });
        console.log('[V4] Critic HITL appeared!');
      } catch {
        console.log('[V4] Critic HITL not detected by text, waiting...');
        await wait(3000);
      }

      console.log('[V4] Showing Critic L1-L5 score bars...');
      await hideCursor(page);
      await wait(PAUSE.hero); // 3s hold for reading scores
      await showCursor(page);

      // Hover over L1-L5 score labels if visible
      const scoreLabels = ['L1', 'L2', 'L3', 'L4', 'L5'];
      for (const label of scoreLabels) {
        const labelEl = page.locator(`text=${label}`).first();
        if (await labelEl.isVisible({ timeout: 1000 }).catch(() => false)) {
          const box = await labelEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 10);
            await wait(PAUSE.brief);
          }
        }
      }
      await wait(PAUSE.normal);
    } catch (err) {
      console.warn('[V4] Section 11 (critic scores) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 12. Click "Approve Scores"
    // [0:37] Approve the final result.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Approving Critic scores...');
      const approveScoresBtn = page.locator('button:has-text("Approve")').first();
      if (await approveScoresBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
        await moveToElement(page, 'button:has-text("Approve")');
        await wait(PAUSE.brief);
        await approveScoresBtn.click({ timeout: 5000 });
      } else {
        console.log('[V4] Approve Scores button not visible, clicking via evaluate...');
        await page.evaluate(`
          (function() {
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
              if (btns[i].textContent && btns[i].textContent.indexOf('Approve') !== -1) {
                btns[i].click(); break;
              }
            }
          })()
        `);
      }
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V4] Section 12 (approve critic) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 13. Wait for Queen decision panel — NEW
    // [0:37] Every decision you made — the system remembers.
    // Queen shows ACCEPT/RERUN decision
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Waiting for Queen decision panel...');

      // Wait for Queen stage indicator or decision text
      let queenFound = false;
      try {
        await page.waitForSelector('text=/Queen|ACCEPT|RERUN|Final Decision/i', { timeout: 15000 });
        queenFound = true;
        console.log('[V4] Queen decision panel appeared!');
      } catch {
        console.log('[V4] Queen text not detected, trying decision icon selectors...');
        // Try finding the bold uppercase decision text
        try {
          await page.waitForSelector('span.text-lg.font-bold.uppercase', { timeout: 5000 });
          queenFound = true;
        } catch {
          console.log('[V4] Queen decision panel not found, continuing...');
        }
      }

      if (queenFound) {
        // Hold on Queen decision display
        await hideCursor(page);
        await wait(PAUSE.section); // 2.5s hold

        // Hover over the decision text (ACCEPT/RERUN)
        await showCursor(page);
        const decisionText = page.locator('span.text-lg.font-bold.uppercase').first();
        if (await decisionText.isVisible({ timeout: 3000 }).catch(() => false)) {
          const dBox = await decisionText.boundingBox();
          if (dBox) {
            await moveTo(page, dBox.x + dBox.width / 2, dBox.y + dBox.height / 2, 12);
            await wait(PAUSE.read);
          }
        }

        // If HITL is enabled, Queen may also pause for approval
        const queenApproveBtn = page.locator('button:has-text("Approve"), button:has-text("Accept")').first();
        if (await queenApproveBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
          console.log('[V4] Queen approval button found, clicking...');
          await moveToElement(page, 'button:has-text("Approve"), button:has-text("Accept")');
          await wait(PAUSE.brief);
          await queenApproveBtn.click({ timeout: 5000 });
          await wait(PAUSE.section);
        } else {
          // No button — Queen auto-decided, just hold
          await wait(PAUSE.read);
        }
      }
    } catch (err) {
      console.warn('[V4] Section 13 (Queen decision) failed, skipping:', err);
    }

    // ─────────────────────────────────────────────────────
    // 14. Final hold — show completed pipeline
    // [0:42] Full automation when you want speed. Full control when it matters.
    // ─────────────────────────────────────────────────────
    try {
      console.log('[V4] Final hold on completed pipeline...');
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[V4] Section 14 (final hold) failed, skipping:', err);
    }

    console.log('[V4] Recording complete!');
  } catch (err) {
    console.error('[V4] Error during recording:', err);
  }

  // ─────────────────────────────────────────────────────
  // Finalize: close browser, save video
  // ─────────────────────────────────────────────────────
  await finalize(browser, context, page, 'v4-hitl');
}

main().catch(console.error);
