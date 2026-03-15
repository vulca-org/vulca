import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import ProcessingNodeBase from './ProcessingNodeBase';

function ColorHarmonyNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <ProcessingNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Color Harmony', icon: props.data.icon || '🌈' }}>
      <p className="text-[9px] text-gray-400 mt-1">Optimize color balance</p>
    </ProcessingNodeBase>
  );
}

export default memo(ColorHarmonyNode);
