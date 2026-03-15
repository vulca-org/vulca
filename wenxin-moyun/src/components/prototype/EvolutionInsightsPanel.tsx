/**
 * EvolutionInsightsPanel — shows the system's self-evolution state.
 *
 * Fetches from GET /api/v1/prototype/evolution/stats and displays:
 * - Session count (how many runs the system has learned from)
 * - Active traditions (which cultures the system understands)
 * - Emerged concepts (patterns the system has discovered)
 * - Evolution count + last evolution timestamp
 */

import { useState, useEffect } from 'react';
import { IOSCard, IOSCardContent } from '../ios';
import { API_PREFIX } from '@/config/api';
import { formatTradition } from '@/utils/formatTradition';

interface EvolutionStats {
  total_sessions: number;
  traditions_active: string[];
  evolutions_count: number;
  emerged_concepts: { name: string; description: string }[];
  archetypes: string[];
  last_evolved_at: string | null;
}

export default function EvolutionInsightsPanel() {
  const [stats, setStats] = useState<EvolutionStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_PREFIX}/prototype/evolution/stats`, {
      headers: { Authorization: 'Bearer demo-key' },
    })
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setStats(data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats || (stats.total_sessions === 0 && stats.evolutions_count === 0)) {
    return null; // Nothing to show until data arrives
  }

  return (
    <IOSCard variant="elevated" padding="md" animate={false}>
      <IOSCardContent>
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          System Evolution
        </h3>

        {/* Key metrics row */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          <div className="text-center py-1.5 rounded-lg bg-stone-50 dark:bg-stone-800/50">
            <p className="text-lg font-bold font-mono text-[#C87F4A] dark:text-[#DDA574]">
              {stats.total_sessions}
            </p>
            <p className="text-[9px] text-gray-400 dark:text-gray-500">Sessions</p>
          </div>
          <div className="text-center py-1.5 rounded-lg bg-stone-50 dark:bg-stone-800/50">
            <p className="text-lg font-bold font-mono text-[#5F8A50] dark:text-[#87A878]">
              {stats.evolutions_count}
            </p>
            <p className="text-[9px] text-gray-400 dark:text-gray-500">Evolutions</p>
          </div>
          <div className="text-center py-1.5 rounded-lg bg-stone-50 dark:bg-stone-800/50">
            <p className="text-lg font-bold font-mono text-[#B8923D] dark:text-[#D4AE5A]">
              {stats.traditions_active.length}
            </p>
            <p className="text-[9px] text-gray-400 dark:text-gray-500">Cultures</p>
          </div>
        </div>

        {/* Active traditions */}
        {stats.traditions_active.length > 0 && (
          <div className="mb-2">
            <p className="text-[10px] text-gray-500 dark:text-gray-400 mb-1">Active Traditions</p>
            <div className="flex flex-wrap gap-1">
              {stats.traditions_active.map(t => (
                <span
                  key={t}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574]"
                >
                  {formatTradition(t)}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Emerged concepts */}
        {stats.emerged_concepts.length > 0 && (
          <div className="mb-2">
            <p className="text-[10px] text-gray-500 dark:text-gray-400 mb-1">Emerged Patterns</p>
            <div className="space-y-1">
              {stats.emerged_concepts.slice(0, 5).map((c, i) => (
                <div key={i} className="flex items-start gap-1.5">
                  <span className="text-[9px] text-[#5F8A50] mt-0.5">●</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">
                      {c.name}
                    </span>
                    {c.description && (
                      <p className="text-[9px] text-gray-400 dark:text-gray-500 line-clamp-2">
                        {c.description}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Archetypes */}
        {stats.archetypes.length > 0 && (
          <div className="mb-2">
            <p className="text-[10px] text-gray-500 dark:text-gray-400 mb-1">Archetypes</p>
            <div className="flex flex-wrap gap-1">
              {stats.archetypes.map(a => (
                <span
                  key={a}
                  className="text-[9px] px-1.5 py-0.5 rounded bg-[#334155]/10 dark:bg-[#334155]/20 text-[#334155] dark:text-[#94A3B8]"
                >
                  {a.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Last evolved timestamp */}
        {stats.last_evolved_at && (
          <p className="text-[9px] text-gray-400 dark:text-gray-500 text-right">
            Last evolved: {new Date(stats.last_evolved_at).toLocaleDateString()}
          </p>
        )}
      </IOSCardContent>
    </IOSCard>
  );
}
