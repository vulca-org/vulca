import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import FlowNodeBase from './FlowNodeBase';

function MergeNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <div className="relative">
      <Handle type="target" position={Position.Left} id="a" className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" style={{ top: '30%' }} />
      <Handle type="target" position={Position.Left} id="b" className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" style={{ top: '70%' }} />
      <FlowNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Merge', icon: props.data.icon || '🔗' }} />
      <Handle type="source" position={Position.Right} className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" />
    </div>
  );
}

export default memo(MergeNode);
