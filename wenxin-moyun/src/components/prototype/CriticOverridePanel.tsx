/**
 * HITL panel for the Critic stage — allows users to lock or override
 * individual dimension scores before Queen evaluation.
 *
 * Displayed when status === 'waiting_human' && hitlWaitInfo.stage === 'critic'.
 */

import { useState } from 'react';
import type { ScoredCandidate } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';

interface Props {
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  onAction: (
    action: string,
    options?: {
      locked_dimensions?: string[];
      reason?: string;
    },
  ) => void;
}

export default function CriticOverridePanel({ scoredCandidates, bestCandidateId, onAction }: Props) {
  const [lockedDims, setLockedDims] = useState<Set<string>>(new Set());
  const [reason, setReason] = useState('');

  const bestCandidate = scoredCandidates.find(c => c.candidate_id === bestCandidateId)
    || scoredCandidates[0];

  const toggleDim = (dim: string) => {
    setLockedDims(prev => {
      const next = new Set(prev);
      if (next.has(dim)) next.delete(dim); else next.add(dim);
      return next;
    });
  };

  const handleApprove = () => {
    const opts: { locked_dimensions?: string[]; reason?: string } = {};
    if (lockedDims.size > 0) opts.locked_dimensions = [...lockedDims];
    if (reason.trim()) opts.reason = reason.trim();
    onAction('approve', Object.keys(opts).length > 0 ? opts : undefined);
  };

  return (
    <div className="rounded-xl border border-[#C9C2B8] dark:border-[#4A433C] bg-[#C87F4A]/5 dark:bg-[#C87F4A]/10 p-4 space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xl">📊</span>
        <h3 className="font-semibold text-on-surface">
          Review Critic Scores
        </h3>
        {bestCandidate && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-[#C87F4A]/20 text-on-surface">
            Best: {bestCandidate.weighted_total.toFixed(3)}
          </span>
        )}
      </div>

      <p className="text-xs text-[#C87F4A] dark:text-[#DDA574]">
        Lock dimensions whose scores you agree with. Locked dimensions will be preserved across reruns.
      </p>

      {/* Dimension scores with lock toggles */}
      {bestCandidate && (
        <div className="space-y-1">
          {PROTOTYPE_DIMENSIONS.map(dim => {
            const ds = bestCandidate.dimension_scores.find(d => d.dimension === dim);
            const score = ds?.score ?? 0;
            const label = PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.short || dim;
            const isLocked = lockedDims.has(dim);
            const barWidth = `${Math.min(score * 100, 100)}%`;
            const barColor = score >= 0.8 ? 'bg-[#5F8A50]' : score >= 0.5 ? 'bg-amber-500' : 'bg-red-500';

            return (
              <button
                key={dim}
                onClick={() => toggleDim(dim)}
                className={`w-full flex items-center gap-2 p-2 rounded-lg transition-colors text-left ${
                  isLocked
                    ? 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20 ring-2 ring-[#C87F4A]'
                    : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750'
                }`}
              >
                <span className="text-xs w-5">{isLocked ? '🔒' : ''}</span>
                <span className="text-xs font-medium w-16 text-gray-700 dark:text-gray-300">
                  {label}
                </span>
                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div className={`h-full ${barColor} rounded-full transition-all`} style={{ width: barWidth }} />
                </div>
                <span className="text-xs font-mono w-10 text-right text-gray-600 dark:text-gray-400">
                  {score.toFixed(2)}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Risk tags */}
      {bestCandidate && bestCandidate.risk_tags.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-red-600 dark:text-red-400 mb-1">Risk Tags</h4>
          <div className="flex flex-wrap gap-1">
            {bestCandidate.risk_tags.map((tag, i) => (
              <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 rounded text-xs text-red-700 dark:text-red-300">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      <div>
        <label className="block text-xs font-semibold text-[#C87F4A] dark:text-[#DDA574] mb-1">
          Override Notes (optional)
        </label>
        <input
          type="text"
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="e.g., L5 score seems too low for this tradition"
          className="w-full px-2 py-1.5 text-sm border border-[#C87F4A]/30 dark:border-[#4A433C] rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        />
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2 border-t border-[#C9C2B8] dark:border-[#4A433C]">
        <button
          onClick={handleApprove}
          className="px-4 py-2 bg-[#5F8A50] text-white rounded-lg text-sm font-medium hover:bg-[#4A7040] transition-colors"
        >
          Approve Scores{lockedDims.size > 0 ? ` (${lockedDims.size} locked)` : ''}
        </button>
        <button
          onClick={() => onAction('rerun', { reason: reason || 'Re-evaluate scores' })}
          className="px-4 py-2 bg-[#C87F4A] text-white rounded-lg text-sm font-medium hover:bg-[#A85D3B] transition-colors"
        >
          Re-evaluate
        </button>
        <button
          onClick={() => onAction('reject', { reason: reason || 'Scores unacceptable' })}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Reject & Stop
        </button>
      </div>
    </div>
  );
}
