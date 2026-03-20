/**
 * L1-L5 critic scoring table with expandable rationale details.
 *
 * Features:
 * - Per-dimension score bars with color coding
 * - Click-to-expand rationale for each dimension
 * - Risk tag display with severity indicators
 * - Gate status (PASS/FAIL) per candidate
 * - Best candidate highlighting
 */

import { useState, Fragment } from 'react';
import type { ScoredCandidate } from '../../hooks/usePrototypePipeline';
import CriticDetailModal from './CriticDetailModal';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';

interface CrossLayerSignal {
  source_layer: string;
  target_layer: string;
  signal_type: string;
  message: string;
  strength: number;
}

interface AgentMetrics {
  escalation_rate: number;
  tool_calls: number;
  re_plan_rate: number;
  total_escalations: number;
  total_dims_evaluated: number;
}

interface Props {
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  agentMetrics?: AgentMetrics | null;
  crossLayerSignals?: CrossLayerSignal[];
  evaluationSummary?: string | null;
}

const RISK_TAG_COLORS: Record<string, string> = {
  taboo: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  cultural_mismatch: 'bg-[#B8923D]/10 dark:bg-[#B8923D]/10 text-[#8F7030] dark:text-[#D4A94E]',
  color_saturation: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
  detail_consistency: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574]',
  composition_imbalance: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574]',
};

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    score >= 0.7 ? 'bg-[#5F8A50]' :
    score >= 0.4 ? 'bg-yellow-500' :
    'bg-red-500';

  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono w-10 text-right">{score.toFixed(2)}</span>
    </div>
  );
}

function LayerProgressBar({ scores }: { scores: { dimension: string; score: number }[] }) {
  const layers = PROTOTYPE_DIMENSIONS;
  return (
    <div className="flex gap-0.5 items-end h-6">
      {layers.map(dim => {
        const found = scores.find(s => s.dimension === dim);
        const score = found?.score ?? 0;
        const pct = Math.round(score * 100);
        const color =
          score >= 0.7 ? 'bg-[#5F8A50]' :
          score >= 0.4 ? 'bg-yellow-400' :
          'bg-red-400';
        return (
          <div
            key={dim}
            className={`w-2 ${color} rounded-t-sm transition-all`}
            style={{ height: `${Math.max(pct, 4)}%` }}
            title={`${PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.layer ?? dim}: ${score.toFixed(2)}`}
          />
        );
      })}
    </div>
  );
}

