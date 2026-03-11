/**
 * AdminDashboardPage - Self-Evolution System Dashboard
 *
 * Displays agent status, feedback statistics, skill ecosystem overview,
 * and evolution timeline. Fetches live data from /api/v1/feedback/stats
 * and /api/v1/skills, with graceful fallback to defaults.
 */

import { useState, useEffect } from 'react';
import { IOSCard, IOSCardHeader, IOSCardContent, IOSCardGrid } from '../components/ios';
import { API_PREFIX } from '../config/api';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface EvolutionData {
  total_sessions: number;
  traditions_active: string[];
  evolutions_count: number;
  emerged_concepts: { name: string; description: string }[];
  archetypes: string[];
  last_evolved_at: string | null;
}

interface DigestionStatusData {
  total_sessions: number;
  traditions: Record<string, unknown>;
  cultures: Record<string, unknown>;
  prompt_contexts: { archetypes?: unknown[] };
  feature_space: { clusters?: unknown[] };
  agent_insights: Record<string, string>;
  tradition_insights: Record<string, string>;
  evolutions: number;
  last_evolved_at: string | null;
}

interface FeedbackStatsData {
  total: number;
  thumbsUp: number;
  thumbsDown: number;
  ratio: number;
  recentComments: string[];
}

interface SkillEcosystemData {
  totalSkills: number;
  totalVotes: number;
  topSkill: { name: string; score: number };
}

// ---------------------------------------------------------------------------
// Types for agent data
// ---------------------------------------------------------------------------

interface AgentData {
  name: string;
  status: string;
  lastRun: string | null;
  description: string;
  principlesDistilled?: number;
  avgScore?: number | null;
  lastReport?: string;
}

interface TimelineEntry {
  date: string;
  event: string;
  status: string;
}

const DEFAULT_FEEDBACK: FeedbackStatsData = {
  total: 0,
  thumbsUp: 0,
  thumbsDown: 0,
  ratio: 0,
  recentComments: [],
};

