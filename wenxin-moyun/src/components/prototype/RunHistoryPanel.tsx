/**
 * RunHistoryPanel — displays recent pipeline runs in the Canvas sidebar.
 *
 * - Fetches from GET /api/v1/prototype/gallery?limit=10&sort_by=newest
 * - Each item shows tradition color block, subject, score, relative time
 * - Click opens IOSSheet with full details (L1-L5, image, subject)
 * - "Fork" button sets subject + tradition back into the parent form
 */

import { useState, useCallback } from 'react';
import { useRunHistory } from '../../hooks/useRunHistory';
import type { RunHistoryItem } from '../../hooks/useRunHistory';
import { IOSCard, IOSCardContent, IOSButton, IOSSheet } from '../ios';

/** Map tradition slugs to Art Professional palette colors. */
const TRADITION_COLORS: Record<string, string> = {
  chinese_xieyi: '#C87F4A',       // warm-copper
  chinese_gongbi: '#B8923D',      // amber-gold
  western_academic: '#334155',    // ink-gray
  western_classical: '#334155',
  japanese_wabi_sabi: '#5F8A50',  // sage-green
  japanese_traditional: '#5F8A50',
  persian_miniature: '#C65D4D',   // coral-red
  islamic_geometric: '#C65D4D',
  african_ubuntu: '#B8923D',      // amber-gold
  african_traditional: '#B8923D',
  indian_miniature: '#C87F4A',
  south_asian: '#C87F4A',
  korean_minhwa: '#6B8E7A',       // teal
  aboriginal_dreamtime: '#8B6E4E',
  default: '#9CA3AF',
};

function getTraditionColor(tradition: string): string {
  return TRADITION_COLORS[tradition] ?? TRADITION_COLORS.default;
}

/** Human-friendly relative time (e.g. "3m ago", "2h ago"). */
function relativeTime(epochSec: number): string {
  if (!epochSec) return '';
  const diffSec = Math.max(0, Math.floor(Date.now() / 1000 - epochSec));
  if (diffSec < 60) return 'just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

/** Truncate text to maxLen characters with ellipsis. */
function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen - 1) + '\u2026';
}

/** L1-L5 dimension labels for the detail sheet. */
const L1_L5_LABELS: Record<string, string> = {
  visual_perception: 'L1 Visual',
  technical_analysis: 'L2 Technical',
  cultural_context: 'L3 Cultural',
  critical_interpretation: 'L4 Critical',
  philosophical_aesthetic: 'L5 Philosophical',
};

interface RunHistoryPanelProps {
  onFork: (params: { subject: string; tradition: string }) => void;
}

