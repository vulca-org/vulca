/**
 * AI Collective Sidebar — Extracted from Refined Spacing design HTML.
 * w-80, large agent cards with descriptions, New Session + Pipeline Editor buttons.
 */

import { useMemo } from 'react';
import type { PipelineEvent } from '@/hooks/usePrototypePipeline';
import { getItem } from '@/utils/storageUtils';
import { isGuestMode } from '@/utils/guestSession';

interface Props {
  currentStage: string;
  pipelineStatus: string;
  events: PipelineEvent[];
  tradition?: string;
  subject?: string;
  onNewSession?: () => void;
  onOpenPipelineEditor?: () => void;
}

const AGENTS = [
  { id: 'scout', label: 'Scout', icon: 'explore', desc: 'Identifying data sources and initial research nodes.', activeBg: 'border-primary-500/10 bg-primary-50/30 hover:bg-primary-50/50 shadow-sm', dotColor: 'bg-primary-500 ring-4 ring-primary-500/10', iconBg: 'bg-primary-500 text-white' },
  { id: 'draft', label: 'Draft', icon: 'edit_note', desc: 'Synthesizing raw findings into structured narrative.', activeBg: 'border-primary-500/10 bg-primary-50/30 hover:bg-primary-50/50 shadow-sm', dotColor: 'bg-primary-500 ring-4 ring-primary-500/10', iconBg: 'bg-primary-500 text-white' },
  { id: 'critic', label: 'Critic', icon: 'gavel', desc: 'Challenging assumptions and refining logic.', activeBg: 'border-cultural-amber-500/10 bg-cultural-amber-50/30 hover:bg-cultural-amber-50/50 shadow-sm', dotColor: 'bg-cultural-amber-400', iconBg: 'bg-cultural-amber-50 text-cultural-amber-700' },
  { id: 'queen', label: 'Queen', icon: 'crown', desc: 'Orchestrating workflows and final approvals.', activeBg: 'border-cultural-bronze-500/10 bg-cultural-bronze-50/30 hover:bg-cultural-bronze-50/50 shadow-sm', dotColor: 'bg-cultural-bronze-500', iconBg: 'bg-cultural-bronze-50 text-cultural-bronze-700' },
] as const;

function getAgentStatus(agentId: string, currentStage: string, pipelineStatus: string, completedStages: Set<string>): 'active' | 'done' | 'idle' {
  if (pipelineStatus === 'idle') return 'idle';
  if (pipelineStatus === 'completed' || pipelineStatus === 'failed') {
    return completedStages.has(agentId) ? 'done' : 'idle';
  }
  const current = currentStage.toLowerCase().replace('generate', 'draft').replace('evaluate', 'critic').replace('decide', 'queen');
  if (current === agentId) return 'active';
  const ORDER = ['scout', 'draft', 'critic', 'queen'];
  return ORDER.indexOf(agentId) < ORDER.indexOf(current) ? 'done' : 'idle';
}

export default function AICollectiveSidebar({ currentStage, pipelineStatus, events, tradition, subject: _subject, onNewSession, onOpenPipelineEditor }: Props) {
  const completedStages = useMemo(() => {
    const set = new Set<string>();
    for (const e of events) {
      if (e.event_type === 'stage_completed') {
        set.add(e.stage.toLowerCase().replace('generate', 'draft').replace('evaluate', 'critic').replace('decide', 'queen'));
      }
    }
    return set;
  }, [events]);

  return (
    /* Exact layout from Refined Spacing design HTML line 123-201 */
    <aside className="w-80 bg-white border-r border-slate-200/60 flex flex-col z-20 overflow-y-auto shrink-0">
      <div className="p-8">
        <h2 className="text-[11px] font-bold uppercase tracking-[0.15em] text-slate-400 mb-8">AI Collective</h2>
        <div className="space-y-5">
          {AGENTS.map((agent) => {
            const status = getAgentStatus(agent.id, currentStage, pipelineStatus, completedStages);
            const isActive = status === 'active';
            const isDone = status === 'done';

            return (
              <div
                key={agent.id}
                className={`p-5 rounded-2xl border flex flex-col gap-3.5 group transition-all ${
                  isActive
                    ? agent.activeBg
                    : 'border-slate-200/60 bg-white hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3.5">
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                      isActive ? agent.iconBg : isDone ? 'bg-green-50 text-green-600' : 'bg-slate-100 text-slate-500'
                    }`}>
                      <span className="material-symbols-outlined text-base" style={isActive ? { fontVariationSettings: "'FILL' 1" } : undefined}>
                        {isDone ? 'check_circle' : agent.icon}
                      </span>
                    </div>
                    <span className={`font-bold text-[15px] ${isActive ? 'text-slate-900' : 'text-slate-700'}`}>
                      {agent.label}
                    </span>
                  </div>
                  <span className={`w-2 h-2 rounded-full ${
                    isActive ? agent.dotColor : isDone ? 'bg-green-500' : 'bg-slate-300'
                  }`} />
                </div>
                <p className={`text-[13px] leading-relaxed ${isActive ? 'text-slate-600' : 'text-slate-500'}`}>
                  {agent.desc}
                </p>
                {isActive && (
                  <div className="flex gap-2.5">
                    <span className="px-2.5 py-1 bg-white border border-slate-200/60 text-[10px] font-bold uppercase tracking-wider text-slate-500 rounded-md">
                      Processing
                    </span>
                    <span className="px-2.5 py-1 bg-primary-500/10 text-[10px] font-bold uppercase tracking-wider text-primary-500 rounded-md">
                      Active
                    </span>
                  </div>
                )}
                {isDone && (
                  <span className="px-2.5 py-1 bg-green-50 text-[10px] font-bold uppercase tracking-wider text-green-600 rounded-md w-fit">
                    Complete
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tradition indicator */}
      {tradition && tradition !== 'default' && (
        <div className="px-8 mb-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-cultural-bronze-500">
            {tradition.replace(/_/g, ' ')}
          </span>
        </div>
      )}

      {/* Bottom Tools — from design HTML line 186-200 */}
      <div className="mt-auto p-8 border-t border-slate-200/60 space-y-4">
        <button
          onClick={onNewSession}
          className="w-full py-3.5 bg-slate-900 text-white rounded-xl font-semibold text-sm flex items-center justify-center gap-2.5 hover:bg-slate-800 transition-all active:scale-[0.98]"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          New Session
        </button>
        {onOpenPipelineEditor && (
          <button
            onClick={onOpenPipelineEditor}
            className="w-full py-2.5 bg-slate-50 text-slate-600 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-slate-100 transition-all"
          >
            <span className="material-symbols-outlined text-base">tune</span>
            Pipeline Editor
          </button>
        )}
        <div className="flex items-center gap-4 px-1">
          {(() => {
            const guest = isGuestMode();
            const username = getItem('username') || (guest ? 'Guest' : 'User');
            const initial = username.charAt(0).toUpperCase();
            return (
              <>
                <div className="w-10 h-10 rounded-full bg-slate-100 ring-4 ring-slate-50 flex items-center justify-center text-slate-600 text-sm font-bold">
                  {initial}
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-900">{username}</span>
                  <span className="text-[11px] font-semibold text-slate-400">{guest ? 'Guest Mode' : 'VULCA Canvas'}</span>
                </div>
              </>
            );
          })()}
        </div>
      </div>
    </aside>
  );
}
