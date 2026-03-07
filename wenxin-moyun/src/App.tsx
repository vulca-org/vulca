import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import ErrorBoundary from './components/common/ErrorBoundary';
import { cacheUtils } from './services/api';
import { useEffect, Suspense, lazy } from 'react';
import { loadModelsPage, loadVulcaDemoPage, setupCriticalRoutePreload } from './routes/preloadCriticalRoutes';

// Core pages - eagerly loaded
import HomePage from './pages/HomePage';
const ModelsPage = lazy(loadModelsPage);
const ModelDetailPage = lazy(() => import('./pages/ModelDetailPage'));
const EvaluationsPage = lazy(() => import('./pages/EvaluationsPage'));
const EvaluationDetailPage = lazy(() => import('./pages/EvaluationDetailPage'));
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Marketing pages - lazy loaded (Scale.com style)
const PricingPage = lazy(() => import('./pages/PricingPage'));
const CustomersPage = lazy(() => import('./pages/CustomersPage'));
const TrustPage = lazy(() => import('./pages/TrustPage'));
const BookDemoPage = lazy(() => import('./pages/BookDemoPage'));
const DemoConfirmationPage = lazy(() => import('./pages/DemoConfirmationPage'));

// Solutions pages - lazy loaded
const SolutionsPage = lazy(() => import('./pages/solutions/SolutionsPage'));

// VULCA and Exhibitions - lazy loaded
const VULCADemoPage = lazy(loadVulcaDemoPage);
const ExhibitionsPage = lazy(() => import('./pages/exhibitions/ExhibitionsPage'));
const ExhibitionDetailPage = lazy(() => import('./pages/exhibitions/ExhibitionDetailPage'));
const ArtworkPage = lazy(() => import('./pages/exhibitions/ArtworkPage'));

// New integrated pages
const EvaluatePage = lazy(() => import('./pages/EvaluatePage'));
const ResearchPage = lazy(() => import('./pages/ResearchPage'));
const SkillsPage = lazy(() => import('./pages/SkillsPage'));
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'));

// Legal pages - lazy loaded
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));

// Knowledge Base page - lazy loaded
const KnowledgeBasePage = lazy(() => import('./pages/KnowledgeBasePage'));

// Report page - lazy loaded
const ModelReportPage = lazy(() => import('./pages/ModelReportPage'));

// Comparison page - lazy loaded
const CompareModelsPage = lazy(() => import('./pages/CompareModelsPage'));

// Prototype pipeline - lazy loaded
const PrototypePage = lazy(() => import('./pages/prototype/PrototypePage'));

// Reusable loading component
function PageLoader({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">{text}</p>
      </div>
    </div>
  );
}

