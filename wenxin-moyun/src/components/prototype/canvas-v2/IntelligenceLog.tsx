/**
 * Intelligence Log — Terminal-style SSE event stream viewer.
 * Formats pipeline events into colored log lines with cultural context.
 */

import { useRef, useEffect } from 'react';
import type { PipelineEvent } from '@/hooks/usePrototypePipeline';

interface Props {
  events: PipelineEvent[];
  currentStage: string;
  status: string;
}

interface LogLine {
  prefix: string;
  prefixColor: string;
  text: string;
}

const L_LABELS: Record<string, string> = {
  L1: 'Visual Perception',
  L2: 'Technical Analysis',
  L3: 'Cultural Context',
  L4: 'Critical Interpretation',
  L5: 'Philosophical Aesthetic',
};

function formatEvent(e: PipelineEvent): LogLine[] {
  const type = e.event_type;
  const stage = (e.stage || '').toUpperCase().replace('GENERATE', 'DRAFT').replace('EVALUATE', 'CRITIC').replace('DECIDE', 'QUEEN');

  if (type === 'pipeline_started') {
    return [{ prefix: '[SYSTEM]', prefixColor: 'text-primary-400', text: 'Initializing cultural synthesis module...' }];
  }
  if (type === 'stage_started') {
    return [{ prefix: `[AGENT/${stage}]`, prefixColor: 'text-primary-400', text: `${stage} agent activated — round ${e.round_num}` }];
  }
  if (type === 'stage_completed') {
    const payload = e.payload || {};
    const latency = payload.latency_ms ? ` (${Math.round(Number(payload.latency_ms))}ms)` : '';
    const lines: LogLine[] = [];

    // Show cultural guidance injected during generation
    const guidance = payload.cultural_guidance as { terminology?: string[]; taboos?: string[]; tradition?: string; evolved_weights?: Record<string, number> } | undefined;
    if (guidance && (guidance.terminology?.length || guidance.taboos?.length)) {
      const terms = guidance.terminology?.slice(0, 5);
      lines.push({ prefix: `[${stage}]`, prefixColor: 'text-cultural-sage-500', text: `Cultural injection active${latency}` });
      if (terms?.length) {
        lines.push({ prefix: '', prefixColor: '', text: `  ↳ Terminology: ${terms.join(', ')}${(guidance.terminology?.length || 0) > 5 ? ` +${(guidance.terminology?.length || 0) - 5} more` : ''}` });
      }
      if (guidance.taboos?.length) {
        lines.push({ prefix: '', prefixColor: '', text: `  ↳ Cultural constraints: ${guidance.taboos.length} rules enforced` });
      }
      if (guidance.evolved_weights) {
        const top = Object.entries(guidance.evolved_weights)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([k, v]) => `${k} ${Math.round(v * 100)}%`);
        lines.push({ prefix: '', prefixColor: '', text: `  ↳ Evolved weights: ${top.join(', ')}` });
      }
      return lines;
    }

    // Show evaluation rationale summary with actual content
    const rationales = payload.rationales as Record<string, string> | undefined;
    if (rationales && Object.keys(rationales).length > 0) {
      const wt = payload.weighted_total;
      const score = wt ? ` → ${Number(wt).toFixed(2)}` : '';
      const scores = payload.scores as Record<string, number> | undefined;
      lines.push({ prefix: `[${stage}]`, prefixColor: 'text-cultural-sage-500', text: `L1-L5 evaluation complete${latency}${score}` });

      // Show each dimension's score + rationale snippet
      for (const dim of ['L1', 'L2', 'L3', 'L4', 'L5']) {
        const rat = rationales[`${dim}_rationale`];
        const dimScore = scores?.[dim];
        if (rat) {
          const snippet = rat.length > 80 ? rat.slice(0, 77) + '...' : rat;
          const scoreStr = dimScore != null ? ` [${Number(dimScore).toFixed(2)}]` : '';
          const label = L_LABELS[dim] || dim;
          lines.push({ prefix: '', prefixColor: '', text: `  ${dim}${scoreStr} ${label}: ${snippet}` });
        }
      }
      return lines;
    }

    return [{ prefix: `[${stage}]`, prefixColor: 'text-cultural-sage-500', text: `Stage complete${latency}` }];
  }
  if (type === 'decision_made') {
    const action = (e.payload?.action || e.payload?.decision || 'unknown') as string;
    const wt = e.payload?.weighted_total;
    const extra = wt ? ` (score: ${Number(wt).toFixed(3)})` : '';
    const weakest = e.payload?.weakest_dimensions as string[] | undefined;
    const focus = e.payload?.improvement_focus as string | undefined;
    let hint = '';
    if (action === 'rerun' && weakest?.length) {
      hint = ` → Focus on: ${weakest.join(', ')}`;
    }
    if (focus) hint += ` — "${focus}"`;
    return [{ prefix: '[QUEEN]', prefixColor: 'text-cultural-bronze-500', text: `Decision: ${action}${extra}${hint}` }];
  }
  if (type === 'human_required') {
    return [{ prefix: '[HITL]', prefixColor: 'text-cultural-amber-500', text: `Waiting for human input at ${stage}` }];
  }
  if (type === 'human_received') {
    return [{ prefix: '[HITL]', prefixColor: 'text-cultural-sage-500', text: 'Human action received — resuming pipeline' }];
  }
  if (type === 'pipeline_completed') {
    return [{ prefix: '[SUCCESS]', prefixColor: 'text-cultural-sage-500', text: 'Pipeline complete. Evolution Phase enabled.' }];
  }
  if (type === 'pipeline_failed') {
    return [{ prefix: '[ERROR]', prefixColor: 'text-cultural-coral-500', text: `Failed: ${e.payload?.error || 'Unknown error'}` }];
  }
  if (type === 'session_digest') {
    return [{ prefix: '[EVOLUTION]', prefixColor: 'text-cultural-bronze-500', text: 'Session digest generated — weights updated' }];
  }
  return [{ prefix: `[${stage || 'SYS'}]`, prefixColor: 'text-primary-400', text: type.replace(/_/g, ' ') }];
}

