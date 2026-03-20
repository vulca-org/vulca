/**
 * VULCA Canvas — slim container wiring store, pipeline hook, and panel components.
 *
 * Layout:
 *   Edit mode:       [Left 300px] [PipelineEditor flex]
 *   Run mode:        [Left 300px] [Center flex] [Right 380px]
 *   Traditions mode: [Left 300px] [Explore/Build flex]
 *   Mobile:          Single column with tab switching.
 */

import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import { usePrototypePipeline } from '@/hooks/usePrototypePipeline';
import type { CreateRunParams, ScoredCandidate } from '@/hooks/usePrototypePipeline';
import { useCanvasStore } from '@/store/canvasStore';
import { useTraditionDetection } from '@/hooks/useTraditionDetection';
import { API_PREFIX } from '@/config/api';
import { IOSAlert } from '@/components/ios';

import type { RunConfigParams } from '@/components/prototype/RunConfigForm';
import type { StageStatus, ReportOutput } from '@/components/prototype/editor';
import HitlOverlay from '@/components/prototype/HitlOverlay';
import CriticDetailModal from '@/components/prototype/CriticDetailModal';
import OnboardingTour from '@/components/prototype/OnboardingTour';

// Old 3-panel layout replaced by CanvasV2Layout + mobile simplified view
import CanvasV2Layout from '@/components/prototype/canvas-v2/CanvasV2Layout';
import ArtworkHUD from '@/components/prototype/canvas-v2/ArtworkHUD';
import IntelligenceLog from '@/components/prototype/canvas-v2/IntelligenceLog';
import PipelineEditorModal from '@/components/prototype/canvas-v2/PipelineEditorModal';

