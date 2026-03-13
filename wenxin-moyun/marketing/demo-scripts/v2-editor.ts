/**
 * VULCA Demo Video 2: Pipeline Editor (~60s)
 *
 * Demonstrates the Canvas Edit Mode with the visual pipeline editor:
 *   Overview of 6 pipeline nodes → Template gallery (11 templates) →
 *   Add Node menu (9 node types) → Add Upload node → Sticky note →
 *   Fit View → Advanced Config (presets, media type, tradition) →
 *   Scroll sidebar settings → Hover "Run" button (next episode hint)
 *
 * Narration timestamps:
 * [0:00] Most AI tools hide their pipeline. VULCA shows you everything.
 * [0:04] This is the Canvas Editor. Six nodes in a visual graph.
 * [0:13] The template gallery gives you eleven starting points.
 * [0:22] The Add Node menu offers nine node types.
 * [0:30] Sticky notes let you annotate. Fit View snaps everything into frame.
 * [0:37] Open Advanced Config — cultural presets with tradition-specific parameters.
 * [0:47] This isn't a black box. It's a visual, editable creation pipeline.
 * [0:55] Next — let's run it.
 *
 * Usage:
 *   npx ts-node marketing/demo-scripts/v2-editor.ts
 *
 * Pre-requisites:
 *   - Frontend running on :5173
 *   - Backend running on :8001 (for API templates)
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
  const { browser, context, page } = await launchRecorder('v2-editor');

  try {
    // ─── 1. Navigate to Canvas ───
    // [0:00] Most AI tools hide their pipeline. VULCA shows you everything.
    await page.goto(`${BASE_URL}/canvas`, { waitUntil: 'networkidle' });

    // Wait for the canvas to load
    await Promise.race([
      page.waitForSelector('.react-flow', { timeout: 15000 }).catch(() => null),
      page.waitForSelector('textarea', { timeout: 15000 }).catch(() => null),
      page.waitForSelector('[data-tour-canvas]', { timeout: 15000 }).catch(() => null),
    ]);
    await wait(PAUSE.section);
    await waitForImages(page);

    // Make sure we're in Edit mode (the default)
    const editBtn = page.locator('button:has-text("Edit")');
    if (await editBtn.count() > 0) {
      await clickWith(page, 'button:has-text("Edit")');
      await wait(PAUSE.normal);
    }

    // ─── 2. Hold on Edit mode overview — 6 pipeline nodes ───
    // [0:04] This is the Canvas Editor. Six nodes in a visual graph.
    try {
      await showCursor(page);

      // Pan across the pipeline nodes in the react-flow canvas
      await moveToElement(page, '[data-tour-canvas]');
      await wait(PAUSE.read);

      // Hover over individual nodes — increased dwell time (800ms per node)
      const nodeLabels = ['Scout', 'Router', 'Draft', 'Critic', 'Queen', 'Archivist'];
      for (const label of nodeLabels) {
        const nodeEl = page.locator(`.react-flow-node:has-text("${label}"), [data-id] >> text="${label}"`).first();
        if (await nodeEl.isVisible().catch(() => false)) {
          const box = await nodeEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 20);
            await wait(PAUSE.normal); // 800ms per node (was 400ms)
          }
        }
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[v2] Section 2 (node overview) failed, skipping:', err);
    }

    // ─── 3. Click template dropdown — show available templates ───
    // [0:13] The template gallery gives you eleven starting points.
    try {
      await hideCursor(page);
      await wait(PAUSE.brief);
      await showCursor(page);

      // Try multiple selectors for the template button
      let templateClicked = false;

      // Strategy 1: button containing the chevron character
      const templateBtn = page.locator('button:has-text("\u25BE")').first();
      if (await templateBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        const box = await templateBtn.boundingBox();
        if (box) {
          await moveTo(page, box.x + box.width / 2, box.y + box.height / 2);
          await wait(200);
          await templateBtn.click({ timeout: 5000 });
          templateClicked = true;
        }
      }

      // Strategy 2: button with span containing chevron
      if (!templateClicked) {
        const templateBtn2 = page.locator('button:has(span:has-text("\u25BE"))').first();
        if (await templateBtn2.isVisible({ timeout: 3000 }).catch(() => false)) {
          const box = await templateBtn2.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2);
            await wait(200);
            await templateBtn2.click({ timeout: 5000 });
            templateClicked = true;
          }
        }
      }

      // Strategy 3: find by toolbar position + template name keywords
      if (!templateClicked) {
        console.log('[v2] Template button not found by chevron, trying evaluate...');
        await page.evaluate(`
          (function() {
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
              var text = btns[i].textContent || '';
              if (text.indexOf('\u25BE') !== -1 || text.indexOf('template') !== -1 || text.indexOf('Template') !== -1) {
                btns[i].click();
                break;
              }
            }
          })()
        `);
      }

      await wait(PAUSE.section);

      // Let the viewer see the template gallery/dropdown (11 templates)
      // Slowly move cursor over some template options
      const templateNames = ['fast_draft', 'critique_only', 'interactive_full'];
      for (const tpl of templateNames) {
        const tplEl = page.locator(`text=${tpl.replace(/_/g, ' ')}`).first();
        if (await tplEl.isVisible().catch(() => false)) {
          await moveToElement(page, `text=${tpl.replace(/_/g, ' ')}`);
          await wait(PAUSE.normal); // 800ms per template (was 400ms)
        }
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[v2] Section 3 (template dropdown) failed, skipping:', err);
    }

    // ─── 4. Close template dropdown, click "+ Node" button ───
    // [0:22] The Add Node menu offers nine node types.
    try {
      await page.keyboard.press('Escape');
      await wait(PAUSE.normal);

      // Click the "+ Node" button to show 9 node types
      await clickWith(page, 'button:has-text("+ Node")');
      await wait(PAUSE.read);

      // Hover over node types in the dropdown — increased dwell time
      const nodeTypes = ['Scout', 'Router', 'Draft', 'Critic', 'Queen', 'Upload', 'Identify', 'Report'];
      for (const nt of nodeTypes) {
        const ntEl = page.locator(`.absolute >> text="${nt}"`).first();
        if (await ntEl.isVisible().catch(() => false)) {
          const box = await ntEl.boundingBox();
          if (box) {
            await moveTo(page, box.x + box.width / 2, box.y + box.height / 2, 12);
            await wait(PAUSE.brief); // 400ms per node type
          }
        }
      }
      await wait(PAUSE.read);
    } catch (err) {
      console.warn('[v2] Section 4 (add node) failed, skipping:', err);
    }

    // ─── 5. Click "Upload" node type to add it to the canvas ───
    try {
      const uploadItem = page.locator('.absolute >> text=Upload').first();
      if (await uploadItem.isVisible().catch(() => false)) {
        await clickWith(page, '.absolute >> text=Upload');
      } else {
        await clickWith(page, 'button:has-text("Upload")');
      }
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v2] Section 5 (add upload) failed, skipping:', err);
    }

    // ─── 6. Click sticky note button — add a note and type text ───
    // [0:30] Sticky notes let you annotate.
    try {
      await clickWith(page, 'button[title="Add sticky note"]');
      await wait(PAUSE.normal);

      // Find the newly added sticky note textarea and type into it
      const stickyTextarea = page.locator('textarea').last();
      if (await stickyTextarea.isVisible().catch(() => false)) {
        await stickyTextarea.click();
        await wait(PAUSE.brief);
        await stickyTextarea.type('Cultural pipeline demo', { delay: 60 });
        await wait(PAUSE.read);
        // Click outside to deselect
        await moveTo(page, 800, 400);
        await page.mouse.click(800, 400);
        await wait(PAUSE.brief);
      }
    } catch (err) {
      console.warn('[v2] Section 6 (sticky note) failed, skipping:', err);
    }

    // ─── 7. Click "Fit View" button — simplified, skip on fail ───
    // [0:30] Fit View snaps everything into frame.
    try {
      const fitSelectors = [
        '.react-flow__controls button[title="fit view"]',
        '.react-flow__controls-fitview',
        'button[aria-label="fit view"]',
      ];
      let clicked = false;
      for (const sel of fitSelectors) {
        const btn = page.locator(sel).first();
        if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
          await moveToElement(page, sel);
          await wait(PAUSE.brief);
          await btn.click({ timeout: 3000 });
          clicked = true;
          break;
        }
      }
      if (!clicked) {
        console.log('[v2] Fit view button not found, skipping...');
      } else {
        await wait(PAUSE.section);
        // Hold on the full canvas view with all nodes visible
        await hideCursor(page);
        await wait(PAUSE.read);
      }
    } catch (err) {
      console.warn('[v2] Section 7 (fit view) failed, skipping:', err);
    }

    // ─── 8. Click "Advanced Config" to expand it ───
    // [0:37] Open Advanced Config — cultural presets with tradition-specific parameters.
    try {
      await showCursor(page);

      await clickWith(page, 'summary:has-text("Advanced Config")');
      await wait(PAUSE.read);

      // Show the cultural presets (scroll the sidebar if needed)
      const presetLabels = ['\u6C34\u58A8\u5C71\u6C34', '\u5DE5\u7B14\u82B1\u9E1F', 'Ukiyo-e Wave', 'Persian Garden'];
      for (const preset of presetLabels) {
        const presetEl = page.locator(`text=${preset}`).first();
        if (await presetEl.isVisible().catch(() => false)) {
          await moveToElement(page, `text=${preset}`);
          await wait(PAUSE.normal); // 800ms per preset (was 400ms)
        }
      }
      await wait(PAUSE.read);

      // Hover over Media Type selector if visible
      const mediaTypeEl = page.locator('text=Media Type').first();
      if (await mediaTypeEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Media Type');
        await wait(PAUSE.read); // increased from normal
      }

      // Hover over Subject field
      const subjectEl = page.locator('text=Subject').first();
      if (await subjectEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Subject');
        await wait(PAUSE.read); // increased from normal
      }

      // Look for "Emerged Concepts" section
      const emergedEl = page.locator('text=Emerged Concepts').first();
      if (await emergedEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Emerged Concepts');
        await wait(PAUSE.read); // increased from normal
      }
    } catch (err) {
      console.warn('[v2] Section 8 (advanced config) failed, skipping:', err);
    }

    // ─── 9. Scroll sidebar down to show Template, Tradition, Provider, Candidates ───
    // [0:47] This isn't a black box. It's a visual, editable creation pipeline.
    try {
      // The sidebar is the left aside with overflow-y-auto
      const sidebar = page.locator('aside.overflow-y-auto').first();
      if (await sidebar.isVisible().catch(() => false)) {
        await sidebar.evaluate(`
          (function(el) { el.scrollBy({ top: 400, behavior: 'smooth' }); })
        `);
        await wait(PAUSE.read);
      }

      // Hover over Tradition selector
      const traditionEl = page.locator('text=Tradition').first();
      if (await traditionEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Tradition');
        await wait(PAUSE.read); // increased from normal
      }

      // Hover over Provider selector
      const providerEl = page.locator('text=Provider').first();
      if (await providerEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Provider');
        await wait(PAUSE.read); // increased from normal
      }

      // Hover over Candidates selector
      const candidatesEl = page.locator('text=Candidates').first();
      if (await candidatesEl.isVisible().catch(() => false)) {
        await moveToElement(page, 'text=Candidates');
        await wait(PAUSE.read); // increased from normal
      }

      // Scroll sidebar a bit more to show any remaining settings
      if (await sidebar.isVisible().catch(() => false)) {
        await sidebar.evaluate(`
          (function(el) { el.scrollBy({ top: 300, behavior: 'smooth' }); })
        `);
        await wait(PAUSE.read);
      }

      // Hold on the complete editor view
      await hideCursor(page);
      await wait(PAUSE.section);
    } catch (err) {
      console.warn('[v2] Section 9 (sidebar scroll) failed, skipping:', err);
    }

    // ─── 10. NEW: Hover "Run" button as next-episode hint ───
    // [0:55] Next — let's run it.
    try {
      console.log('[v2] Hovering Run button as next-episode hint...');
      await showCursor(page);

      // Scroll back up if needed to see the mode buttons
      await page.evaluate('window.scrollTo({ top: 0, behavior: "smooth" })');
      await wait(800);

      // Find the "Run" mode button or the run/create button
      const runBtn = page.locator('button:has-text("Run")').first();
      if (await runBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        const runBox = await runBtn.boundingBox();
        if (runBox) {
          // Move to the Run button slowly — but DO NOT click
          await moveTo(page, runBox.x + runBox.width / 2, runBox.y + runBox.height / 2, 25);
          await wait(PAUSE.hero); // 3s hold on the Run button
        }
      } else {
        // Fallback: just hold on the canvas
        await hideCursor(page);
        await wait(PAUSE.section);
      }
    } catch (err) {
      console.warn('[v2] Section 10 (run hint) failed, skipping:', err);
    }
  } catch (err) {
    console.error('[v2] Error during recording:', err);
  }

  // ─── Finalize ───
  await finalize(browser, context, page, 'v2-editor');
  console.log('v2-editor recording complete.');
}

main().catch(console.error);
