/**
 * Finalize Section — Publish button + cost/time stats.
 */

import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { Sparkles } from 'lucide-react';
import { API_PREFIX, getProtoAuthHeaders } from '@/config/api';

interface Props {
  taskId: string | null;
  pipelineStatus: string;
  totalLatencyMs: number;
  totalCostUsd: number;
  weightedTotal: number | null;
  onReset: () => void;
}

export default function FinalizeSection({ taskId, pipelineStatus, totalLatencyMs, totalCostUsd, weightedTotal, onReset }: Props) {
  const [publishing, setPublishing] = useState(false);
  const isComplete = pipelineStatus === 'completed';

  const handlePublish = useCallback(async () => {
    if (!taskId) return;
    setPublishing(true);
    try {
      const res = await fetch(`${API_PREFIX}/prototype/gallery/${taskId}/publish`, {
        method: 'POST',
        headers: getProtoAuthHeaders(),
      });
      if (res.ok) {
        toast.success('Published to Gallery!');
      } else {
        toast.error(`Publish failed (${res.status})`);
      }
    } catch {
      toast.error('Failed to publish — backend unavailable');
    } finally {
      setPublishing(false);
    }
  }, [taskId]);

  const latencyStr = totalLatencyMs > 0 ? `${(totalLatencyMs / 1000).toFixed(1)}s` : '—';
  const costStr = totalCostUsd > 0 ? `$${totalCostUsd.toFixed(2)}` : '—';
  const scoreStr = weightedTotal != null ? `${(weightedTotal * 100).toFixed(1)}%` : '—';

  return (
    <div className="mt-auto pt-6">
      {/* Stats row */}
      {isComplete && (
        <div className="flex items-center justify-between text-[10px] text-outline mb-4">
          <span>{scoreStr} score</span>
          <span>{latencyStr}</span>
          <span>{costStr}</span>
        </div>
      )}

      {/* Primary CTA */}
      <button
        onClick={isComplete ? handlePublish : onReset}
        disabled={publishing || (!isComplete && pipelineStatus !== 'failed' && pipelineStatus !== 'idle')}
        className="w-full bg-primary-500 text-white font-bold py-4 rounded-xl shadow-xl shadow-primary-500/20 hover:bg-primary-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
      >
        {isComplete ? (
          <>
            {publishing ? 'Publishing...' : 'Finalize Artifact'}
            <Sparkles className="w-4 h-4" />
          </>
        ) : pipelineStatus === 'waiting_human' ? (
          'Awaiting Your Input...'
        ) : pipelineStatus === 'failed' ? (
          'Retry'
        ) : pipelineStatus === 'idle' ? (
          'Start Pipeline'
        ) : (
          'Processing...'
        )}
      </button>

      {isComplete && (
        <button
          onClick={onReset}
          className="w-full text-center text-[11px] text-outline mt-3 hover:text-on-surface-variant transition-colors"
        >
          New creation →
        </button>
      )}
    </div>
  );
}
