import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import FlowNodeBase from './FlowNodeBase';

function LoopNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string; iteration?: number; maxIterations?: number } }) {
  const iteration = (props.data.iteration as number) || 0;
  const max = (props.data.maxIterations as number) || 3;

  return (
    <div className="relative">
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" />
      <FlowNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Loop', icon: props.data.icon || '🔄' }}>
        <span className="inline-block mt-1 px-1.5 py-0.5 rounded-full bg-white/10 text-[8px] text-gray-200 font-mono">
          {iteration}/{max}
        </span>
      </FlowNodeBase>
      <Handle type="source" position={Position.Right} className="!w-2.5 !h-2.5 !bg-[#6B7B8D] !border-white !border-2" />
    </div>
  );
}

export default memo(LoopNode);
