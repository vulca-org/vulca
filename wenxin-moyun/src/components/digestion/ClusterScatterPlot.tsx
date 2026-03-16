/**
 * ClusterScatterPlot - Feature Space Cluster Visualization
 *
 * Renders a Recharts ScatterChart of digestion system clusters.
 * Each tradition gets its own Scatter series with a unique Art Professional color.
 * Dot size encodes member count; custom tooltip shows centroid dimensions.
 */

import { useState, useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ZAxis,
} from 'recharts';
import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';
import { useChartTheme } from '../../hooks/useChartTheme';
import { chartConfig } from '../../config/chartTheme';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ClusterData {
  cluster_id: string;
  feature_centroid: Record<string, number>;
  session_ids?: string[];
  size: number;
  tradition: string;
  source?: string;
  traditions?: string[];
}

interface ClusterScatterPlotProps {
  clusters: ClusterData[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

type DimensionKey =
  | 'avg_score'
  | 'cultural_depth'
  | 'l5_emphasis'
  | 'l4_emphasis'
  | 'tradition_specificity'
  | 'dimension_variance';

const DIMENSION_OPTIONS: { value: DimensionKey; label: string }[] = [
  { value: 'avg_score', label: 'Avg Score' },
  { value: 'cultural_depth', label: 'Cultural Depth' },
  { value: 'l5_emphasis', label: 'L5 Emphasis' },
  { value: 'l4_emphasis', label: 'L4 Emphasis' },
  { value: 'tradition_specificity', label: 'Tradition Specificity' },
  { value: 'dimension_variance', label: 'Dimension Variance' },
];

/** Art Professional palette — no blue/purple/indigo/violet. */
const TRADITION_COLORS: Record<string, string> = {
  chinese_xieyi: '#C87F4A',
  japanese_wabi_sabi: '#5F8A50',
  european_renaissance: '#B8923D',
  islamic_geometric: '#C65D4D',
  indian_rasa: '#9B6B56',
  korean_dancheong: '#8F7860',
  african_ubuntu: '#4A7A46',
  persian_miniature: '#C65D4D',
  default: '#64748B',
};

const FALLBACK_COLORS = [
  '#C87F4A', '#5F8A50', '#B8923D', '#C65D4D', '#9B6B56',
  '#8F7860', '#4A7A46', '#C65D4D', '#64748B', '#6B8E7A',
];

function getTraditionColor(tradition: string, index: number): string {
  return TRADITION_COLORS[tradition] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

function formatTraditionLabel(tradition: string): string {
  return tradition
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Custom Tooltip
// ---------------------------------------------------------------------------

interface TooltipPayloadEntry {
  payload?: {
    cluster_id?: string;
    size?: number;
    tradition?: string;
    centroid?: Record<string, number>;
  };
}

function ClusterTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const data = payload[0].payload;
  if (!data) return null;

  return (
    <div className="rounded-lg px-4 py-3 shadow-lg bg-white/95 dark:bg-gray-900/95 border border-gray-200 dark:border-gray-700 text-sm max-w-xs">
      <div className="font-semibold text-gray-800 dark:text-gray-100 mb-1">
        {data.cluster_id}
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
        {formatTraditionLabel(data.tradition ?? '')} &middot; {data.size} member{data.size !== 1 ? 's' : ''}
      </div>
      {data.centroid && (
        <div className="space-y-0.5">
          {Object.entries(data.centroid).map(([key, val]) => (
            <div key={key} className="flex justify-between gap-4 text-xs">
              <span className="text-gray-500 dark:text-gray-400">
                {key.replace(/_/g, ' ')}
              </span>
              <span className="font-mono text-gray-700 dark:text-gray-300">
                {typeof val === 'number' ? val.toFixed(4) : String(val)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function ClusterScatterPlot({ clusters }: ClusterScatterPlotProps) {
  const [xDim, setXDim] = useState<DimensionKey>('avg_score');
  const [yDim, setYDim] = useState<DimensionKey>('cultural_depth');
  const { colors, rechartsTheme } = useChartTheme();

  // Group clusters by tradition and build per-tradition data arrays
  const { traditionGroups, traditions } = useMemo(() => {
    const groups: Record<string, Array<{
      x: number;
      y: number;
      z: number;
      cluster_id: string;
      size: number;
      tradition: string;
      centroid: Record<string, number>;
    }>> = {};

    for (const cluster of clusters) {
      const centroid = cluster.feature_centroid ?? {};
      const tradition = cluster.tradition || 'default';
      if (!groups[tradition]) groups[tradition] = [];
      groups[tradition].push({
        x: centroid[xDim] ?? 0,
        y: centroid[yDim] ?? 0,
        z: Math.sqrt(cluster.size) * 3,
        cluster_id: cluster.cluster_id,
        size: cluster.size,
        tradition,
        centroid,
      });
    }

    return {
      traditionGroups: groups,
      traditions: Object.keys(groups).sort(),
    };
  }, [clusters, xDim, yDim]);

  // Determine axis domains with a little padding
  const { xDomain, yDomain } = useMemo(() => {
    const allX: number[] = [];
    const allY: number[] = [];
    for (const pts of Object.values(traditionGroups)) {
      for (const p of pts) {
        allX.push(p.x);
        allY.push(p.y);
      }
    }
    if (allX.length === 0) return { xDomain: [0, 1] as const, yDomain: [0, 1] as const };

    const pad = 0.05;
    const xMin = Math.min(...allX);
    const xMax = Math.max(...allX);
    const yMin = Math.min(...allY);
    const yMax = Math.max(...allY);
    const xRange = xMax - xMin || 0.1;
    const yRange = yMax - yMin || 0.1;

    return {
      xDomain: [
        Math.max(0, xMin - xRange * pad),
        Math.min(1, xMax + xRange * pad),
      ] as const,
      yDomain: [
        Math.max(0, yMin - yRange * pad),
        Math.min(1, yMax + yRange * pad),
      ] as const,
    };
  }, [traditionGroups]);

  if (!clusters || clusters.length === 0) {
    return (
      <IOSCard variant="elevated" padding="lg">
        <IOSCardHeader
          title="Feature Space Clusters"
          subtitle="No cluster data available yet"
        />
        <IOSCardContent>
          <div className="text-center py-10 text-gray-400 dark:text-gray-500 text-sm">
            Run a digestion cycle to generate feature space clusters.
          </div>
        </IOSCardContent>
      </IOSCard>
    );
  }

  const selectClass =
    'rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 ' +
    'px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 ' +
    'focus:outline-none focus:ring-2 focus:ring-[#C87F4A]/40';

  return (
    <IOSCard variant="elevated" padding="lg">
      <IOSCardHeader
        title="Feature Space Clusters"
        subtitle={`${clusters.length} clusters across ${traditions.length} traditions`}
      />
      <IOSCardContent>
        {/* Axis selectors */}
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            X-axis
            <select
              value={xDim}
              onChange={(e) => setXDim(e.target.value as DimensionKey)}
              className={selectClass}
            >
              {DIMENSION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            Y-axis
            <select
              value={yDim}
              onChange={(e) => setYDim(e.target.value as DimensionKey)}
              className={selectClass}
            >
              {DIMENSION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 10 }}>
            <CartesianGrid
              stroke={colors.grid.line}
              strokeDasharray={rechartsTheme.cartesianGrid.strokeDasharray}
              strokeOpacity={rechartsTheme.cartesianGrid.strokeOpacity}
            />
            <XAxis
              type="number"
              dataKey="x"
              name={DIMENSION_OPTIONS.find((d) => d.value === xDim)?.label ?? xDim}
              domain={[xDomain[0], xDomain[1]]}
              tickFormatter={(v: number) => v.toFixed(2)}
              stroke={colors.grid.axis}
              tick={{ fill: colors.grid.text, fontSize: chartConfig.font.sizes.tick }}
              label={{
                value: DIMENSION_OPTIONS.find((d) => d.value === xDim)?.label ?? xDim,
                position: 'bottom',
                offset: 10,
                fill: colors.grid.text,
                fontSize: chartConfig.font.sizes.label,
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name={DIMENSION_OPTIONS.find((d) => d.value === yDim)?.label ?? yDim}
              domain={[yDomain[0], yDomain[1]]}
              tickFormatter={(v: number) => v.toFixed(2)}
              stroke={colors.grid.axis}
              tick={{ fill: colors.grid.text, fontSize: chartConfig.font.sizes.tick }}
              label={{
                value: DIMENSION_OPTIONS.find((d) => d.value === yDim)?.label ?? yDim,
                angle: -90,
                position: 'insideLeft',
                offset: 0,
                fill: colors.grid.text,
                fontSize: chartConfig.font.sizes.label,
              }}
            />
            <ZAxis type="number" dataKey="z" range={[40, 400]} />
            <Tooltip
              content={<ClusterTooltip />}
              cursor={{ strokeDasharray: '3 3', stroke: colors.grid.axis }}
            />
            <Legend
              wrapperStyle={rechartsTheme.legend.wrapperStyle}
              formatter={(value: string) => (
                <span className="text-gray-600 dark:text-gray-400 text-xs">
                  {formatTraditionLabel(value)}
                </span>
              )}
            />
            {traditions.map((tradition, idx) => (
              <Scatter
                key={tradition}
                name={tradition}
                data={traditionGroups[tradition]}
                fill={getTraditionColor(tradition, idx)}
                fillOpacity={0.75}
                stroke={getTraditionColor(tradition, idx)}
                strokeWidth={1}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </IOSCardContent>
    </IOSCard>
  );
}
