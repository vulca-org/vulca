/**
 * Provider Quick Switch — segmented control for toggling between Mock and NB2 providers.
 *
 * Mock: instant, free (sage-green #5F8A50)
 * NB2:  $0.067/img, real generation (amber-gold #B8923D)
 */

import { IOSSegmentedControl } from '../ios';
import type { SegmentItem } from '../ios';

const PROVIDER_SEGMENTS: SegmentItem[] = [
  { id: 'mock', label: 'Mock', value: 'mock' },
  { id: 'nb2', label: 'NB2', value: 'nb2' },
];

interface ProviderQuickSwitchProps {
  value: string;
  onChange: (provider: string) => void;
  disabled?: boolean;
  /** Number of candidates — used for cost estimate. */
  nCandidates?: number;
}

export default function ProviderQuickSwitch({
  value,
  onChange,
  disabled = false,
  nCandidates = 4,
}: ProviderQuickSwitchProps) {
  const selectedIndex = value === 'nb2' ? 1 : 0;
  const isNb2 = value === 'nb2';
  const estCost = (nCandidates * 0.067).toFixed(2);

  return (
    <div className="px-1 space-y-1.5">
      {/* Segmented control with custom active-segment colors */}
      <div className="relative">
        <IOSSegmentedControl
          segments={PROVIDER_SEGMENTS}
          selectedIndex={selectedIndex}
          onChange={(idx) => {
            const seg = PROVIDER_SEGMENTS[idx];
            onChange(String(seg.value ?? seg.id));
          }}
          size="compact"
          style="bordered"
          disabled={disabled}
          className="w-full"
        />

        {/* Color overlay for active segment */}
        <div
          className="pointer-events-none absolute inset-y-0 flex"
          style={{ width: '100%' }}
        >
          <div
            className="flex-1 flex items-center justify-center rounded-md text-xs font-medium transition-colors duration-200"
            style={{
              color: selectedIndex === 0 ? '#5F8A50' : undefined,
              opacity: selectedIndex === 0 ? 1 : 0,
            }}
          />
          <div
            className="flex-1 flex items-center justify-center rounded-md text-xs font-medium transition-colors duration-200"
            style={{
              color: selectedIndex === 1 ? '#B8923D' : undefined,
              opacity: selectedIndex === 1 ? 1 : 0,
            }}
          />
        </div>
      </div>

      {/* Descriptive text */}
      <div className="flex items-center justify-between text-[11px] px-0.5">
        <span
          className="transition-colors duration-200"
          style={{ color: isNb2 ? '#9CA3AF' : '#5F8A50' }}
        >
          {isNb2 ? '' : 'Instant, free'}
        </span>
        <span
          className="transition-colors duration-200"
          style={{ color: isNb2 ? '#B8923D' : '#9CA3AF' }}
        >
          {isNb2 ? '$0.067/img' : ''}
        </span>
      </div>

      {/* Cost hint when NB2 is selected */}
      {isNb2 && (
        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-[#B8923D]/10 dark:bg-[#B8923D]/15 border border-[#B8923D]/20 dark:border-[#B8923D]/25">
          <span className="text-[11px] text-[#B8923D] dark:text-[#D4A94E]">
            Est. ~${estCost} for {nCandidates} candidate{nCandidates !== 1 ? 's' : ''}
          </span>
        </div>
      )}
    </div>
  );
}
