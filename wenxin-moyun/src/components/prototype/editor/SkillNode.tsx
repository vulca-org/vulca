/**
 * SkillNode — Skill marketplace node with amber/gold accent.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface SkillNodeData {
  [key: string]: unknown;
  skillName: string;
  skillId: string;
  tags?: string[];
  status?: 'idle' | 'running' | 'done' | 'error';
  config?: Record<string, unknown>;
}

function SkillNodeComponent({ data, selected }: NodeProps & { data: SkillNodeData }) {
  const status = data.status || 'idle';

  return (
    <div
      className={[
        'min-w-[140px] max-w-[200px] bg-white dark:bg-gray-800 rounded-xl border-2 transition-all',
        selected
          ? 'border-[#B8923D] ring-2 ring-[#B8923D]/30'
          : status === 'running'
            ? 'border-[#B8923D] animate-pulse'
            : status === 'done'
              ? 'border-[#5F8A50]'
              : status === 'error'
                ? 'border-red-400'
                : 'border-[#B8923D]/40',
      ].join(' ')}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-[#B8923D] !border-white dark:!border-gray-800 !border-2"
      />

      {/* Header */}
      <div className="px-3 py-2 border-b border-[#B8923D]/20">
        <div className="flex items-center gap-1.5">
          <span className="text-sm">⚡</span>
          <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
            {data.skillName || 'Skill'}
          </span>
        </div>
        {data.tags && data.tags.length > 0 && (
          <div className="flex flex-wrap gap-0.5 mt-1">
            {data.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-[7px] px-1 py-0.5 rounded bg-[#B8923D]/10 text-[#B8923D] dark:text-[#DDA574]"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Status */}
      {status !== 'idle' && (
        <div className="px-3 py-1">
          <span
            className={`text-[9px] font-medium ${
              status === 'done' ? 'text-[#5F8A50]' : status === 'error' ? 'text-red-500' : 'text-[#B8923D]'
            }`}
          >
            {status === 'running' ? 'Running...' : status === 'done' ? 'Complete' : status === 'error' ? 'Error' : ''}
          </span>
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-[#5F8A50] !border-white dark:!border-gray-800 !border-2"
      />
    </div>
  );
}

export default memo(SkillNodeComponent);
