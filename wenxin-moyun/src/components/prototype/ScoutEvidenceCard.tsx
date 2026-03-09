/**
 * Scout evidence summary card — shows cultural evidence gathered by Scout agent.
 *
 * Features:
 * - Stats overview (samples, terms, taboos)
 * - Expandable terminology list with cultural context
 * - Sample match previews (title + similarity)
 * - Taboo violation details
 */

import { useState } from 'react';
import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';

interface TerminologyHit {
  term?: string;
  category?: string;
  source?: string;
  relevance?: number;
}

interface SampleMatch {
  title?: string;
  name?: string;
  similarity?: number;
  score?: number;
  tradition?: string;
}

interface TabooViolation {
  term?: string;
  severity?: string;
  description?: string;
}

interface Props {
  evidence: Record<string, unknown>;
}

export default function ScoutEvidenceCard({ evidence }: Props) {
  const [expanded, setExpanded] = useState(false);

  const sampleMatchesRaw = evidence.sample_matches as SampleMatch[] | undefined;
  const terminologyHitsRaw = evidence.terminology_hits as TerminologyHit[] | undefined;
  const tabooViolations = evidence.taboo_violations as TabooViolation[] | undefined;
  const tradition = evidence.cultural_tradition as string | undefined;

  const sampleCount = sampleMatchesRaw?.length ?? 0;
  const termCount = terminologyHitsRaw?.length ?? 0;
  const tabooCount = tabooViolations?.length ?? 0;

  return (
    <IOSCard variant="elevated" padding="md" animate={false}>
      <IOSCardHeader
        title="Scout Evidence"
        subtitle={tradition ? tradition.replace(/_/g, ' ') : undefined}
      />
      <IOSCardContent>
        {/* Stats grid */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 bg-[#FAF7F2] dark:bg-[#C87F4A]/10 rounded-xl">
            <div className="text-xl font-bold text-[#C87F4A] dark:text-[#DDA574]">{sampleCount}</div>
            <div className="text-[11px] text-gray-600 dark:text-gray-400 mt-0.5">Samples</div>
          </div>
          <div className="text-center p-3 bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10 rounded-xl">
            <div className="text-xl font-bold text-[#5F8A50] dark:text-[#87A878]">{termCount}</div>
            <div className="text-[11px] text-gray-600 dark:text-gray-400 mt-0.5">Terms</div>
          </div>
          <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-xl">
            <div className="text-xl font-bold text-red-600 dark:text-red-400">{tabooCount}</div>
            <div className="text-[11px] text-gray-600 dark:text-gray-400 mt-0.5">Taboos</div>
          </div>
        </div>

        {/* Expand toggle */}
        {(termCount > 0 || sampleCount > 0 || tabooCount > 0) && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2 w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors text-left"
          >
            {expanded ? '\u25BC Hide' : '\u25B6 Show'} details
          </button>
        )}

        {expanded && (
          <div className="mt-2 space-y-3">
            {/* Terminology hits */}
            {termCount > 0 && terminologyHitsRaw && (
              <div className="p-2.5 bg-[#5F8A50]/5 dark:bg-[#5F8A50]/5 rounded-lg">
                <h4 className="text-xs font-semibold text-[#5F8A50] dark:text-[#87A878] mb-1.5">Cultural Terms</h4>
                <div className="flex flex-wrap gap-1.5">
                  {terminologyHitsRaw.slice(0, 12).map((t, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#4A7040] dark:text-[#87A878]"
                      title={t.source ? `Source: ${t.source}` : undefined}
                    >
                      {t.term || JSON.stringify(t)}
                      {t.relevance != null && (
                        <span className="text-[#5F8A50] dark:text-[#5F8A50] font-mono">{t.relevance.toFixed(2)}</span>
                      )}
                    </span>
                  ))}
                  {termCount > 12 && (
                    <span className="text-[11px] text-gray-400">+{termCount - 12} more</span>
                  )}
                </div>
              </div>
            )}

            {/* Sample matches */}
            {sampleCount > 0 && sampleMatchesRaw && (
              <div className="p-2.5 bg-[#FAF7F2] dark:bg-[#C87F4A]/10 rounded-lg">
                <h4 className="text-xs font-semibold text-[#C87F4A] dark:text-[#DDA574] mb-1.5">Reference Samples</h4>
                <div className="space-y-1">
                  {sampleMatchesRaw.slice(0, 5).map((s, i) => (
                    <div key={i} className="flex items-center justify-between text-[11px]">
                      <span className="text-gray-700 dark:text-gray-300 truncate mr-2">
                        {s.title || s.name || `Sample ${i + 1}`}
                      </span>
                      {(s.similarity ?? s.score) != null && (
                        <span className="font-mono text-[#C87F4A] dark:text-[#DDA574] shrink-0">
                          {((s.similarity ?? s.score ?? 0) * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Taboo violations */}
            {tabooCount > 0 && tabooViolations && (
              <div className="p-2.5 bg-red-50 dark:bg-red-900/10 rounded-lg">
                <h4 className="text-xs font-semibold text-red-700 dark:text-red-400 mb-1">Taboo Violations</h4>
                <ul className="text-xs text-red-600 dark:text-red-400 space-y-0.5">
                  {tabooViolations.slice(0, 5).map((v, i) => (
                    <li key={i}>
                      <span className="font-medium">{v.term || JSON.stringify(v)}</span>
                      {v.severity && <span className="ml-1 text-red-400">({v.severity})</span>}
                      {v.description && <span className="ml-1 text-red-500 dark:text-red-400">{v.description}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </IOSCardContent>
    </IOSCard>
  );
}
