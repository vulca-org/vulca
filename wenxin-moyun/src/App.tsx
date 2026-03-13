import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import ErrorBoundary from './components/common/ErrorBoundary';
import RequireAdmin from './components/common/RequireAdmin';
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
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const CustomersPage = lazy(() => import('./pages/CustomersPage'));
const TrustPage = lazy(() => import('./pages/TrustPage'));
const BookDemoPage = lazy(() => import('./pages/BookDemoPage'));
const DemoConfirmationPage = lazy(() => import('./pages/DemoConfirmationPage'));
const SolutionsPage = lazy(() => import('./pages/solutions/SolutionsPage'));
const ExhibitionsPage = lazy(() => import('./pages/exhibitions/ExhibitionsPage'));
const ExhibitionDetailPage = lazy(() => import('./pages/exhibitions/ExhibitionDetailPage'));
const ArtworkPage = lazy(() => import('./pages/exhibitions/ArtworkPage'));
const ResearchPage = lazy(() => import('./pages/ResearchPage'));
const SkillsPage = lazy(() => import('./pages/SkillsPage'));
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const CompareModelsPage = lazy(() => import('./pages/CompareModelsPage'));
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
            {/* Login — no Layout wrapper */}
            <Route path="/login" element={<LazyRoute component={LoginPage} text="Loading Login..." />} />

            <Route element={<Layout />}>
              {/* ── Core product ── */}
              <Route path="/" element={<HomePage />} />
              <Route path="/canvas" element={<LazyRoute component={PrototypePage} text="Loading Canvas..." />} />
              <Route path="/gallery" element={<LazyRoute component={GalleryPage} text="Loading Gallery..." />} />

              {/* ── Supporting ── */}
              <Route path="/models" element={<LazyRoute component={ModelsPage} text="Loading Models..." />} />
              <Route path="/models/:category" element={<LazyRoute component={ModelsPage} text="Loading Models..." />} />
              <Route path="/model/:id" element={<LazyRoute component={ModelDetailPage} text="Loading Model..." />} />
              <Route path="/compare/:comparison" element={<LazyRoute component={CompareModelsPage} text="Loading Comparison..." />} />
              <Route path="/research" element={<LazyRoute component={ResearchPage} text="Loading Research..." />} />
              <Route path="/skills" element={<LazyRoute component={SkillsPage} text="Loading Skills..." />} />
              <Route path="/admin" element={
                <RequireAdmin>
                  <LazyRoute component={AdminDashboardPage} text="Loading Admin..." />
                </RequireAdmin>
              } />

              {/* ── Marketing ── */}
              <Route path="/pricing" element={<LazyRoute component={PricingPage} text="Loading Pricing..." />} />
              <Route path="/customers" element={<LazyRoute component={CustomersPage} text="Loading Customers..." />} />
              <Route path="/trust" element={<LazyRoute component={TrustPage} text="Loading Trust..." />} />
              <Route path="/demo" element={<LazyRoute component={BookDemoPage} text="Loading Demo..." />} />
              <Route path="/demo/confirmation" element={<LazyRoute component={DemoConfirmationPage} />} />
              <Route path="/solutions" element={<LazyRoute component={SolutionsPage} text="Loading Solutions..." />} />

              {/* ── Exhibitions ── */}
              <Route path="/exhibitions" element={<LazyRoute component={ExhibitionsPage} text="Loading Exhibitions..." />} />
              <Route path="/exhibitions/:id" element={<LazyRoute component={ExhibitionDetailPage} text="Loading Exhibition..." />} />
              <Route path="/exhibitions/:id/:artworkId" element={<LazyRoute component={ArtworkPage} text="Loading Artwork..." />} />

              {/* ── Legal ── */}
              <Route path="/privacy" element={<LazyRoute component={PrivacyPage} />} />
              <Route path="/terms" element={<LazyRoute component={TermsPage} />} />

              {/* ── Legacy redirects (consolidated) ── */}
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
              <Route path="/pilot" element={<Navigate to="/demo" replace />} />
              <Route path="/methodology" element={<Navigate to="/research?tab=methodology" replace />} />
              <Route path="/dataset" element={<Navigate to="/research?tab=dataset" replace />} />
              <Route path="/papers" element={<Navigate to="/research?tab=papers" replace />} />
              <Route path="/knowledge-base" element={<Navigate to="/research" replace />} />
              <Route path="/data-ethics" element={<Navigate to="/trust?tab=data-ethics" replace />} />
              <Route path="/sop" element={<Navigate to="/trust?tab=sop" replace />} />
              <Route path="/solutions/ai-labs" element={<Navigate to="/solutions?tab=ai-labs" replace />} />
              <Route path="/solutions/research" element={<Navigate to="/solutions?tab=research" replace />} />
              <Route path="/solutions/museums" element={<Navigate to="/solutions?tab=museums" replace />} />

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
