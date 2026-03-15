import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import FlowNodeBase from './FlowNodeBase';

function SplitNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <div className="relative">
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" />
      <FlowNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Split', icon: props.data.icon || '🔱' }} />
      <Handle type="source" position={Position.Right} id="a" className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" style={{ top: '30%' }} />
      <Handle type="source" position={Position.Right} id="b" className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" style={{ top: '70%' }} />
    </div>
  );
}

export default memo(SplitNode);
