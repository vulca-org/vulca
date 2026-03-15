/**
 * RerouteNode — small diamond junction node (12x12px).
 * Used to redirect edge paths cleanly.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface RerouteNodeData {
  [key: string]: unknown;
}

function RerouteNodeComponent({ selected }: NodeProps & { data: RerouteNodeData }) {
  return (
    <div
      className={[
        'w-3 h-3 rotate-45 border-2 transition-colors',
        selected
          ? 'bg-[#C87F4A] border-[#C87F4A]'
          : 'bg-gray-400 dark:bg-gray-500 border-gray-300 dark:border-gray-600',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2 !h-2 !bg-gray-400 !border-0 !-left-2 !top-1/2 !-translate-y-1/2 -rotate-45"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2 !h-2 !bg-gray-400 !border-0 !-right-2 !top-1/2 !-translate-y-1/2 -rotate-45"
      />
    </div>
  );
}

export default memo(RerouteNodeComponent);