export default function RunHistoryPanel({ onFork }: RunHistoryPanelProps) {
  const { items, loading, error, refresh } = useRunHistory(10);
  const [selectedItem, setSelectedItem] = useState<RunHistoryItem | null>(null);

  const handleFork = useCallback((item: RunHistoryItem) => {
    onFork({ subject: item.subject, tradition: item.tradition });
    setSelectedItem(null);
  }, [onFork]);

  return (
    <>
      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Run History
            </h3>
            <button
              onClick={refresh}
              className="text-[10px] text-gray-400 hover:text-[#C87F4A] transition-colors"
              title="Refresh"
            >
              Refresh
            </button>
          </div>

          {/* Loading skeleton */}
          {loading && items.length === 0 && (
            <div className="space-y-2">
              {[0, 1, 2].map(i => (
                <div key={i} className="flex items-center gap-2 animate-pulse">
                  <div className="w-3 h-8 rounded bg-stone-200 dark:bg-stone-700 shrink-0" />
                  <div className="flex-1 space-y-1">
                    <div className="h-3 w-3/4 rounded bg-stone-200 dark:bg-stone-700" />
                    <div className="h-2 w-1/2 rounded bg-stone-200 dark:bg-stone-700" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <p className="text-xs text-[#C65D4D]">{error}</p>
          )}

          {/* Empty state */}
          {!loading && !error && items.length === 0 && (
            <p className="text-xs text-gray-400 dark:text-gray-500 py-2 text-center">
              No past runs yet
            </p>
          )}

          {/* List */}
          {items.length > 0 && (
            <ul className="space-y-1">
              {items.map(item => (
                <li key={item.id}>
                  <button
                    onClick={() => setSelectedItem(item)}
                    className="w-full flex items-center gap-2 px-1.5 py-1.5 rounded-lg
                      hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors text-left group"
                  >
                    {/* Tradition color block */}
                    <div
                      className="w-2.5 h-8 rounded-sm shrink-0"
                      style={{ backgroundColor: getTraditionColor(item.tradition) }}
                    />
                    {/* Subject + meta */}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">
                        {truncate(item.subject, 36)}
                      </p>
                      <div className="flex items-center gap-2 text-[10px] text-gray-400 dark:text-gray-500">
                        <span className="font-mono">
                          {item.overall != null ? item.overall.toFixed(2) : 'N/A'}
                        </span>
                        <span>{relativeTime(item.created_at)}</span>
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </IOSCardContent>
      </IOSCard>

      {/* Detail Sheet */}
      <IOSSheet
        visible={selectedItem !== null}
        onClose={() => setSelectedItem(null)}
        height="medium"
      >
        {selectedItem && (
          <div className="space-y-4 pb-6">
            {/* Header */}
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                {selectedItem.subject}
              </h3>
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <span
                  className="inline-block w-2.5 h-2.5 rounded-sm"
                  style={{ backgroundColor: getTraditionColor(selectedItem.tradition) }}
                />
                <span>{selectedItem.tradition.replace(/_/g, ' ')}</span>
                <span className="mx-1">&middot;</span>
                <span>{relativeTime(selectedItem.created_at)}</span>
                {selectedItem.total_rounds > 0 && (
                  <>
                    <span className="mx-1">&middot;</span>
                    <span>{selectedItem.total_rounds} round{selectedItem.total_rounds !== 1 ? 's' : ''}</span>
                  </>
                )}
              </div>
            </div>

            {/* Image preview */}
            {selectedItem.best_image_url && (
              <div className="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
                <img
                  src={selectedItem.best_image_url}
                  alt={selectedItem.subject}
                  className="w-full max-h-48 object-contain bg-stone-50 dark:bg-stone-900"
                />
              </div>
            )}

            {/* Overall score */}
            <div className="flex items-center justify-between px-2 py-2 rounded-lg bg-stone-50 dark:bg-stone-800/50">
              <span className="text-sm text-gray-600 dark:text-gray-300">Overall</span>
              <span className="text-lg font-bold font-mono text-[#C87F4A] dark:text-[#DDA574]">
                {selectedItem.overall != null ? selectedItem.overall.toFixed(2) : 'N/A'}
              </span>
            </div>

            {/* L1-L5 Scores */}
            {selectedItem.scores && Object.keys(selectedItem.scores).length > 0 && (
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Dimension Scores
                </h4>
                <div className="space-y-1">
                  {Object.entries(selectedItem.scores).map(([dim, score]) => (
                    <div
                      key={dim}
                      className="flex items-center justify-between px-2 py-1 rounded bg-stone-50 dark:bg-stone-800/40 text-xs"
                    >
                      <span className="text-gray-600 dark:text-gray-400">
                        {L1_L5_LABELS[dim] ?? dim.replace(/_/g, ' ')}
                      </span>
                      <span className="font-mono font-medium text-gray-800 dark:text-gray-200">
                        {score != null ? Number(score).toFixed(2) : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fork button */}
            <IOSButton
              variant="secondary"
              size="sm"
              onClick={() => handleFork(selectedItem)}
              className="w-full"
            >
              Fork &mdash; use this subject &amp; tradition
            </IOSButton>
          </div>
        )}
      </IOSSheet>
    </>
  );
}
