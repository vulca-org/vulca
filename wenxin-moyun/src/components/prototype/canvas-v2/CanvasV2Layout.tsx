/**
 * Canvas V2 Layout — Fusion of Refined Spacing + Functional Apple V1.
 *
 * Three-column layout with bottom chat bar for "Instruct the Collective...".
 * Exact Tailwind classes extracted from design HTML files.
 */

import { useState, useCallback, useRef } from 'react';
import { Paperclip, Image, BarChart3, Link2, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import type { PipelineState } from '@/hooks/usePrototypePipeline';
import { useCanvasStore } from '@/store/canvasStore';

import AICollectiveSidebar from './AICollectiveSidebar';
import ArtworkHUD from './ArtworkHUD';
import IntelligenceLog from './IntelligenceLog';
import MaturityLevelPanel from './MaturityLevelPanel';
import MetadataTagsPanel from './MetadataTagsPanel';
import FinalizeSection from './FinalizeSection';
import FeedbackCollector from '../FeedbackCollector';
import HitlDecisionPanel from './HitlDecisionPanel';
import WeightSlidersPanel from './WeightSlidersPanel';
import RoundComparisonChart from './RoundComparisonChart';

interface Props {
  pipeline: PipelineState;
  onAction: (action: string, options?: Record<string, unknown>) => Promise<void>;
  onReset: () => void;
  onStartPipeline?: (subject: string, tradition: string, provider: string, nodeParams?: Record<string, Record<string, unknown>>, referenceImageBase64?: string) => void;
  onInstruct?: (instruction: string) => void;
  onOpenPipelineEditor?: () => void;
}

export default function CanvasV2Layout({ pipeline, onAction, onReset, onStartPipeline, onInstruct, onOpenPipelineEditor }: Props) {
  const { currentSubject, currentTradition } = useCanvasStore();
  const [instructText, setInstructText] = useState('');
  const [lockedDimensions, setLockedDimensions] = useState<string[]>([]);
  const [weights, setWeights] = useState<Record<string, number>>({
    L1: 0.20, L2: 0.20, L3: 0.25, L4: 0.20, L5: 0.15,
  });
  const imageUploadRef = useRef<HTMLInputElement>(null);
  const rightPanelRef = useRef<HTMLElement>(null);

  const isComplete = pipeline.status === 'completed';
  const isRunning = pipeline.status === 'running';
  const bestRiskTags = pipeline.scoredCandidates.length > 0
    ? (pipeline.scoredCandidates.find(c => c.candidate_id === pipeline.bestCandidateId) || pipeline.scoredCandidates[0])?.risk_tags
    : undefined;

  const bestWeightedTotal = pipeline.scoredCandidates.length > 0
    ? (pipeline.scoredCandidates.find(c => c.candidate_id === pipeline.bestCandidateId) || pipeline.scoredCandidates[0])?.weighted_total ?? null
    : null;

  const handleInstruct = useCallback(() => {
    if (!instructText.trim()) return;
    if (onInstruct) {
      onInstruct(instructText.trim());
    } else if (onStartPipeline) {
      // MVP fallback: start new run with instruction as subject
      onStartPipeline(instructText.trim(), currentTradition || 'default', 'auto');
    }
    setInstructText('');
  }, [instructText, onInstruct, onStartPipeline, currentTradition]);

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] overflow-hidden">
      {/* Three-column layout (single interface, no tabs) */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: AI Collective (w-80, from Refined Spacing design) */}
        <AICollectiveSidebar
          currentStage={pipeline.currentStage}
          pipelineStatus={pipeline.status}
          events={pipeline.events}
          tradition={currentTradition}
          subject={currentSubject}
          onNewSession={onReset}
          onOpenPipelineEditor={onOpenPipelineEditor}
        />

        {/* Center: Artwork + Log + Chat Bar */}
        <section className="flex-1 flex flex-col relative bg-surface-container-low overflow-hidden">
          {/* Artwork area */}
          <div className="flex-1 p-4 pb-0 overflow-hidden">
            <ArtworkHUD
              bestImageUrl={pipeline.bestImageUrl}
              candidates={pipeline.candidates}
              currentStage={pipeline.currentStage}
              subject={currentSubject || ''}
              pipelineStatus={pipeline.status}
              onStartPipeline={(subject, tradition, provider, referenceImageBase64) => {
                // Build node_params with weight sliders
                const nodeParams: Record<string, Record<string, unknown>> = {
                  critic: {
                    w_l1: weights.L1, w_l2: weights.L2, w_l3: weights.L3,
                    w_l4: weights.L4, w_l5: weights.L5,
                  },
                };
                onStartPipeline?.(subject, tradition, provider, nodeParams, referenceImageBase64);
              }}
            />
          </div>

          {/* Intelligence Log */}
          <div className="px-4 pb-0">
            <IntelligenceLog
              events={pipeline.events}
              currentStage={pipeline.currentStage}
              status={pipeline.status}
            />
          </div>

          {/* ── Bottom Chat Bar (from Refined Spacing design) ── */}
          <div className="px-4 py-3 shrink-0">
            <div className="bg-surface-container-lowest/90 backdrop-blur-xl border border-surface-container-high/60 shadow-ambient-lg rounded-full px-4 py-2.5 flex items-center gap-3">
              {/* Tool icons — 📎 🖼️ 📊 🔗 */}
              {/* Image upload for evaluate mode */}
              <input
                ref={imageUploadRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  e.target.value = '';
                  try {
                    const base64 = await new Promise<string>((resolve, reject) => {
                      const reader = new FileReader();
                      reader.onload = () => resolve((reader.result as string).split(',')[1] ?? '');
                      reader.onerror = reject;
                      reader.readAsDataURL(file);
                    });
                    const { API_PREFIX } = await import('@/config/api');
                    const res = await fetch(`${API_PREFIX}/create`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ intent: 'evaluate', image_base64: base64, tradition: currentTradition || 'default' }),
                    });
                    if (res.ok) {
                      const result = await res.json();
                      toast.success(`Evaluation complete: ${result.overall_score ? (result.overall_score * 100).toFixed(0) + '%' : 'Done'}`);
                    } else {
                      toast.error(`Evaluation failed (${res.status})`);
                    }
                  } catch {
                    toast.error('Image evaluation failed — backend may be unavailable');
                  }
                }}
              />
              <div className="flex items-center gap-1">
                <button
                  className="p-2 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
                  title="Attach file"
                  onClick={() => toast('File attachment coming soon', { icon: '📎' })}
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
                  title="Upload image to evaluate"
                  onClick={() => imageUploadRef.current?.click()}
                >
                  <Image className="w-4 h-4" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
                  title="View scores"
                  onClick={() => rightPanelRef.current?.scrollTo({ top: 0, behavior: 'smooth' })}
                >
                  <BarChart3 className="w-4 h-4" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
                  title="Copy run ID"
                  onClick={() => {
                    if (pipeline.taskId) {
                      navigator.clipboard.writeText(pipeline.taskId).then(
                        () => toast.success(`Run ID copied: ${pipeline.taskId}`),
                        () => toast.error('Failed to copy')
                      );
                    } else {
                      toast('No active run to share', { icon: '🔗' });
                    }
                  }}
                >
                  <Link2 className="w-4 h-4" />
                </button>
              </div>

              {/* Input */}
              <input
                type="text"
                value={instructText}
                onChange={(e) => setInstructText(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleInstruct(); } }}
                placeholder={isRunning ? 'Pipeline running...' : 'Instruct the Collective...'}
                disabled={isRunning}
                className="flex-1 bg-transparent border-none focus:ring-0 text-sm placeholder:text-on-surface-variant/50 italic font-medium text-on-surface disabled:opacity-40"
              />

              {/* Send button */}
              <button
                onClick={handleInstruct}
                disabled={isRunning || !instructText.trim()}
                className="w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center shadow-lg shadow-primary-500/30 hover:scale-105 active:scale-95 transition-all disabled:opacity-40 disabled:pointer-events-none"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>

        {/* Right: Curation Engine */}
        <aside ref={rightPanelRef} className="w-80 p-6 overflow-y-auto shrink-0 flex flex-col bg-surface-container-low/30">
          {/* Weight sliders — visible when idle or configuring */}
          {(pipeline.status === 'idle' || pipeline.status === 'waiting_human') && (
            <WeightSlidersPanel
              weights={weights}
              onChange={setWeights}
              disabled={isRunning}
            />
          )}

          {/* Round comparison chart — visible when we have round data */}
          <RoundComparisonChart rounds={pipeline.rounds} />

          <MaturityLevelPanel
            scoredCandidates={pipeline.scoredCandidates}
            bestCandidateId={pipeline.bestCandidateId}
            lockedDimensions={lockedDimensions}
            onToggleLock={(dim) => setLockedDimensions(prev =>
              prev.includes(dim) ? prev.filter(d => d !== dim) : [...prev, dim]
            )}
          />

          {/* HITL Decision Panel */}
          <HitlDecisionPanel
            pipelineStatus={pipeline.status}
            lockedDimensions={lockedDimensions}
            weakestDimensions={pipeline.decision?.rerun_dimensions}
            onAction={onAction}
          />

          <MetadataTagsPanel
            evidence={pipeline.evidence}
            tradition={currentTradition || 'default'}
            riskTags={bestRiskTags}
          />

          {isComplete && pipeline.taskId && (
            <div className="mb-4">
              <FeedbackCollector
                sessionId={pipeline.taskId}
                evaluationId={pipeline.taskId}
                candidateId={pipeline.bestCandidateId || ''}
                tradition={currentTradition || ''}
              />
            </div>
          )}

          {/* Confidence / Cost stats (from Refined Spacing design) */}
          {(isComplete || pipeline.status === 'running') && (
            <div className="bg-white rounded-xl p-4 mb-4">
              <div className="grid grid-cols-2 gap-8">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Confidence</span>
                  <span className="text-xl font-bold text-slate-900">
                    {bestWeightedTotal != null ? `${(bestWeightedTotal * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Cost</span>
                  <span className="text-xl font-bold text-slate-900">
                    {pipeline.totalCostUsd > 0 ? `$${pipeline.totalCostUsd.toFixed(2)}` : '—'}
                  </span>
                </div>
              </div>
            </div>
          )}

          <FinalizeSection
            taskId={pipeline.taskId}
            pipelineStatus={pipeline.status}
            totalLatencyMs={pipeline.totalLatencyMs}
            totalCostUsd={pipeline.totalCostUsd}
            weightedTotal={bestWeightedTotal}
            onReset={onReset}
          />
        </aside>
      </div>
    </div>
  );
}
