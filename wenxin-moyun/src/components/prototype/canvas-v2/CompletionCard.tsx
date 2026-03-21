/**
 * CompletionCard — Unified completion experience combining:
 *   - Score summary + strongest/weakest rationale
 *   - Confidence / Cost / Latency stats
 *   - Feedback collector (5-star + comment)
 *   - Finalize (Publish) + New creation actions
 *
 * Shown in the right panel only when pipeline status === 'completed'.
 */

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';
import { API_PREFIX, getProtoAuthHeaders } from '@/config/api';
import { L_LABELS } from '@/utils/tradition-labels';
import type { ScoredCandidate } from '@/hooks/usePrototypePipeline';

interface Props {
  taskId: string | null;
  totalLatencyMs: number;
  totalCostUsd: number;
  weightedTotal: number | null;
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  tradition: string;
  scoresSnapshot: Record<string, number>;
  onReset: () => void;
}

type FeedbackStatus = 'idle' | 'submitting' | 'success' | 'error';

export default function CompletionCard({
  taskId, totalLatencyMs, totalCostUsd, weightedTotal,
  scoredCandidates, bestCandidateId, tradition, scoresSnapshot, onReset,
}: Props) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [comment, setComment] = useState('');
  const [feedbackStatus, setFeedbackStatus] = useState<FeedbackStatus>('idle');
  const [publishing, setPublishing] = useState(false);

  const displayRating = hoveredStar || rating;

  // Find best candidate's scores + rationales
  const best = scoredCandidates.find(c => c.candidate_id === bestCandidateId) || scoredCandidates[0];
  const dimScores = best?.dimension_scores || [];

  let strongest = { dim: 'L1', label: '', score: 0, rationale: '' };
  let weakest = { dim: 'L5', label: '', score: 1, rationale: '' };
  for (const ds of dimScores) {
    const l = ds.dimension.startsWith('L') ? ds.dimension : `L${ds.dimension}`;
    if (ds.score > strongest.score) strongest = { dim: l, label: L_LABELS[l] || l, score: ds.score, rationale: ds.rationale || '' };
    if (ds.score < weakest.score) weakest = { dim: l, label: L_LABELS[l] || l, score: ds.score, rationale: ds.rationale || '' };
  }

  // Truncate at word boundary
  const truncate = (s: string, max: number) =>
    s.length > max ? s.slice(0, max).replace(/\s+\S*$/, '') + '...' : s;

  // Publish to gallery
  const handlePublish = useCallback(async () => {
    if (!taskId) return;
    setPublishing(true);
    try {
      const res = await fetch(`${API_PREFIX}/prototype/gallery/${taskId}/publish`, {
        method: 'POST',
        headers: getProtoAuthHeaders(),
      });
      if (res.ok) toast.success('Published to Gallery!');
      else toast.error(`Publish failed (${res.status})`);
    } catch {
      toast.error('Failed to publish');
    } finally {
      setPublishing(false);
    }
  }, [taskId]);

  // Submit feedback
  const handleFeedback = useCallback(async () => {
    if (rating === 0 || !taskId) return;
    setFeedbackStatus('submitting');
    try {
      const res = await fetch(`${API_PREFIX}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getProtoAuthHeaders() },
        body: JSON.stringify({
          evaluation_id: taskId,
          rating: rating >= 3 ? 'thumbs_up' : 'thumbs_down',
          comment: comment ? `[${rating}/5] ${comment}` : `[${rating}/5]`,
          feedback_type: 'explicit',
          candidate_id: bestCandidateId || '',
          tradition: tradition || '',
          scores_snapshot: scoresSnapshot || null,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setFeedbackStatus('success');
      toast.success('Feedback submitted — thank you!');
    } catch {
      setFeedbackStatus('error');
    }
  }, [rating, comment, taskId, bestCandidateId, tradition, scoresSnapshot]);

  const latencyStr = totalLatencyMs > 0 ? `${(totalLatencyMs / 1000).toFixed(1)}s` : '—';
  const costStr = totalCostUsd > 0 ? `$${totalCostUsd.toFixed(2)}` : '—';
  const scoreStr = weightedTotal != null ? `${(weightedTotal * 100).toFixed(0)}` : '—';

  return (
    <div className="bg-white rounded-2xl p-5 shadow-ambient-md space-y-5">
      {/* Header: Score + Stats */}
      <div className="flex items-center gap-4">
        <div className="text-4xl font-bold text-primary-500">{scoreStr}</div>
        <div className="flex-1">
          <div className="text-sm font-semibold text-on-surface">Cultural Score</div>
          <div className="flex items-center gap-3 text-[10px] text-on-surface-variant mt-0.5">
            <span>{latencyStr}</span>
            <span>{costStr}</span>
          </div>
        </div>
      </div>

      {/* Strongest + Weakest rationale */}
      {dimScores.length > 0 && strongest.dim !== weakest.dim && (
        <div className="space-y-2">
          {strongest.rationale && (
            <div className="bg-cultural-sage-50/60 p-3 rounded-2xl">
              <p className="text-[10px] font-bold text-cultural-sage-700 mb-0.5">
                {strongest.dim} {strongest.label} — {Math.round(strongest.score * 100)}%
              </p>
              <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
                {truncate(strongest.rationale, 100)}
              </p>
            </div>
          )}
          {weakest.rationale && (
            <div className="bg-cultural-coral-50/40 p-3 rounded-2xl">
              <p className="text-[10px] font-bold text-cultural-coral-600 mb-0.5">
                {weakest.dim} {weakest.label} — {Math.round(weakest.score * 100)}%
              </p>
              <p className="text-[11px] text-on-surface-variant leading-relaxed italic">
                {truncate(weakest.rationale, 100)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Feedback — inline 5-star */}
      {feedbackStatus !== 'success' ? (
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-primary-500/70">
            Rate this creation
          </p>
          <div className="flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((star) => (
              <motion.button
                key={star}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredStar(star)}
                onMouseLeave={() => setHoveredStar(0)}
                whileTap={{ scale: 0.85 }}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center"
              >
                <span className={`text-2xl transition-colors ${
                  star <= displayRating ? 'text-cultural-amber-400' : 'text-surface-container-high'
                }`}>&#9733;</span>
              </motion.button>
            ))}
          </div>
          {rating > 0 && (
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Optional comment..."
              rows={2}
              className="w-full px-3 py-2 text-xs rounded-xl bg-surface-container-lowest text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            />
          )}
          {rating > 0 && (
            <button
              onClick={handleFeedback}
              disabled={feedbackStatus === 'submitting'}
              className="w-full text-xs font-semibold text-primary-500 py-2 rounded-xl hover:bg-primary-50 transition-colors disabled:opacity-50"
            >
              {feedbackStatus === 'submitting' ? 'Submitting...' : 'Submit Feedback'}
            </button>
          )}
        </div>
      ) : (
        <p className="text-xs text-cultural-sage-600 text-center py-2">Feedback submitted</p>
      )}

      {/* Action buttons */}
      <div className="space-y-2 pt-2">
        <button
          onClick={handlePublish}
          disabled={publishing}
          className="w-full bg-primary-500 text-white font-bold py-3.5 rounded-2xl shadow-lg shadow-primary-500/20 hover:bg-primary-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 min-h-[44px]"
        >
          {publishing ? 'Publishing...' : 'Finalize Artifact'}
          <Sparkles className="w-4 h-4" />
        </button>
        <button
          onClick={onReset}
          className="w-full flex items-center justify-center gap-1.5 text-[11px] text-on-surface-variant py-2 hover:text-on-surface transition-colors min-h-[44px]"
        >
          <RotateCcw className="w-3 h-3" />
          New creation
        </button>
      </div>
    </div>
  );
}
