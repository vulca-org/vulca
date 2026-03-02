/**
 * Critic Detail Modal — transparent view into the LLM Critic evaluation process.
 *
 * Shows per-dimension agent metadata, tool call history (parsed from rationale),
 * cross-layer signals, confidence levels, and cost/latency breakdown.
 */

import { useEffect, useRef } from 'react';
import type { ScoredCandidate } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
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
  candidate: ScoredCandidate;
  onClose: () => void;
  agentMetrics?: AgentMetrics | null;
  crossLayerSignals?: CrossLayerSignal[];
}

const SIGNAL_TYPE_STYLES: Record<string, { bg: string; icon: string }> = {
  REINTERPRET: { bg: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800', icon: '🔄' },
  CONFLICT: { bg: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800', icon: '⚡' },
  EVIDENCE_GAP: { bg: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800', icon: '🔍' },
  CONFIRMATION: { bg: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800', icon: '✓' },
};

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    value >= 0.8 ? 'bg-green-500' :
    value >= 0.5 ? 'bg-blue-500' :
    'bg-orange-500';
  const label =
    value >= 0.8 ? 'High' :
    value >= 0.5 ? 'Medium' :
    'Low';

  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-medium text-gray-500 dark:text-gray-400">{label} ({pct}%)</span>
    </div>
  );
}

function ModeBadge({ isAgent, mode }: { isAgent: boolean; mode?: string }) {
  if (isAgent) {
    const progressive = mode?.includes('progressive');
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400">
        🤖 {progressive ? 'Agent (Progressive)' : 'Agent'}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
      📐 Rule-based
    </span>
  );
}

export default function CriticDetailModal({ candidate, onClose, agentMetrics, crossLayerSignals }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const shortId = candidate.candidate_id.split('-').pop();
  const agentDims = candidate.dimension_scores.filter(d => d.agent_metadata);
  const ruleDims = candidate.dimension_scores.filter(d => !d.agent_metadata);
  const totalCost = agentDims.reduce((sum, d) => sum + (d.agent_metadata?.cost_usd ?? 0), 0);
  const totalToolCalls = agentDims.reduce((sum, d) => sum + (d.agent_metadata?.tool_calls_made ?? 0), 0);
  const avgLatency = agentDims.length > 0
    ? agentDims.reduce((sum, d) => sum + (d.agent_metadata?.latency_ms ?? 0), 0) / agentDims.length
    : 0;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[85vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-5 py-3 flex items-center justify-between rounded-t-2xl z-10">
          <div>
            <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
              Critic Detail — #{shortId}
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              Total: {candidate.weighted_total.toFixed(3)} · Gate: {candidate.gate_passed ? 'PASS' : 'FAIL'} · {agentDims.length}/{candidate.dimension_scores.length} Agent-enhanced
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500"
          >
            ✕
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Agent Summary */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: 'Agent Dims', value: `${agentDims.length}/${candidate.dimension_scores.length}` },
              { label: 'Tool Calls', value: totalToolCalls.toString() },
              { label: 'Avg Latency', value: avgLatency > 0 ? `${(avgLatency / 1000).toFixed(1)}s` : '-' },
              { label: 'Cost', value: totalCost > 0 ? `$${totalCost.toFixed(4)}` : '$0' },
            ].map(stat => (
              <div key={stat.label} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{stat.value}</div>
                <div className="text-[10px] text-gray-500 dark:text-gray-400 mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Layer-by-Layer */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              Layer-by-Layer Breakdown
            </h3>
            <div className="space-y-2">
              {candidate.dimension_scores.map(d => {
                const meta = d.agent_metadata;
                const isAgent = !!meta && !meta.fallback_used;
                const scoreColor =
                  d.score >= 0.7 ? 'text-green-600 dark:text-green-400' :
                  d.score >= 0.4 ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-red-600 dark:text-red-400';

                return (
                  <div key={d.dimension} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
                    {/* Dimension Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {PROTOTYPE_DIM_LABELS[d.dimension as PrototypeDimension]?.complete ?? d.dimension}
                        </span>
                        <ModeBadge isAgent={isAgent} mode={meta?.mode} />
                      </div>
                      <span className={`text-lg font-bold ${scoreColor}`}>
                        {d.score.toFixed(3)}
                      </span>
                    </div>

                    {/* Agent Details */}
                    {isAgent && meta && (
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 mb-2 pl-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Confidence</span>
                          <ConfidenceBar value={meta.confidence} />
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Model</span>
                          <span className="text-[10px] font-mono text-gray-600 dark:text-gray-300">{meta.model_used}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Score Split</span>
                          <span className="text-[10px] font-mono text-gray-600 dark:text-gray-300">
                            rule={meta.rule_score.toFixed(3)} agent={meta.agent_score.toFixed(3)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Tools / LLM</span>
                          <span className="text-[10px] font-mono text-gray-600 dark:text-gray-300">
                            {meta.tool_calls_made} tools · {meta.llm_calls_made} LLM
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Latency</span>
                          <span className="text-[10px] font-mono text-gray-600 dark:text-gray-300">
                            {(meta.latency_ms / 1000).toFixed(1)}s
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-500 dark:text-gray-400">Cost</span>
                          <span className="text-[10px] font-mono text-gray-600 dark:text-gray-300">
                            ${meta.cost_usd.toFixed(4)}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Rationale */}
                    {d.rationale && (
                      <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed mt-1 border-t border-gray-200 dark:border-gray-700 pt-2">
                        {d.rationale}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Cross-Layer Signals */}
          {crossLayerSignals && crossLayerSignals.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Cross-Layer Signals
              </h3>
              <div className="space-y-2">
                {crossLayerSignals.map((sig, i) => {
                  const style = SIGNAL_TYPE_STYLES[sig.signal_type] ?? SIGNAL_TYPE_STYLES.EVIDENCE_GAP;
                  return (
                    <div key={i} className={`rounded-lg border p-2.5 ${style.bg}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm">{style.icon}</span>
                        <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                          {sig.source_layer} → {sig.target_layer}
                        </span>
                        <span className="text-[10px] font-mono text-gray-500 dark:text-gray-400">
                          {sig.signal_type}
                        </span>
                        <span className="ml-auto text-[10px] text-gray-500 dark:text-gray-400">
                          strength: {sig.strength.toFixed(2)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">{sig.message}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Agent Metrics Summary */}
          {agentMetrics && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Agent Performance
              </h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {(agentMetrics.escalation_rate * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-gray-500 dark:text-gray-400">Escalation Rate</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {(agentMetrics.re_plan_rate * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-gray-500 dark:text-gray-400">Re-plan Rate</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {agentMetrics.tool_calls}
                  </div>
                  <div className="text-[10px] text-gray-500 dark:text-gray-400">Total Tool Calls</div>
                </div>
              </div>
            </div>
          )}

          {/* Rejection Reasons */}
          {!candidate.gate_passed && candidate.risk_tags.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-red-500 dark:text-red-400 uppercase tracking-wider mb-2">
                Rejection Reasons
              </h3>
              <ul className="space-y-1">
                {candidate.risk_tags.map((tag, i) => (
                  <li key={i} className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1.5">
                    <span className="w-1 h-1 rounded-full bg-red-400 flex-shrink-0" />
                    {tag.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
