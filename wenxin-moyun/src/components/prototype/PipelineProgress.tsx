/**
 * Pipeline stage progress indicator with per-step timing and card-style event log.
 *
 * Features:
 * - Dynamic stage list via optional `templateNodes` prop
 * - Colour-coded agent event cards with expandable details
 * - Per-stage duration badges computed from event timestamps
 */

import { useState } from 'react';
import type { PipelineEvent } from '../../hooks/usePrototypePipeline';
import SubStageProgress from './SubStageProgress';
import type { SubStage } from './SubStageProgress';

const DEFAULT_STAGES = ['scout', 'draft', 'critic', 'queen', 'archivist'];

const STAGE_LABELS: Record<string, string> = {
  scout: 'Scout',
  draft: 'Draft',
  critic: 'Critic',
  queen: 'Queen',
  archivist: 'Archive',
};

// Agent colour theme for event cards
const AGENT_COLORS: Record<string, { border: string; bg: string; text: string; emoji: string }> = {
  scout:     { border: 'border-l-[#C87F4A]',   bg: 'bg-[#FAF7F2] dark:bg-[#C87F4A]/10',     text: 'text-[#C87F4A] dark:text-[#DDA574]',   emoji: '\u{1F50D}' },
  draft:     { border: 'border-l-[#C87F4A]',  bg: 'bg-[#C87F4A]/5 dark:bg-[#C87F4A]/10',  text: 'text-[#C87F4A] dark:text-[#DDA574]', emoji: '\u{1F3A8}' },
  critic:    { border: 'border-l-[#B8923D]',  bg: 'bg-[#B8923D]/5 dark:bg-[#B8923D]/10',  text: 'text-[#B8923D] dark:text-[#D4A94E]', emoji: '\u{1F4CA}' },
  queen:     { border: 'border-l-yellow-500',  bg: 'bg-yellow-50 dark:bg-yellow-900/20',  text: 'text-yellow-600 dark:text-yellow-400', emoji: '\u{1F451}' },
  archivist: { border: 'border-l-gray-400',    bg: 'bg-gray-50 dark:bg-gray-800/40',      text: 'text-gray-500 dark:text-gray-400',    emoji: '\u{1F4BE}' },
};

const DEFAULT_COLOR = AGENT_COLORS.archivist;

interface Props {
  currentStage: string;
  currentRound: number;
  status: string;
  events: PipelineEvent[];
  /** Dynamic stage list from template (overrides default 5-stage pipeline) */
  templateNodes?: string[];
  /** Sub-stage progress for nested display (e.g. Draft sub-steps) */
  subStages?: SubStage[];
}

/** Compute per-stage duration from events. */
function computeStageDurations(events: PipelineEvent[]): Record<string, number> {
  const starts: Record<string, number> = {};
  const durations: Record<string, number> = {};
  for (const e of events) {
    if (e.event_type === 'stage_started') {
      starts[e.stage] = e.timestamp_ms;
    } else if (e.event_type === 'stage_completed' && starts[e.stage]) {
      durations[e.stage] = e.timestamp_ms - starts[e.stage];
    }
  }
  return durations;
}

