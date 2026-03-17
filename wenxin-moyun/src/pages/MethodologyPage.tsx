/**
 * MethodologyPage - VULCA Framework Methodology
 *
 * Detailed explanation of the VULCA evaluation methodology including:
 * - L1-L5 Five-Layer Framework
 * - 6D to 47D Expansion Algorithm
 * - 8 Cultural Perspectives
 * - Technical Implementation Details
 *
 * @module pages/MethodologyPage
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Layers,
  Globe,
  FlaskConical,
  ChevronRight,
  GitBranch,
  Users,
  Target,
} from 'lucide-react';
import { IOSCard, IOSCardContent } from '../components/ios';
import { ProvenanceCard } from '../components/trustlayer';
import { dimensionsService, type L1L5Level, type Persona } from '../services/dimensions';
import { VULCA_VERSION } from '../config/version';

const MethodologyPage: React.FC = () => {
  const [l1l5Levels, setL1L5Levels] = useState<Record<string, L1L5Level>>({});
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        await dimensionsService.load();
        setL1L5Levels(dimensionsService.getAllL1L5Levels());
        setPersonas(dimensionsService.getAllPersonas());
      } catch (err) {
        console.error('Failed to load methodology data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const levelColors: Record<string, string> = {
    L1: '#22c55e',
    L2: '#334155',
    L3: '#f59e0b',
    L4: '#ef4444',
    L5: '#C87F4A',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
    >
      {/* Hero Section */}
      <section className="text-center mb-12">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-100 dark:bg-amber-900/30 mb-4"
        >
          <FlaskConical className="w-8 h-8 text-amber-600" />
        </motion.div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          VULCA Methodology
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          A comprehensive framework for evaluating AI-generated art across 47 dimensions
          and 8 cultural perspectives, based on the L1-L5 five-layer evaluation model.
        </p>
      </section>

      {/* Data Provenance */}
      <section className="mb-12">
        <ProvenanceCard
          source="VULCA Framework"
          version={VULCA_VERSION.framework}
          lastUpdated={VULCA_VERSION.lastUpdated}
          license="Apache 2.0"
          doi="10.18653/v1/2025.findings-emnlp.103"
          algorithm={`VULCA Core v${VULCA_VERSION.protocol}`}
          github="https://github.com/vulca-org/vulca"
        />
      </section>

      {/* L1-L5 Framework */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Layers className="w-6 h-6 text-slate-600" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            L1-L5 Five-Layer Framework
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          The VULCA framework evaluates art understanding across five hierarchical levels,
          from basic visual perception to deep philosophical aesthetics. Each level builds
          upon the previous, with increasing cultural and contextual complexity.
        </p>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600" />
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(l1l5Levels).map(([key, level], index) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <IOSCard variant="elevated" className="overflow-hidden">
                  <div className="flex items-stretch">
                    {/* Level Indicator */}
                    <div
                      className="w-20 flex flex-col items-center justify-center py-4"
                      style={{ backgroundColor: levelColors[key] }}
                    >
                      <span className="text-white text-2xl font-bold">{key}</span>
                      <span className="text-white/80 text-xs mt-1">
                        {level.avgVLMScore}%
                      </span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 p-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                        {level.name}
                        <span className="text-gray-500 dark:text-gray-400 font-normal ml-2">
                          ({level.name_zh})
                        </span>
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {level.description}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {level.exampleTasks.map((task, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-400"
                          >
                            {task}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Score Bar */}
                    <div className="w-24 flex items-center px-3">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="h-2 rounded-full transition-all duration-500"
                          style={{
                            width: `${level.avgVLMScore}%`,
                            backgroundColor: levelColors[key],
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </IOSCard>
              </motion.div>
            ))}
          </div>
        )}
      </section>

      {/* 6D to 47D Expansion */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <GitBranch className="w-6 h-6 text-[#5F8A50]" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            6D to 47D Dimension Expansion
          </h2>
        </div>

        <IOSCard variant="elevated">
          <IOSCardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Core 6D Dimensions
                </h3>
                <ul className="space-y-2">
                  {[
                    { name: 'Creativity', color: '#FF6B6B' },
                    { name: 'Technique', color: '#4ECDC4' },
                    { name: 'Emotion', color: '#45B7D1' },
                    { name: 'Context', color: '#96CEB4' },
                    { name: 'Innovation', color: '#FFEAA7' },
                    { name: 'Impact', color: '#DDA0DD' },
                  ].map(dim => (
                    <li key={dim.name} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: dim.color }}
                      />
                      <span className="text-gray-700 dark:text-gray-300">{dim.name}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Expansion Algorithm
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Each 6D dimension expands into 7-8 sub-dimensions using an inter-dimensional
                  correlation matrix derived from art theory and empirical validation.
                </p>
                <div className="flex items-center gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-600">6</div>
                    <div className="text-gray-500">Core</div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-[#5F8A50]">47</div>
                    <div className="text-gray-500">Sub-dimensions</div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-amber-600">8</div>
                    <div className="text-gray-500">Perspectives</div>
                  </div>
                </div>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* Cultural Perspectives */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Globe className="w-6 h-6 text-[#B8923D]" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            8 Cultural Perspectives
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          VULCA evaluates art through 8 distinct cultural lenses, each with unique
          aesthetic values and interpretive frameworks.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { id: 'western', name: 'Western', emoji: '🏛️' },
            { id: 'eastern', name: 'Eastern', emoji: '🏯' },
            { id: 'african', name: 'African', emoji: '🌍' },
            { id: 'latin_american', name: 'Latin American', emoji: '🌺' },
            { id: 'middle_eastern', name: 'Middle Eastern', emoji: '🕌' },
            { id: 'south_asian', name: 'South Asian', emoji: '🪷' },
            { id: 'oceanic', name: 'Oceanic', emoji: '🌊' },
            { id: 'indigenous', name: 'Indigenous', emoji: '🌿' },
          ].map((perspective, index) => (
            <motion.div
              key={perspective.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
            >
              <IOSCard variant="flat" className="text-center p-4">
                <span className="text-3xl mb-2 block">{perspective.emoji}</span>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {perspective.name}
                </span>
              </IOSCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Historical Personas */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <Users className="w-6 h-6 text-slate-600" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Art Critic Personas
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Evaluations are grounded in the aesthetic theories of historical art critics,
          providing diverse and culturally-informed perspectives.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {personas.map((persona, index) => (
            <motion.div
              key={persona.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <IOSCard variant="elevated" className="h-full">
                <IOSCardContent>
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {persona.name}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {persona.name_zh}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {persona.era}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                    {persona.focus}
                  </p>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Technical Details */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Target className="w-6 h-6 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Technical Implementation
          </h2>
        </div>

        <IOSCard variant="elevated">
          <IOSCardContent>
            <div className="prose dark:prose-invert max-w-none">
              <h3>Algorithm Overview</h3>
              <ul>
                <li>
                  <strong>Inter-dimensional Correlation Matrix:</strong> A 6×47 matrix
                  mapping core dimensions to sub-dimensions based on art theory
                </li>
                <li>
                  <strong>Cultural Weight Adjustment:</strong> Perspective-specific
                  weights applied to emphasize culturally-relevant dimensions
                </li>
                <li>
                  <strong>Nonlinear Score Transformation:</strong> Sigmoid-based
                  normalization ensuring scores remain in valid ranges
                </li>
                <li>
                  <strong>Confidence Calibration:</strong> Model uncertainty quantification
                  using Monte Carlo dropout
                </li>
              </ul>

              <h3>Validation</h3>
              <p>
                The VULCA framework was validated against human expert annotations
                across 7,410 image-text pairs spanning 8 cultures. Inter-annotator
                agreement (Krippendorff's alpha) exceeded 0.85 for all core dimensions.
              </p>
            </div>
          </IOSCardContent>
        </IOSCard>
      </section>
    </motion.div>
  );
};

export default MethodologyPage;
