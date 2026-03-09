/**
 * HITL panel for the Draft stage — allows users to select which candidates
 * to keep and optionally request more variants before Critic evaluation.
 *
 * Displayed when status === 'waiting_human' && hitlWaitInfo.stage === 'draft'.
 */

import { useState } from 'react';
import type { DraftCandidate } from '../../hooks/usePrototypePipeline';

interface Props {
  candidates: DraftCandidate[];
  onAction: (
    action: string,
    options?: { candidate_id?: string; reason?: string },
  ) => void;
}

export default function DraftSelectionPanel({ candidates, onAction }: Props) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(
    new Set(candidates.map(c => c.candidate_id)),
  );
  const [reason, setReason] = useState('');

  const toggleCandidate = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const handleProceed = () => {
    // Approve with the best selected candidate
    const firstSelected = candidates.find(c => selectedIds.has(c.candidate_id));
    onAction('approve', {
      candidate_id: firstSelected?.candidate_id,
      reason: reason || undefined,
    });
  };

  return (
    <div className="rounded-xl border border-[#C9C2B8] dark:border-[#4A433C] bg-[#FAF7F2] dark:bg-[#C87F4A]/10 p-4 space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xl">🎨</span>
        <h3 className="font-semibold text-[#334155] dark:text-[#DDA574]">
          Review Draft Candidates
        </h3>
        <span className="ml-auto text-xs text-[#C87F4A] dark:text-[#DDA574]">
          {selectedIds.size}/{candidates.length} selected
        </span>
      </div>

      <p className="text-xs text-[#C87F4A] dark:text-[#DDA574]">
        Select candidates to keep for Critic evaluation. Deselected candidates will be discarded.
      </p>

      {/* Candidate grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {candidates.map(c => {
          const isSelected = selectedIds.has(c.candidate_id);
          const shortId = c.candidate_id.split('-').pop() || c.candidate_id;
          return (
            <button
              key={c.candidate_id}
              onClick={() => toggleCandidate(c.candidate_id)}
              className={`relative rounded-lg border-2 p-2 text-left transition-colors ${
                isSelected
                  ? 'border-[#C87F4A] bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20'
                  : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 opacity-60'
              }`}
            >
              {/* Thumbnail placeholder */}
              <div className="w-full aspect-square bg-gray-200 dark:bg-gray-700 rounded mb-1 flex items-center justify-center text-gray-400 text-xs">
                {c.image_url ? (
                  <img src={c.image_url} alt={`Candidate ${shortId}`} className="w-full h-full object-cover rounded" />
                ) : (
                  `#${shortId}`
                )}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400 truncate">
                seed: {c.seed}
              </div>
              {isSelected && (
                <div className="absolute top-1 right-1 w-5 h-5 bg-[#C87F4A] rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#C87F4A] dark:text-[#DDA574] mb-1">
          Notes (optional)
        </label>
        <input
          type="text"
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="e.g., prefer more atmospheric depth, less saturated colors"
          className="w-full px-2 py-1.5 text-sm border border-[#C9C2B8] dark:border-[#4A433C] rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        />
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2 border-t border-[#C9C2B8] dark:border-[#4A433C]">
        <button
          onClick={handleProceed}
          disabled={selectedIds.size === 0}
          className="px-4 py-2 bg-[#5F8A50] text-white rounded-lg text-sm font-medium hover:bg-[#4A7040] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Proceed to Critic ({selectedIds.size} candidates)
        </button>
        <button
          onClick={() => onAction('rerun', { reason: reason || 'Generate more variants' })}
          className="px-4 py-2 bg-[#C87F4A] text-white rounded-lg text-sm font-medium hover:bg-[#A85D3B] transition-colors"
        >
          Request More Variants
        </button>
        <button
          onClick={() => onAction('reject', { reason: reason || 'No suitable candidates' })}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Reject & Stop
        </button>
      </div>
    </div>
  );
}
