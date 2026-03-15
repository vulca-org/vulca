/**
 * FlowNodeBase — Shared base for flow control nodes.
 * Slate accent #334155, hexagonal/diamond shape feel.
 */

import { memo, type ReactNode } from 'react';
import { type NodeProps } from '@xyflow/react';

interface FlowNodeData {
  [key: string]: unknown;
  label: string;
  icon: string;
}

function FlowNodeBaseComponent({
  data,
  selected,
  children,
}: NodeProps & { data: FlowNodeData; children?: ReactNode }) {
  return (
    <div
      className={[
        'min-w-[100px] bg-[#334155] dark:bg-[#1E293B] rounded-lg border-2 transition-all',
        selected ? 'border-[#C87F4A] ring-2 ring-[#C87F4A]/30' : 'border-[#475569]',
      ].join(' ')}
    >
      <div className="px-3 py-2 text-center">
        <span className="text-sm">{data.icon}</span>
        <p className="text-[10px] font-semibold text-white mt-0.5">{data.label}</p>
        {children}
      </div>
    </div>
  );
}

export default memo(FlowNodeBaseComponent);
