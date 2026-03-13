/**
 * CritiqueViewer Component
 *
 * Displays RPAIT critiques from multiple personas with iOS-style design
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Critique, Persona } from '../../types/exhibition';
import { IOSCard, IOSCardContent, IOSCardHeader } from '../ios';
import { RPAITScoreCard, RPAITBadge } from './RPAITScoreCard';
import { SinglePersonaRadar } from './RPAITRadar';

interface CritiqueViewerProps {
  critiques: Critique[];
  personas: Persona[];
  artworkTitle: string;
}

export function CritiqueViewer({
  critiques,
  personas,
  artworkTitle,
}: CritiqueViewerProps) {
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(
    critiques[0]?.personaId || null
  );
  const [language, setLanguage] = useState<'en' | 'zh'>('zh');

  if (critiques.length === 0) {
    return null;
  }

  const selectedCritique = critiques.find((c) => c.personaId === selectedPersonaId);
  const selectedPersona = personas.find((p) => p.id === selectedPersonaId);

  return (
    <IOSCard variant="elevated">
      <IOSCardHeader
        title="RPAIT Art Critiques"
        subtitle={`AI-generated critiques for "${artworkTitle}"`}
        action={
          <div className="flex gap-1">
            {(['en', 'zh'] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`px-2 py-1 text-xs rounded-md transition-colors ${
                  language === lang
                    ? 'bg-slate-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                }`}
              >
                {lang === 'en' ? 'EN' : '中'}
              </button>
            ))}
          </div>
        }
      />

      <IOSCardContent className="space-y-4">
        {/* Persona Selector */}
        <div className="flex flex-wrap gap-2 pb-4 border-b border-gray-200 dark:border-gray-700">
          {personas.map((persona) => {
            const critique = critiques.find((c) => c.personaId === persona.id);
            if (!critique) return null;

            return (
              <button
                key={persona.id}
                onClick={() => setSelectedPersonaId(persona.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl transition-all ${
                  selectedPersonaId === persona.id
                    ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold"
                  style={{ backgroundColor: persona.color }}
                >
                  {persona.nameZh[0]}
                </div>
                <span className="text-sm font-medium">
                  {language === 'zh' ? persona.nameZh : persona.nameEn}
                </span>
              </button>
            );
          })}
        </div>

        {/* Selected Critique Content */}
        <AnimatePresence mode="wait">
          {selectedCritique && selectedPersona && (
            <motion.div
              key={selectedPersonaId}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="space-y-4"
            >
              {/* Persona Info */}
              <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                <div
                  className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-bold"
                  style={{ backgroundColor: selectedPersona.color }}
                >
                  {selectedPersona.nameZh[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {language === 'zh' ? selectedPersona.nameZh : selectedPersona.nameEn}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {selectedPersona.period}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {selectedPersona.bias}
                  </p>
                </div>
                <RPAITBadge scores={selectedCritique.rpait} />
              </div>

              {/* Critique Text */}
              <div className="p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {language === 'zh' ? selectedCritique.textZh : selectedCritique.textEn}
                </p>
              </div>

              {/* RPAIT Radar */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Score Distribution
                  </h5>
                  <SinglePersonaRadar
                    scores={selectedCritique.rpait}
                    color={selectedPersona.color}
                    size="md"
                  />
                </div>
                <div>
                  <RPAITScoreCard
                    scores={selectedCritique.rpait}
                    showLabels={true}
                    size="sm"
                    animated={false}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </IOSCardContent>
    </IOSCard>
  );
}

/**
 * Compact critique list for artwork cards
 */
export function CritiqueList({
  critiques,
  personas,
}: {
  critiques: Critique[];
  personas: Persona[];
}) {
  if (critiques.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">RPAIT Critiques:</p>
      <div className="flex flex-wrap gap-1.5">
        {critiques.map((critique) => {
          const persona = personas.find((p) => p.id === critique.personaId);
          if (!persona) return null;

          const average =
            (critique.rpait.R +
              critique.rpait.P +
              critique.rpait.A +
              critique.rpait.I +
              critique.rpait.T) /
            5;

          return (
            <div
              key={critique.personaId}
              className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg"
              title={`${persona.nameEn}: ${average.toFixed(1)}/10`}
            >
              <div
                className="w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px] font-bold"
                style={{ backgroundColor: persona.color }}
              >
                {persona.nameZh[0]}
              </div>
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                {average.toFixed(1)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default CritiqueViewer;
