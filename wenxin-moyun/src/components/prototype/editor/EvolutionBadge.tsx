/**
 * EvolutionBadge — Sparkle icon with "AI suggests..." tooltip.
 * Amber accent #B8923D, shown when evolution suggestions exist.
 */

import { memo, useState } from 'react';

interface EvolutionBadgeProps {
  suggestion?: string;
}

function EvolutionBadgeComponent({ suggestion }: EvolutionBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  if (!suggestion) return null;

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className="text-[10px] text-[#B8923D] animate-pulse cursor-help">✨</span>
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 rounded bg-[#B8923D] text-white text-[8px] whitespace-nowrap shadow-lg z-50 max-w-[200px]">
          <span className="font-semibold">AI suggests:</span> {suggestion}
        </div>
      )}
    </div>
  );
}

export default memo(EvolutionBadgeComponent);
