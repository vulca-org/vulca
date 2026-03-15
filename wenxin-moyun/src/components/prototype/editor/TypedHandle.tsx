/**
 * TypedHandle — React Flow Handle wrapper with DataType-colored socket.
 * Shows a colored circle matching the data type and tooltip on hover.
 */

import { memo, useState } from 'react';
import { Handle, Position, type HandleProps } from '@xyflow/react';
import { getSocketColor, DATA_TYPE_LABELS, type DataType } from './dataTypeColors';

interface TypedHandleProps extends Omit<HandleProps, 'position'> {
  dataType?: DataType | string;
  position?: Position;
  label?: string;
}

function TypedHandleComponent({
  dataType = 'text',
  position = Position.Left,
  label,
  type,
  ...rest
}: TypedHandleProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const color = getSocketColor(dataType);
  const displayLabel = label || DATA_TYPE_LABELS[dataType as DataType] || dataType;

  return (
    <div
      className="relative"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <Handle
        type={type}
        position={position}
        {...rest}
        style={{
          width: 10,
          height: 10,
          backgroundColor: color,
          border: '2px solid white',
          ...(rest.style || {}),
        }}
      />
      {showTooltip && (
        <div
          className="absolute z-50 px-2 py-1 text-[9px] font-medium text-white rounded shadow-lg whitespace-nowrap pointer-events-none"
          style={{
            backgroundColor: color,
            [position === Position.Left ? 'right' : 'left']: '16px',
            top: '50%',
            transform: 'translateY(-50%)',
          }}
        >
          {displayLabel}
        </div>
      )}
    </div>
  );
}

export default memo(TypedHandleComponent);
