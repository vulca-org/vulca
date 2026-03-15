import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface CompareNodeData {
  [key: string]: unknown;
}

function CompareNodeComponent({ selected }: NodeProps & { data: CompareNodeData }) {
  return (
    <div
      className={[
        'min-w-[120px] bg-white dark:bg-gray-800 rounded-xl border-2 transition-all',
        selected ? 'border-[#5F8A50] ring-2 ring-[#5F8A50]/30' : 'border-[#5F8A50]/40',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        id="a"
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
        style={{ top: '30%' }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="b"
        className="!w-2.5 !h-2.5 !bg-[#B8923D] !border-white dark:!border-gray-800 !border-2"
        style={{ top: '70%' }}
      />
      <div className="px-3 py-2 text-center">
        <span className="text-sm">⚖️</span>
        <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 mt-0.5">Compare</p>
        <p className="text-[9px] text-gray-400">A/B side-by-side</p>
      </div>
    </div>
  );
}

export default memo(CompareNodeComponent);
