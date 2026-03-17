import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import ErrorBoundary from './components/common/ErrorBoundary';
import { cacheUtils } from './services/api';
import { useEffect, Suspense, lazy } from 'react';
import type { ComponentType } from 'react';
import { loadModelsPage, setupCriticalRoutePreload } from './routes/preloadCriticalRoutes';

// Core pages - eagerly loaded
import HomePage from './pages/HomePage';

// Lazy-loaded pages
const ModelsPage = lazy(loadModelsPage);
const ModelDetailPage = lazy(() => import('./pages/ModelDetailPage'));
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const ResearchPage = lazy(() => import('./pages/ResearchPage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const PrototypePage = lazy(() => import('./pages/prototype/PrototypePage'));

/** Reduces Suspense boilerplate for lazy-loaded routes. */
function LazyRoute({ component: Component, text = 'Loading...' }: { component: ComponentType; text?: string }) {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">{text}</p>
        </div>
      </div>
    }>
      <Component />
    </Suspense>
  );
}

function App() {
  useEffect(() => {
    const versionUpdated = cacheUtils.checkVersion();
    const timer = setTimeout(() => {
      if (versionUpdated) console.log('App: Version updated, warming cache with fresh data');
      cacheUtils.warmUp();
    }, versionUpdated ? 500 : 2000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    return setupCriticalRoutePreload();
  }, []);

  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    console.error('App Error Boundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
    });
  };

  return (
    <ErrorBoundary onError={handleError}>
      <ThemeProvider>
        <Router>
          <Routes>
            {/* Auth — no Layout wrapper */}
            <Route path="/login" element={<LazyRoute component={LoginPage} text="Loading Login..." />} />
            <Route path="/register" element={<LazyRoute component={RegisterPage} text="Loading Register..." />} />

            <Route element={<Layout />}>
              {/* ── Core product ── */}
              <Route path="/" element={<HomePage />} />
              <Route path="/canvas" element={<LazyRoute component={PrototypePage} text="Loading Canvas..." />} />
              <Route path="/gallery" element={<LazyRoute component={GalleryPage} text="Loading Gallery..." />} />

              {/* ── Supporting ── */}
              <Route path="/models" element={<LazyRoute component={ModelsPage} text="Loading Models..." />} />
              <Route path="/models/:category" element={<LazyRoute component={ModelsPage} text="Loading Models..." />} />
              <Route path="/model/:id" element={<LazyRoute component={ModelDetailPage} text="Loading Model..." />} />
              <Route path="/research" element={<LazyRoute component={ResearchPage} text="Loading Research..." />} />

              {/* ── Legal ── */}
              <Route path="/privacy" element={<LazyRoute component={PrivacyPage} />} />
              <Route path="/terms" element={<LazyRoute component={TermsPage} />} />

              {/* ── Redirects for removed pages ── */}
              <Route path="/pricing" element={<Navigate to="/" replace />} />
              <Route path="/demo" element={<Navigate to="/" replace />} />
              <Route path="/demo/confirmation" element={<Navigate to="/" replace />} />
              <Route path="/solutions" element={<Navigate to="/" replace />} />
              <Route path="/solutions/*" element={<Navigate to="/" replace />} />
              <Route path="/exhibitions" element={<Navigate to="/gallery" replace />} />
              <Route path="/exhibitions/*" element={<Navigate to="/gallery" replace />} />
              <Route path="/skills" element={<Navigate to="/canvas" replace />} />
              <Route path="/admin" element={<Navigate to="/" replace />} />
              <Route path="/compare/*" element={<Navigate to="/models" replace />} />
              <Route path="/trust" element={<Navigate to="/" replace />} />
              <Route path="/customers" element={<Navigate to="/" replace />} />

              {/* ── Legacy redirects (preserved) ── */}
              <Route path="/vulca" element={<Navigate to="/canvas" replace />} />
              <Route path="/create" element={<Navigate to="/canvas" replace />} />
              <Route path="/evaluate" element={<Navigate to="/canvas" replace />} />
              <Route path="/prototype" element={<Navigate to="/canvas" replace />} />
              <Route path="/evaluations" element={<Navigate to="/canvas" replace />} />
              <Route path="/evaluations/:id" element={<Navigate to="/canvas" replace />} />
              <Route path="/leaderboard" element={<Navigate to="/models" replace />} />
              <Route path="/leaderboard/:category" element={<Navigate to="/models" replace />} />
              <Route path="/model/:id/report" element={<Navigate to="/models" replace />} />
              <Route path="/product" element={<Navigate to="/" replace />} />
              <Route path="/changelog" element={<Navigate to="/" replace />} />
              <Route path="/pilot" element={<Navigate to="/" replace />} />
              <Route path="/methodology" element={<Navigate to="/research" replace />} />
              <Route path="/dataset" element={<Navigate to="/research" replace />} />
              <Route path="/papers" element={<Navigate to="/research" replace />} />
              <Route path="/knowledge-base" element={<Navigate to="/research" replace />} />
              <Route path="/data-ethics" element={<Navigate to="/" replace />} />
              <Route path="/sop" element={<Navigate to="/" replace />} />

              {/* 404 */}
              <Route path="*" element={<LazyRoute component={NotFoundPage} />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
