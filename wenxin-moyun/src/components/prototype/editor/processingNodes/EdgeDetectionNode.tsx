import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import ProcessingNodeBase from './ProcessingNodeBase';

function EdgeDetectionNode(props: NodeProps & { data: { [key: string]: unknown; label?: string; icon?: string } }) {
  return (
    <ProcessingNodeBase {...props} data={{ ...props.data, label: props.data.label || 'Edge Detection', icon: props.data.icon || '✂️' }}>
      <p className="text-[9px] text-gray-400 mt-1">Detect edges/contours</p>
    </ProcessingNodeBase>
  );
}

export default memo(EdgeDetectionNode);
