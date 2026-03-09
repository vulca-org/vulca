/**
 * Draft candidate image gallery with selectable candidates.
 *
 * Enhancements:
 * - Score badge overlay on each candidate (from Critic scored data)
 * - Round tab switcher when multiple rounds are available
 * - Best candidate badge shows score
 */

import { useState } from 'react';
import type { DraftCandidate, ScoredCandidate, RoundData } from '../../hooks/usePrototypePipeline';
import { API_BASE_URL } from '../../config/api';

interface Props {
  candidates: DraftCandidate[];
  bestCandidateId: string | null;
  selectedCandidateId?: string | null;
  onSelect?: (candidateId: string) => void;
  /** Scored candidates from Critic for score badge overlay */
  scoredCandidates?: ScoredCandidate[];
  /** Historical round data for round tab switcher */
  rounds?: RoundData[];
}

function toBackendStaticUrl(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}

/** Resolve image source from candidate metadata. */
function imageUrl(candidate: DraftCandidate): string | null {
  const path = candidate.image_url || candidate.image_path;
  if (!path) return null;
  if (path.startsWith('data:')) return path;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (path.startsWith('/static/') || path.startsWith('static/')) {
    return toBackendStaticUrl(path);
  }
  return null;
}

/** Build a score lookup from scored candidates. */
function buildScoreMap(scored?: ScoredCandidate[]): Map<string, number> {
  const map = new Map<string, number>();
  if (!scored) return map;
  for (const sc of scored) {
    map.set(sc.candidate_id, sc.weighted_total);
  }
  return map;
}

export default function CandidateGallery({
  candidates,
  bestCandidateId,
  selectedCandidateId,
  onSelect,
  scoredCandidates,
  rounds,
}: Props) {
  const [selectedRound, setSelectedRound] = useState<number | null>(null);

  // Determine which data to show based on round selection
  const hasMultipleRounds = rounds && rounds.length > 1;
  const activeRoundIdx = selectedRound ?? (rounds ? rounds.length - 1 : 0);
  const activeRound = hasMultipleRounds ? rounds![activeRoundIdx] : null;

  const displayCandidates = activeRound?.candidates ?? candidates;
  const displayScored = activeRound?.scoredCandidates ?? scoredCandidates;
  const displayBestId = activeRound?.bestCandidateId ?? bestCandidateId;
  const scoreMap = buildScoreMap(displayScored);

  if (displayCandidates.length === 0) {
    return (
      <div className="py-8 text-center text-gray-400 dark:text-gray-500">
        No candidates generated yet
      </div>
    );
  }

  return (
    <div>
      {/* Round tab switcher */}
      {hasMultipleRounds && (
        <div className="flex gap-1 mb-3">
          {rounds!.map((r, i) => (
            <button
              key={r.round}
              onClick={() => setSelectedRound(i)}
              className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                i === activeRoundIdx
                  ? 'bg-[#C87F4A] text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              R{r.round}
              {r.weightedTotal != null && (
                <span className="ml-1 opacity-75">{r.weightedTotal.toFixed(2)}</span>
              )}
            </button>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {displayCandidates.map((c) => {
          const isBest = c.candidate_id === displayBestId;
          const isSelected = c.candidate_id === selectedCandidateId;
          const shortId = c.candidate_id.split('-').pop() || c.candidate_id;
          const imgSrc = imageUrl(c);
          const score = scoreMap.get(c.candidate_id);

          return (
            <div
              key={c.candidate_id}
              onClick={() => onSelect?.(c.candidate_id)}
              className={`
                relative rounded-xl overflow-hidden border-2 transition-all
                ${onSelect ? 'cursor-pointer hover:shadow-md' : ''}
                ${isSelected
                  ? 'border-[#C87F4A] dark:border-[#DDA574] ring-2 ring-[#C87F4A]/20 dark:ring-[#C87F4A]/20'
                  : isBest
                    ? 'border-yellow-400 dark:border-yellow-500 ring-2 ring-yellow-200 dark:ring-yellow-800'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
              `}
            >
              {isSelected && (
                <div className="absolute top-2 right-2 z-10 w-6 h-6 bg-[#C87F4A] rounded-full flex items-center justify-center text-white text-xs font-bold shadow">
                  ✓
                </div>
              )}

              {/* Score badge overlay */}
              {score != null && (
                <div className="absolute bottom-12 right-2 z-10 bg-black/60 text-white text-xs rounded px-1.5 py-0.5 font-mono">
                  {score.toFixed(3)}
                </div>
              )}

              <div className="aspect-square bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                {imgSrc ? (
                  <img
                    src={imgSrc}
                    alt={`Candidate ${shortId}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                      (e.target as HTMLImageElement).parentElement!.innerHTML = '<span class="text-4xl">\u{1F3A8}</span>';
                    }}
                  />
                ) : (c.image_url || c.image_path) ? (
                  <div className="w-full h-full bg-gradient-to-br from-[#C87F4A]/20 to-[#C87F4A]/20 dark:from-[#C87F4A]/10 dark:to-[#C87F4A]/20 flex items-center justify-center text-4xl">
                    🎨
                  </div>
                ) : (
                  <span className="text-gray-400 text-sm">No image</span>
                )}
              </div>

              <div className="p-2 bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-gray-500">#{shortId}</span>
                  <div className="flex items-center gap-1">
                    {isBest && (
                      <span className="text-xs bg-yellow-100 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-400 px-2 py-0.5 rounded-full">
                        Best{score != null ? ` ${score.toFixed(2)}` : ''}
                      </span>
                    )}
                    {isSelected && !isBest && (
                      <span className="text-xs bg-[#C87F4A]/10 dark:bg-[#C87F4A]/25 text-[#C87F4A] dark:text-[#DDA574] px-2 py-0.5 rounded-full">
                        Selected
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-1 truncate">
                  seed: {c.seed} | {c.model_ref}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
