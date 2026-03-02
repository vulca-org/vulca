/**
 * L1-L5 Radar Chart for comparing Critic scores across rounds.
 *
 * Shows each round as a separate polygon on the radar, making it easy
 * to see which dimensions improved or degraded between rounds.
 * Also overlays dynamic weights as a dashed outline.
 */

import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, Legend, ResponsiveContainer, Tooltip,
} from 'recharts';
import type { RoundData } from '../../hooks/usePrototypePipeline';
import { PROTOTYPE_DIMENSIONS, PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';

const ROUND_COLORS = [
  '#3B82F6', // blue
  '#10B981', // emerald
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // violet
];

interface Props {
  rounds: RoundData[];
  dynamicWeights?: Record<string, number> | null;
}

interface RadarDataPoint {
  dimension: string;
  label: string;
  weight: number;
  [key: string]: string | number;
}

export default function CriticRadarChart({ rounds, dynamicWeights }: Props) {
  if (rounds.length === 0) return null;

  // Build data points: one entry per dimension
  const data: RadarDataPoint[] = PROTOTYPE_DIMENSIONS.map(dim => {
    const point: RadarDataPoint = {
      dimension: dim,
      label: PROTOTYPE_DIM_LABELS[dim].short,
      weight: dynamicWeights?.[dim] ? dynamicWeights[dim] * 5 : 0, // scale weights to 0-1 range (max weight ~0.25 → scaled to ~1.25)
    };

    for (const rd of rounds) {
      const best = rd.scoredCandidates.length > 0
        ? rd.scoredCandidates.reduce((a, b) => a.weighted_total > b.weighted_total ? a : b)
        : null;
      const score = best?.dimension_scores.find(s => s.dimension === dim);
      point[`R${rd.round}`] = score?.score ?? 0;
    }

    return point;
  });

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">L1-L5 Radar</h3>
      <div style={{ width: '100%', minWidth: 200, height: 256 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: '#6b7280' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 1]}
              tick={{ fontSize: 9, fill: '#9ca3af' }}
              tickCount={6}
            />

            {/* Dynamic weights as dashed outline */}
            {dynamicWeights && (
              <Radar
                name="Weight"
                dataKey="weight"
                stroke="#d1d5db"
                fill="none"
                strokeDasharray="4 4"
                strokeWidth={1}
              />
            )}

            {/* Per-round score polygons */}
            {rounds.map((rd, i) => (
              <Radar
                key={rd.round}
                name={`Round ${rd.round}`}
                dataKey={`R${rd.round}`}
                stroke={ROUND_COLORS[i % ROUND_COLORS.length]}
                fill={ROUND_COLORS[i % ROUND_COLORS.length]}
                fillOpacity={i === rounds.length - 1 ? 0.2 : 0.05}
                strokeWidth={i === rounds.length - 1 ? 2 : 1}
              />
            ))}

            <Tooltip
              formatter={((value?: number, name?: string) => [(value ?? 0).toFixed(3), name ?? '']) as never}
              contentStyle={{
                backgroundColor: 'rgba(255,255,255,0.95)',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                fontSize: '12px',
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: '11px' }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
