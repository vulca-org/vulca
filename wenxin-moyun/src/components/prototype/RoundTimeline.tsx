/**
 * Round-by-round timeline visualizing the Agent self-correction loop.
 *
 * Shows each round as a card with: candidate count, weighted score,
 * L1-L5 mini bars, Queen decision, and score delta vs previous round.
 */

import type { RoundData } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';

const DECISION_STYLES: Record<string, { icon: string; bg: string; text: string }> = {
  accept:    { icon: '\u2705', bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  stop:      { icon: '\u{1F6D1}', bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
  rerun:     { icon: '\u{1F504}', bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' },
  rerun_local: { icon: '\u{1F3AF}', bg: 'bg-indigo-100 dark:bg-indigo-900/30', text: 'text-indigo-700 dark:text-indigo-400' },
  downgrade: { icon: '\u2B07\uFE0F', bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400' },
};

interface Props {
  rounds: RoundData[];
  currentRound: number;
  status: string;
}

function MiniScoreBars({ scores }: { scores: { dimension: string; score: number }[] }) {
  const dims = PROTOTYPE_DIMENSIONS;
  return (
    <div className="flex gap-0.5 items-end h-8">
      {dims.map(dim => {
        const found = scores.find(s => s.dimension === dim);
        const score = found?.score ?? 0;
        const pct = Math.round(score * 100);
        const info = PROTOTYPE_DIM_LABELS[dim as PrototypeDimension];
        return (
          <div key={dim} className="flex flex-col items-center gap-0.5">
            <div
              className={`w-3 ${info?.color ?? 'bg-gray-400'} rounded-t-sm transition-all`}
              style={{ height: `${Math.max(pct * 0.28, 2)}px` }}
              title={`${info?.layer ?? dim}: ${score.toFixed(2)}`}
            />
            <span className="text-[8px] text-gray-400 leading-none">{info?.layer}</span>
          </div>
        );
      })}
    </div>
  );
}

function ScoreDelta({ current, previous }: { current: number | null; previous: number | null }) {
  if (current === null || previous === null) return null;
  const delta = current - previous;
  if (Math.abs(delta) < 0.001) {
    return <span className="text-[10px] text-gray-400 font-mono">=0</span>;
  }
  const isUp = delta > 0;
  return (
    <span className={`text-[10px] font-mono ${isUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
      {isUp ? '+' : ''}{delta.toFixed(3)}
    </span>
  );
}

export default function RoundTimeline({ rounds, currentRound, status }: Props) {
  if (rounds.length === 0) {
    if (status === 'running' && currentRound > 0) {
      return (
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          Round {currentRound} in progress...
        </div>
      );
    }
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Agent Loop</h3>
        <span className="text-xs text-gray-400">
          {rounds.length} round{rounds.length > 1 ? 's' : ''}
          {rounds[0]?.decision?.budget_state && (
            <> / max {rounds[0].decision.budget_state.max_rounds}</>
          )}
        </span>
      </div>

      <div className="flex items-stretch gap-2 overflow-x-auto pb-1">
        {rounds.map((rd, i) => {
          const prevRound = i > 0 ? rounds[i - 1] : null;
          const style = DECISION_STYLES[rd.decision?.action ?? ''] ?? DECISION_STYLES.stop;
          const bestScores = rd.scoredCandidates.length > 0
            ? rd.scoredCandidates.reduce((best, sc) =>
                sc.weighted_total > (best?.weighted_total ?? -1) ? sc : best
              ).dimension_scores
            : [];

          return (
            <div key={rd.round} className="flex items-stretch">
              {/* Connector arrow */}
              {i > 0 && (
                <div className="flex items-center px-1">
                  <div className="flex items-center gap-0.5">
                    <div className="w-4 h-0.5 bg-gray-300 dark:bg-gray-600" />
                    <span className="text-gray-400 text-xs">&rarr;</span>
                    <div className="w-4 h-0.5 bg-gray-300 dark:bg-gray-600" />
                  </div>
                </div>
              )}

              {/* Round card */}
              <div className={`
                flex flex-col rounded-xl border p-3 min-w-[160px] transition-all
                ${style.bg} border-gray-200 dark:border-gray-700
              `}>
                {/* Round header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-gray-600 dark:text-gray-300">
                    R{rd.round}
                  </span>
                  <div className="flex items-center gap-1">
                    <span className="text-sm">{style.icon}</span>
                    <span className={`text-[10px] font-semibold uppercase ${style.text}`}>
                      {rd.decision?.action ?? '?'}
                    </span>
                  </div>
                </div>

                {/* L1-L5 mini bars */}
                <MiniScoreBars scores={bestScores} />

                {/* Weighted total + delta */}
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500 dark:text-gray-400">Score</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold font-mono text-gray-800 dark:text-gray-200">
                      {rd.weightedTotal !== null ? rd.weightedTotal.toFixed(3) : '—'}
                    </span>
                    <ScoreDelta current={rd.weightedTotal} previous={prevRound?.weightedTotal ?? null} />
                  </div>
                </div>

                {/* Budget info */}
                {rd.decision?.budget_state && (
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-[10px] text-gray-400">Images</span>
                    <span className="text-[10px] font-mono text-gray-500 dark:text-gray-400">
                      {rd.decision.budget_state.candidates_generated}
                    </span>
                  </div>
                )}

                {/* Decision reason */}
                {rd.decision?.reason && (
                  <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-1.5 leading-tight line-clamp-2" title={rd.decision.reason}>
                    {rd.decision.reason}
                  </p>
                )}

                {/* FixItPlan indicator */}
                {rd.fixItPlan && (
                  <div className="mt-1.5 flex items-center gap-1">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 font-medium">
                      FixIt: {rd.fixItPlan.overall_strategy.replace(/_/g, ' ')}
                    </span>
                  </div>
                )}

                {/* Cross-layer signals */}
                {rd.crossLayerSignals && rd.crossLayerSignals.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-0.5">
                    {rd.crossLayerSignals.slice(0, 3).map((sig, j) => (
                      <span
                        key={j}
                        className="text-[8px] px-1 py-0.5 rounded bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400"
                        title={sig.message}
                      >
                        {sig.signal_type}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Active round indicator */}
        {status === 'running' && currentRound > rounds.length && (
          <div className="flex items-stretch">
            <div className="flex items-center px-1">
              <div className="flex items-center gap-0.5">
                <div className="w-4 h-0.5 bg-gray-300 dark:bg-gray-600" />
                <span className="text-gray-400 text-xs">&rarr;</span>
                <div className="w-4 h-0.5 bg-gray-300 dark:bg-gray-600" />
              </div>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-blue-300 dark:border-blue-700 p-3 min-w-[120px]">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-1" />
              <span className="text-xs text-blue-500 font-medium">R{currentRound}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