const DEFAULT_SKILLS: SkillEcosystemData = {
  totalSkills: 0,
  totalVotes: 0,
  topSkill: { name: 'N/A', score: 0 },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusColors: Record<string, string> = {
  healthy: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[status] || statusColors.healthy}`}>
      {status.toUpperCase()}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function AdminDashboardPage() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStatsData>(DEFAULT_FEEDBACK);
  const [skillEcosystem, setSkillEcosystem] = useState<SkillEcosystemData>(DEFAULT_SKILLS);
  const [evolution, setEvolution] = useState<EvolutionData | null>(null);
  const [digestionStatus, setDigestionStatus] = useState<DigestionStatusData | null>(null);

  useEffect(() => {
    let cancelled = false;

    // Fetch evolution status (agents + timeline)
    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/evolution/status`);
        if (!res.ok) throw new Error('API unavailable');
        const data = await res.json();
        if (cancelled) return;
        if (Array.isArray(data.agents)) setAgents(data.agents);
        if (Array.isArray(data.timeline) && data.timeline.length > 0) setTimeline(data.timeline);
      } catch {
        // keep empty defaults
      }
    })();

    // Fetch feedback stats
    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/feedback/stats`);
        if (!res.ok) throw new Error('API unavailable');
        const data = await res.json();
        if (cancelled) return;
        const up = data.thumbs_up ?? 0;
        const down = data.thumbs_down ?? 0;
        const total = data.total_feedback ?? (up + down);
        setFeedbackStats({
          total,
          thumbsUp: up,
          thumbsDown: down,
          ratio: total > 0 ? up / total : 0,
          recentComments: data.recent_comments ?? [],
        });
      } catch {
        // keep defaults
      }
    })();

    // Fetch skills for ecosystem stats
    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/skills`);
        if (!res.ok) throw new Error('API unavailable');
        const skills = await res.json();
        if (cancelled || !Array.isArray(skills) || skills.length === 0) return;
        const totalVotes = skills.reduce(
          (sum: number, s: { upvotes?: number; downvotes?: number }) =>
            sum + (s.upvotes ?? 0) + (s.downvotes ?? 0),
          0
        );
        const topSkill = skills.reduce(
          (best: { upvotes: number; name: string }, s: { upvotes?: number; name?: string }) =>
            (s.upvotes ?? 0) > best.upvotes ? { upvotes: s.upvotes ?? 0, name: s.name ?? '' } : best,
          { upvotes: 0, name: '' }
        );
        setSkillEcosystem({
          totalSkills: skills.length,
          totalVotes,
          topSkill: { name: topSkill.name || 'N/A', score: topSkill.upvotes },
        });
      } catch {
        // keep defaults
      }
    })();

    // Fetch digestion/evolution stats
    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/prototype/evolution`);
        if (!res.ok) throw new Error('API unavailable');
        const data = await res.json();
        if (!cancelled) setEvolution(data);
      } catch {
        // keep null
      }
    })();

    // Fetch detailed digestion status
    (async () => {
      try {
        const res = await fetch(`${API_PREFIX}/digestion/status`);
        if (!res.ok) throw new Error('API unavailable');
        const data = await res.json();
        if (!cancelled) setDigestionStatus(data);
      } catch {
        // keep null
      }
    })();

    return () => { cancelled = true; };
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Self-Evolution Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Monitor the autonomous evolution agents, feedback health, and skill ecosystem.
        </p>
      </div>

      {/* Digestion System Overview */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
          Digestion System
        </h2>
        <IOSCardGrid columns={4} gap="md">
          <IOSCard variant="elevated" padding="lg">
            <IOSCardContent>
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Sessions Learned</div>
              <div className="text-3xl font-bold text-[#C87F4A]">{evolution?.total_sessions ?? 0}</div>
            </IOSCardContent>
          </IOSCard>
          <IOSCard variant="elevated" padding="lg">
            <IOSCardContent>
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Traditions Active</div>
              <div className="text-3xl font-bold text-[#5F8A50]">{evolution?.traditions_active?.length ?? 0}</div>
              {evolution?.traditions_active && evolution.traditions_active.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {evolution.traditions_active.slice(0, 4).map(t => (
                    <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-[#5F8A50]/10 text-[#5F8A50] dark:text-[#87A878]">
                      {t.replace(/_/g, ' ')}
                    </span>
                  ))}
                  {evolution.traditions_active.length > 4 && (
                    <span className="text-[10px] text-gray-400">+{evolution.traditions_active.length - 4}</span>
                  )}
                </div>
              )}
            </IOSCardContent>
          </IOSCard>
          <IOSCard variant="elevated" padding="lg">
            <IOSCardContent>
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Evolution Cycles</div>
              <div className="text-3xl font-bold text-[#B8923D]">{evolution?.evolutions_count ?? 0}</div>
              {evolution?.last_evolved_at && (
                <div className="text-[10px] text-gray-400 mt-1">Last: {evolution.last_evolved_at}</div>
              )}
            </IOSCardContent>
          </IOSCard>
          <IOSCard variant="elevated" padding="lg">
            <IOSCardContent>
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Emerged Concepts</div>
              <div className="text-3xl font-bold text-[#C65D4D]">{evolution?.emerged_concepts?.length ?? 0}</div>
              {evolution?.emerged_concepts && evolution.emerged_concepts.length > 0 && (
                <div className="mt-2 space-y-0.5">
                  {evolution.emerged_concepts.slice(0, 3).map(c => (
                    <div key={c.name} className="text-[10px] text-gray-500 dark:text-gray-400 truncate" title={c.description}>
                      {c.name}
                    </div>
                  ))}
                </div>
              )}
            </IOSCardContent>
          </IOSCard>
        </IOSCardGrid>
      </section>

      {/* Digestion System Details */}
      {digestionStatus && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Evolved Context Coverage
          </h2>
          <IOSCardGrid columns={2} gap="md">
            {/* Context Coverage Stats */}
            <IOSCard variant="elevated" padding="lg">
              <IOSCardHeader
                title="Context Coverage"
                subtitle="Evolved context data dimensions"
              />
              <IOSCardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Cultures emerged</span>
                    <span className="text-lg font-bold text-[#C87F4A]">
                      {Object.keys(digestionStatus.cultures ?? {}).length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Prompt archetypes</span>
                    <span className="text-lg font-bold text-[#B8923D]">
                      {Array.isArray(digestionStatus.prompt_contexts?.archetypes)
                        ? digestionStatus.prompt_contexts.archetypes.length
                        : 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Feature clusters</span>
                    <span className="text-lg font-bold text-[#5F8A50]">
                      {Array.isArray(digestionStatus.feature_space?.clusters)
                        ? digestionStatus.feature_space.clusters.length
                        : 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Tradition weights</span>
                    <span className="text-lg font-bold text-[#334155] dark:text-gray-300">
                      {Object.keys(digestionStatus.traditions ?? {}).length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Evolution cycles</span>
                    <span className="text-lg font-bold text-[#C65D4D]">
                      {digestionStatus.evolutions ?? 0}
                    </span>
                  </div>
                  {digestionStatus.last_evolved_at && (
                    <div className="pt-2 border-t border-gray-100 dark:border-gray-800">
                      <span className="text-xs text-gray-400 dark:text-gray-500">
                        Last evolution: {digestionStatus.last_evolved_at}
                      </span>
                    </div>
                  )}
                </div>
              </IOSCardContent>
            </IOSCard>

            {/* Agent Insights Summary */}
            <IOSCard variant="elevated" padding="lg">
              <IOSCardHeader
                title="Agent Insights"
                subtitle="LLM-generated guidance for pipeline agents"
              />
              <IOSCardContent>
                {digestionStatus.agent_insights && Object.keys(digestionStatus.agent_insights).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(digestionStatus.agent_insights).map(([role, insight]) => (
                      <div key={role} className="p-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold text-[#C87F4A] uppercase">{role}</span>
                        </div>
                        <p className="text-[11px] text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-3">
                          {insight}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
                    No agent insights yet. Run a digestion cycle with LLM to generate.
                  </div>
                )}
              </IOSCardContent>
            </IOSCard>
          </IOSCardGrid>
        </section>
      )}

      {/* Agent Status Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
          Agent Status
        </h2>
        {agents.length > 0 ? (
          <IOSCardGrid columns={3} gap="md">
            {agents.map((agent) => (
              <IOSCard key={agent.name} variant="elevated" padding="lg">
                <IOSCardHeader
                  title={agent.name}
                  subtitle={agent.description}
                  action={<StatusBadge status={agent.status} />}
                />
                <IOSCardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Last run</span>
                      <span className="font-mono text-gray-700 dark:text-gray-300">
                        {agent.lastRun ?? 'Never'}
                      </span>
                    </div>
                    {agent.principlesDistilled != null && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Principles</span>
                        <span className="font-semibold text-gray-700 dark:text-gray-300">{agent.principlesDistilled}</span>
                      </div>
                    )}
                    {agent.avgScore != null && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Avg Score</span>
                        <span className="font-semibold text-gray-700 dark:text-gray-300">{agent.avgScore}</span>
                      </div>
                    )}
                    {agent.lastReport && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Last report</span>
                        <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{agent.lastReport}</span>
                      </div>
                    )}
                  </div>
                </IOSCardContent>
              </IOSCard>
            ))}
          </IOSCardGrid>
        ) : (
          <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
            No agent data available. Run an evolution cycle to populate.
          </div>
        )}
      </section>

      {/* Feedback Stats + Skill Ecosystem */}
      <section className="mb-8">
        <IOSCardGrid columns={2} gap="md">
          {/* Feedback Stats */}
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Feedback Stats"
              subtitle="Aggregated user feedback signals"
            />
            <IOSCardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Total feedback</span>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">{feedbackStats.total}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Positive / Negative</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {feedbackStats.thumbsUp} / {feedbackStats.thumbsDown}
                  </span>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Approval ratio</span>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {(feedbackStats.ratio * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${feedbackStats.ratio * 100}%` }}
                    />
                  </div>
                </div>
                {/* Chart placeholder */}
                <div className="mt-4 h-24 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex items-center justify-center border border-dashed border-gray-300 dark:border-gray-600">
                  <span className="text-sm text-gray-400 dark:text-gray-500">Feedback trend chart (coming soon)</span>
                </div>
              </div>
            </IOSCardContent>
          </IOSCard>

          {/* Skill Ecosystem */}
          <IOSCard variant="elevated" padding="lg">
            <IOSCardHeader
              title="Skill Ecosystem"
              subtitle="Active skills and community engagement"
            />
            <IOSCardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Active skills</span>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">{skillEcosystem.totalSkills}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Total votes</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{skillEcosystem.totalVotes.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-900/20 rounded-lg">
                  <div className="text-xs text-slate-600 dark:text-slate-400 font-medium mb-1">Top Skill</div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {skillEcosystem.topSkill.name}
                    </span>
                    <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                      {skillEcosystem.topSkill.score}
                    </span>
                  </div>
                </div>
              </div>
            </IOSCardContent>
          </IOSCard>
        </IOSCardGrid>
      </section>

      {/* Evolution Timeline */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
          Evolution Timeline
        </h2>
        <IOSCard variant="elevated" padding="lg">
          <IOSCardContent>
            {timeline.length > 0 ? (
              <div className="space-y-0">
                {timeline.map((entry, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-4 py-3 ${
                      idx < timeline.length - 1 ? 'border-b border-gray-100 dark:border-gray-800' : ''
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <div
                        className={`w-2.5 h-2.5 rounded-full ${
                          entry.status === 'healthy'
                            ? 'bg-green-500'
                            : entry.status === 'warning'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 dark:text-gray-200">{entry.event}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{entry.date}</p>
                    </div>
                    <StatusBadge status={entry.status} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
                No evolution events yet. Timeline will populate after the first evolution cycle.
              </div>
            )}
          </IOSCardContent>
        </IOSCard>
      </section>
    </div>
  );
}
