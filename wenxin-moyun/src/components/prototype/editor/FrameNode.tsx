/**
 * FrameNode — resizable group container with label + color.
 * Groups related nodes visually (like ComfyUI's Group Node).
 */

import { memo, useState } from 'react';
import { type NodeProps, NodeResizer } from '@xyflow/react';

interface FrameNodeData {
  [key: string]: unknown;
  label: string;
  color: string;
}

const FRAME_COLORS = [
  { label: 'Slate', value: '#334155' },
  { label: 'Bronze', value: '#C87F4A' },
  { label: 'Sage', value: '#5F8A50' },
  { label: 'Amber', value: '#B8923D' },
  { label: 'Coral', value: '#C65D4D' },
];

function FrameNodeComponent({ data, selected }: NodeProps & { data: FrameNodeData }) {
  const [editing, setEditing] = useState(false);
  const color = data.color || FRAME_COLORS[0].value;

  return (
    <>
      <NodeResizer
        minWidth={200}
        minHeight={150}
        isVisible={selected}
        lineClassName="!border-[#C87F4A]"
        handleClassName="!w-3 !h-3 !bg-[#C87F4A] !border-white"
      />
      <div
        className="w-full h-full rounded-xl border-2 border-dashed"
        style={{
          borderColor: color,
          backgroundColor: `${color}08`,
          minWidth: 200,
          minHeight: 150,
        }}
      >
        <div
          className="px-3 py-1.5 text-xs font-semibold rounded-t-lg"
          style={{ color, backgroundColor: `${color}15` }}
          onDoubleClick={() => setEditing(true)}
        >
          {editing ? (
            <input
              autoFocus
              defaultValue={data.label}
              className="bg-transparent outline-none w-full text-xs font-semibold"
              style={{ color }}
              onBlur={() => setEditing(false)}
              onKeyDown={(e) => e.key === 'Enter' && setEditing(false)}
            />
          ) : (
            data.label || 'Frame'
          )}
        </div>
      </div>
    </>
  );
}

export default memo(FrameNodeComponent);
export { FRAME_COLORS };
