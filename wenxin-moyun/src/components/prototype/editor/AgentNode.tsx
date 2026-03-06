/**
 * AgentNode — React Flow custom node for the pipeline editor.
 *
 * M8 redesign: status ring (idle/running/done/error/skipped),
 * pulse animation during execution, duration badge, port labels.
 * ComfyUI green-pulse + n8n stage-coloring reference.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { AgentNodeData } from './types';

const RING_COLORS: Record<string, string> = {
  idle: 'border-gray-300 dark:border-gray-600',
  running: 'border-blue-500 dark:border-blue-400',
  done: 'border-green-500 dark:border-green-400',
  error: 'border-red-500 dark:border-red-400',
  skipped: 'border-gray-400 dark:border-gray-500',
};

const BG_COLORS: Record<string, string> = {
  idle: 'bg-white dark:bg-gray-800',
  running: 'bg-blue-50 dark:bg-blue-900/20',
  done: 'bg-green-50 dark:bg-green-900/20',
  error: 'bg-red-50 dark:bg-red-900/20',
  skipped: 'bg-gray-100 dark:bg-gray-800',
};

function AgentNodeComponent({ data, selected }: NodeProps & { data: AgentNodeData }) {
  const hasError = !!data.validationError;
  const status = data.status || 'idle';
  const ringColor = RING_COLORS[status] || RING_COLORS.idle;
  const bgColor = BG_COLORS[status] || BG_COLORS.idle;

  return (
    <div
      className={[
        'relative flex flex-col items-center justify-center px-4 py-3 rounded-xl border-2',
        'min-w-[100px] transition-all duration-300',
        bgColor,
        selected
          ? 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-400/50'
          : hasError
            ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/40'
            : ringColor,
        status === 'running' ? 'animate-pulse' : '',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-blue-400 !border-white dark:!border-gray-800 !border-2"
      />

      {/* Status dot */}
      {status !== 'idle' && (
        <div
          className={[
            'absolute -top-1.5 -right-1.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-800',
            status === 'running'
              ? 'bg-blue-500 animate-ping'
              : status === 'done'
                ? 'bg-green-500'
                : status === 'error'
                  ? 'bg-red-500'
                  : 'bg-gray-400',
          ].join(' ')}
        />
      )}

      <span className="text-xl leading-none select-none">{data.icon}</span>
      <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 mt-1">
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

      {/* Duration badge */}
      {status === 'done' && data.duration != null && (
        <div className="absolute -bottom-1.5 -right-1.5 text-[8px] bg-green-500 text-white rounded-full px-1.5 py-0.5 font-mono leading-none">
          {(data.duration / 1000).toFixed(1)}s
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-blue-400 !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(AgentNodeComponent);
