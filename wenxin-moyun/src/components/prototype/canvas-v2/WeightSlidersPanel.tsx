/**
 * WeightSlidersPanel — L1-L5 weight sliders for custom scoring weights.
 * Uses IOSSlider components, visible in right panel idle/config state.
 */

import { IOSSlider } from '@/components/ios';

const DIMENSIONS = [
  { key: 'L1', label: 'L1 · Visual Perception', color: 'primary' as const },
  { key: 'L2', label: 'L2 · Technical Execution', color: 'green' as const },
  { key: 'L3', label: 'L3 · Cultural Context', color: 'orange' as const },
  { key: 'L4', label: 'L4 · Critical Interpretation', color: 'primary' as const },
  { key: 'L5', label: 'L5 · Philosophical Aesthetics', color: 'red' as const },
];

interface Props {
  weights: Record<string, number>;
  onChange: (weights: Record<string, number>) => void;
  disabled?: boolean;
}

export default function WeightSlidersPanel({ weights, onChange, disabled }: Props) {
  const handleChange = (key: string, value: number) => {
    onChange({ ...weights, [key]: value });
  };

  return (
    <div className="mb-4">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-outline mb-3">
        Scoring Weights
      </h3>
      <div className="bg-white rounded-2xl p-4 space-y-3">
        {DIMENSIONS.map(({ key, label, color }) => (
          <IOSSlider
            key={key}
            label={label}
            value={Math.round((weights[key] ?? 0.2) * 100)}
            onChange={(v) => handleChange(key, v / 100)}
            min={0}
            max={50}
            step={1}
            color={color}
            size="sm"
            showValue
            formatValue={(v) => `${v}%`}
          />
        ))}
        <p className="text-[9px] text-on-surface-variant/60 mt-2 text-center">
          Adjust weights to emphasize specific dimensions during evaluation
        </p>
      </div>
    </div>
  );
}
