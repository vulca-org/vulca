/**
 * AdminDashboardPage - Self-Evolution System Dashboard
 *
 * Displays agent status, feedback statistics, skill ecosystem overview,
 * and evolution timeline. Uses mock data since the API may not exist yet.
 */

import { IOSCard, IOSCardHeader, IOSCardContent, IOSCardGrid } from '../components/ios';

// ---------------------------------------------------------------------------
// Mock data (replace with real API calls when backend endpoints are ready)
// ---------------------------------------------------------------------------

const AGENTS = [
  {
    name: 'EvolutionAgent',
    status: 'healthy' as const,
    lastRun: '2026-03-07 14:30 UTC',
    description: 'Drives weight adjustments and principle extraction',
    principlesDistilled: 8,
  },
  {
    name: 'QualityAgent',
    status: 'healthy' as const,
    lastRun: '2026-03-07 14:30 UTC',
    description: 'Monitors evaluation quality and detects drift',
    avgScore: 3.72,
  },
  {
    name: 'AdminAgent',
    status: 'healthy' as const,
    lastRun: '2026-03-07 14:30 UTC',
    description: 'Orchestrates sub-agents and generates weekly reports',
    lastReport: 'weekly_2026-03-07.md',
  },
];

const FEEDBACK_STATS = {
  total: 247,
  thumbsUp: 189,
  thumbsDown: 58,
  ratio: 0.765,
};

const SKILL_ECOSYSTEM = {
  totalSkills: 14,
  totalVotes: 1823,
  topSkill: { name: 'cultural_context_analysis', score: 4.6 },
};

const EVOLUTION_TIMELINE = [
  { date: '2026-03-07', event: 'Evolved 8 principles, adjusted 5 tradition weights', status: 'healthy' as const },
  { date: '2026-03-06', event: 'Quality drift detected in East Asian tradition scoring', status: 'warning' as const },
  { date: '2026-03-05', event: 'Baseline reset after pipeline update', status: 'healthy' as const },
  { date: '2026-03-04', event: 'Evolved 6 principles, no drift detected', status: 'healthy' as const },
  { date: '2026-03-03', event: '3 anomalies flagged in L5 evaluations', status: 'warning' as const },
];

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

      {/* Agent Status Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
          Agent Status
        </h2>
        <IOSCardGrid columns={3} gap="md">
          {AGENTS.map((agent) => (
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
                    <span className="font-mono text-gray-700 dark:text-gray-300">{agent.lastRun}</span>
                  </div>
                  {'principlesDistilled' in agent && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Principles</span>
                      <span className="font-semibold text-gray-700 dark:text-gray-300">{agent.principlesDistilled}</span>
                    </div>
                  )}
                  {'avgScore' in agent && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Avg Score</span>
                      <span className="font-semibold text-gray-700 dark:text-gray-300">{agent.avgScore}</span>
                    </div>
                  )}
                  {'lastReport' in agent && (
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
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">{FEEDBACK_STATS.total}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Positive / Negative</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {FEEDBACK_STATS.thumbsUp} / {FEEDBACK_STATS.thumbsDown}
                  </span>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Approval ratio</span>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {(FEEDBACK_STATS.ratio * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${FEEDBACK_STATS.ratio * 100}%` }}
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
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">{SKILL_ECOSYSTEM.totalSkills}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Total votes</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{SKILL_ECOSYSTEM.totalVotes.toLocaleString()}</span>
                </div>
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">Top Skill</div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {SKILL_ECOSYSTEM.topSkill.name}
                    </span>
                    <span className="text-sm font-bold text-blue-700 dark:text-blue-300">
                      {SKILL_ECOSYSTEM.topSkill.score}
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
            <div className="space-y-0">
              {EVOLUTION_TIMELINE.map((entry, idx) => (
                <div
                  key={idx}
                  className={`flex items-start gap-4 py-3 ${
                    idx < EVOLUTION_TIMELINE.length - 1 ? 'border-b border-gray-100 dark:border-gray-800' : ''
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
          </IOSCardContent>
        </IOSCard>
      </section>
    </div>
  );
}
