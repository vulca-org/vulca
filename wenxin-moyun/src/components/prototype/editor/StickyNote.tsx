/**
 * StickyNote — decorative canvas annotation node (React Flow custom node).
 *
 * Four color variants (yellow/bronze/coral/green), editable text via textarea,
 * no connection handles. Inspired by n8n's sticky notes.
 */

import { memo, useState, useCallback } from 'react';
import { useReactFlow, type NodeProps } from '@xyflow/react';
import type { StickyNoteData } from './types';

const COLOR_CLASSES: Record<StickyNoteData['color'], string> = {
  yellow: 'bg-yellow-100 dark:bg-yellow-900/40 border-yellow-300 dark:border-yellow-700',
  bronze: 'bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20 border-[#C9C2B8] dark:border-[#4A433C]',
  coral: 'bg-[#C65D4D]/10 dark:bg-[#C65D4D]/20 border-[#C65D4D]/30 dark:border-[#A04A3D]',
  green: 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/20 border-[#5F8A50]/30 dark:border-[#4A7040]',
};

function StickyNoteComponent({ id, data, selected }: NodeProps & { data: StickyNoteData }) {
  const { setNodes } = useReactFlow();
  const [localText, setLocalText] = useState(data.text);
  const colorClass = COLOR_CLASSES[data.color] || COLOR_CLASSES.yellow;

  const handleBlur = useCallback(() => {
    setNodes((nodes) =>
      nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, text: localText } } : n,
      ),
    );
  }, [id, localText, setNodes]);

  return (
    <div
      className={[
        'min-w-[150px] min-h-[100px] rounded-lg border p-3 shadow-sm',
        colorClass,
        selected ? 'ring-2 ring-[#C87F4A]/30' : '',
      ].join(' ')}
    >
      <textarea
        value={localText}
        onChange={(e) => setLocalText(e.target.value)}
        onBlur={handleBlur}
        className="w-full min-h-[80px] bg-transparent resize-none outline-none text-xs text-gray-800 dark:text-gray-200 placeholder-gray-400"
        placeholder="Type a note..."
      />
    </div>
  );
}

export default memo(StickyNoteComponent);
