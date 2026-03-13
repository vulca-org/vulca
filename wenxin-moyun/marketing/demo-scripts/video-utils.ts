/**
 * Shared utilities for VULCA 2K video recording scripts.
 *
 * Features:
 * - 2560×1440 viewport with recordVideo
 * - Visible cursor overlay (works in headed & headless)
 * - Smooth scroll, hover, and click helpers
 * - Consistent timing for professional-looking videos
 */

import { chromium, type Browser, type BrowserContext, type Page } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const WIDTH = 2560;
export const HEIGHT = 1440;
export const BASE_URL = 'http://localhost:5173';
export const API_URL = 'http://localhost:8001';
export const EXPORT_DIR = path.join(__dirname, '..', 'exports', 'videos');

// Timing constants (ms)
export const PAUSE = {
  brief: 400,       // After small UI change
  normal: 800,      // After navigation/click
  read: 1500,       // Let viewer read content
  section: 2500,    // Between major sections
  hero: 3000,       // Hold on hero/important content
};

/** Wait helper */
export const wait = (ms: number) => new Promise(r => setTimeout(r, ms));

/** Launch browser with video recording */
export async function launchRecorder(videoName: string): Promise<{
  browser: Browser;
  context: BrowserContext;
  page: Page;
}> {
  const videoDir = path.join(EXPORT_DIR, videoName);
  if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });

  const browser = await chromium.launch({
    headless: false,
    args: [
      `--window-size=${WIDTH},${HEIGHT}`,
      '--disable-extensions',
      '--disable-default-apps',
    ],
  });

  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    recordVideo: {
      dir: videoDir,
      size: { width: WIDTH, height: HEIGHT },
    },
    colorScheme: 'light',
  });

  const page = await context.newPage();

  // Skip onboarding tour overlay on Canvas pages
  await page.addInitScript(() => {
    localStorage.setItem('vulca_tour_seen', 'true');
  });

  // Hide browser performance overlays and watermarks
  await page.addStyleTag({ content: `
    [class*="performance"], [class*="fps-counter"],
    .performance-overlay, #performance-overlay,
    [class*="devtools"], [class*="browser-overlay"],
    div[style*="position: fixed"][style*="z-index: 2147483647"]:not(#pw-cursor):not(#pw-cursor-ripple) {
      display: none !important;
      visibility: hidden !important;
      opacity: 0 !important;
    }
  ` });

  // Inject visible cursor overlay
  page.on('framenavigated', async () => {
    try { await injectCursor(page); } catch { /* expected */ }
  });

  return { browser, context, page };
}

/** Inject a warm copper cursor dot overlay */
async function injectCursor(page: Page) {
  await page.evaluate(() => {
    if (document.getElementById('pw-cursor')) return;
    const cursor = document.createElement('div');
    cursor.id = 'pw-cursor';
    cursor.style.cssText = `
      position: fixed; z-index: 2147483647; pointer-events: none;
      width: 24px; height: 24px; border-radius: 50%;
      background: radial-gradient(circle, rgba(200,127,74,0.7) 0%, rgba(200,127,74,0.3) 60%, transparent 70%);
      border: 2.5px solid rgba(200,127,74,0.85);
      transform: translate(-50%, -50%);
      transition: left 0.12s cubic-bezier(.4,0,.2,1), top 0.12s cubic-bezier(.4,0,.2,1), opacity 0.2s;
      left: -100px; top: -100px;
      box-shadow: 0 0 8px rgba(200,127,74,0.3);
    `;
    document.body.appendChild(cursor);

    // Click ripple effect
    const ripple = document.createElement('div');
    ripple.id = 'pw-cursor-ripple';
    ripple.style.cssText = `
      position: fixed; z-index: 2147483646; pointer-events: none;
      width: 40px; height: 40px; border-radius: 50%;
      border: 2px solid rgba(200,127,74,0.5);
      transform: translate(-50%, -50%) scale(0);
      left: -100px; top: -100px;
      opacity: 0; transition: none;
    `;
    document.body.appendChild(ripple);
  });
}

/** Move cursor smoothly to coordinates */
export async function moveTo(page: Page, x: number, y: number, steps = 15) {
  await page.mouse.move(x, y, { steps });
  await page.evaluate(([cx, cy]) => {
    const cursor = document.getElementById('pw-cursor');
    if (cursor) { cursor.style.left = cx + 'px'; cursor.style.top = cy + 'px'; }
  }, [x, y]);
  await wait(100);
}

/** Move cursor to element center */
export async function moveToElement(page: Page, selector: string) {
  const el = await page.locator(selector).first().boundingBox();
  if (el) {
    await moveTo(page, el.x + el.width / 2, el.y + el.height / 2);
  }
}

