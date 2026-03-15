import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface AudioImportNodeData {
  [key: string]: unknown;
}

function AudioImportNodeComponent({ selected }: NodeProps & { data: AudioImportNodeData }) {
  return (
    <div
      className={[
        'min-w-[160px] max-w-[200px] bg-white dark:bg-gray-800 rounded-lg border opacity-60',
        selected ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30' : 'border-gray-200 dark:border-gray-700',
      ].join(' ')}
    >
      <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-gray-100 dark:border-gray-700">
        <span className="text-sm">🎵</span>
        <span className="text-[10px] font-semibold text-gray-700 dark:text-gray-300">Audio</span>
        <span className="ml-auto text-[7px] px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400">
          Coming Soon
        </span>
      </div>
      <div className="p-2">
        <div className="w-full h-16 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
          <span className="text-[9px] text-gray-400">.mp3 / .wav</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#9B6A8C] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(AudioImportNodeComponent);