function App() {
  // Initialize cache warming on app start with version check
  useEffect(() => {
    const versionUpdated = cacheUtils.checkVersion();

    const timer = setTimeout(() => {
      if (versionUpdated) {
        console.log('App: Version updated, warming cache with fresh data');
      }
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

    if (process.env.NODE_ENV === 'production') {
      // Error reporting would go here
    }
  };

  return (
    <ErrorBoundary onError={handleError}>
      <ThemeProvider>
        <Router>
          <Routes>
            {/* Login page without Layout */}
            <Route path="/login" element={
              <Suspense fallback={<PageLoader text="Loading Login..." />}>
                <LoginPage />
              </Suspense>
            } />

            {/* All other pages with Layout */}
            <Route element={<Layout />}>
              {/* Marketing pages (Scale.com style) */}
              <Route path="/" element={<HomePage />} />
              <Route path="/pricing" element={
                <Suspense fallback={<PageLoader text="Loading Pricing..." />}>
                  <PricingPage />
                </Suspense>
              } />
              <Route path="/customers" element={
                <Suspense fallback={<PageLoader text="Loading Customers..." />}>
                  <CustomersPage />
                </Suspense>
              } />
              <Route path="/trust" element={
                <Suspense fallback={<PageLoader text="Loading Trust & Security..." />}>
                  <TrustPage />
                </Suspense>
              } />
              <Route path="/demo" element={
                <Suspense fallback={<PageLoader text="Loading Demo Scheduler..." />}>
                  <BookDemoPage />
                </Suspense>
              } />
              <Route path="/demo/confirmation" element={
                <Suspense fallback={<PageLoader text="Loading..." />}>
                  <DemoConfirmationPage />
                </Suspense>
              } />

              {/* Solutions pages */}
              <Route path="/solutions" element={
                <Suspense fallback={<PageLoader text="Loading Solutions..." />}>
                  <SolutionsPage />
                </Suspense>
              } />
              <Route path="/solutions/ai-labs" element={<Navigate to="/solutions?tab=ai-labs" replace />} />
              <Route path="/solutions/research" element={<Navigate to="/solutions?tab=research" replace />} />
              <Route path="/solutions/museums" element={<Navigate to="/solutions?tab=museums" replace />} />

              {/* Public Demo / Models */}
              <Route path="/models" element={
                <Suspense fallback={<PageLoader text="Loading Models..." />}>
                  <ModelsPage />
                </Suspense>
              } />
              <Route path="/models/:category" element={
                <Suspense fallback={<PageLoader text="Loading Models..." />}>
                  <ModelsPage />
                </Suspense>
              } />
              {/* Legacy route redirects */}
              <Route path="/leaderboard" element={
                <Suspense fallback={<PageLoader text="Loading Models..." />}>
                  <ModelsPage />
                </Suspense>
              } />
              <Route path="/leaderboard/:category" element={
                <Suspense fallback={<PageLoader text="Loading Models..." />}>
                  <ModelsPage />
                </Suspense>
              } />
              <Route path="/model/:id" element={
                <Suspense fallback={<PageLoader text="Loading Model..." />}>
                  <ModelDetailPage />
                </Suspense>
              } />
              <Route path="/model/:id/report" element={
                <Suspense fallback={<PageLoader text="Loading Report..." />}>
                  <ModelReportPage />
                </Suspense>
              } />

              {/* Model Comparison - SEO-friendly URLs */}
              <Route path="/compare/:comparison" element={
                <Suspense fallback={<PageLoader text="Loading Comparison..." />}>
                  <CompareModelsPage />
                </Suspense>
              } />

              {/* VULCA Demo */}
              <Route path="/vulca" element={
                <Suspense fallback={<PageLoader text="Loading VULCA Demo..." />}>
                  <VULCADemoPage />
                </Suspense>
              } />

              {/* Canvas (renamed from prototype) */}
              <Route path="/canvas" element={
                <Suspense fallback={<PageLoader text="Loading Canvas..." />}>
                  <PrototypePage />
                </Suspense>
              } />

              {/* Evaluate (NoCode) */}
              <Route path="/evaluate" element={
                <Suspense fallback={<PageLoader text="Loading Evaluate..." />}>
                  <EvaluatePage />
                </Suspense>
              } />

              {/* Research (merged academic pages) */}
              <Route path="/research" element={
                <Suspense fallback={<PageLoader text="Loading Research..." />}>
                  <ResearchPage />
                </Suspense>
              } />

              {/* Skills Marketplace */}
              <Route path="/skills" element={
                <Suspense fallback={<PageLoader text="Loading Skills..." />}>
                  <SkillsPage />
                </Suspense>
              } />

              {/* Admin Dashboard */}
              <Route path="/admin" element={
                <Suspense fallback={<PageLoader text="Loading Admin..." />}>
                  <AdminDashboardPage />
                </Suspense>
              } />

              {/* Exhibition Routes */}
              <Route path="/exhibitions" element={
                <Suspense fallback={<PageLoader text="Loading Exhibitions..." />}>
                  <ExhibitionsPage />
                </Suspense>
              } />
              <Route path="/exhibitions/:id" element={
                <Suspense fallback={<PageLoader text="Loading Exhibition..." />}>
                  <ExhibitionDetailPage />
                </Suspense>
              } />
              <Route path="/exhibitions/:id/:artworkId" element={
                <Suspense fallback={<PageLoader text="Loading Artwork..." />}>
                  <ArtworkPage />
                </Suspense>
              } />

              {/* Redirects for merged/renamed pages */}
              <Route path="/product" element={<Navigate to="/" replace />} />
              <Route path="/pilot" element={<Navigate to="/demo" replace />} />
              <Route path="/prototype" element={<Navigate to="/canvas" replace />} />
              <Route path="/methodology" element={<Navigate to="/research?tab=methodology" replace />} />
              <Route path="/dataset" element={<Navigate to="/research?tab=dataset" replace />} />
              <Route path="/papers" element={<Navigate to="/research?tab=papers" replace />} />
              <Route path="/data-ethics" element={<Navigate to="/trust?tab=data-ethics" replace />} />
              <Route path="/sop" element={<Navigate to="/trust?tab=sop" replace />} />

              {/* Legal Pages */}
              <Route path="/privacy" element={
                <Suspense fallback={<PageLoader text="Loading Privacy Policy..." />}>
                  <PrivacyPage />
                </Suspense>
              } />
              <Route path="/terms" element={
                <Suspense fallback={<PageLoader text="Loading Terms of Service..." />}>
                  <TermsPage />
                </Suspense>
              } />

              {/* User Evaluations */}
              <Route path="/evaluations" element={
                <Suspense fallback={<PageLoader text="Loading Evaluations..." />}>
                  <EvaluationsPage />
                </Suspense>
              } />
              <Route path="/evaluations/:id" element={
                <Suspense fallback={<PageLoader text="Loading Evaluation..." />}>
                  <EvaluationDetailPage />
                </Suspense>
              } />
              <Route path="/gallery" element={
                <Suspense fallback={<PageLoader text="Loading Gallery..." />}>
                  <GalleryPage />
                </Suspense>
              } />
              <Route path="/knowledge-base" element={
                <Suspense fallback={<PageLoader text="Loading Knowledge Base..." />}>
                  <KnowledgeBasePage />
                </Suspense>
              } />

              {/* 404 catch-all route */}
              <Route path="*" element={
                <Suspense fallback={<PageLoader text="Loading..." />}>
                  <NotFoundPage />
                </Suspense>
              } />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
