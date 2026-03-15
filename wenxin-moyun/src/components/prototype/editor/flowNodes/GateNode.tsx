import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import FlowNodeBase from './FlowNodeBase';

function GateNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string; threshold?: number; passed?: boolean } }) {
  const threshold = (props.data.threshold as number) || 0.7;
  const passed = props.data.passed as boolean | undefined;

  return (
    <div className="relative">
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !bg-[#C65D4D] !border-white !border-2" />
      <FlowNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Quality Gate', icon: props.data.icon || '🚦' }}>
        <div className="mt-1 flex items-center gap-1">
          <span className="text-[8px] text-gray-300 font-mono">≥{threshold}</span>
          {passed !== undefined && (
            <span className={`text-[8px] font-semibold ${passed ? 'text-[#5F8A50]' : 'text-[#C65D4D]'}`}>
              {passed ? 'PASS' : 'FAIL'}
            </span>
          )}
        </div>
      </FlowNodeBase>
      <Handle type="source" position={Position.Right} id="pass" className="!w-2.5 !h-2.5 !bg-[#5F8A50] !border-white !border-2" style={{ top: '30%' }} />
      <Handle type="source" position={Position.Right} id="fail" className="!w-2.5 !h-2.5 !bg-[#C65D4D] !border-white !border-2" style={{ top: '70%' }} />
    </div>
  );
}

export default memo(GateNode);