function RiskTagBadge({ tag }: { tag: string }) {
  const colorClass = RISK_TAG_COLORS[tag] || 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400';
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium ${colorClass}`}>
      {tag.replace(/_/g, ' ')}
    </span>
  );
}

function RationalePanel({ rationale, dimension }: { rationale: string; dimension: string }) {
  const info = PROTOTYPE_DIM_LABELS[dimension as PrototypeDimension];
  if (!rationale) return null;

  return (
    <div className="mt-1 p-2.5 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-100 dark:border-gray-800">
      <div className="flex items-center gap-1.5 mb-1.5">
        <span className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
          {info?.layer ?? ''} Analysis
        </span>
        <span className="text-[10px] text-gray-400 dark:text-gray-600">
          {info?.full ?? dimension}
        </span>
      </div>
      <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
        {rationale}
      </p>
    </div>
  );
}

export default function CriticScoreTable({ scoredCandidates, bestCandidateId, agentMetrics, crossLayerSignals, evaluationSummary }: Props) {
  const [expandedCells, setExpandedCells] = useState<Set<string>>(new Set());
  const [expandedRisks, setExpandedRisks] = useState<Set<string>>(new Set());
  const [detailCandidate, setDetailCandidate] = useState<ScoredCandidate | null>(null);

  if (scoredCandidates.length === 0) {
    return (
      <div className="py-4 text-center text-gray-400 dark:text-gray-500 text-sm">
        Waiting for critic scores...
      </div>
    );
  }

  const toggleCell = (key: string) => {
    setExpandedCells(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleRisks = (candidateId: string) => {
    setExpandedRisks(prev => {
      const next = new Set(prev);
      if (next.has(candidateId)) next.delete(candidateId);
      else next.add(candidateId);
      return next;
    });
  };

  return (
    <div className="space-y-3">
      {/* Evaluation summary */}
      {evaluationSummary && (
        <div className="px-3 py-2 bg-[#f9f9ff] dark:bg-gray-800/40 border-l-2 border-[#5F8A50] rounded-r-lg text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {evaluationSummary}
        </div>
      )}

      {/* Compact table view */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-2 px-2 text-gray-500 dark:text-gray-400 font-medium">Candidate</th>
              <th className="text-left py-2 px-1 text-gray-500 dark:text-gray-400 font-medium text-xs w-14">
                L1-L5
              </th>
              {scoredCandidates[0]?.dimension_scores.map(d => (
                <th key={d.dimension} className="text-left py-2 px-2 text-gray-500 dark:text-gray-400 font-medium text-xs">
                  {PROTOTYPE_DIM_LABELS[d.dimension as PrototypeDimension]?.short || d.dimension}
                </th>
              ))}
              <th className="text-left py-2 px-2 text-gray-500 dark:text-gray-400 font-medium">Total</th>
              <th className="text-left py-2 px-2 text-gray-500 dark:text-gray-400 font-medium">Gate</th>
            </tr>
          </thead>
          <tbody>
            {scoredCandidates.map(sc => {
              const isBest = sc.candidate_id === bestCandidateId;
              const shortId = sc.candidate_id.split('-').pop();
              const hasRisks = sc.risk_tags.length > 0;
              const risksExpanded = expandedRisks.has(sc.candidate_id);

              return (
                <Fragment key={sc.candidate_id}>
                  <tr
                    className={`border-b border-gray-100 dark:border-gray-800 ${isBest ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''}`}
                  >
                    <td className="py-2 px-2 font-mono text-xs">
                      <div className="flex items-center gap-1">
                        #{shortId}
                        {isBest && <span className="text-yellow-500">★</span>}
                        {sc.dimension_scores.some(d => d.agent_metadata) && (
                          <span className="text-[10px] text-[#C87F4A]" title="Agent-enhanced">🤖</span>
                        )}
                        {hasRisks && (
                          <button
                            onClick={() => toggleRisks(sc.candidate_id)}
                            className="ml-1 text-[10px] text-[#B8923D] hover:text-[#8F7030] transition-colors"
                            title={`${sc.risk_tags.length} risk tag(s)`}
                          >
                            ⚠ {sc.risk_tags.length}
                          </button>
                        )}
                        <button
                          onClick={() => setDetailCandidate(sc)}
                          className="ml-1 text-[10px] text-[#C87F4A] hover:text-[#A85D3B] dark:text-[#DDA574] dark:hover:text-[#DDA574] transition-colors"
                          title="View critic details"
                        >
                          🔍
                        </button>
                      </div>
                    </td>
                    <td className="py-2 px-1">
                      <LayerProgressBar scores={sc.dimension_scores} />
                    </td>
                    {sc.dimension_scores.map(d => {
                      const cellKey = `${sc.candidate_id}:${d.dimension}`;
                      const hasRationale = !!d.rationale;

                      return (
                        <td key={d.dimension} className="py-2 px-2">
                          <button
                            onClick={() => hasRationale && toggleCell(cellKey)}
                            className={`w-full text-left ${hasRationale ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}
                            title={d.summary || (hasRationale ? 'Click for analysis details' : undefined)}
                          >
                            <ScoreBar score={d.score} />
                          </button>
                        </td>
                      );
                    })}
                    <td className="py-2 px-2 font-semibold text-sm">
                      {sc.weighted_total.toFixed(3)}
                    </td>
                    <td className="py-2 px-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        sc.gate_passed
                          ? 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#5F8A50] dark:text-[#87A878]'
                          : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                      }`}>
                        {sc.gate_passed ? 'PASS' : 'FAIL'}
                      </span>
                    </td>
                  </tr>

                  {/* Risk tags row */}
                  {risksExpanded && hasRisks && (
                    <tr key={`${sc.candidate_id}-risks`}>
                      <td colSpan={scoredCandidates[0].dimension_scores.length + 4} className="px-2 pb-2">
                        <div className="flex flex-wrap gap-1 py-1.5 px-2 bg-[#B8923D]/5 dark:bg-[#B8923D]/10 rounded-lg">
                          <span className="text-[10px] font-semibold text-[#8F7030] dark:text-[#D4A94E] mr-1 self-center">
                            Risk Tags:
                          </span>
                          {sc.risk_tags.map(tag => (
                            <RiskTagBadge key={tag} tag={tag} />
                          ))}
                        </div>
                      </td>
                    </tr>
                  )}

                  {/* Expanded rationale rows */}
                  {sc.dimension_scores.map(d => {
                    const cellKey = `${sc.candidate_id}:${d.dimension}`;
                    if (!expandedCells.has(cellKey) || !d.rationale) return null;
                    return (
                      <tr key={cellKey}>
                        <td colSpan={scoredCandidates[0].dimension_scores.length + 4} className="px-2 pb-2">
                          <RationalePanel rationale={d.rationale} dimension={d.dimension} />
                        </td>
                      </tr>
                    );
                  })}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Expand all / collapse all controls */}
      {scoredCandidates.some(sc => sc.dimension_scores.some(d => d.rationale)) && (
        <div className="flex justify-end gap-2 pt-1">
          <button
            onClick={() => {
              const allKeys = new Set<string>();
              scoredCandidates.forEach(sc =>
                sc.dimension_scores.forEach(d => {
                  if (d.rationale) allKeys.add(`${sc.candidate_id}:${d.dimension}`);
                })
              );
              setExpandedCells(allKeys);
              setExpandedRisks(new Set(scoredCandidates.filter(sc => sc.risk_tags.length > 0).map(sc => sc.candidate_id)));
            }}
            className="text-[10px] text-[#C87F4A] hover:text-[#A85D3B] dark:text-[#DDA574] dark:hover:text-[#DDA574] transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={() => { setExpandedCells(new Set()); setExpandedRisks(new Set()); }}
            className="text-[10px] text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 transition-colors"
          >
            Collapse All
          </button>
        </div>
      )}

      {/* Critic Detail Modal */}
      {detailCandidate && (
        <CriticDetailModal
          candidate={detailCandidate}
          onClose={() => setDetailCandidate(null)}
          agentMetrics={agentMetrics}
          crossLayerSignals={crossLayerSignals}
        />
      )}
    </div>
  );
}
