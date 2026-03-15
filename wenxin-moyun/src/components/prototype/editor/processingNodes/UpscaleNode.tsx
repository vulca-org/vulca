import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import ProcessingNodeBase from './ProcessingNodeBase';

function UpscaleNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <ProcessingNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Upscale', icon: props.data.icon || '🔍' }}>
      <p className="text-[9px] text-gray-400 mt-1">AI upscale 2x/4x</p>
    </ProcessingNodeBase>
  );
}

export default memo(UpscaleNode);
