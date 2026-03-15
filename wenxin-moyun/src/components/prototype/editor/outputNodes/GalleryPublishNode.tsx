import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface GalleryPublishNodeData {
  [key: string]: unknown;
  published?: boolean;
}

function GalleryPublishNodeComponent({ data, selected }: NodeProps & { data: GalleryPublishNodeData }) {
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
        <span className="text-sm">🖼️</span>
        <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 mt-0.5">Gallery</p>
        <p className="text-[9px] text-gray-400">Publish to gallery</p>
        {data.published && (
          <span className="text-[8px] text-[#5F8A50] font-medium">Published ✓</span>
        )}
      </div>
    </div>
  );
}

export default memo(GalleryPublishNodeComponent);
