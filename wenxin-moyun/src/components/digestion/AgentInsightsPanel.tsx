/**
 * AgentInsightsPanel — Enhanced Agent Insights with expandable cards,
 * tradition insights, and trajectory stats. Replaces the flat summary
 * in AdminDashboardPage with a rich, interactive view.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IOSCard, IOSCardContent, IOSCardHeader } from '../ios';
import { formatDimensionTitleCase } from '../../utils/formatDimension';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AgentInsightsPanelProps {
  agentInsights: Record<string, string>;
  traditionInsights: Record<string, string>;
  trajectoryInsights?: {
    total_trajectories: number;
    common_weak_dimensions: string[];
    avg_rounds_to_accept: number;
    repair_success_rate: number;
    tradition_avg_rounds?: Record<string, number>;
  };
}

interface ParsedInsight {
  working: string[];
  improvement: string[];
  guidance: string[];
  raw: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const AGENT_META: Record<string, { emoji: string; color: string; label: string }> = {
  scout: { emoji: '\uD83D\uDD0D', color: '#B8923D', label: 'Scout' },
  draft: { emoji: '\uD83C\uDFA8', color: '#C87F4A', label: 'Draft' },
  critic: { emoji: '\uD83D\uDCDD', color: '#5F8A50', label: 'Critic' },
  queen: { emoji: '\uD83D\uDC51', color: '#C65D4D', label: 'Queen' },
};

const AGENT_ORDER = ['scout', 'draft', 'critic', 'queen'] as const;

const TRADITION_EMOJIS: Record<string, string> = {
  african_traditional: '\uD83C\uDFA8',
  chinese_gongbi: '\uD83C\uDFEF',
  chinese_xieyi: '\u2712\uFE0F',
  default: '\uD83C\uDF10',
  islamic_geometric: '\uD83D\uDD37',
  japanese_traditional: '\uD83C\uDF38',
  south_asian: '\uD83E\uDE94',
  watercolor: '\uD83D\uDCA7',
  western_academic: '\uD83C\uDFDB\uFE0F',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseInsight(text: string): ParsedInsight {
  const result: ParsedInsight = { working: [], improvement: [], guidance: [], raw: text };

  // Try to split by known section headings
  const workingMatch = text.match(/(?:what'?s?\s*working|strengths?|positives?)[:\s]*([^]*?)(?=(?:needs?\s*improvement|weaknesses?|areas?\s*for|guidance|to\s*improve|$))/i);
  const improvementMatch = text.match(/(?:needs?\s*improvement|weaknesses?|areas?\s*for\s*improvement|to\s*improve)[:\s]*([^]*?)(?=(?:guidance|recommendation|suggestion|$))/i);
  const guidanceMatch = text.match(/(?:guidance|recommendation|suggestion)[:\s]*([^]*?)$/i);

  if (workingMatch) {
    result.working = extractBullets(workingMatch[1]);
  }
  if (improvementMatch) {
    result.improvement = extractBullets(improvementMatch[1]);
  }
  if (guidanceMatch) {
    result.guidance = extractBullets(guidanceMatch[1]);
  }

  // If no structured sections found, split into sentences as guidance
  if (result.working.length === 0 && result.improvement.length === 0 && result.guidance.length === 0) {
    const sentences = text
      .split(/\.\s+/)
      .map(s => s.trim().replace(/\.$/, ''))
      .filter(s => s.length > 10);
    result.guidance = sentences.length > 0 ? sentences : [text];
  }

  return result;
}

function extractBullets(text: string): string[] {
  return text
    .split(/[.;]\s+|[\n\r]+/)
    .map(s => s.replace(/^[-*\u2022]\s*/, '').trim())
    .filter(s => s.length > 5);
}

function truncateLines(text: string, maxLines: number): string {
  const sentences = text.split(/\.\s+/);
  return sentences.slice(0, maxLines).join('. ').trim() + (sentences.length > maxLines ? '...' : '');
}

