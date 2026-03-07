import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IntentInput } from '../components/evaluate/IntentInput';
import { ResultCard } from '../components/evaluate/ResultCard';
import type { EvaluationResult } from '../components/evaluate/ResultCard';
import { FlowToggle } from '../components/evaluate/FlowToggle';
import { CodeExport } from '../components/evaluate/CodeExport';

// ── Mock evaluation result ──────────────────────────────────────────
const MOCK_RESULT: EvaluationResult = {
  score: 0.82,
  summary:
    'This artwork demonstrates strong compositional balance and effective use of negative space consistent with the Chinese ink painting tradition. Minor inconsistencies were found in brush-stroke rhythm in the lower-left quadrant, but overall cultural alignment is high.',
  riskLevel: 'low',
  dimensions: [
    { name: 'Creativity', score: 0.88 },
    { name: 'Technique', score: 0.79 },
    { name: 'Emotion', score: 0.85 },
    { name: 'Cultural Context', score: 0.91 },
    { name: 'Innovation', score: 0.72 },
    { name: 'Impact', score: 0.78 },
  ],
  recommendations: [
    'Consider refining the lower-left brush strokes for more consistent rhythm.',
    'The seal placement could be adjusted for better visual balance.',
    'Adding a colophon would strengthen the cultural authenticity signal.',
  ],
  traditionUsed: 'Chinese Ink Painting',
};

// ── Page states ─────────────────────────────────────────────────────
type PageState = 'input' | 'loading' | 'result';

const EvaluatePage: React.FC = () => {
  const [pageState, setPageState] = useState<PageState>('input');
  const [submittedIntent, setSubmittedIntent] = useState('');

  const handleSubmit = useCallback((intent: string, _image?: File) => {
    setSubmittedIntent(intent);
    setPageState('loading');

    // Simulate API call
    setTimeout(() => {
      setPageState('result');
    }, 2200);
  }, []);

  const handleReset = useCallback(() => {
    setPageState('input');
    setSubmittedIntent('');
  }, []);

  return (
    <div className="min-h-[70vh] py-12 px-4 sm:px-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="text-center mb-10"
      >
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
          Evaluate
        </h1>
        <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
          Describe what you want to evaluate
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* ── Input state ─────────────────────────────────────────── */}
        {pageState === 'input' && (
          <motion.div
            key="input"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <IntentInput onSubmit={handleSubmit} />
          </motion.div>
        )}

        {/* ── Loading state ───────────────────────────────────────── */}
        {pageState === 'loading' && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <div className="relative w-16 h-16 mb-6">
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-slate-200 dark:border-slate-700"
              />
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-transparent border-t-slate-600 dark:border-t-slate-400"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
            </div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Analyzing your input...
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              Running VULCA evaluation pipeline
            </p>
          </motion.div>
        )}

        {/* ── Result state ────────────────────────────────────────── */}
        {pageState === 'result' && (
          <motion.div
            key="result"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-2xl mx-auto space-y-6"
          >
            <ResultCard result={MOCK_RESULT} />
            <FlowToggle />
            <CodeExport intent={submittedIntent} traditionUsed={MOCK_RESULT.traditionUsed} />

            {/* Reset button */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="pt-2 text-center"
            >
              <button
                type="button"
                onClick={handleReset}
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 underline underline-offset-2 transition-colors"
              >
                Start a new evaluation
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EvaluatePage;
