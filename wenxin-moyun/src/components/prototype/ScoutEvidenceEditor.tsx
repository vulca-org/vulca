/**
 * HITL panel for the Scout stage — allows users to review, edit,
 * and supplement cultural evidence before it flows to Draft.
 *
 * Displayed when status === 'waiting_human' && hitlWaitInfo.stage === 'scout'.
 */

import { useState } from 'react';

interface EvidenceItem {
  term?: string;
  sample_id?: string;
  rule_id?: string;
  confidence?: number;
  similarity?: number;
  severity?: string;
  description?: string;
}

interface Props {
  evidence: Record<string, unknown> | null;
  onAction: (
    action: string,
    options?: { reason?: string },
  ) => void;
}

export default function ScoutEvidenceEditor({ evidence, onAction }: Props) {
  const [additionalTerms, setAdditionalTerms] = useState('');
  const [reason, setReason] = useState('');

  const sampleMatches = (evidence?.sample_matches as EvidenceItem[]) || [];
  const terminologyHits = (evidence?.terminology_hits as EvidenceItem[]) || [];
  const tabooViolations = (evidence?.taboo_violations as EvidenceItem[]) || [];
  const coverage = typeof evidence?.evidence_coverage === 'number'
    ? (evidence.evidence_coverage as number)
    : null;

  const handleApprove = () => {
    const reasonText = [reason, additionalTerms && `Additional terms: ${additionalTerms}`]
      .filter(Boolean).join('. ');
    onAction('approve', reasonText ? { reason: reasonText } : undefined);
  };

  const handleRequestMore = () => {
    onAction('rerun', {
      reason: reason || `Request supplementary evidence. Additional terms: ${additionalTerms}`,
    });
  };

  return (
    <div className="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 p-4 space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xl">🔍</span>
        <h3 className="font-semibold text-amber-800 dark:text-amber-300">
          Review Scout Evidence
        </h3>
        {coverage !== null && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-200">
            Coverage: {(coverage * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {/* Sample matches */}
      {sampleMatches.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-amber-700 dark:text-amber-400 mb-1">
            Sample Matches ({sampleMatches.length})
          </h4>
          <div className="flex flex-wrap gap-1">
            {sampleMatches.map((m, i) => (
              <span key={i} className="px-2 py-0.5 bg-white dark:bg-gray-800 rounded text-xs text-gray-700 dark:text-gray-300">
                {m.sample_id} ({((m.similarity || 0) * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Terminology hits */}
      {terminologyHits.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-amber-700 dark:text-amber-400 mb-1">
            Terminology ({terminologyHits.length})
          </h4>
          <div className="flex flex-wrap gap-1">
            {terminologyHits.map((h, i) => (
              <span key={i} className="px-2 py-0.5 bg-white dark:bg-gray-800 rounded text-xs text-gray-700 dark:text-gray-300">
                {h.term} ({((h.confidence || 0) * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Taboo violations */}
      {tabooViolations.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-red-600 dark:text-red-400 mb-1">
            Taboo Violations ({tabooViolations.length})
          </h4>
          <div className="space-y-1">
            {tabooViolations.map((v, i) => (
              <div key={i} className="px-2 py-1 bg-red-50 dark:bg-red-900/30 rounded text-xs text-red-700 dark:text-red-300">
                <span className="font-medium">[{v.severity}]</span> {v.description}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User input */}
      <div>
        <label className="block text-xs font-semibold text-amber-700 dark:text-amber-400 mb-1">
          Add Terms (comma-separated)
        </label>
        <input
          type="text"
          value={additionalTerms}
          onChange={e => setAdditionalTerms(e.target.value)}
          placeholder="e.g., 留白, 墨分五色, hemp-fiber strokes"
          className="w-full px-2 py-1.5 text-sm border border-amber-300 dark:border-amber-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-amber-700 dark:text-amber-400 mb-1">
          Notes (optional)
        </label>
        <input
          type="text"
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="Additional context or corrections..."
          className="w-full px-2 py-1.5 text-sm border border-amber-300 dark:border-amber-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        />
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2 border-t border-amber-200 dark:border-amber-800">
        <button
          onClick={handleApprove}
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
        >
          Approve Evidence
        </button>
        <button
          onClick={handleRequestMore}
          className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 transition-colors"
        >
          Request More Evidence
        </button>
        <button
          onClick={() => onAction('reject', { reason: reason || 'Evidence insufficient' })}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Reject & Stop
        </button>
      </div>
    </div>
  );
}
