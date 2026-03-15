import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import FlowNodeBase from './FlowNodeBase';

function IfElseNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string; condition?: string } }) {
  return (
    <div className="relative">
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" />
      <FlowNodeBase {...props} data={{ ...props.data, label: props.data.label || 'If / Else', icon: props.data.icon || '🔀' }}>
        <p className="text-[8px] text-gray-300 mt-1">{(props.data.condition as string) || 'score >= threshold'}</p>
      </FlowNodeBase>
      <Handle type="source" position={Position.Right} id="true" className="!w-2.5 !h-2.5 !bg-[#5F8A50] !border-white !border-2" style={{ top: '30%' }} />
      <Handle type="source" position={Position.Right} id="false" className="!w-2.5 !h-2.5 !bg-[#C65D4D] !border-white !border-2" style={{ top: '70%' }} />
    </div>
  );
}

export default memo(IfElseNode);
