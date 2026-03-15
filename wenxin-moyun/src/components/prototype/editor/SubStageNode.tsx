/**
 * SubStageNode — Compact node for sub-stages within Draft/Critic.
 * min-w-[80px], status dot, compact layout.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface SubStageNodeData {
  [key: string]: unknown;
  label: string;
  icon: string;
  parentAgent: string;
  subStageId: string;
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  durationMs?: number;
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-300 dark:bg-gray-600',
  running: 'bg-[#C87F4A] animate-pulse',
  completed: 'bg-[#5F8A50]',
  failed: 'bg-red-500',
  skipped: 'bg-gray-400',
};

const PARENT_TINTS: Record<string, string> = {
  draft: 'border-[#C87F4A]/30 bg-[#C87F4A]/5 dark:bg-[#C87F4A]/10',
  critic: 'border-[#B8923D]/30 bg-[#B8923D]/5 dark:bg-[#B8923D]/10',
};

function SubStageNodeComponent({ data, selected }: NodeProps & { data: SubStageNodeData }) {
  const status = data.status || 'pending';
  const statusColor = STATUS_COLORS[status] || STATUS_COLORS.pending;
  const parentTint = PARENT_TINTS[data.parentAgent] || '';

  return (
    <div
      className={[
        'flex items-center gap-1.5 px-2 py-1.5 rounded-lg border min-w-[80px] transition-all',
        parentTint,
        selected ? 'ring-2 ring-[#C87F4A]/30' : '',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-1.5 !h-1.5 !bg-gray-400 !border-0"
      />

      {/* Status dot */}
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${statusColor}`} />

      {/* Icon + Label */}
      <span className="text-xs leading-none select-none">{data.icon}</span>
      <span className="text-[10px] font-medium text-gray-700 dark:text-gray-300 truncate">
        {data.label}
      </span>

      {/* Duration */}
      {status === 'completed' && data.durationMs != null && (
        <span className="text-[8px] text-gray-400 ml-auto font-mono">
          {(data.durationMs / 1000).toFixed(1)}s
        </span>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!w-1.5 !h-1.5 !bg-gray-400 !border-0"
      />
    </div>
  );
}

export default memo(SubStageNodeComponent);