export default function IntelligenceLog({ events, currentStage, status }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events.length, status]);

  const isWaiting = status === 'running' || status === 'waiting_human';

  // Flatten multi-line events
  const allLines: { key: string; line: LogLine }[] = [];
  events.forEach((e, i) => {
    const lines = formatEvent(e);
    lines.forEach((line, j) => {
      allLines.push({ key: `${i}-${j}`, line });
    });
  });

  return (
    <div className="mt-4 bg-white/70 backdrop-blur-xl rounded-xl p-4 font-mono text-[11px] h-52 overflow-hidden relative shadow-ambient-md">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 pb-2">
        <span className="text-outline flex items-center gap-2">
          <span className="text-[14px]">$</span>
          INTELLIGENCE_LOG
        </span>
        {status === 'running' && (
          <span className="text-primary-500 font-bold text-[10px] animate-pulse">LIVE FEED</span>
        )}
        {status === 'completed' && (
          <span className="text-cultural-sage-500 font-bold text-[10px]">COMPLETE</span>
        )}
      </div>

      {/* Log lines */}
      <div ref={scrollRef} className="space-y-0.5 text-on-surface-variant overflow-y-auto h-[calc(100%-2rem)]">
        {allLines.length === 0 && (
          <p className="text-outline italic">Waiting for pipeline initialization...</p>
        )}
        {allLines.map(({ key, line }) => (
          <p key={key} className={line.prefix ? '' : 'text-on-surface-variant/70'}>
            {line.prefix && (
              <><span className={line.prefixColor}>{line.prefix}</span>{' '}</>
            )}
            <span>{line.text}</span>
          </p>
        ))}
        {isWaiting && (
          <p className="text-outline italic">
            Waiting for {currentStage || 'next'} directive...
            <span className="animate-blink">_</span>
          </p>
        )}
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white/90 to-transparent pointer-events-none" />
    </div>
  );
}
