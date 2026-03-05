/**
 * TraditionWeightGrid — 9 traditions × 5 dimensions heatmap.
 * Embedded at the bottom of Critic's NodeParamPanel.
 *
 * Shows how the cultural router adjusts L1-L5 weights per tradition.
 * Read-only reference; user edits weights via the sliders above.
 */

const TRADITIONS = [
  { id: 'chinese_xieyi', label: 'Xieyi' },
  { id: 'chinese_gongbi', label: 'Gongbi' },
  { id: 'chinese_guohua', label: 'Guohua' },
  { id: 'western_academic', label: 'Western' },
  { id: 'islamic_geometric', label: 'Islamic' },
  { id: 'watercolor', label: 'Watercolor' },
  { id: 'african_traditional', label: 'African' },
  { id: 'south_asian', label: 'S. Asian' },
  { id: 'default', label: 'Default' },
] as const;

const DIMENSIONS = ['L1', 'L2', 'L3', 'L4', 'L5'] as const;

/** Default weight profiles per tradition (sum = 1.0 each row) */
const WEIGHT_PROFILES: Record<string, number[]> = {
  chinese_xieyi:      [0.15, 0.15, 0.20, 0.20, 0.30],
  chinese_gongbi:     [0.25, 0.20, 0.15, 0.20, 0.20],
  chinese_guohua:     [0.20, 0.20, 0.20, 0.20, 0.20],
  western_academic:   [0.25, 0.25, 0.15, 0.20, 0.15],
  islamic_geometric:  [0.20, 0.15, 0.25, 0.15, 0.25],
  watercolor:         [0.20, 0.25, 0.15, 0.20, 0.20],
  african_traditional:[0.15, 0.20, 0.25, 0.15, 0.25],
  south_asian:        [0.15, 0.20, 0.20, 0.20, 0.25],
  default:            [0.20, 0.20, 0.20, 0.20, 0.20],
};

function heatColor(weight: number): string {
  // 0.15 → light, 0.30 → intense
  const intensity = Math.min(1, Math.max(0, (weight - 0.10) / 0.25));
  const r = Math.round(59 + intensity * 140);   // blue(59) → purple(199)
  const g = Math.round(130 - intensity * 80);    // 130 → 50
  const b = Math.round(246 - intensity * 40);    // 246 → 206
  return `rgb(${r}, ${g}, ${b})`;
}

export default function TraditionWeightGrid() {
  return (
    <div className="mt-3">
      <div className="text-[10px] font-semibold text-gray-600 dark:text-gray-400 mb-1.5 uppercase tracking-wider">
        Router Weight Profiles
      </div>
      <div
        className="grid gap-px text-[9px]"
        style={{ gridTemplateColumns: `64px repeat(${DIMENSIONS.length}, 1fr)` }}
      >
        {/* Header row */}
        <div />
        {DIMENSIONS.map(d => (
          <div key={d} className="text-center font-semibold text-gray-500 dark:text-gray-400 py-0.5">
            {d}
          </div>
        ))}

        {/* Data rows */}
        {TRADITIONS.map(t => {
          const weights = WEIGHT_PROFILES[t.id] ?? WEIGHT_PROFILES.default;
          return (
            <div key={t.id} className="contents">
              <div className="text-right pr-1.5 text-gray-600 dark:text-gray-400 py-0.5 truncate">
                {t.label}
              </div>
              {weights.map((w, i) => (
                <div
                  key={i}
                  className="text-center text-white font-mono py-0.5 rounded-sm"
                  style={{ backgroundColor: heatColor(w), opacity: 0.85 }}
                  title={`${t.label} ${DIMENSIONS[i]}: ${w.toFixed(2)}`}
                >
                  {w.toFixed(2)}
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
