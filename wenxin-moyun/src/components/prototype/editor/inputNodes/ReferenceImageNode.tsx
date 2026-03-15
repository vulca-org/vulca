import { memo, useState } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface ReferenceImageNodeData {
  [key: string]: unknown;
  imageUrl?: string;
}

function ReferenceImageNodeComponent({ data, selected }: NodeProps & { data: ReferenceImageNodeData }) {
  const [preview, setPreview] = useState<string | null>(data.imageUrl || null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setPreview(URL.createObjectURL(file));
    }
  };

  return (
    <div
      className={[
        'min-w-[160px] max-w-[200px] bg-white dark:bg-gray-800 rounded-lg border',
        selected ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30' : 'border-gray-200 dark:border-gray-700',
      ].join(' ')}
    >
      <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-gray-100 dark:border-gray-700">
        <span className="text-sm">🖼️</span>
        <span className="text-[10px] font-semibold text-gray-700 dark:text-gray-300">Reference Image</span>
      </div>
      <div className="p-2" onDrop={handleDrop} onDragOver={(e) => e.preventDefault()}>
        {preview ? (
          <img src={preview} alt="Reference" className="w-full h-20 object-cover rounded" />
        ) : (
          <div className="w-full h-20 border-2 border-dashed border-gray-200 dark:border-gray-600 rounded flex items-center justify-center">
            <span className="text-[9px] text-gray-400">Drop image or paste URL</span>
          </div>
        )}
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#C87F4A] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(ReferenceImageNodeComponent);
