/**
 * ReportNode — in-canvas evaluation report display (React Flow custom node).
 *
 * Shows traffic-light indicator, L1-L5 mini bar chart, tradition badge,
 * and risk flags. Wider than AgentNode (min 280px) for data-rich display.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { AgentNodeData } from './types';

function ReportNodeComponent({ data, selected }: NodeProps & { data: AgentNodeData }) {
  const report = data.reportOutput;
  const status = data.status || 'idle';

  const trafficColor = !report
    ? 'bg-gray-300'
    : report.weighted_total >= 0.85
      ? 'bg-[#5F8A50]'
      : report.weighted_total >= 0.70
        ? 'bg-yellow-500'
        : 'bg-red-500';

  return (
    <div
      className={[
        'rounded-xl border-2 bg-white dark:bg-gray-800 min-w-[280px] max-w-[320px] transition-all duration-300',
        selected
          ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30'
          : 'border-gray-300 dark:border-gray-600',
        status === 'running' ? 'animate-pulse' : '',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
      />

      {/* Header */}
      <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
        <span className="text-lg select-none">📊</span>
        <span className="text-sm font-semibold text-gray-900 dark:text-white">Report</span>
        {report && <div className={`w-3 h-3 rounded-full ${trafficColor} ml-auto`} />}
      </div>

      {/* Body */}
      <div className="p-3">
        {!report ? (
          <div className="text-center py-4 text-sm text-gray-400">
            <div className="text-2xl mb-1 select-none">📋</div>
            Run pipeline to see results
          </div>
        ) : (
          <>
            {/* Total score */}
            <div className="text-center mb-2">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {(report.weighted_total * 100).toFixed(0)}
              </span>
              <span className="text-xs text-gray-500 ml-1">/100</span>
            </div>

            {/* Summary */}
            <p className="text-[11px] text-gray-600 dark:text-gray-300 text-center mb-3">
              {report.summary}
            </p>

            {/* L1-L5 mini bar chart */}
            <div className="space-y-1.5">
              {report.dimension_scores.map((d) => (
                <div key={d.dimension} className="flex items-center gap-2">
                  <span className="text-[9px] text-gray-500 w-6 text-right shrink-0">
                    {d.label}
                  </span>
                  <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        d.score >= 0.85
                          ? 'bg-[#5F8A50]'
                          : d.score >= 0.7
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                      }`}
                      style={{ width: `${d.score * 100}%` }}
                    />
                  </div>
                  <span className="text-[9px] font-mono text-gray-500 w-7 shrink-0">
                    {(d.score * 100).toFixed(0)}
                  </span>
                </div>
              ))}
            </div>

            {/* Tradition badge */}
            {report.tradition && (
              <div className="mt-2 text-center">
                <span className="text-[9px] bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574] px-2 py-0.5 rounded-full">
                  {report.tradition}
                </span>
              </div>
            )}

            {/* Risk flags */}
            {report.risk_flags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {report.risk_flags.map((flag) => (
                  <span
                    key={flag}
                    className="text-[8px] bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded"
                  >
                    {flag}
                  </span>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(ReportNodeComponent);
