/**
 * CriticPreview — 5 horizontal L1-L5 mini bars with color coding.
 * Green >= 0.85, Yellow >= 0.7, Red below.
 */

import { memo } from 'react';

interface CriticPreviewProps {
  scores: { dimension: string; score: number }[];
}

const DIMENSION_SHORT: Record<string, string> = {
  L1_visual_perception: 'L1',
  L2_technique_analysis: 'L2',
  L3_cultural_context: 'L3',
  L4_creative_expression: 'L4',
  L5_holistic_integration: 'L5',
};

function getScoreColor(score: number): string {
  if (score >= 0.85) return 'bg-[#5F8A50]';
  if (score >= 0.7) return 'bg-[#B8923D]';
  return 'bg-[#C65D4D]';
}

function CriticPreviewComponent({ scores }: CriticPreviewProps) {
  if (scores.length === 0) return null;

  // Show up to 5 scores
  const shown = scores.slice(0, 5);

  return (
    <div className="flex flex-col gap-0.5 mt-1.5 w-full">
      {shown.map((s) => {
        const label = DIMENSION_SHORT[s.dimension] || s.dimension.slice(0, 3);
        const pct = Math.round(s.score * 100);
        return (
          <div key={s.dimension} className="flex items-center gap-1">
            <span className="text-[7px] text-gray-500 dark:text-gray-400 w-4 text-right font-mono">
              {label}
            </span>
            <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${getScoreColor(s.score)}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-[7px] text-gray-400 w-5 text-right font-mono">{pct}</span>
          </div>
        );
      })}
    </div>
  );
}

export default memo(CriticPreviewComponent);