/** Click with cursor movement + ripple animation */
export async function clickWith(page: Page, selector: string, opts?: { delay?: number }) {
  const el = await page.locator(selector).first().boundingBox();
  if (!el) return;
  const x = el.x + el.width / 2;
  const y = el.y + el.height / 2;

  await moveTo(page, x, y);
  await wait(opts?.delay ?? 200);

  // Trigger ripple
  await page.evaluate(([rx, ry]) => {
    const ripple = document.getElementById('pw-cursor-ripple');
    if (ripple) {
      ripple.style.transition = 'none';
      ripple.style.left = rx + 'px';
      ripple.style.top = ry + 'px';
      ripple.style.opacity = '1';
      ripple.style.transform = 'translate(-50%, -50%) scale(0)';
      void ripple.offsetHeight; // force reflow
      ripple.style.transition = 'transform 0.4s ease-out, opacity 0.4s ease-out';
      ripple.style.transform = 'translate(-50%, -50%) scale(1)';
      ripple.style.opacity = '0';
    }
  }, [x, y]);

  await page.locator(selector).first().click();
  await wait(300);
}

/** Type text character by character with cursor visible */
export async function typeText(page: Page, selector: string, text: string, delay = 50) {
  await moveToElement(page, selector);
  await wait(200);
  await page.locator(selector).first().click();
  await wait(200);
  await page.locator(selector).first().type(text, { delay });
}

/** Smooth scroll down by pixels */
export async function smoothScroll(page: Page, pixels: number, duration = 800) {
  const startY: number = await page.evaluate('window.scrollY');
  const steps = 20;
  const stepDelay = Math.floor(duration / steps);
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    const target = Math.round(startY + pixels * ease);
    await page.evaluate(`window.scrollTo(0, ${target})`);
    await wait(stepDelay);
  }
}

/** Scroll to element with smooth animation — uses Playwright locator (supports text= selectors) */
export async function scrollToElement(page: Page, selector: string, block: ScrollLogicalPosition = 'center') {
  const el = page.locator(selector).first();
  if (await el.isVisible({ timeout: 3000 }).catch(() => false)) {
    await el.scrollIntoViewIfNeeded();
  }
  await wait(1000);
}

/** Admin login via API */
export async function adminLogin(page: Page) {
  await page.evaluate(async (apiUrl: string) => {
    const params = new URLSearchParams();
    params.append('username', 'admin');
    params.append('password', 'admin123');
    const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      body: params,
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access_token', data.access_token);
    }
  }, API_URL);
}

/** Finalize recording: close browser, rename video, convert to mp4 */
export async function finalize(
  browser: Browser,
  context: BrowserContext,
  page: Page,
  videoName: string,
) {
  const videoDir = path.join(EXPORT_DIR, videoName);

  // Close page to flush video
  const videoPath = await page.video()?.path();
  await page.close();
  await context.close();
  await browser.close();

  if (videoPath && fs.existsSync(videoPath)) {
    const dest = path.join(EXPORT_DIR, `${videoName}.webm`);
    fs.renameSync(videoPath, dest);
    console.log(`\nVideo saved: ${dest}`);
    console.log(`Resolution: ${WIDTH}x${HEIGHT} (2K)`);
    console.log(`\nTo convert to MP4:`);
    console.log(`  ffmpeg -i "${dest}" -c:v libx264 -crf 18 -preset slow -c:a aac "${dest.replace('.webm', '.mp4')}"`);
    return dest;
  }

  // Fallback: find any webm in the dir
  const webms = fs.readdirSync(videoDir).filter(f => f.endsWith('.webm'));
  if (webms.length > 0) {
    const src = path.join(videoDir, webms[webms.length - 1]);
    const dest = path.join(EXPORT_DIR, `${videoName}.webm`);
    fs.renameSync(src, dest);
    console.log(`\nVideo saved: ${dest}`);
    return dest;
  }

  console.log('Warning: no video file found');
  return null;
}

/** Hide cursor (move off-screen) */
export async function hideCursor(page: Page) {
  await page.evaluate(() => {
    const c = document.getElementById('pw-cursor');
    if (c) c.style.opacity = '0';
  });
}

/** Show cursor */
export async function showCursor(page: Page) {
  await page.evaluate(() => {
    const c = document.getElementById('pw-cursor');
    if (c) c.style.opacity = '1';
  });
}

/** Wait for all images on the page to load (with hard timeout) */
export async function waitForImages(page: Page, timeout = 5000) {
  await Promise.race([
    page.evaluate(`Promise.all(
      Array.from(document.images).map(function(img) {
        return img.complete ? Promise.resolve() :
          new Promise(function(resolve) { img.onload = resolve; img.onerror = resolve; });
      })
    )`),
    wait(timeout),
  ]);
}
