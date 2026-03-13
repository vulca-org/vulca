/**
 * ResearchPage - Unified Academic Research Hub
 *
 * Merges Methodology, Dataset, and Papers into a single tabbed page.
 * Uses IOSSegmentedControl for tab navigation and useSearchParams
 * to persist the active tab in the URL (?tab=methodology|dataset|papers).
 *
 * @module pages/ResearchPage
 */

import React, { Suspense, lazy, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FlaskConical } from 'lucide-react';
import { IOSSegmentedControl } from '../components/ios';
import type { SegmentItem } from '../components/ios';

const MethodologyPage = lazy(() => import('./MethodologyPage'));
const DatasetPage = lazy(() => import('./DatasetPage'));
const PapersPage = lazy(() => import('./PapersPage'));

const TAB_KEYS = ['methodology', 'dataset', 'papers'] as const;
type TabKey = (typeof TAB_KEYS)[number];

const SEGMENTS: SegmentItem[] = [
  { id: 'methodology', label: 'Methodology' },
  { id: 'dataset', label: 'Dataset' },
  { id: 'papers', label: 'Papers' },
];

function TabLoader() {
  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-slate-600 mx-auto mb-3" />
        <p className="text-gray-500 dark:text-gray-400 text-sm">Loading...</p>
      </div>
    </div>
  );
}

const ResearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const activeTab: TabKey = useMemo(() => {
    const raw = searchParams.get('tab');
    if (raw && TAB_KEYS.includes(raw as TabKey)) {
      return raw as TabKey;
    }
    return 'methodology';
  }, [searchParams]);

  const selectedIndex = TAB_KEYS.indexOf(activeTab);

  const handleTabChange = (index: number) => {
    const key = TAB_KEYS[index];
    setSearchParams({ tab: key }, { replace: true });
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center pt-8 pb-4 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800/50 mb-4"
        >
          <FlaskConical className="w-8 h-8 text-slate-600 dark:text-slate-300" />
        </motion.div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
          Research
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
          Peer-reviewed evaluation methodology
        </p>

        {/* Segmented Control */}
        <div className="flex justify-center">
          <IOSSegmentedControl
            segments={SEGMENTS}
            selectedIndex={selectedIndex}
            onChange={handleTabChange}
            size="regular"
            style="filled"
            className="w-full max-w-md"
          />
        </div>
      </motion.section>

      {/* Tab Content */}
      <Suspense fallback={<TabLoader />}>
        {activeTab === 'methodology' && <MethodologyPage />}
        {activeTab === 'dataset' && <DatasetPage />}
        {activeTab === 'papers' && <PapersPage />}
      </Suspense>
    </div>
  );
};

export default ResearchPage;
