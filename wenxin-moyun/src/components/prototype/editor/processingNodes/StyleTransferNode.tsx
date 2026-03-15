import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import ProcessingNodeBase from './ProcessingNodeBase';

function StyleTransferNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <ProcessingNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Style Transfer', icon: props.data.icon || '🎨' }}>
      <p className="text-[9px] text-gray-400 mt-1">Apply artistic style</p>
    </ProcessingNodeBase>
  );
}

export default memo(StyleTransferNode);
