import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface MaskRegionNodeData {
  [key: string]: unknown;
}

function MaskRegionNodeComponent({ selected }: NodeProps & { data: MaskRegionNodeData }) {
  return (
    <div
      className={[
        'min-w-[160px] max-w-[200px] bg-white dark:bg-gray-800 rounded-lg border',
        selected ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30' : 'border-gray-200 dark:border-gray-700',
      ].join(' ')}
    >
      <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-gray-100 dark:border-gray-700">
        <span className="text-sm">🎭</span>
        <span className="text-[10px] font-semibold text-gray-700 dark:text-gray-300">Mask Region</span>
      </div>
      <div className="p-2">
        <div className="w-full h-20 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
          <span className="text-[9px] text-gray-400">Draw mask region</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#8B7355] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(MaskRegionNodeComponent);
