import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import PageErrorBoundary from './PageErrorBoundary';
import CacheStats from './CacheStats';
import Vulca3DBackground from './Vulca3DBackground';
import BackToTop from './BackToTop';
import OfflineBanner from './OfflineBanner';
import { useState, useEffect } from 'react';
import {
  detectDevicePerformance,
  type PerformanceLevel
} from '../../utils/performanceOptimizer';
import { useSEO } from '../../hooks/useSEO';

export default function Layout() {
  const location = useLocation();
  const [performanceLevel, setPerformanceLevel] = useState<PerformanceLevel>('medium');

  // Update SEO meta tags on route change
  useSEO();

  const isCanvas = location.pathname === '/canvas';

  // Get page name from route for error boundary
  const getPageName = (pathname: string) => {
    const routes: Record<string, string> = {
      '/': 'Home',
      '/canvas': 'Canvas',
      '/gallery': 'Gallery',
      '/models': 'Models',
      '/research': 'Research',
    };

    // Handle dynamic routes
    if (pathname.startsWith('/model/')) return 'Model Detail';

    return routes[pathname] || 'Page';
  };

  // Detect device performance on mount
  useEffect(() => {
    const level = detectDevicePerformance();
    setPerformanceLevel(level);
    console.log('Device performance level:', level);
  }, []);

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-[var(--bg-base)] transition-colors duration-300">
      {/* 3D Background - Scale AI inspired (React Three Fiber) */}
      <Vulca3DBackground />

      {/* Performance indicator (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 left-4 z-50 px-3 py-1 bg-black/50 text-white text-xs rounded-full backdrop-blur-md">
          Performance: {performanceLevel}
        </div>
      )}

      {/* Cache Statistics (development only) */}
      {process.env.NODE_ENV === 'development' && <CacheStats />}

      {/* Content layer */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Skip to main content link for accessibility */}
        <a
          href="#main-content"
          className="sr-only skip-to-main"
        >
          Skip to main content
        </a>
        <Header />
        <OfflineBanner />
        <main id="main-content" className="flex-grow" tabIndex={-1}>
          {isCanvas ? (
            <PageErrorBoundary pageName="Canvas">
              <Outlet />
            </PageErrorBoundary>
          ) : (
            <div className="container mx-auto px-4 sm:px-6 py-8 sm:py-12">
              <PageErrorBoundary pageName={getPageName(location.pathname)}>
                <Outlet />
              </PageErrorBoundary>
            </div>
          )}
        </main>
        {!isCanvas && <Footer />}
        <BackToTop />
      </div>
    </div>
  );
}
