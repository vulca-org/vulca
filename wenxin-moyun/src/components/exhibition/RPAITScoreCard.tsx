/**
 * RPAITScoreCard Component
 *
 * Displays RPAIT 5-dimension scores with iOS-style design
 * R: Reasoning, P: Practical, A: Aesthetic, I: Innovation, T: Technical
 */

import { motion } from 'framer-motion';
import type { RPAITScores, Persona } from '../../types/exhibition';
import { RPAIT_LABELS, RPAIT_COLORS } from '../../types/exhibition';
import { IOSCard, IOSCardContent, IOSCardHeader } from '../ios';

interface RPAITScoreCardProps {
  scores: RPAITScores;
  persona?: Persona;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const DIMENSION_ORDER: (keyof RPAITScores)[] = ['R', 'P', 'A', 'I', 'T'];

export function RPAITScoreCard({
  scores,
  persona,
  showLabels = true,
  size = 'md',
  animated = true,
}: RPAITScoreCardProps) {
  const maxScore = 10;
  const average = DIMENSION_ORDER.reduce((sum, d) => sum + scores[d], 0) / 5;

  const barHeight = size === 'sm' ? 'h-2' : size === 'lg' ? 'h-4' : 'h-3';
  const fontSize = size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-base' : 'text-sm';

  return (
    <IOSCard variant="elevated" className="overflow-hidden">
      {persona && (
        <IOSCardHeader
          title={persona.nameEn}
          subtitle={persona.period}
          emoji={
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold"
              style={{ backgroundColor: persona.color }}
            >
              {persona.nameZh[0]}
            </div>
          }
        />
      )}
      <IOSCardContent className="space-y-3">
        {DIMENSION_ORDER.map((dimension, index) => (
          <div key={dimension} className="space-y-1">
            <div className={`flex items-center justify-between ${fontSize}`}>
              <span className="font-medium text-gray-700 dark:text-gray-300">
                {RPAIT_LABELS[dimension].en}
                {showLabels && (
                  <span className="ml-1 text-gray-500 dark:text-gray-400">
                    ({RPAIT_LABELS[dimension].zh})
                  </span>
                )}
              </span>
              <span
                className="font-bold"
                style={{ color: RPAIT_COLORS[dimension] }}
              >
                {scores[dimension]}
              </span>
            </div>
            <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full ${barHeight}`}>
              <motion.div
                className={`${barHeight} rounded-full`}
                style={{ backgroundColor: RPAIT_COLORS[dimension] }}
                initial={animated ? { width: 0 } : undefined}
                animate={{ width: `${(scores[dimension] / maxScore) * 100}%` }}
                transition={{
                  duration: 0.6,
                  delay: animated ? index * 0.1 : 0,
                  ease: 'easeOut',
                }}
              />
            </div>
          </div>
        ))}

        {/* Average Score */}
        <div className="pt-3 mt-3 border-t border-gray-200 dark:border-gray-700">
          <div className={`flex items-center justify-between ${fontSize}`}>
            <span className="font-semibold text-gray-900 dark:text-white">
              Overall
            </span>
            <span className="font-bold text-lg text-slate-600">
              {average.toFixed(1)}
            </span>
          </div>
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}

/**
 * Compact RPAIT badge for list views
 */
export function RPAITBadge({ scores }: { scores: RPAITScores }) {
  const average = DIMENSION_ORDER.reduce((sum, d) => sum + scores[d], 0) / 5;

  return (
    <div className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
      {DIMENSION_ORDER.map((d) => (
        <div
          key={d}
          className="w-5 h-5 rounded text-[10px] font-bold flex items-center justify-center text-white"
          style={{ backgroundColor: RPAIT_COLORS[d] }}
          title={`${RPAIT_LABELS[d].en}: ${scores[d]}`}
        >
          {scores[d]}
        </div>
      ))}
      <span className="ml-1 text-xs font-bold text-gray-600 dark:text-gray-400">
        {average.toFixed(1)}
      </span>
    </div>
  );
}

export default RPAITScoreCard;
