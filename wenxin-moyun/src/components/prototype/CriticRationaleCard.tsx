/**
 * Critic rationale card — shows LLM analysis details for the best candidate.
 *
 * Enhancements:
 * - L1-L5 dimension colour coding
 * - Bracketed text [cultural analysis] highlighted as tags
 * - Mini progress bar next to score badge
 */

import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';
import { PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';
import type { ScoredCandidate } from '../../hooks/usePrototypePipeline';

// L1-L5 colour scheme
const DIM_COLORS: Record<string, { text: string; bg: string; bar: string }> = {
  L1: { text: 'text-[#C87F4A] dark:text-[#DDA574]',   bg: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15',     bar: 'bg-[#C87F4A]' },
  L2: { text: 'text-cyan-600 dark:text-cyan-400',   bg: 'bg-cyan-100 dark:bg-cyan-900/30',     bar: 'bg-cyan-500' },
  L3: { text: 'text-orange-600 dark:text-orange-400', bg: 'bg-orange-100 dark:bg-orange-900/30', bar: 'bg-orange-500' },
  L4: { text: 'text-red-600 dark:text-red-400',     bg: 'bg-red-100 dark:bg-red-900/30',       bar: 'bg-red-500' },
  L5: { text: 'text-[#C87F4A] dark:text-[#DDA574]', bg: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15', bar: 'bg-[#C87F4A]' },
};

/** Extract L-level from dimension name. */
function dimLevel(dim: string): string | null {
  // Check if dimension starts with L1-L5 pattern
  const match = dim.match(/^(L[1-5])/i);
  if (match) return match[1].toUpperCase();
  // Map known dimension names to levels
  const levelMap: Record<string, string> = {
    technical_quality: 'L1', composition: 'L1',
    style_fidelity: 'L2', aesthetic_quality: 'L2',
    cultural_accuracy: 'L3', cultural_context: 'L3',
    creative_innovation: 'L4', innovation: 'L4',
    emotional_resonance: 'L5', cultural_depth: 'L5',
  };
  return levelMap[dim.toLowerCase()] || null;
}

function getDimColor(dim: string) {
  const level = dimLevel(dim);
  return level ? DIM_COLORS[level] : null;
}

/** Score-based colour for the mini progress bar. */
function scoreBarColor(score: number): string {
  if (score >= 0.8) return 'bg-[#5F8A50]';
  if (score >= 0.5) return 'bg-yellow-500';
  return 'bg-red-500';
}

/** Highlight [bracketed text] as cultural analysis tags. */
function renderRationale(text: string) {
  const parts = text.split(/(\[[^\]]+\])/g);
  return parts.map((part, i) => {
    if (part.startsWith('[') && part.endsWith(']')) {
      return (
        <span key={i} className="bg-amber-100 dark:bg-amber-900/30 px-1 rounded text-amber-800 dark:text-amber-300">
          {part}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

function formatDimension(dim: string): string {
  return PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.short || dim.replace(/_/g, ' ');
}

interface Props {
  scoredCandidates: ScoredCandidate[];
}

export default function CriticRationaleCard({ scoredCandidates }: Props) {
  // Only render if there are meaningful rationales
  const hasRationale = scoredCandidates.some(sc =>
    sc.dimension_scores.some(ds => ds.rationale && ds.rationale.length > 20)
  );
  if (!hasRationale) return null;

  const best = scoredCandidates.reduce((a, b) =>
    b.weighted_total > a.weighted_total ? b : a
  );
  const rationaleDims = best.dimension_scores.filter(ds => ds.rationale && ds.rationale.length > 20);

  return (
    <IOSCard variant="elevated" padding="md" animate={false}>
      <IOSCardHeader title="Rationale" subtitle="LLM analysis" />
      <IOSCardContent>
        <div className="space-y-2">
          {rationaleDims.map((ds, i) => {
            const color = getDimColor(ds.dimension);
            const level = dimLevel(ds.dimension);

            return (
              <div key={i} className="p-2.5 rounded-lg bg-gray-50 dark:bg-gray-900/40">
                <div className="flex items-center gap-2 mb-1">
                  {/* Dimension level badge */}
                  {level && color && (
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${color.bg} ${color.text}`}>
                      {level}
                    </span>
                  )}
                  <span className={`text-xs font-bold ${color?.text || 'text-gray-600 dark:text-gray-300'}`}>
                    {formatDimension(ds.dimension)}
                  </span>
                  {/* Score badge */}
                  <span className="text-xs font-mono text-gray-500">{ds.score.toFixed(2)}</span>
                  {/* Mini progress bar */}
                  <div className="flex-1 max-w-[60px] h-1 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${scoreBarColor(ds.score)}`}
                      style={{ width: `${Math.min(ds.score * 100, 100)}%` }}
                    />
                  </div>
                  {ds.agent_metadata && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574]">
                      {ds.agent_metadata.mode}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                  {renderRationale(ds.rationale)}
                </p>
              </div>
            );
          })}
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}
