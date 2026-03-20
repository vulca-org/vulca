/**
 * Maturity Level Panel — L1-L5 dimension buttons + rationale.
 * Maps scored candidate dimension scores to visual buttons.
 */

import { useState, useMemo } from 'react';
import type { ScoredCandidate } from '@/hooks/usePrototypePipeline';

interface Props {
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
}

const L_LABELS: Record<string, string> = {
  L1: 'Visual Perception',
  L2: 'Technical Execution',
  L3: 'Cultural Context',
  L4: 'Critical Interpretation',
  L5: 'Philosophical Aesthetics',
};

export default function MaturityLevelPanel({ scoredCandidates, bestCandidateId }: Props) {
  const [selectedL, setSelectedL] = useState<string | null>(null);

  const bestCandidate = useMemo(() => {
    if (!scoredCandidates.length) return null;
    return scoredCandidates.find(c => c.candidate_id === bestCandidateId) || scoredCandidates[0];
  }, [scoredCandidates, bestCandidateId]);

  const scores = useMemo(() => {
    if (!bestCandidate?.dimension_scores) return {};
    const DIM_TO_L: Record<string, string> = {
      visual_perception: 'L1', technical_analysis: 'L2', technical_execution: 'L2',
      cultural_context: 'L3', critical_interpretation: 'L4', philosophical_aesthetic: 'L5',
      L1: 'L1', L2: 'L2', L3: 'L3', L4: 'L4', L5: 'L5',
      '1': 'L1', '2': 'L2', '3': 'L3', '4': 'L4', '5': 'L5',
    };
    const map: Record<string, { score: number; rationale: string }> = {};
    for (const ds of bestCandidate.dimension_scores) {
      const key = DIM_TO_L[ds.dimension] || (ds.dimension.startsWith('L') ? ds.dimension : `L${ds.dimension}`);
      map[key] = { score: ds.score, rationale: ds.rationale || '' };
    }
    return map;
  }, [bestCandidate]);

  const highestL = useMemo(() => {
    let best = 'L1';
    let bestScore = 0;
    for (const [k, v] of Object.entries(scores)) {
      if (v.score > bestScore) {
        bestScore = v.score;
        best = k;
      }
    }
    return best;
  }, [scores]);

  const activeL = selectedL || highestL;
  const activeInfo = scores[activeL];
  const hasScores = Object.keys(scores).length > 0;

  return (
    <div className="mb-8">
      <label className="text-[10px] font-black uppercase tracking-widest text-primary-500/70 block mb-4">
        Maturity Level Analysis
      </label>

      {/* L1-L5 button grid */}
      <div className="grid grid-cols-5 gap-2">
        {['L1', 'L2', 'L3', 'L4', 'L5'].map((l) => {
          const isActive = l === activeL && hasScores;
          const score = scores[l]?.score;
          return (
            <div key={l} className="relative flex flex-col items-center">
              {isActive && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full border-2 border-white z-10 shadow-sm" />
              )}
              <button
                onClick={() => setSelectedL(l)}
                className={`w-full aspect-square rounded-xl flex items-center justify-center text-sm font-bold transition-all ${
                  isActive
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30 ring-2 ring-primary-500/20'
                    : hasScores && score != null
                      ? 'bg-surface-container-lowest text-on-surface-variant shadow-ambient-sm hover:bg-white hover:ring-1 hover:ring-primary-500/20'
                      : 'bg-surface-container-high text-outline'
                }`}
              >
                {l}
              </button>
              {score != null && (
                <span className={`text-[9px] mt-1 font-bold ${isActive ? 'text-primary-500' : 'text-on-surface-variant'}`}>
                  {(score * 100).toFixed(0)}%
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Rationale card */}
      {hasScores && activeInfo && (
        <div className="mt-4 bg-surface-container-low/50 p-3 rounded-lg">
          <p className="text-[10px] font-bold text-on-surface-variant mb-1">
            {L_LABELS[activeL] || activeL}
          </p>
          <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
            {activeInfo.rationale || 'No rationale available.'}
          </p>
        </div>
      )}

      {!hasScores && (
        <p className="mt-4 text-[11px] text-outline italic">
          Scores will appear after the Critic evaluates the artwork.
        </p>
      )}
    </div>
  );
}
