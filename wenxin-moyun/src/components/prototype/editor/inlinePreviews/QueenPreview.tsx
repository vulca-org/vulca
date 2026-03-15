/**
 * QueenPreview — Decision pill badge with round counter.
 * ACCEPT (green), RERUN (amber), FIX (red)
 */

import { memo } from 'react';

interface QueenPreviewProps {
  decision: { action: string; reason?: string; round?: number };
}

const ACTION_STYLES: Record<string, { bg: string; text: string }> = {
  accept: { bg: 'bg-[#5F8A50]/15', text: 'text-[#5F8A50]' },
  rerun: { bg: 'bg-[#B8923D]/15', text: 'text-[#B8923D]' },
  fix: { bg: 'bg-[#C65D4D]/15', text: 'text-[#C65D4D]' },
  stop: { bg: 'bg-gray-200 dark:bg-gray-700', text: 'text-gray-500' },
};

function QueenPreviewComponent({ decision }: QueenPreviewProps) {
  const action = decision.action?.toLowerCase() || 'stop';
  const style = ACTION_STYLES[action] || ACTION_STYLES.stop;

  return (
    <div className="flex items-center gap-1.5 mt-1.5">
      <span
        className={`px-2 py-0.5 rounded-full text-[9px] font-semibold uppercase ${style.bg} ${style.text}`}
      >
        {action}
      </span>
      {decision.round != null && (
        <span className="text-[8px] text-gray-400 font-mono">R{decision.round}</span>
      )}
    </div>
  );
}

export default memo(QueenPreviewComponent);