function formatMs(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

/** Extract a short detail string from event payload. */
function eventDetail(e: PipelineEvent): string | null {
  const p = e.payload;
  if (!p) return null;
  if (e.stage === 'scout' && e.event_type.includes('completed')) {
    const n = (p.sample_count as number) || (p.n_samples as number) || 0;
    const t = (p.term_count as number) || (p.n_terms as number) || 0;
    if (n || t) return `${n} samples, ${t} terms`;
  }
  if (e.stage === 'draft' && e.event_type.includes('completed')) {
    const n = (p.n_candidates as number) || (p.candidate_count as number) || 0;
    const prov = (p.provider as string) || '';
    if (n) return `${n} candidates${prov ? ` (${prov})` : ''}`;
  }
  if (e.stage === 'critic' && e.event_type.includes('completed')) {
    const best = (p.best_score as number) || (p.weighted_total as number) || 0;
    if (best) return `best: ${best.toFixed(3)}`;
  }
  if (e.stage === 'queen' && e.event_type.includes('completed')) {
    const action = (p.action as string) || (p.decision as string) || '';
    if (action) return action;
  }
  return null;
}

export default function PipelineProgress({ currentStage, currentRound, status, events, templateNodes, subStages }: Props) {
  const [showLog, setShowLog] = useState(false);

  const stages = templateNodes ?? DEFAULT_STAGES;

  const completedStages = new Set(
    events
      .filter(e => e.event_type === 'stage_completed')
      .map(e => e.stage)
  );
  const durations = computeStageDurations(events);

  return (
    <div>
      {/* Stage pipeline */}
      <div className="flex items-center gap-2 py-4 overflow-x-auto">
        {stages.map((stage, i) => {
          const isActive = stage === currentStage && status === 'running';
          const isCompleted = completedStages.has(stage);
          const isPending = !isActive && !isCompleted;
          const dur = durations[stage];

          return (
            <div key={stage} className="flex items-center">
              {i > 0 && (
                <div className={`w-8 h-0.5 mx-1 ${isCompleted ? 'bg-[#5F8A50]' : 'bg-gray-300 dark:bg-gray-600'}`} />
              )}
              <div className="flex flex-col items-center gap-1">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
                    transition-all duration-300
                    ${isActive ? 'bg-[#C87F4A] text-white ring-2 ring-[#C87F4A]/30 animate-pulse' : ''}
                    ${isCompleted ? 'bg-[#5F8A50] text-white' : ''}
                    ${isPending ? 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400' : ''}
                  `}
                >
                  {isCompleted ? '\u2713' : i + 1}
                </div>
                <span className={`text-xs ${isActive ? 'text-[#C87F4A] dark:text-[#DDA574] font-semibold' : 'text-gray-500 dark:text-gray-400'}`}>
                  {STAGE_LABELS[stage] || stage}
                  {stage !== 'scout' && currentRound > 1 && isActive ? ` R${currentRound}` : ''}
                </span>
                {dur !== undefined && (
                  <span className="text-[10px] text-gray-400 font-mono">{formatMs(dur)}</span>
                )}
              </div>
            </div>
          );
        })}

        {status === 'completed' && (
          <div className="ml-4 px-3 py-1 bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#5F8A50] dark:text-[#87A878] rounded-full text-sm font-medium">
            Done
          </div>
        )}
        {status === 'failed' && (
          <div className="ml-4 px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-sm font-medium">
            Failed
          </div>
        )}
      </div>

      {/* Sub-stage progress (shown when Draft is active/completed and subStages exist) */}
      {subStages && subStages.length > 0 && (
        currentStage === 'draft' || currentStage === 'draft_refine' || completedStages.has('draft')
      ) && (
        <div className="mt-2 ml-12">
          <SubStageProgress stages={subStages} />
        </div>
      )}

      {/* Card-style event log */}
      {events.length > 0 && (
        <div className="mt-2">
          <button
            onClick={() => setShowLog(!showLog)}
            className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            {showLog ? '\u25BC Hide' : '\u25B6 Show'} event log ({events.length} events)
          </button>

          {showLog && (
            <div className="mt-2 max-h-64 overflow-y-auto space-y-1.5">
              {events.map((e, i) => {
                const color = AGENT_COLORS[e.stage] || DEFAULT_COLOR;
                const detail = eventDetail(e);
                const isComplete = e.event_type.includes('completed');
                const isFailed = e.event_type.includes('failed');
                const isHuman = e.event_type.includes('human');

                return (
                  <div
                    key={i}
                    className={`flex items-start gap-2 px-3 py-1.5 rounded-lg border-l-4 ${color.border} ${color.bg}`}
                  >
                    <span className="text-sm shrink-0">{color.emoji}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-xs font-semibold ${color.text}`}>
                          {STAGE_LABELS[e.stage] || e.stage}
                        </span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                          isComplete ? 'bg-[#5F8A50]/10 dark:bg-[#5F8A50]/20 text-[#5F8A50] dark:text-[#87A878]' :
                          isFailed ? 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-400' :
                          isHuman ? 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400' :
                          'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                        }`}>
                          {e.event_type.replace('stage_', '').replace('_', ' ')}
                        </span>
                        {e.round_num > 0 && (
                          <span className="text-[10px] text-gray-400">R{e.round_num}</span>
                        )}
                        {durations[e.stage] !== undefined && isComplete && (
                          <span className="text-[10px] font-mono text-gray-400">
                            {formatMs(durations[e.stage])}
                          </span>
                        )}
                      </div>
                      {detail && (
                        <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 truncate">
                          {detail}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
