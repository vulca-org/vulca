/**
 * Queen decision display + full HITL action controls.
 *
 * Supports: approve, reject, rerun (with dimension selection),
 * lock_dimensions, and force_accept (with candidate picker).
 */

import { useState } from 'react';
import type { QueenDecision, ScoredCandidate } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';

const DECISION_ICONS: Record<string, string> = {
  accept: '✅',
  stop: '🛑',
  rerun: '🔄',
  rerun_local: '🎯',
  downgrade: '⬇️',
};

const DECISION_COLORS: Record<string, string> = {
  accept: 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#4A7040] dark:text-[#87A878] border-[#5F8A50]/20 dark:border-[#4A7040]',
  stop: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
  rerun: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#334155] dark:text-[#DDA574] border-[#C9C2B8] dark:border-[#4A433C]',
  rerun_local: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#334155] dark:text-[#DDA574] border-[#C9C2B8] dark:border-[#4A433C]',
  downgrade: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
};

interface Props {
  decision: QueenDecision | null;
  finalDecision: string | null;
  status: string;
  scoredCandidates?: ScoredCandidate[];
  selectedCandidateId?: string | null;
  onAction?: (
    action: string,
    options?: {
      locked_dimensions?: string[];
      rerun_dimensions?: string[];
      candidate_id?: string;
      reason?: string;
    },
  ) => void;
}

export default function QueenDecisionPanel({
  decision, finalDecision, status, scoredCandidates, selectedCandidateId, onAction,
}: Props) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [lockedDims, setLockedDims] = useState<Set<string>>(new Set());
  const [rerunDims, setRerunDims] = useState<Set<string>>(new Set());
  const [reason, setReason] = useState('');

  if (!decision && !finalDecision) {
    return (
      <div className="py-4 text-center text-gray-400 dark:text-gray-500 text-sm">
        Waiting for Queen decision...
      </div>
    );
  }

  const d = decision;
  const action = finalDecision || d?.action || '?';
  const icon = DECISION_ICONS[action] || '❓';
  const colorClass = DECISION_COLORS[action] || 'bg-gray-100 dark:bg-gray-800';
  const isWaiting = status === 'waiting_human' && !!onAction;

  const toggleDim = (dim: string, set: Set<string>, setter: (s: Set<string>) => void) => {
    const next = new Set(set);
    if (next.has(dim)) next.delete(dim); else next.add(dim);
    setter(next);
  };

  const handleAction = (act: string) => {
    const opts: Record<string, unknown> = {};
    if (lockedDims.size > 0) opts.locked_dimensions = [...lockedDims];
    if (act === 'rerun' && rerunDims.size > 0) opts.rerun_dimensions = [...rerunDims];
    if (act === 'force_accept' && selectedCandidateId) opts.candidate_id = selectedCandidateId;
    if (reason.trim()) opts.reason = reason.trim();
    onAction?.(act, opts as Parameters<NonNullable<typeof onAction>>[1]);
  };

  return (
    <div className={`rounded-xl border p-4 ${colorClass}`}>
      {/* Decision header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-2xl mr-2">{icon}</span>
          <span className="text-lg font-bold uppercase">{action}</span>
          {d?.round && <span className="ml-2 text-sm opacity-70">Round {d.round}</span>}
        </div>
      </div>

      {d?.reason && (
        <p className="mt-2 text-sm opacity-80">{d.reason}</p>
      )}

      {d?.rerun_dimensions && d.rerun_dimensions.length > 0 && (
        <div className="mt-2">
          <span className="text-xs font-medium opacity-60">Queen suggests rerun:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {d.rerun_dimensions.map(dim => (
              <span key={dim} className="px-2 py-0.5 bg-white/50 dark:bg-black/20 rounded text-xs">
                {PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.short || dim.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* HITL Controls */}
      {isWaiting && (
        <div className="mt-4 pt-3 border-t border-current/10 space-y-3">
          {/* Quick actions */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleAction('approve')}
              className="px-4 py-2 bg-[#5F8A50] text-white rounded-lg text-sm font-medium hover:bg-[#4A7040] transition-colors"
            >
              Approve
            </button>
            <button
              onClick={() => handleAction('rerun')}
              className="px-4 py-2 bg-[#C87F4A] text-white rounded-lg text-sm font-medium hover:bg-[#A85D3B] transition-colors"
            >
              Rerun{rerunDims.size > 0 ? ` (${rerunDims.size} dims)` : ''}
            </button>
            <button
              onClick={() => handleAction('reject')}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
            >
              Reject
            </button>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              {showAdvanced ? 'Hide Advanced' : 'Advanced'}
            </button>
          </div>

          {/* Advanced HITL panel */}
          {showAdvanced && (
            <div className="bg-white/60 dark:bg-black/20 rounded-lg p-3 space-y-3">
              {/* Dimension lock */}
              <div>
                <label className="block text-xs font-semibold mb-1">Lock Dimensions (preserve scores)</label>
                <div className="flex flex-wrap gap-1">
                  {PROTOTYPE_DIMENSIONS.map(dim => (
                    <button
                      key={dim}
                      onClick={() => toggleDim(dim, lockedDims, setLockedDims)}
                      className={`px-2 py-1 rounded text-xs transition-colors ${
                        lockedDims.has(dim)
                          ? 'bg-[#5F8A50] text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                      }`}
                    >
                      {lockedDims.has(dim) ? '🔒 ' : ''}{PROTOTYPE_DIM_LABELS[dim].short}
                    </button>
                  ))}
                </div>
              </div>

              {/* Rerun dimension selection */}
              <div>
                <label className="block text-xs font-semibold mb-1">Rerun Dimensions (re-evaluate only these)</label>
                <div className="flex flex-wrap gap-1">
                  {PROTOTYPE_DIMENSIONS.filter(d => !lockedDims.has(d)).map(dim => (
                    <button
                      key={dim}
                      onClick={() => toggleDim(dim, rerunDims, setRerunDims)}
                      className={`px-2 py-1 rounded text-xs transition-colors ${
                        rerunDims.has(dim)
                          ? 'bg-[#C87F4A] text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                      }`}
                    >
                      {rerunDims.has(dim) ? '🔄 ' : ''}{PROTOTYPE_DIM_LABELS[dim].short}
                    </button>
                  ))}
                </div>
              </div>

              {/* Reason input */}
              <div>
                <label className="block text-xs font-semibold mb-1">Reason (optional)</label>
                <input
                  type="text"
                  value={reason}
                  onChange={e => setReason(e.target.value)}
                  placeholder="Why are you overriding?"
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                />
              </div>

              {/* Advanced actions */}
              <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => handleAction('lock_dimensions')}
                  disabled={lockedDims.size === 0}
                  className="px-3 py-1.5 bg-[#5F8A50] text-white rounded text-xs font-medium hover:bg-[#4A7040] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Lock {lockedDims.size} Dimensions
                </button>
                <button
                  onClick={() => handleAction('force_accept')}
                  disabled={!selectedCandidateId}
                  className="px-3 py-1.5 bg-[#B8923D] text-white rounded text-xs font-medium hover:bg-[#8F7030] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title={selectedCandidateId ? `Force accept: ${selectedCandidateId}` : 'Select a candidate first'}
                >
                  Force Accept{selectedCandidateId ? ` #${selectedCandidateId.split('-').pop()}` : ''}
                </button>
              </div>

              {scoredCandidates && scoredCandidates.length > 0 && !selectedCandidateId && (
                <p className="text-xs text-[#B8923D] dark:text-[#D4A94E]">
                  Tip: Click a candidate in the gallery above to select it for Force Accept.
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
