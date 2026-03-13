import type { ComponentType } from 'react';

type LazyPageModule = { default: ComponentType<object> };
type RouteLoader = () => Promise<LazyPageModule>;

export const loadModelsPage: RouteLoader = () => import('../pages/LeaderboardPage');

const criticalRouteLoaders: Record<string, RouteLoader> = {
  '/models': loadModelsPage,
};

const preloaded = new Set<string>();

function normalizeCriticalRoute(pathname: string): '/models' | null {
  if (pathname.startsWith('/models') || pathname.startsWith('/model/')) {
    return '/models';
  }
  return null;
}

export function preloadCriticalRoute(pathname: string): void {
  const routeKey = normalizeCriticalRoute(pathname);
  if (!routeKey || preloaded.has(routeKey)) {
    return;
  }

  const loader = criticalRouteLoaders[routeKey];
  if (!loader) {
    return;
  }

  preloaded.add(routeKey);
  void loader().catch(() => {
    // Allow retries if preload failed due to transient network/chunk issues.
    preloaded.delete(routeKey);
  });
}

export function preloadCriticalRoutes(): void {
  preloadCriticalRoute('/models');
}

function preloadFromEvent(event: Event): void {
  const target = event.target;
  if (!(target instanceof Element)) {
    return;
  }

  const link = target.closest('a[href]');
  if (!(link instanceof HTMLAnchorElement)) {
    return;
  }

  if (link.target && link.target !== '_self') {
    return;
  }

  if (link.origin !== window.location.origin) {
    return;
  }

  preloadCriticalRoute(link.pathname);
}

function scheduleIdlePreload(): () => void {
  const run = () => preloadCriticalRoutes();
  const requestIdle = window.requestIdleCallback?.bind(window);
  const cancelIdle = window.cancelIdleCallback?.bind(window);

  if (requestIdle) {
    const idleId = requestIdle(run, { timeout: 3500 });
    return () => {
      if (cancelIdle) {
        cancelIdle(idleId);
      }
    };
  }

  const timeoutId = setTimeout(run, 1800);
  return () => clearTimeout(timeoutId);
}

export function setupCriticalRoutePreload(): () => void {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return () => {};
  }

  const cancelIdle = scheduleIdlePreload();

  document.addEventListener('pointerover', preloadFromEvent, { passive: true });
  document.addEventListener('focusin', preloadFromEvent);
  document.addEventListener('touchstart', preloadFromEvent, { passive: true });

  return () => {
    cancelIdle();
    document.removeEventListener('pointerover', preloadFromEvent);
    document.removeEventListener('focusin', preloadFromEvent);
    document.removeEventListener('touchstart', preloadFromEvent);
  };
}
