/**
 * AgentNode — React Flow custom node for the pipeline editor.
 * Mirrors TopologyViewer's colour/emoji style but adds handles for connecting.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { AgentNodeData } from './types';

function AgentNodeComponent({ data, selected }: NodeProps & { data: AgentNodeData }) {
  const hasError = !!data.validationError;

  return (
    <div
      className={[
        'flex flex-col items-center justify-center px-4 py-3 rounded-xl border-2',
        'bg-white dark:bg-gray-800 min-w-[90px] transition-all duration-200',
        selected
          ? 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-400/50'
          : hasError
            ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/40'
            : 'border-gray-300 dark:border-gray-600',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-blue-400 !border-white dark:!border-gray-800 !border-2"
      />

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

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-blue-400 !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(AgentNodeComponent);
