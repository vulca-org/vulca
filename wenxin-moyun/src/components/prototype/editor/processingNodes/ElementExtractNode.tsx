import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import ProcessingNodeBase from './ProcessingNodeBase';

function ElementExtractNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <ProcessingNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Element Extract', icon: props.data.icon || '🧩' }}>
      <p className="text-[9px] text-gray-400 mt-1">Extract visual elements</p>
    </ProcessingNodeBase>
  );
}

export default memo(ElementExtractNode);
