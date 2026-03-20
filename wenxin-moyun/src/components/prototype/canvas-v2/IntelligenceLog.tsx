/**
 * Intelligence Log — Terminal-style SSE event stream viewer.
 * Formats pipeline events into colored log lines.
 */

import { useRef, useEffect } from 'react';
import type { PipelineEvent } from '@/hooks/usePrototypePipeline';

interface Props {
  events: PipelineEvent[];
  currentStage: string;
  status: string;
}

function formatEvent(e: PipelineEvent): { prefix: string; prefixColor: string; text: string } {
  const type = e.event_type;
  const stage = (e.stage || '').toUpperCase().replace('GENERATE', 'DRAFT').replace('EVALUATE', 'CRITIC').replace('DECIDE', 'QUEEN');

  if (type === 'pipeline_started') {
    return { prefix: '[SYSTEM]', prefixColor: 'text-primary-400', text: 'Initializing cultural synthesis module...' };
  }
  if (type === 'stage_started') {
    return { prefix: `[AGENT/${stage}]`, prefixColor: 'text-primary-400', text: `${stage} agent activated — round ${e.round_num}` };
  }
  if (type === 'stage_completed') {
    const payload = e.payload || {};
    const latency = payload.latency_ms ? ` (${Math.round(Number(payload.latency_ms))}ms)` : '';
    return { prefix: `[${stage}]`, prefixColor: 'text-success-500', text: `Stage complete${latency}` };
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
    return { prefix: '[QUEEN]', prefixColor: 'text-secondary-500', text: `Decision: ${action}${extra}${hint}` };
  }
  if (type === 'human_required') {
    return { prefix: '[HITL]', prefixColor: 'text-warning-500', text: `Waiting for human input at ${stage}` };
  }
  if (type === 'human_received') {
    return { prefix: '[HITL]', prefixColor: 'text-success-500', text: 'Human action received — resuming pipeline' };
  }
  if (type === 'pipeline_completed') {
    return { prefix: '[SUCCESS]', prefixColor: 'text-success-500', text: 'Pipeline complete. Evolution Phase enabled.' };
  }
  if (type === 'pipeline_failed') {
    return { prefix: '[ERROR]', prefixColor: 'text-error-500', text: `Failed: ${e.payload?.error || 'Unknown error'}` };
  }
  if (type === 'session_digest') {
    return { prefix: '[EVOLUTION]', prefixColor: 'text-secondary-500', text: 'Session digest generated — weights updated' };
  }
  return { prefix: `[${stage || 'SYS'}]`, prefixColor: 'text-primary-400', text: type.replace(/_/g, ' ') };
}

export default function IntelligenceLog({ events, currentStage, status }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events.length, status]);

  const isWaiting = status === 'running' || status === 'waiting_human';

  return (
    <div className="mt-4 bg-white/70 backdrop-blur-xl rounded-xl p-4 font-mono text-[11px] h-40 overflow-hidden relative shadow-ambient-md">
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
          <span className="text-success-500 font-bold text-[10px]">COMPLETE</span>
        )}
      </div>

      {/* Log lines */}
      <div ref={scrollRef} className="space-y-1 text-on-surface-variant overflow-y-auto h-[calc(100%-2rem)]">
        {events.length === 0 && (
          <p className="text-outline italic">Waiting for pipeline initialization...</p>
        )}
        {events.map((e, i) => {
          const { prefix, prefixColor, text } = formatEvent(e);
          return (
            <p key={i}>
              <span className={prefixColor}>{prefix}</span>{' '}
              <span>{text}</span>
            </p>
          );
        })}
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
