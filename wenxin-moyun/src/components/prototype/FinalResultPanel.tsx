/**
 * FinalResultPanel — displayed when the pipeline completes successfully.
 *
 * Shows the winning candidate image, overall weighted score, per-dimension
 * L1-L5 score bars, round info, latency/cost stats, and a link to Gallery.
 *
 * Art Professional palette: #334155 #C87F4A #5F8A50 #B8923D #C65D4D bg:#FAF7F2
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import type { DraftCandidate, ScoredCandidate, RoundData } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';
import { IOSButton } from '../../components/ios';
import { API_BASE_URL, API_PREFIX } from '../../config/api';

interface Props {
  /** All candidates from the final round */
  candidates: DraftCandidate[];
  /** Scored candidates from the critic */
  scoredCandidates: ScoredCandidate[];
  /** ID of the best candidate chosen by the Queen */
  bestCandidateId: string | null;
  /** Final decision text */
  finalDecision: string | null;
  /** Total rounds executed */
  totalRounds: number;
  /** Total pipeline latency in ms */
  totalLatencyMs: number;
  /** Total cost in USD */
  totalCostUsd: number;
  /** Round-by-round history */
  rounds: RoundData[];
  /** Handler to reset and start a new run */
  onNewRun: () => void;
  /** Pipeline task ID for publishing */
  taskId?: string | null;
}

/** Resolve image source from candidate metadata (mirrors CandidateGallery logic). */
function resolveImageUrl(candidate: DraftCandidate): string | null {
  const path = candidate.image_url || candidate.image_path;
  if (!path) return null;
  if (path.startsWith('data:')) return path;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (path.startsWith('/')) return `${API_BASE_URL}${path}`;
  if (path.startsWith('static/') || path.startsWith('prototype/')) return `${API_BASE_URL}/${path}`;
  return null;
}

/** Map score value to a tailwind color class. */
function scoreColor(score: number): string {
  if (score >= 0.7) return 'bg-[#5F8A50]';
  if (score >= 0.4) return 'bg-[#B8923D]';
  return 'bg-[#C65D4D]';
}

/** Map score value to a text color class. */
function scoreTextColor(score: number): string {
  if (score >= 0.7) return 'text-[#5F8A50] dark:text-[#87A878]';
  if (score >= 0.4) return 'text-[#B8923D] dark:text-[#D4AD5C]';
  return 'text-[#C65D4D] dark:text-[#D98070]';
}