function formatTradition(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function InsightSection({ label, items, color }: { label: string; items: string[]; color: string }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-2">
      <div className="text-[11px] font-semibold uppercase tracking-wide mb-1" style={{ color }}>
        {label}
      </div>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-[12px] text-gray-600 dark:text-gray-400 leading-relaxed pl-3 relative">
            <span
              className="absolute left-0 top-[6px] w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: color }}
            />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function AgentCard({ role, insight }: { role: string; insight: string }) {
  const [expanded, setExpanded] = useState(false);
  const meta = AGENT_META[role] ?? { emoji: '\uD83E\uDD16', color: '#334155', label: role };
  const parsed = parseInsight(insight);

  return (
    <IOSCard
      variant="elevated"
      padding="none"
      className="overflow-hidden cursor-pointer"
      interactive
      onClick={() => setExpanded(prev => !prev)}
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
        style={{ backgroundColor: meta.color }}
      />
      <div className="pl-4 pr-4 py-3">
        {/* Collapsed header */}
        <div className="flex items-center gap-2">
          <span className="text-lg">{meta.emoji}</span>
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            {meta.label}
          </span>
          <span className="ml-auto text-gray-400 dark:text-gray-500 text-xs">
            {expanded ? '\u25B2' : '\u25BC'}
          </span>
        </div>

        {/* Preview (always visible) */}
        {!expanded && (
          <p className="mt-1 text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed line-clamp-2">
            {truncateLines(insight, 2)}
          </p>
        )}

        {/* Expanded detail */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <InsightSection label="What's Working" items={parsed.working} color="#5F8A50" />
              <InsightSection label="Needs Improvement" items={parsed.improvement} color="#C65D4D" />
              <InsightSection label="Guidance" items={parsed.guidance} color="#B8923D" />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </IOSCard>
  );
}

function TraditionRow({ tradition, insight }: { tradition: string; insight: string }) {
  const [expanded, setExpanded] = useState(false);
  const emoji = TRADITION_EMOJIS[tradition] ?? '\uD83C\uDFA8';

  return (
    <div
      className="border-b border-gray-100 dark:border-gray-800 last:border-b-0 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors"
      onClick={() => setExpanded(prev => !prev)}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        <span className="text-sm">{emoji}</span>
        <span className="text-xs font-medium text-gray-800 dark:text-gray-200 flex-1">
          {formatTradition(tradition)}
        </span>
        <span className="text-gray-400 dark:text-gray-500 text-[10px]">
          {expanded ? '\u25B2' : '\u25BC'}
        </span>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <p className="px-3 pb-3 text-[11px] text-gray-600 dark:text-gray-400 leading-relaxed">
              {insight}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function AgentInsightsPanel({
  agentInsights,
  traditionInsights,
  trajectoryInsights,
}: AgentInsightsPanelProps) {
  const hasAgents = Object.keys(agentInsights).length > 0;
  const hasTraditions = Object.keys(traditionInsights).length > 0;

  if (!hasAgents && !hasTraditions && !trajectoryInsights) {
    return (
      <IOSCard variant="elevated" padding="lg">
        <IOSCardHeader
          title="Agent Insights"
          subtitle="LLM-generated guidance for pipeline agents"
        />
        <IOSCardContent>
          <div className="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
            No agent insights yet. Run a digestion cycle with LLM to generate.
          </div>
        </IOSCardContent>
      </IOSCard>
    );
  }

  return (
    <div className="space-y-4">
      {/* Agent Insight Cards */}
      {hasAgents && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Pipeline Agents
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {AGENT_ORDER.filter(role => agentInsights[role]).map(role => (
              <AgentCard key={role} role={role} insight={agentInsights[role]} />
            ))}
            {/* Render any extra agents not in AGENT_ORDER */}
            {Object.keys(agentInsights)
              .filter(role => !(AGENT_ORDER as readonly string[]).includes(role))
              .map(role => (
                <AgentCard key={role} role={role} insight={agentInsights[role]} />
              ))}
          </div>
        </div>
      )}

      {/* Tradition Insights */}
      {hasTraditions && (
        <IOSCard variant="elevated" padding="none">
          <div className="px-4 pt-4 pb-2">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Tradition Insights
            </h3>
            <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5">
              {Object.keys(traditionInsights).length} traditions analyzed
            </p>
          </div>
          <div>
            {Object.entries(traditionInsights)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([tradition, insight]) => (
                <TraditionRow
                  key={tradition}
                  tradition={tradition}
                  insight={insight}
                />
              ))}
          </div>
        </IOSCard>
      )}

      {/* Trajectory Stats */}
      {trajectoryInsights && (
        <IOSCard variant="elevated" padding="lg">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Trajectory Stats
          </h3>
          <div className="grid grid-cols-3 gap-4 mb-3">
            <div>
              <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-0.5">
                Total Trajectories
              </div>
              <div className="text-xl font-bold text-[#B8923D]">
                {trajectoryInsights.total_trajectories}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-0.5">
                Avg Rounds
              </div>
              <div className="text-xl font-bold text-[#C87F4A]">
                {trajectoryInsights.avg_rounds_to_accept.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-0.5">
                Repair Rate
              </div>
              <div className="text-xl font-bold text-[#5F8A50]">
                {(trajectoryInsights.repair_success_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Weak dimensions as capsule tags */}
          {trajectoryInsights.common_weak_dimensions.length > 0 && (
            <div>
              <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-1.5">
                Common Weak Dimensions
              </div>
              <div className="flex flex-wrap gap-1.5">
                {trajectoryInsights.common_weak_dimensions.map(dim => (
                  <span
                    key={dim}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-[#C65D4D]/10 text-[#C65D4D] dark:text-[#E08A7D] font-medium"
                  >
                    {formatDimensionTitleCase(dim)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Per-tradition avg rounds */}
          {trajectoryInsights.tradition_avg_rounds &&
            Object.keys(trajectoryInsights.tradition_avg_rounds).length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-1.5">
                  Avg Rounds by Tradition
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(trajectoryInsights.tradition_avg_rounds)
                    .sort(([, a], [, b]) => a - b)
                    .map(([tradition, rounds]) => (
                      <span
                        key={tradition}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-[#B8923D]/10 text-[#B8923D] dark:text-[#D4B06A] font-medium"
                      >
                        {formatTradition(tradition)}: {rounds.toFixed(2)}
                      </span>
                    ))}
                </div>
              </div>
            )}
        </IOSCard>
      )}
    </div>
  );
}
