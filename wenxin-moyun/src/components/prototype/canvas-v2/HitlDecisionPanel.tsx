/**
 * HITL Decision Panel — Accept/Refine/Reject buttons for human-in-the-loop.
 * Shows when pipeline is waiting_human or completed (before finalize).
 */

import { Check, RefreshCw, X } from 'lucide-react';

interface Props {
  pipelineStatus: string;
  lockedDimensions: string[];
  weakestDimensions?: string[];
  onAction: (action: string, options?: Record<string, unknown>) => Promise<void>;
}

export default function HitlDecisionPanel({ pipelineStatus, lockedDimensions, weakestDimensions, onAction }: Props) {
  const showPanel = pipelineStatus === 'waiting_human' || pipelineStatus === 'completed';
  if (!showPanel) return null;

  const rerunDimensions = weakestDimensions?.filter(d => !lockedDimensions.includes(d)) || [];

  return (
    <div className="mb-6">
      <label className="text-[10px] font-black uppercase tracking-widest text-outline block mb-3">
        {pipelineStatus === 'waiting_human' ? 'Your Decision' : 'Refine Further?'}
      </label>

      {/* Improvement suggestion */}
      {rerunDimensions.length > 0 && (
        <div className="bg-cultural-amber-50 rounded-lg p-3 mb-3">
          <p className="text-[11px] text-cultural-amber-700 font-medium">
            Suggested focus: {rerunDimensions.join(', ')} could be improved
          </p>
        </div>
      )}

      {/* Decision buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => onAction('approve')}
          className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-cultural-sage-500 text-white rounded-xl text-sm font-semibold hover:bg-cultural-sage-600 active:scale-[0.98] transition-all"
        >
          <Check className="w-4 h-4" />
          Accept
        </button>
        <button
          onClick={() => onAction('rerun', { locked_dimensions: lockedDimensions, rerun_dimensions: rerunDimensions })}
          className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-primary-500 text-white rounded-xl text-sm font-semibold hover:bg-primary-600 active:scale-[0.98] transition-all"
        >
          <RefreshCw className="w-4 h-4" />
          Refine
        </button>
        <button
          onClick={() => onAction('reject')}
          className="flex items-center justify-center gap-1.5 py-2.5 px-4 bg-surface-container-high text-on-surface-variant rounded-xl text-sm font-medium hover:bg-cultural-coral-50 hover:text-cultural-coral-600 active:scale-[0.98] transition-all"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Locked dimensions summary */}
      {lockedDimensions.length > 0 && (
        <p className="text-[10px] text-on-surface-variant mt-2">
          🔒 Locked: {lockedDimensions.join(', ')} — these will be preserved during refinement
        </p>
      )}
    </div>
  );
}
