/**
 * TypedEdge — Custom bezier edge with DataType-colored stroke.
 */

import { memo } from 'react';
import { getBezierPath, type EdgeProps } from '@xyflow/react';
import { getSocketColor } from './dataTypeColors';

interface TypedEdgeData {
  dataType?: string;
  [key: string]: unknown;
}

function TypedEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
  selected,
}: EdgeProps & { data?: TypedEdgeData }) {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const color = getSocketColor(data?.dataType || 'text');

  return (
    <path
      id={id}
      className="react-flow__edge-path"
      d={edgePath}
      stroke={color}
      strokeWidth={selected ? 3 : 2}
      strokeOpacity={selected ? 1 : 0.7}
      fill="none"
      markerEnd={markerEnd}
    />
  );
}

export default memo(TypedEdgeComponent);
