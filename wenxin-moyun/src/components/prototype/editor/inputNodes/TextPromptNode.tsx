import { memo, useState } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface TextPromptNodeData {
  [key: string]: unknown;
  text?: string;
}

function TextPromptNodeComponent({ data, selected }: NodeProps & { data: TextPromptNodeData }) {
  const [text, setText] = useState(data.text || '');

  return (
    <div
      className={[
        'min-w-[160px] max-w-[200px] bg-white dark:bg-gray-800 rounded-lg border',
        selected ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30' : 'border-gray-200 dark:border-gray-700',
      ].join(' ')}
    >
      <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-gray-100 dark:border-gray-700">
        <span className="text-sm">📝</span>
        <span className="text-[10px] font-semibold text-gray-700 dark:text-gray-300">Text Prompt</span>
      </div>
      <div className="p-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter prompt text..."
          className="w-full h-16 text-[10px] bg-gray-50 dark:bg-gray-700 rounded p-1.5 resize-none outline-none text-gray-700 dark:text-gray-300 placeholder-gray-400"
        />
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(TextPromptNodeComponent);
