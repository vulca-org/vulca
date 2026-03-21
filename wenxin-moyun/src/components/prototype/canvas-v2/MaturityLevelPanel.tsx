/**
 * Maturity Level Panel — L1-L5 dimension buttons with lock/unlock + rationale.
 * Users can lock good dimensions and request refinement on weak ones.
 */

import { useState, useMemo, useCallback } from 'react';
import { Lock, Unlock } from 'lucide-react';
import type { ScoredCandidate } from '@/hooks/usePrototypePipeline';

interface Props {
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  lockedDimensions?: string[];
  onToggleLock?: (dimension: string) => void;
}

import { L_LABELS } from '@/utils/tradition-labels';

const DIM_TO_L: Record<string, string> = {
  visual_perception: 'L1', technical_analysis: 'L2', technical_execution: 'L2',
  cultural_context: 'L3', critical_interpretation: 'L4', philosophical_aesthetic: 'L5',
  L1: 'L1', L2: 'L2', L3: 'L3', L4: 'L4', L5: 'L5',
  '1': 'L1', '2': 'L2', '3': 'L3', '4': 'L4', '5': 'L5',
};

export default function MaturityLevelPanel({ scoredCandidates, bestCandidateId, lockedDimensions = [], onToggleLock }: Props) {
  const [selectedL, setSelectedL] = useState<string | null>(null);

  const bestCandidate = useMemo(() => {
    if (!scoredCandidates.length) return null;
    return scoredCandidates.find(c => c.candidate_id === bestCandidateId) || scoredCandidates[0];
  }, [scoredCandidates, bestCandidateId]);

  const scores = useMemo(() => {
    if (!bestCandidate?.dimension_scores) return {};
    const map: Record<string, { score: number; rationale: string }> = {};
    for (const ds of bestCandidate.dimension_scores) {
      const key = DIM_TO_L[ds.dimension] || (ds.dimension.startsWith('L') ? ds.dimension : `L${ds.dimension}`);
      map[key] = { score: ds.score, rationale: ds.rationale || '' };
    }
    return map;
  }, [bestCandidate]);

  const { highestL, lowestL } = useMemo(() => {
    let best = 'L1', worst = 'L5';
    let bestScore = -1, worstScore = 2;
    for (const [k, v] of Object.entries(scores)) {
      if (v.score > bestScore) { bestScore = v.score; best = k; }
      if (v.score < worstScore) { worstScore = v.score; worst = k; }
    }
    return { highestL: best, lowestL: worst };
  }, [scores]);

  const activeL = selectedL || highestL;
  const activeInfo = scores[activeL];
  const hasScores = Object.keys(scores).length > 0;

  const handleToggleLock = useCallback((l: string) => {
    if (onToggleLock) onToggleLock(l);
  }, [onToggleLock]);

  return (
    <div className="mb-8">
      <label className="text-[10px] font-black uppercase tracking-widest text-primary-500/70 block mb-4">
        Maturity Level Analysis
      </label>

      {/* L1-L5 button grid with lock indicators */}
      <div className="grid grid-cols-5 gap-2">
        {['L1', 'L2', 'L3', 'L4', 'L5'].map((l) => {
          const isActive = l === activeL && hasScores;
          const isLocked = lockedDimensions.includes(l);
          const score = scores[l]?.score;
          return (
            <div key={l} className="relative flex flex-col items-center">
              {isActive && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full border-2 border-white z-10 shadow-sm" />
              )}
              {isLocked && (
                <div className="absolute -top-1 -left-1 z-10">
                  <Lock className="w-3 h-3 text-cultural-amber-500" />
                </div>
              )}
              <button
                onClick={() => {
                  setSelectedL(l);
                  // Double-click to toggle lock
                  if (selectedL === l && hasScores) handleToggleLock(l);
                }}
                className={`w-full aspect-square rounded-xl flex items-center justify-center text-sm font-bold transition-all ${
                  isActive
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30 ring-2 ring-primary-500/20'
                    : isLocked
                      ? 'bg-cultural-amber-50 text-cultural-amber-700 ring-2 ring-cultural-amber-300'
                      : hasScores && score != null
                        ? 'bg-surface-container-lowest text-on-surface-variant shadow-ambient-sm hover:bg-white hover:ring-1 hover:ring-primary-500/20'
                        : 'bg-surface-container-high text-outline'
                }`}
                title={isLocked ? `${l} locked — click to unlock` : hasScores ? `Click to view, double-click to lock ${l}` : l}
              >
                {l}
              </button>
              {score != null && (
                <span className={`text-[9px] mt-1 font-bold ${isActive ? 'text-primary-500' : isLocked ? 'text-cultural-amber-600' : 'text-on-surface-variant'}`}>
                  {(score * 100).toFixed(0)}%
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Lock hint */}
      {hasScores && (
        <p className="text-[9px] text-outline mt-2 text-center">
          Click to view · Double-click to lock/unlock for refinement
        </p>
      )}

      {/* Rationale cards — show selected or default highest + lowest */}
      {hasScores && selectedL && activeInfo ? (
        <div className="mt-4 bg-surface-container-low/50 p-3 rounded-2xl">
          <p className="text-[10px] font-bold text-on-surface-variant mb-1">
            {L_LABELS[activeL] || activeL}
            {lockedDimensions.includes(activeL) && <span className="ml-1 text-cultural-amber-500">🔒 Locked</span>}
          </p>
          <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
            {activeInfo.rationale || 'No rationale available.'}
          </p>
        </div>
      ) : hasScores && highestL !== lowestL ? (
        <div className="mt-4 space-y-2">
          {/* Strongest dimension */}
          {scores[highestL]?.rationale && (
            <div className="bg-cultural-sage-50/60 p-3 rounded-2xl">
              <p className="text-[10px] font-bold text-cultural-sage-700 mb-1">
                Strongest: {highestL} {L_LABELS[highestL]} — {((scores[highestL]?.score ?? 0) * 100).toFixed(0)}%
              </p>
              <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
                {scores[highestL].rationale.length > 120 ? scores[highestL].rationale.slice(0, 120).replace(/\s+\S*$/, '') + '...' : scores[highestL].rationale}
              </p>
            </div>
          )}
          {/* Weakest dimension */}
          {scores[lowestL]?.rationale && (
            <div className="bg-cultural-coral-50/40 p-3 rounded-2xl">
              <p className="text-[10px] font-bold text-cultural-coral-600 mb-1">
                Needs work: {lowestL} {L_LABELS[lowestL]} — {((scores[lowestL]?.score ?? 0) * 100).toFixed(0)}%
              </p>
              <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
                {scores[lowestL].rationale.length > 120 ? scores[lowestL].rationale.slice(0, 120).replace(/\s+\S*$/, '') + '...' : scores[lowestL].rationale}
              </p>
            </div>
          )}
        </div>
      ) : hasScores && activeInfo ? (
        <div className="mt-4 bg-surface-container-low/50 p-3 rounded-2xl">
          <p className="text-[10px] font-bold text-on-surface-variant mb-1">{L_LABELS[activeL] || activeL}</p>
          <p className="text-[11px] text-on-surface-variant leading-relaxed italic">{activeInfo.rationale || 'No rationale available.'}</p>
        </div>
      ) : null}

      {!hasScores && (
        <p className="mt-4 text-[11px] text-outline italic">
          Scores will appear after the Critic evaluates the artwork.
        </p>
      )}
    </div>
  );
}
