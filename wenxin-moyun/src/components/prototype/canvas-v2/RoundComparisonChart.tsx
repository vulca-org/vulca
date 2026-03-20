/**
 * RoundComparisonChart — Line chart showing round-by-round score trends.
 * Uses Recharts to visualize L1-L5 dimension scores across pipeline rounds.
 */

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { RoundData } from '@/hooks/usePrototypePipeline';

const DIM_COLORS: Record<string, string> = {
  L1: '#005ab4',
  L2: '#5F8A50',
  L3: '#B8923D',
  L4: '#C87F4A',
  L5: '#C65D4D',
};

const DIM_LABELS: Record<string, string> = {
  L1: 'Visual',
  L2: 'Technical',
  L3: 'Cultural',
  L4: 'Critical',
  L5: 'Philosophical',
};

// Map full dimension names back to L labels
const FULL_TO_L: Record<string, string> = {
  visual_perception: 'L1',
  technical_analysis: 'L2',
  cultural_context: 'L3',
  critical_interpretation: 'L4',
  philosophical_aesthetic: 'L5',
};

interface Props {
  rounds: RoundData[];
}

export default function RoundComparisonChart({ rounds }: Props) {
  if (rounds.length === 0) return null;

  // Build chart data from rounds
  const data = rounds.map((r) => {
    const entry: Record<string, number | string> = { round: `R${r.round}` };

    // Extract scores from scoredCandidates
    const best = r.scoredCandidates[0];
    if (best?.dimension_scores) {
      for (const ds of best.dimension_scores) {
        const lKey = FULL_TO_L[ds.dimension] || ds.dimension;
        entry[lKey] = Math.round(ds.score * 100);
      }
    }

    // Overall
    if (r.weightedTotal != null) {
      entry.overall = Math.round(r.weightedTotal * 100);
    }

    return entry;
  });

  // Determine which L keys have data
  const activeKeys = Object.keys(DIM_COLORS).filter(k =>
    data.some(d => typeof d[k] === 'number')
  );

  if (activeKeys.length === 0) return null;

  return (
    <div className="mb-4">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-outline mb-3">
        Round Progress
      </h3>
      <div className="bg-white rounded-xl p-4">
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
            <XAxis
              dataKey="round"
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                background: '#f9f9ff',
                border: 'none',
                borderRadius: 12,
                boxShadow: '0 4px 24px rgba(28,28,25,0.06)',
                fontSize: 11,
              }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(value: any, name: any) => [`${value ?? 0}%`, DIM_LABELS[name] || name]}
            />
            {activeKeys.map(key => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={DIM_COLORS[key]}
                strokeWidth={2}
                dot={{ r: 3, strokeWidth: 2 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-2 mt-2 justify-center">
          {activeKeys.map(key => (
            <span key={key} className="flex items-center gap-1 text-[9px] text-on-surface-variant">
              <span className="w-2 h-2 rounded-full" style={{ background: DIM_COLORS[key] }} />
              {DIM_LABELS[key]}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