/** Auth headers for prototype API calls — reads real user token from localStorage */
function getProtoAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export default function PrototypePage() {
  // --- Core pipeline hook ---
  const { state, startRun, connectToRun, submitAction, reset } = usePrototypePipeline();

  // --- Shared canvas store ---
  const store = useCanvasStore();
  const {
    playgroundMode, setPlaygroundMode,
    currentSubject, setCurrentSubject,
    currentTradition, setCurrentTradition,
    currentProvider, enableHitl,
    setTraditionManuallySet,
  } = store;

  // --- Tradition auto-detection ---
  useTraditionDetection();

  // --- URL params for Gallery Fork pre-fill ---
  const [searchParams] = useSearchParams();
  const urlSubject = searchParams.get('subject') || '';
  const urlTradition = searchParams.get('tradition') || '';
  // Initialize store from URL params on first render
  useEffect(() => {
    if (urlSubject) setCurrentSubject(urlSubject);
    if (urlTradition) {
      setCurrentTradition(urlTradition);
      setTraditionManuallySet(true);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // --- Local UI state (not shared across panels) ---
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [lastRunParams, setLastRunParams] = useState<RunConfigParams | null>(null);
  const [criticDetailCandidate, setCriticDetailCandidate] = useState<ScoredCandidate | null>(null);
  const [pipelineEditorOpen, setPipelineEditorOpen] = useState(false);
  const [evaluateResult, setEvaluateResult] = useState<Record<string, unknown> | null>(null);
  const [evaluateLoading, setEvaluateLoading] = useState(false);

  const isRunning = state.status === 'running' || state.status === 'waiting_human';
  const isDone = state.status === 'completed' || state.status === 'failed';

  // --- Handlers ---

  const handleIntentChange = useCallback((text: string) => {
    setCurrentSubject(text);
  }, [setCurrentSubject]);

  const handleIntentSubmit = useCallback(async (intent: string, imageFile?: File) => {
    setEvaluateResult(null);
    setCurrentSubject(intent);
    if (imageFile) {
      setEvaluateLoading(true);
      try {
        const reader = new FileReader();
        const base64 = await new Promise<string>((resolve, reject) => {
          reader.onload = () => resolve((reader.result as string).split(',')[1] ?? '');
          reader.onerror = reject;
          reader.readAsDataURL(imageFile);
        });
        const res = await fetch(`${API_PREFIX}/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getProtoAuthHeaders() },
          body: JSON.stringify({ intent, image_base64: base64, tradition: currentTradition }),
        });
        if (res.ok) {
          setEvaluateResult(await res.json());
          setPlaygroundMode('run');
          toast.success('Evaluation complete!');
        } else {
          toast.error(`Evaluation failed (${res.status})`);
          setEvaluateResult({ error: `Server error (${res.status})`, scores: null, summary: 'Evaluation unavailable — backend returned an error.' });
          setPlaygroundMode('run');
        }
      } catch (err) {
        toast.error('Backend unavailable — running in offline mode');
        setEvaluateResult({ error: 'offline', scores: null, summary: 'Backend unavailable — running in offline mode.' });
        setPlaygroundMode('run');
      } finally {
        setEvaluateLoading(false);
      }
    } else {
      const params: CreateRunParams = {
        subject: intent,
        tradition: currentTradition,
        intent: lastRunParams?.intent || '',
        provider: currentProvider,
        n_candidates: lastRunParams?.n_candidates || 2,
        max_rounds: lastRunParams?.max_rounds || 3,
        enable_hitl: enableHitl,
        enable_agent_critic: true,
        enable_parallel_critic: false,
        use_graph: false,
        template: 'default',
      };
      setLastRunParams({ ...params, template: 'default' } as RunConfigParams);
      setPlaygroundMode('run');
      startRun(params);
    }
  }, [lastRunParams, startRun, enableHitl, currentTradition, currentProvider, setCurrentSubject, setPlaygroundMode]);

  const handleStartRun = useCallback((params: RunConfigParams) => {
    setActiveTemplate(params.template || 'default');
    setLastRunParams(params);
    if (params.subject) setCurrentSubject(params.subject);
    if (params.tradition) {
      setCurrentTradition(params.tradition);
      setTraditionManuallySet(true);
    }
    startRun(params);
  }, [startRun, setCurrentSubject, setCurrentTradition, setTraditionManuallySet]);

  const handleFork = useCallback((params: { subject: string; tradition: string }) => {
    setCurrentSubject(params.subject);
    setCurrentTradition(params.tradition);
    setTraditionManuallySet(true);
  }, [setCurrentSubject, setCurrentTradition, setTraditionManuallySet]);

  const handleReset = useCallback(() => {
    setSelectedCandidateId(null);
    setEvaluateResult(null);
    setTraditionManuallySet(false);
    reset();
  }, [reset, setTraditionManuallySet]);


  // --- Computed stage data ---

  const completedStages = state.events
    .filter(e => e.event_type === 'stage_completed')
    .map(e => e.stage)
    .filter((v, i, a) => a.indexOf(v) === i);

  const stageDurations: Record<string, number> = {};
  const stageStarts: Record<string, number> = {};
  for (const e of state.events) {
    if (e.event_type === 'stage_started') stageStarts[e.stage] = e.timestamp_ms;
    else if (e.event_type === 'stage_completed' && stageStarts[e.stage])
      stageDurations[e.stage] = e.timestamp_ms - stageStarts[e.stage];
  }

  const stageStatuses: Record<string, StageStatus> = {};
  for (const e of state.events) {
    if (e.event_type === 'stage_started') stageStatuses[e.stage] = { status: 'running' };
    else if (e.event_type === 'stage_completed')
      stageStatuses[e.stage] = { status: 'done', duration: stageStarts[e.stage] ? e.timestamp_ms - stageStarts[e.stage] : undefined };
  }
  if (state.currentStage && !stageStatuses[state.currentStage]) stageStatuses[state.currentStage] = { status: 'running' };
  if (state.status === 'failed' && state.currentStage) stageStatuses[state.currentStage] = { status: 'error' };

  const reportOutput = state.reportOutput as ReportOutput | null;

  // --- Layout ---

  return (
    <>
      {/* Desktop: Single unified Canvas V2 layout (no tabs, no mode switching) */}
      <div className="hidden lg:block h-[calc(100vh-56px)]">
        <CanvasV2Layout
          pipeline={state}
          onAction={submitAction}
          onReset={handleReset}
          onOpenPipelineEditor={() => setPipelineEditorOpen(true)}
          onStartPipeline={(subject, tradition, provider, nodeParams, referenceImageBase64) => {
            store.setCurrentSubject(subject);
            store.setCurrentTradition(tradition);
            startRun({ subject, tradition, provider, n_candidates: 4, max_rounds: 3, enable_hitl: true, enable_agent_critic: true, node_params: nodeParams, reference_image_base64: referenceImageBase64 });
          }}
          onInstruct={async (instruction) => {
            if (state.taskId) {
              // Instruct API creates a new run server-side, returns new_task_id
              try {
                const res = await fetch(`${API_PREFIX}/prototype/runs/${state.taskId}/instruct`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', ...getProtoAuthHeaders() },
                  body: JSON.stringify({ instruction }),
                });
                if (res.ok) {
                  const data = await res.json();
                  store.setCurrentSubject(instruction);
                  // Connect SSE to the new run (don't create another one)
                  connectToRun(data.new_task_id);
                  toast.success('Instruction sent');
                } else {
                  toast.error(`Instruct failed (${res.status})`);
                }
              } catch {
                toast.error('Failed to send instruction');
              }
            } else {
              // No previous run — create a fresh one
              store.setCurrentSubject(instruction);
              startRun({ subject: instruction, tradition: store.currentTradition || 'default', provider: 'auto', n_candidates: 4, max_rounds: 3, enable_hitl: true, enable_agent_critic: true });
            }
          }}
        />
      </div>

      {/* Mobile: simplified single-column Canvas V2 view */}
      <div className="lg:hidden flex flex-col h-[calc(100vh-64px)] overflow-y-auto bg-surface-container-low">
        <div className="p-4 space-y-4">
          {/* Artwork + Intent Input */}
          <ArtworkHUD
            bestImageUrl={state.bestImageUrl}
            candidates={state.candidates}
            currentStage={state.currentStage}
            subject={store.currentSubject || ''}
            pipelineStatus={state.status}
            onStartPipeline={(subject, tradition, provider, referenceImageBase64) => {
              store.setCurrentSubject(subject);
              store.setCurrentTradition(tradition);
              startRun({ subject, tradition, provider, n_candidates: 4, max_rounds: 3, enable_hitl: true, enable_agent_critic: true, reference_image_base64: referenceImageBase64 });
            }}
          />

          {/* Intelligence Log */}
          <IntelligenceLog
            events={state.events}
            currentStage={state.currentStage}
            status={state.status}
          />

          {/* L1-L5 scores (when available) */}
          {state.scoredCandidates.length > 0 && (
            <div className="bg-white rounded-xl p-4">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-outline mb-3">Scores</h3>
              <div className="grid grid-cols-5 gap-2">
                {(state.scoredCandidates[0]?.dimension_scores || []).map((ds) => {
                  const lKey = ds.dimension.startsWith('L') ? ds.dimension : '';
                  return (
                    <div key={ds.dimension} className="text-center">
                      <div className={`w-full aspect-square rounded-lg flex items-center justify-center text-xs font-bold ${ds.score >= 0.9 ? 'bg-primary-500 text-white' : 'bg-surface-container-high text-on-surface-variant'}`}>
                        {lKey || ds.dimension.slice(0, 3)}
                      </div>
                      <span className="text-[9px] font-bold text-on-surface-variant">{Math.round(ds.score * 100)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Actions */}
          {(state.status === 'completed' || state.status === 'failed') && (
            <button
              onClick={handleReset}
              className="w-full bg-primary-500 text-white py-3 rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
            >
              {state.status === 'failed' ? 'Retry' : 'New Creation'}
            </button>
          )}
        </div>
      </div>

      {/* Overlays */}
      <HitlOverlay
        hitlWaitInfo={state.hitlWaitInfo}
        evidence={state.evidence}
        candidates={state.candidates}
        scoredCandidates={state.scoredCandidates}
        bestCandidateId={state.bestCandidateId}
        onAction={submitAction}
        onClose={() => { /* HITL requires explicit action — do not auto-approve on close */ }}
      />

      {criticDetailCandidate && (
        <CriticDetailModal
          candidate={criticDetailCandidate}
          onClose={() => setCriticDetailCandidate(null)}
          crossLayerSignals={state.crossLayerSignals ?? undefined}
        />
      )}

      <OnboardingTour />

      {/* Pipeline Editor Modal */}
      <PipelineEditorModal
        open={pipelineEditorOpen}
        onClose={() => setPipelineEditorOpen(false)}
        isRunning={isRunning}
        stageStatuses={isRunning || isDone ? stageStatuses : undefined}
        reportOutput={reportOutput ?? undefined}
      />

      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#f9f9ff',
            color: '#181c22',
            boxShadow: '0 4px 24px rgba(28,28,25,0.06)',
            fontFamily: 'Inter, system-ui, sans-serif',
          },
          success: { iconTheme: { primary: '#5F8A50', secondary: '#fcf9f4' } },
          error: { iconTheme: { primary: '#C65D4D', secondary: '#fcf9f4' } },
        }}
      />

      <IOSAlert
        visible={state.status === 'failed' && !!state.error}
        onClose={handleReset}
        type="error"
        title="Pipeline Failed"
        message={state.error || 'An unexpected error occurred.'}
        actions={[
          { label: 'New Run', onPress: handleReset, style: 'default' },
          { label: 'Dismiss', onPress: handleReset, style: 'cancel' },
        ]}
      />
    </>
  );
}
