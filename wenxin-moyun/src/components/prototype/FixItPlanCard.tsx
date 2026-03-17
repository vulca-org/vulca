/**
 * FixItPlan display card — shows agent repair strategy and per-layer items.
 */

import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';
import type { FixItPlan } from '../../hooks/usePrototypePipeline';

interface Props {
  fixItPlan: FixItPlan;
}

export default function FixItPlanCard({ fixItPlan }: Props) {
  return (
    <IOSCard variant="elevated" padding="md" animate={false} className="border-[#C9C2B8] dark:border-[#4A433C]">
      <IOSCardHeader
        title="FixItPlan"
        subtitle={fixItPlan.estimated_improvement > 0
          ? `Est. +${fixItPlan.estimated_improvement.toFixed(3)}`
          : undefined}
        action={
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20 text-[#C87F4A] dark:text-[#DDA574] font-medium">
            {fixItPlan.overall_strategy.replace(/_/g, ' ')}
          </span>
        }
      />
      <IOSCardContent>
        <div className="space-y-2">
          {fixItPlan.items.map((item, i) => {
            const sourceScore = fixItPlan.source_scores?.[item.target_layer];
            return (
              <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-gray-50 dark:bg-gray-900/40">
                <div className="flex flex-col items-center gap-0.5 shrink-0">
                  <span className="text-xs font-bold text-[#C87F4A] dark:text-[#DDA574]">
                    {item.target_layer}
                  </span>
                  <span className="text-[10px] px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-mono">
                    P{item.priority}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 text-[11px] text-gray-500 dark:text-gray-400 mb-0.5 flex-wrap">
                    {sourceScore != null && (
                      <span>Score: <span className="font-mono">{sourceScore.toFixed(2)}</span></span>
                    )}
                    {item.mask_region_hint && (
                      <span className="px-1 py-0.5 rounded bg-[#6B8E7A]/10 dark:bg-[#6B8E7A]/10 text-[#6B8E7A] dark:text-[#87A878]">
                        mask: {item.mask_region_hint}
                      </span>
                    )}
                  </div>
                  {item.issue && (
                    <p className="text-xs text-red-600 dark:text-red-400 mb-0.5">{item.issue}</p>
                  )}
                  {item.prompt_delta && (
                    <p className="text-xs text-gray-700 dark:text-gray-300 italic">"{item.prompt_delta}"</p>
                  )}
                  {item.reference_suggestion && (
                    <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">
                      Ref: {item.reference_suggestion}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}
