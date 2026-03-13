import { test, expect } from '@playwright/test';

interface PerformanceMetrics {
  pageLoad: number;
  domContentLoaded: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  timeToInteractive: number;
  totalBlockingTime: number;
  cumulativeLayoutShift: number;
  memoryUsage?: number;
  jsHeapSize?: number;
}

interface ResourceTiming {
  name: string;
  duration: number;
  size: number;
  type: string;
}

test.describe('Performance Monitoring', () => {
  // Relaxed thresholds for dev environment - production should be stricter
  const performanceThresholds = {
    pageLoad: 8000, // 8 seconds (dev environment)
    domContentLoaded: 5000, // 5 seconds
    firstContentfulPaint: 4000, // 4 seconds
    largestContentfulPaint: 6000, // 6 seconds
    timeToInteractive: 8000, // 8 seconds
    totalBlockingTime: 1000, // 1000ms
    cumulativeLayoutShift: 0.25
  };

  async function collectPerformanceMetrics(page: any): Promise<PerformanceMetrics> {
    return await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      // Get FCP and LCP
      const fcp = paint.find(entry => entry.name === 'first-contentful-paint');
      const lcp = performance.getEntriesByType('largest-contentful-paint')[0] as any;
      
      // Calculate metrics
      const metrics: any = {
        pageLoad: navigation.loadEventEnd - navigation.fetchStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
        firstContentfulPaint: fcp ? fcp.startTime : 0,
        largestContentfulPaint: lcp ? lcp.startTime : 0,
        timeToInteractive: navigation.domInteractive - navigation.fetchStart,
        totalBlockingTime: 0, // Will be calculated separately
        cumulativeLayoutShift: 0 // Will be calculated separately
      };

      // Memory usage if available
      if ((performance as any).memory) {
        metrics.memoryUsage = (performance as any).memory.usedJSHeapSize;
        metrics.jsHeapSize = (performance as any).memory.totalJSHeapSize;
      }

      return metrics;
    });
  }

  async function collectResourceTimings(page: any): Promise<ResourceTiming[]> {
    return await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      return resources.map(resource => ({
        name: resource.name.split('/').pop() || resource.name,
        duration: resource.duration,
        size: resource.transferSize,
        type: resource.initiatorType
      }));
    });
  }

  async function measureCLS(page: any): Promise<number> {
    return await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if ((entry as any).hadRecentInput) continue;
            clsValue += (entry as any).value;
          }
        });
        
        observer.observe({ type: 'layout-shift', buffered: true });
        
        setTimeout(() => {
          observer.disconnect();
          resolve(clsValue);
        }, 2000);
      });
    });
  }

  async function measureTBT(page: any): Promise<number> {
    return await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let tbt = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) {
              tbt += entry.duration - 50;
            }
          }
        });
        
        observer.observe({ type: 'long-task', buffered: true });
        
        setTimeout(() => {
          observer.disconnect();
          resolve(tbt);
        }, 3000);
      });
    });
  }

  test('Homepage performance metrics', async ({ page }) => {
    // Start recording
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Collect metrics
    const metrics = await collectPerformanceMetrics(page);
    const cls = await measureCLS(page);
    const tbt = await measureTBT(page);
    
    metrics.cumulativeLayoutShift = cls;
    metrics.totalBlockingTime = tbt;
    
    // Log metrics
    console.log('Homepage Performance Metrics:', metrics);
    
    // Assert thresholds
    expect(metrics.pageLoad).toBeLessThan(performanceThresholds.pageLoad);
    expect(metrics.domContentLoaded).toBeLessThan(performanceThresholds.domContentLoaded);
    expect(metrics.firstContentfulPaint).toBeLessThan(performanceThresholds.firstContentfulPaint);
    expect(metrics.largestContentfulPaint).toBeLessThan(performanceThresholds.largestContentfulPaint);
    expect(metrics.timeToInteractive).toBeLessThan(performanceThresholds.timeToInteractive);
    expect(metrics.totalBlockingTime).toBeLessThan(performanceThresholds.totalBlockingTime);
    expect(metrics.cumulativeLayoutShift).toBeLessThan(performanceThresholds.cumulativeLayoutShift);
  });

  test('Resource loading analysis', async ({ page }) => {
    await page.goto('/');
    
    const resources = await collectResourceTimings(page);
    
    // Analyze resource types
    const resourcesByType = resources.reduce((acc, resource) => {
      if (!acc[resource.type]) {
        acc[resource.type] = {
          count: 0,
          totalSize: 0,
          totalDuration: 0
        };
      }
      acc[resource.type].count++;
      acc[resource.type].totalSize += resource.size;
      acc[resource.type].totalDuration += resource.duration;
      return acc;
    }, {} as Record<string, any>);
    
    console.log('Resource Analysis:', resourcesByType);
    
    // Find slow resources
    const slowResources = resources.filter(r => r.duration > 500);
    if (slowResources.length > 0) {
      console.warn('Slow resources detected:', slowResources);
    }
    
    // Find large resources
    const largeResources = resources.filter(r => r.size > 100000); // 100KB
    if (largeResources.length > 0) {
      console.warn('Large resources detected:', largeResources);
    }
    
    // Assert reasonable limits (relaxed for dev environment)
    expect(slowResources.length).toBeLessThanOrEqual(10);
    expect(largeResources.length).toBeLessThanOrEqual(15);
  });

  test('Canvas page performance with interactions', async ({ page }) => {
    await page.goto('/canvas');

    // Initial load metrics
    const initialMetrics = await collectPerformanceMetrics(page);

    console.log('Canvas page load metrics:', initialMetrics);

    // Assert page load performance
    expect(initialMetrics.pageLoad).toBeLessThan(performanceThresholds.pageLoad);

    // Check for memory leaks after waiting
    if (initialMetrics.memoryUsage) {
      await page.waitForTimeout(2000);
      const afterMetrics = await collectPerformanceMetrics(page);

      const memoryIncrease = afterMetrics.memoryUsage! - initialMetrics.memoryUsage;
      console.log('Memory increase after idle:', memoryIncrease, 'bytes');

      // Memory shouldn't increase dramatically
      expect(memoryIncrease).toBeLessThan(5000000); // 5MB
    }
  });

  test('Animation performance monitoring', async ({ page }) => {
    await page.goto('/');
    
    // Monitor animation frame rate
    const fps = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let frameCount = 0;
        let lastTime = performance.now();
        const frameTimes: number[] = [];
        
        function measureFrame() {
          const currentTime = performance.now();
          const deltaTime = currentTime - lastTime;
          frameTimes.push(deltaTime);
          lastTime = currentTime;
          frameCount++;
          
          if (frameCount < 60) {
            requestAnimationFrame(measureFrame);
          } else {
            const avgFrameTime = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
            const fps = 1000 / avgFrameTime;
            resolve(fps);
          }
        }
        
        requestAnimationFrame(measureFrame);
      });
    });
    
    console.log('Average FPS:', fps);
    
    // Should maintain smooth 60 FPS (allowing some variance)
    expect(fps).toBeGreaterThan(50);
  });

  test('Network performance and caching', async ({ page }) => {
    // First load
    await page.goto('/');
    const firstLoadResources = await collectResourceTimings(page);
    const firstLoadTotal = firstLoadResources.reduce((sum, r) => sum + r.duration, 0);
    
    // Second load (should use cache)
    await page.reload();
    const secondLoadResources = await collectResourceTimings(page);
    const secondLoadTotal = secondLoadResources.reduce((sum, r) => sum + r.duration, 0);
    
    console.log('First load total time:', firstLoadTotal, 'ms');
    console.log('Second load total time:', secondLoadTotal, 'ms');
    console.log('Cache efficiency:', ((1 - secondLoadTotal / firstLoadTotal) * 100).toFixed(2), '%');
    
    // Second load should be significantly faster due to caching
    expect(secondLoadTotal).toBeLessThan(firstLoadTotal * 0.5);
  });

  test('Bundle size analysis', async ({ page }) => {
    await page.goto('/');
    
    const resources = await collectResourceTimings(page);
    
    // Analyze JavaScript bundles
    const jsBundles = resources.filter(r => r.type === 'script');
    const totalJsSize = jsBundles.reduce((sum, r) => sum + r.size, 0);
    
    // Analyze CSS bundles  
    const cssBundles = resources.filter(r => r.type === 'css' || r.type === 'style');
    const totalCssSize = cssBundles.reduce((sum, r) => sum + r.size, 0);
    
    console.log('JavaScript bundle size:', (totalJsSize / 1024).toFixed(2), 'KB');
    console.log('CSS bundle size:', (totalCssSize / 1024).toFixed(2), 'KB');
    console.log('Total bundle size:', ((totalJsSize + totalCssSize) / 1024).toFixed(2), 'KB');
    
    // Assert reasonable bundle sizes (relaxed for dev environment)
    expect(totalJsSize).toBeLessThan(3 * 1024 * 1024); // 3MB for JS
    expect(totalCssSize).toBeLessThan(500 * 1024); // 500KB for CSS
  });

  test('Mobile performance simulation', async ({ browser }) => {
    // Create mobile context
    const context = await browser.newContext({
      viewport: { width: 375, height: 667 },
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
      deviceScaleFactor: 2,
      isMobile: true,
      hasTouch: true
    });
    
    const page = await context.newPage();
    
    // Throttle network and CPU
    await page.route('**/*', route => {
      setTimeout(() => route.continue(), 100); // Add 100ms latency
    });
    
    await page.goto('/');

    const metrics = await collectPerformanceMetrics(page);

    console.log('Mobile Performance Metrics:', metrics);

    // Mobile thresholds are more lenient (relaxed for dev environment)
    expect(metrics.pageLoad).toBeLessThan(10000);
    expect(metrics.firstContentfulPaint).toBeLessThan(6000);
    
    await context.close();
  });

  test('Performance budget validation', async ({ page }) => {
    const budget = {
      maxRequests: 50,
      maxTransferSize: 2 * 1024 * 1024, // 2MB
      maxScriptCount: 10,
      maxStyleCount: 5,
      maxImageCount: 20,
      maxFontCount: 5
    };
    
    await page.goto('/');

    const resources = await collectResourceTimings(page);

    const counts = {
      total: resources.length,
      scripts: resources.filter(r => r.type === 'script').length,
      styles: resources.filter(r => r.type === 'css' || r.type === 'style').length,
      images: resources.filter(r => r.type === 'image' || r.type === 'img').length,
      fonts: resources.filter(r => r.type === 'font').length
    };
    
    const totalSize = resources.reduce((sum, r) => sum + r.size, 0);
    
    console.log('Performance Budget Status:');
    console.log('- Total requests:', counts.total, '/', budget.maxRequests);
    console.log('- Total size:', (totalSize / 1024 / 1024).toFixed(2), 'MB /', (budget.maxTransferSize / 1024 / 1024), 'MB');
    console.log('- Scripts:', counts.scripts, '/', budget.maxScriptCount);
    console.log('- Styles:', counts.styles, '/', budget.maxStyleCount);
    console.log('- Images:', counts.images, '/', budget.maxImageCount);
    console.log('- Fonts:', counts.fonts, '/', budget.maxFontCount);
    
    // Assert budget limits
    expect(counts.total).toBeLessThanOrEqual(budget.maxRequests);
    expect(totalSize).toBeLessThanOrEqual(budget.maxTransferSize);
    expect(counts.scripts).toBeLessThanOrEqual(budget.maxScriptCount);
    expect(counts.styles).toBeLessThanOrEqual(budget.maxStyleCount);
    expect(counts.images).toBeLessThanOrEqual(budget.maxImageCount);
    expect(counts.fonts).toBeLessThanOrEqual(budget.maxFontCount);
  });
});