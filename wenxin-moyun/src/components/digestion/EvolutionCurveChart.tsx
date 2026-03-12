/**
 * EvolutionCurveChart - Cumulative evolution timeline chart.
 *
 * Displays dual lines:
 *   - "Evolution Cycles" (warm-copper #C87F4A, solid)
 *   - "Emerged Cultures" (sage-green #5F8A50, dashed)
 *
 * Fetches data from GET /api/v1/prototype/evolution/timeline,
 * uses recharts LineChart with Art Professional palette and
 * dark-mode support via useChartTheme.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { IOSCard, IOSCardHeader, IOSCardContent } from '../ios';
import { useChartTheme } from '../../hooks/useChartTheme';
import { API_PREFIX } from '../../config/api';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TimelinePoint {
  date: string;
  cultures: number;
  evolutions: number;
}

interface TimelineResponse {
  points: TimelinePoint[];
  total_evolutions: number;
  total_cultures: number;
}

// ---------------------------------------------------------------------------
// Art Professional palette constants
// ---------------------------------------------------------------------------

const COLOR_COPPER = '#C87F4A';
const COLOR_COPPER_DARK = '#DDA574';
const COLOR_SAGE = '#5F8A50';
const COLOR_SAGE_DARK = '#87A878';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function EvolutionCurveChart() {
  const [data, setData] = useState<TimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { isDark, rechartsTheme } = useChartTheme();

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/prototype/evolution/timeline`);
        if (!res.ok) throw new Error('API unavailable');
        const json: TimelineResponse = await res.json();
        if (!cancelled) setData(json);
      } catch {
        // keep null — will show empty state
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const copperColor = isDark ? COLOR_COPPER_DARK : COLOR_COPPER;
  const sageColor = isDark ? COLOR_SAGE_DARK : COLOR_SAGE;

  const hasData = data && data.points.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <IOSCard variant="elevated" padding="lg">
        <IOSCardHeader
          title="Evolution Curve"
          subtitle={
            hasData
              ? `${data.total_evolutions} cycles, ${data.total_cultures} emerged cultures`
              : 'Cumulative evolution and culture emergence over time'
          }
        />
        <IOSCardContent>
          {loading ? (
            <div className="flex items-center justify-center h-56 text-gray-400 dark:text-gray-500 text-sm">
              Loading evolution data...
            </div>
          ) : hasData ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart
                data={data.points}
                margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
              >
                <CartesianGrid
                  stroke={rechartsTheme.cartesianGrid.stroke}
                  strokeDasharray={rechartsTheme.cartesianGrid.strokeDasharray}
                  strokeOpacity={rechartsTheme.cartesianGrid.strokeOpacity}
                />
                <XAxis
                  dataKey="date"
                  stroke={rechartsTheme.axis.stroke}
                  tick={{ ...rechartsTheme.axis.tick, fontSize: 11 }}
                  minTickGap={60}
                  tickFormatter={(v: string) => {
                    const parts = v.split(' ');
                    const d = parts[0] ?? v;
                    const t = parts[1] ?? '';
                    // Show "M/D HH:mm" — concise and non-repeating
                    const shortDate = d.replace(/^\d{4}-/, '');
                    return t ? `${shortDate} ${t}` : shortDate;
                  }}
                />
                <YAxis
                  stroke={rechartsTheme.axis.stroke}
                  tick={rechartsTheme.axis.tick}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={rechartsTheme.tooltip.contentStyle}
                  labelStyle={rechartsTheme.tooltip.labelStyle}
                  itemStyle={rechartsTheme.tooltip.itemStyle}
                />
                <Legend wrapperStyle={rechartsTheme.legend.wrapperStyle} />
                <Line
                  type="monotone"
                  dataKey="evolutions"
                  name="Evolution Cycles"
                  stroke={copperColor}
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: copperColor }}
                  activeDot={{ r: 6 }}
                />
                <Line
                  type="monotone"
                  dataKey="cultures"
                  name="Emerged Cultures"
                  stroke={sageColor}
                  strokeWidth={2.5}
                  strokeDasharray="6 3"
                  dot={{ r: 4, fill: sageColor }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-56 text-gray-400 dark:text-gray-500 text-sm">
              No evolution data yet. Timeline will populate after the first evolution cycle.
            </div>
          )}
        </IOSCardContent>
      </IOSCard>
    </motion.div>
  );
}
