import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface ExportNodeData {
  [key: string]: unknown;
  format?: string;
}

function ExportNodeComponent({ data, selected }: NodeProps & { data: ExportNodeData }) {
  const format = (data.format as string) || 'PNG';

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
        className="!w-2.5 !h-2.5 !bg-[#5F8A50] !border-white dark:!border-gray-800 !border-2"
      />
      <div className="px-3 py-2 text-center">
        <span className="text-sm">📤</span>
        <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 mt-0.5">Export</p>
        <span className="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[8px] bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-mono">
          {format}
        </span>
      </div>
    </div>
  );
}

export default memo(ExportNodeComponent);
