/**
 * CreationModeSelector — unified selector replacing ProviderQuickSwitch + HITL toggle.
 *
 * Three modes:
 *  - Preview:  instant mock results, free, for layout preview
 *  - Guided:   real Gemini images + HITL pauses for human review at each stage
 *  - Generate: real Gemini images, fully automatic pipeline
 */

import { IOSSegmentedControl } from '../ios';
import type { SegmentItem } from '../ios';
import type { CreationMode } from '@/store/canvasStore';

const MODES: { id: CreationMode; label: string; desc: string; cost: number }[] = [
  { id: 'preview',  label: 'Preview',  desc: 'Instant mock — free',           cost: 0     },
  { id: 'guided',   label: 'Guided',   desc: 'Real images — you review each stage', cost: 0.067 },
  { id: 'generate', label: 'Generate', desc: 'Real images — fully automatic', cost: 0.067 },
];

interface Props {
  value: CreationMode;
  onChange: (mode: CreationMode) => void;
  disabled?: boolean;
  nCandidates?: number;
  /** Called when a guest user tries to select a gated mode (guided/generate). */
  onAuthRequired?: (mode: CreationMode) => void;
  /** Whether the user is a guest (shows lock icons on gated modes). */
  isGuest?: boolean;
}

export default function CreationModeSelector({
  value,
  onChange,
  disabled = false,
  nCandidates = 2,
  onAuthRequired,
  isGuest = false,
}: Props) {
  const segments: SegmentItem[] = MODES.map(m => ({
    id: m.id,
    label: isGuest && m.id !== 'preview' ? `${m.label} 🔒` : m.label,
    value: m.id,
  }));

  const selectedIndex = Math.max(0, MODES.findIndex(m => m.id === value));
  const selected = MODES[selectedIndex];
  const estimatedCost = selected.cost * nCandidates;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between px-1">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          Creation Mode
        </span>
        {selected.cost > 0 && (
          <span className="text-[10px] text-gray-400 dark:text-gray-500">
            ~${estimatedCost.toFixed(3)}/run ({nCandidates} images)
          </span>
        )}
      </div>
      <IOSSegmentedControl
        segments={segments}
        selectedIndex={selectedIndex}
        onChange={(idx) => {
          const m = MODES[idx];
          if (!m) return;
          if (isGuest && m.id !== 'preview') {
            onAuthRequired?.(m.id);
            return;
          }
          onChange(m.id);
        }}
        size="compact"
        disabled={disabled}
      />
      <div className="flex items-center gap-1.5 px-1">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{
            backgroundColor: selected.id === 'preview' ? '#5F8A50'
              : selected.id === 'guided' ? '#B8923D'
              : '#C87F4A',
          }}
        />
        <span className="text-[10px] text-gray-400 dark:text-gray-500">
          {selected.desc}
        </span>
      </div>
    </div>
  );
}
