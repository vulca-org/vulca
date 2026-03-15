/**
 * ProcessingNodeBase — Shared base for processing nodes.
 * Teal accent #6B8E7A, input+output handles, params, status.
 */

import { memo, type ReactNode } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface ProcessingNodeData {
  [key: string]: unknown;
  label: string;
  icon: string;
  status?: 'idle' | 'running' | 'done' | 'error';
  params?: Record<string, unknown>;
}

function ProcessingNodeBaseComponent({
  data,
  selected,
  children,
}: NodeProps & { data: ProcessingNodeData; children?: ReactNode }) {
  const status = data.status || 'idle';

  return (
    <div
      className={[
        'min-w-[140px] max-w-[200px] bg-white dark:bg-gray-800 rounded-xl border-2 transition-all',
        selected
          ? 'border-[#6B8E7A] ring-2 ring-[#6B8E7A]/30'
          : status === 'running'
            ? 'border-[#6B8E7A] animate-pulse'
            : status === 'done'
              ? 'border-[#5F8A50]'
              : 'border-[#6B8E7A]/40',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
      />

      <div className="px-3 py-2">
        <div className="flex items-center gap-1.5">
          <span className="text-sm">{data.icon}</span>
          <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
            {data.label}
          </span>
        </div>
        {children}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(ProcessingNodeBaseComponent);