export default function FinalResultPanel({
  candidates,
  scoredCandidates,
  bestCandidateId,
  finalDecision,
  totalRounds,
  totalLatencyMs,
  totalCostUsd,
  rounds,
  onNewRun,
  taskId,
}: Props) {
  const navigate = useNavigate();
  const [publishing, setPublishing] = useState(false);

  const handlePublish = useCallback(async () => {
    if (!taskId) return;
    setPublishing(true);
    try {
      const res = await fetch(`${API_PREFIX}/gallery/${taskId}/publish`, {
        method: 'POST',
        headers: { Authorization: 'Bearer demo-key' },
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

  // Find the best scored candidate
  const bestScored = scoredCandidates.find(sc => sc.candidate_id === bestCandidateId)
    ?? (scoredCandidates.length > 0
      ? scoredCandidates.reduce((best, sc) => sc.weighted_total > best.weighted_total ? sc : best)
      : null);

  // Find the corresponding draft candidate for the image
  const bestDraft = bestScored
    ? candidates.find(c => c.candidate_id === bestScored.candidate_id)
    // Also search across all rounds
    ?? rounds.flatMap(r => r.candidates).find(c => c.candidate_id === bestScored.candidate_id)
    : null;

  const bestImageUrl = bestDraft ? resolveImageUrl(bestDraft) : null;
  const overallScore = bestScored?.weighted_total ?? 0;

  // Determine which round produced the winning candidate
  const winningRound = bestScored
    ? rounds.findIndex(r => r.scoredCandidates.some(sc => sc.candidate_id === bestScored.candidate_id)) + 1
    : totalRounds;

  if (!bestScored) return null;

  return (
    <div className="rounded-2xl overflow-hidden border border-[#5F8A50]/30 dark:border-[#5F8A50]/20 bg-white dark:bg-[#1A1816]">
      {/* Header ribbon */}
      <div className="bg-gradient-to-r from-[#5F8A50] to-[#4A7040] px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">🏆</span>
          <h3 className="text-sm font-bold text-white tracking-wide">Pipeline Complete</h3>
        </div>
        <div className="flex items-center gap-3 text-xs text-white/80">
          {totalRounds > 0 && <span>Round {winningRound}/{totalRounds}</span>}
          {totalLatencyMs > 0 && <span>{(totalLatencyMs / 1000).toFixed(1)}s</span>}
          {totalCostUsd > 0 && <span>${totalCostUsd.toFixed(4)}</span>}
        </div>
      </div>

      <div className="p-5">
        {/* Main result area: image + score */}
        <div className="flex gap-5">
          {/* Winning image */}
          <div className="shrink-0 w-48 h-48 rounded-xl overflow-hidden border-2 border-[#B8923D]/40 dark:border-[#B8923D]/30 shadow-md bg-gray-100 dark:bg-gray-800">
            {bestImageUrl ? (
              <img
                src={bestImageUrl}
                alt="Winning artwork"
                className="w-full h-full object-cover"
                onError={(e) => {
                  const el = e.target as HTMLImageElement;
                  el.style.display = 'none';
                  el.parentElement!.innerHTML = '<div class="w-full h-full flex items-center justify-center text-5xl bg-gradient-to-br from-[#C87F4A]/10 to-[#B8923D]/10">🎨</div>';
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-5xl bg-gradient-to-br from-[#C87F4A]/10 to-[#B8923D]/10 dark:from-[#C87F4A]/5 dark:to-[#B8923D]/5">
                🎨
              </div>
            )}
          </div>

          {/* Score + dimensions */}
          <div className="flex-1 min-w-0">
            {/* Overall score */}
            <div className="mb-4">
              <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Overall Score
              </div>
              <div className="flex items-baseline gap-2">
                <span className={`text-4xl font-bold tabular-nums ${scoreTextColor(overallScore)}`}>
                  {overallScore.toFixed(3)}
                </span>
                <span className="text-sm text-gray-400 dark:text-gray-500">
                  / 1.000
                </span>
              </div>
              {bestScored.gate_passed ? (
                <span className="inline-flex items-center mt-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#5F8A50] dark:text-[#87A878]">
                  Gate Passed
                </span>
              ) : (
                <span className="inline-flex items-center mt-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#C65D4D]/10 dark:bg-[#C65D4D]/15 text-[#C65D4D] dark:text-[#D98070]">
                  Gate Failed
                </span>
              )}
            </div>

            {/* L1-L5 dimension bars */}
            <div className="space-y-2">
              {PROTOTYPE_DIMENSIONS.map(dim => {
                const dimScore = bestScored.dimension_scores.find(d => d.dimension === dim);
                const score = dimScore?.score ?? 0;
                const label = PROTOTYPE_DIM_LABELS[dim as PrototypeDimension];
                const pct = Math.round(score * 100);

                return (
                  <div key={dim} className="group" title={dimScore?.rationale || undefined}>
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-300">
                        {label?.complete || dim}
                      </span>
                      <span className="text-xs font-mono font-semibold text-gray-700 dark:text-gray-200">
                        {score.toFixed(3)}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ease-out ${scoreColor(score)}`}
                        style={{ width: `${Math.max(pct, 2)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Final decision rationale */}
        {finalDecision && (
          <div className="mt-4 p-3 bg-[#FAF7F2] dark:bg-[#1F1D1A] rounded-lg border border-[#C9C2B8]/30 dark:border-gray-700">
            <div className="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
              Queen's Decision
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {finalDecision}
            </p>
          </div>
        )}

        {/* Risk tags if any */}
        {bestScored.risk_tags.length > 0 && (
          <div className="mt-3 flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-medium text-gray-500 dark:text-gray-400">Risks:</span>
            {bestScored.risk_tags.map(tag => (
              <span
                key={tag}
                className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#C65D4D]/10 dark:bg-[#C65D4D]/15 text-[#C65D4D] dark:text-[#D98070]"
              >
                {tag.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="mt-5 flex items-center gap-3">
          <IOSButton variant="primary" size="sm" onClick={handlePublish} disabled={publishing}>
            {publishing ? 'Publishing...' : 'Publish to Gallery'}
          </IOSButton>
          <IOSButton variant="secondary" size="sm" onClick={() => navigate('/gallery')}>
            View Gallery
          </IOSButton>
          <IOSButton variant="secondary" size="sm" onClick={onNewRun}>
            New Run
          </IOSButton>
        </div>
      </div>
    </div>
  );
}
