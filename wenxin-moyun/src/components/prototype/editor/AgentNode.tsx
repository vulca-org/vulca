/**
 * AgentNode — React Flow custom node for the pipeline editor.
 *
 * Phase 5 enhancements:
 * - Typed handles with DataType colors (U2)
 * - Mute/bypass/collapse visual states (U3)
 * - Inline previews: Draft thumbnails, Critic bars, Queen badge (U5)
 * - Evolution badge (U8)
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { AgentNodeData } from './types';
import { getSocketColor } from './dataTypeColors';
import { DraftPreview, CriticPreview, QueenPreview } from './inlinePreviews';
import EvolutionBadge from './EvolutionBadge';

/** Default port DataTypes per agent */
const AGENT_INPUT_TYPE: Record<string, string> = {
  scout: 'pipeline_input',
  router: 'evidence',
  draft: 'evidence',
  critic: 'draft_candidates',
  queen: 'critique',
  archivist: 'pipeline_output',
  upload: 'pipeline_input',
  identify: 'pipeline_input',
  report: 'critique',
};

const AGENT_OUTPUT_TYPE: Record<string, string> = {
  scout: 'evidence',
  router: 'evidence',
  draft: 'draft_candidates',
  critic: 'critique',
  queen: 'queen_decision',
  archivist: 'archive',
  upload: 'image',
  identify: 'text',
  report: 'pipeline_output',
};

const RING_COLORS: Record<string, string> = {
  idle: 'border-gray-300 dark:border-gray-600',
  running: 'border-[#C87F4A] dark:border-[#DDA574]',
  done: 'border-[#5F8A50] dark:border-[#87A878]',
  error: 'border-red-500 dark:border-red-400',
  skipped: 'border-gray-400 dark:border-gray-500',
};

const BG_COLORS: Record<string, string> = {
  idle: 'bg-white dark:bg-gray-800',
  running: 'bg-[#f9f9ff] dark:bg-[#C87F4A]/10',
  done: 'bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10',
  error: 'bg-red-50 dark:bg-red-900/20',
  skipped: 'bg-gray-100 dark:bg-gray-800',
};

function AgentNodeComponent({ data, selected }: NodeProps & { data: AgentNodeData }) {
  const hasError = !!data.validationError;
  const status = data.status || 'idle';
  const ringColor = RING_COLORS[status] || RING_COLORS.idle;
  const bgColor = BG_COLORS[status] || BG_COLORS.idle;

  const isMuted = data.muted === true;
  const isBypassed = data.bypassed === true;
  const isCollapsed = data.collapsed === true;

  // Resolve handle colors
  const inputColor = getSocketColor(
    data.inputPorts?.[0]?.dataType || AGENT_INPUT_TYPE[data.agentId] || 'text',
  );
  const outputColor = getSocketColor(
    data.outputPorts?.[0]?.dataType || AGENT_OUTPUT_TYPE[data.agentId] || 'text',
  );

  // Collapsed: single-row icon + label only
  if (isCollapsed) {
    return (
      <div
        className={[
          'relative flex items-center gap-1.5 px-2 py-1 rounded-lg border',
          isMuted ? 'opacity-50' : '',
          isBypassed ? 'border-dashed border-gray-400' : 'border-gray-300 dark:border-gray-600',
          bgColor,
        ].join(' ')}
      >
        <Handle type="target" position={Position.Left} style={{ width: 8, height: 8, backgroundColor: inputColor, border: '2px solid white' }} />
        <span className="text-sm leading-none select-none">{data.icon}</span>
        <span className="text-[10px] font-semibold text-gray-700 dark:text-gray-300">{data.label}</span>
        <Handle type="source" position={Position.Right} style={{ width: 8, height: 8, backgroundColor: outputColor, border: '2px solid white' }} />
      </div>
    );
  }

  return (
    <div
      className={[
        'relative flex flex-col items-center justify-center px-4 py-3 rounded-xl border-2',
        'min-w-[100px] transition-all duration-300',
        bgColor,
        isMuted ? 'opacity-50' : '',
        isBypassed ? 'border-dashed !border-gray-400 dark:!border-gray-500' : '',
        selected
          ? 'border-[#C87F4A] dark:border-[#DDA574] ring-2 ring-[#C87F4A]/30'
          : hasError
            ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/40'
            : ringColor,
        status === 'running' ? 'animate-pulse' : '',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ width: 10, height: 10, backgroundColor: inputColor, border: '2px solid white' }}
      />

      {/* Bypass badge */}
      {isBypassed && (
        <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 text-[7px] font-bold text-gray-500 bg-gray-200 dark:bg-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full">
          BYPASS
        </div>
      )}

      {/* Status dot */}
      {status !== 'idle' && (
        <div
          className={[
            'absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800',
            status === 'running'
              ? 'bg-[#C87F4A] animate-ping'
              : status === 'done'
                ? 'bg-[#5F8A50]'
                : status === 'error'
                  ? 'bg-red-500'
                  : 'bg-gray-400',
          ].join(' ')}
        />
      )}

      {/* Evolution badge */}
      <div className="absolute top-0.5 left-1">
        <EvolutionBadge suggestion={data.evolutionSuggestion as string | undefined} />
      </div>

      <span className={`text-xl leading-none select-none ${isMuted ? 'line-through' : ''}`}>{data.icon}</span>
      <span className={`text-xs font-semibold text-gray-800 dark:text-gray-200 mt-1 ${isMuted ? 'line-through' : ''}`}>
        {data.label}
      </span>
      <span className="text-[9px] text-gray-500 dark:text-gray-400 text-center leading-tight mt-0.5">
        {data.description}
      </span>

      {hasError && (
        <span className="text-[8px] text-red-500 dark:text-red-400 mt-1 max-w-[80px] text-center truncate">
          {data.validationError}
        </span>
      )}

      {/* Inline previews based on agent type */}
      {data.agentId === 'draft' && data.candidates && data.candidates.length > 0 && (
        <DraftPreview candidates={data.candidates} />
      )}
      {data.agentId === 'critic' && data.scores && data.scores.length > 0 && (
        <CriticPreview scores={data.scores} />
      )}
      {data.agentId === 'queen' && data.decision && (
        <QueenPreview decision={data.decision} />
      )}

      {/* Duration badge */}
      {status === 'done' && data.duration != null && (
        <div className="absolute -bottom-1.5 -right-1.5 text-[8px] bg-[#5F8A50] text-white rounded-full px-1.5 py-0.5 font-mono leading-none">
          {(data.duration / 1000).toFixed(1)}s
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        style={{ width: 10, height: 10, backgroundColor: outputColor, border: '2px solid white' }}
      />
    </div>
  );
}

export default memo(AgentNodeComponent);
