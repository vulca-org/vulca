/**
 * VULCA Canvas — slim container wiring store, pipeline hook, and panel components.
 *
 * Layout:
 *   Edit mode:       [Left 300px] [PipelineEditor flex]
 *   Run mode:        [Left 300px] [Center flex] [Right 380px]
 *   Traditions mode: [Left 300px] [Explore/Build flex]
 *   Mobile:          Single column with tab switching.
 */

import { useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import { usePrototypePipeline } from '@/hooks/usePrototypePipeline';
import type { CreateRunParams, ScoredCandidate } from '@/hooks/usePrototypePipeline';
import { useCanvasStore } from '@/store/canvasStore';
import { useTraditionDetection } from '@/hooks/useTraditionDetection';
import { API_PREFIX } from '@/config/api';
import { IOSSegmentedControl, IOSAlert } from '@/components/ios';

import type { RunConfigParams } from '@/components/prototype/RunConfigForm';
import type { AgentNodeId, StageStatus, ReportOutput } from '@/components/prototype/editor';
import { PipelineEditor, NodeParamPanel } from '@/components/prototype/editor';
import TraditionBuilder from '@/components/prototype/TraditionBuilder';
import TraditionExplorer from '@/components/prototype/TraditionExplorer';
import HitlOverlay from '@/components/prototype/HitlOverlay';
import CriticDetailModal from '@/components/prototype/CriticDetailModal';
import OnboardingTour from '@/components/prototype/OnboardingTour';

import CanvasLeftPanel from '@/components/prototype/CanvasLeftPanel';
import type { EditorRunParams } from '@/components/prototype/CanvasLeftPanel';
import CanvasCenterPanel from '@/components/prototype/CanvasCenterPanel';
import CanvasRightPanel from '@/components/prototype/CanvasRightPanel';

/** Auth headers for prototype API calls — reads real user token from localStorage */
function getProtoAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export default function PrototypePage() {
  // --- Core pipeline hook ---
  const { state, startRun, submitAction, reset } = usePrototypePipeline();

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
  useState(() => {
    if (urlSubject) setCurrentSubject(urlSubject);
    if (urlTradition) {
      setCurrentTradition(urlTradition);
      setTraditionManuallySet(true);
    }
  });

  // --- Local UI state (not shared across panels) ---
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [mobileTab, setMobileTab] = useState(0);
  const [lastRunParams, setLastRunParams] = useState<RunConfigParams | null>(null);
  const [criticDetailCandidate, setCriticDetailCandidate] = useState<ScoredCandidate | null>(null);
  const [evaluateResult, setEvaluateResult] = useState<Record<string, unknown> | null>(null);
  const [evaluateLoading, setEvaluateLoading] = useState(false);
  const [editorNodeParams, setEditorNodeParams] = useState<Record<string, Record<string, unknown>>>({});
  const [selectedEditorNode, setSelectedEditorNode] = useState<AgentNodeId | null>(null);

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
        n_candidates: lastRunParams?.n_candidates || 4,
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

  const handleEditorRun = useCallback((params: EditorRunParams) => {
    const runParams: CreateRunParams = {
      subject: currentSubject.trim() || lastRunParams?.subject || 'Ink wash landscape with mist and mountains',
      tradition: currentTradition || lastRunParams?.tradition || 'chinese_xieyi',
      provider: currentProvider,
      n_candidates: lastRunParams?.n_candidates || 4,
      max_rounds: lastRunParams?.max_rounds || 3,
      enable_hitl: enableHitl,
      enable_agent_critic: lastRunParams?.enable_agent_critic ?? true,
      enable_parallel_critic: lastRunParams?.enable_parallel_critic || false,
      use_graph: lastRunParams?.use_graph || false,
      template: params.template,
      custom_nodes: params.customNodes,
      custom_edges: params.customEdges,
      node_params: params.nodeParams,
    };
    setActiveTemplate(params.template);
    setPlaygroundMode('run');
    startRun(runParams);
  }, [lastRunParams, startRun, currentSubject, currentTradition, currentProvider, enableHitl, setPlaygroundMode]);

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

  const handleNodeParamChange = useCallback((nodeId: AgentNodeId, paramId: string, value: unknown) => {
    setEditorNodeParams(prev => ({
      ...prev,
      [nodeId]: { ...prev[nodeId], [paramId]: value },
    }));
  }, []);

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

  // --- Shared panel props ---
  const leftProps = {
    pipeline: state,
    isRunning, isDone, evaluateLoading,
    lastRunParams, activeTemplate,
    completedStages, stageDurations,
    onIntentSubmit: handleIntentSubmit,
    onIntentChange: handleIntentChange,
    onStartRun: handleStartRun,
    onFork: handleFork,
  };

  // --- Layout ---

  return (
    <>
      {/* Desktop layout */}
      {playgroundMode === 'edit' ? (
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            <CanvasLeftPanel {...leftProps} />
          </aside>
          <main data-tour-canvas className="min-h-0 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden relative">
            <PipelineEditor
              onRun={handleEditorRun}
              disabled={isRunning}
              onNodeSelect={setSelectedEditorNode}
              nodeParams={editorNodeParams}
              stageStatuses={isRunning || isDone ? stageStatuses : undefined}
              reportOutput={reportOutput ?? undefined}
            />
            <NodeParamPanel
              nodeId={selectedEditorNode}
              params={editorNodeParams}
              onChange={handleNodeParamChange}
              onClose={() => setSelectedEditorNode(null)}
            />
          </main>
        </div>
      ) : playgroundMode === 'run' ? (
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr_380px] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            <CanvasLeftPanel {...leftProps} />
          </aside>
          <main className="overflow-y-auto space-y-3 px-1 scrollbar-thin">
            <CanvasCenterPanel
              pipeline={state}
              isDone={isDone}
              evaluateResult={evaluateResult}
              selectedCandidateId={selectedCandidateId}
              onSelectCandidate={setSelectedCandidateId}
              onClearEvaluate={() => setEvaluateResult(null)}
              onReset={handleReset}
            />
          </main>
          <aside className="overflow-y-auto space-y-3 pl-1 scrollbar-thin">
            <CanvasRightPanel
              pipeline={state}
              isDone={isDone}
              selectedCandidateId={selectedCandidateId}
              lastRunParams={lastRunParams}
              onAction={submitAction}
              onReset={handleReset}
              onViewCriticDetail={setCriticDetailCandidate}
            />
          </aside>
        </div>
      ) : (
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            <CanvasLeftPanel {...leftProps} />
          </aside>
          <main className="overflow-y-auto px-1 scrollbar-thin">
            <div className="flex items-center gap-2 mb-4">
              <IOSSegmentedControl
                segments={['Browse', 'Create']}
                selectedIndex={store.traditionsTab === 'browse' ? 0 : 1}
                onChange={(idx) => store.setTraditionsTab(idx === 0 ? 'browse' : 'create')}
                size="compact"
                className="w-48"
              />
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {store.traditionsTab === 'browse' ? '8 cultural traditions' : 'Define custom traditions'}
              </span>
            </div>
            {store.traditionsTab === 'browse' ? <TraditionExplorer /> : <TraditionBuilder />}
          </main>
        </div>
      )}

      {/* Mobile: tab-based single column */}
      <div className="lg:hidden flex flex-col h-[calc(100vh-64px)]">
        <div className="sticky top-0 z-10 bg-white/80 dark:bg-[#0F0D0B]/80 backdrop-blur-lg px-4 py-2 border-b border-gray-200 dark:border-gray-800">
          <IOSSegmentedControl
            segments={['Config', 'Canvas', 'Analysis']}
            selectedIndex={mobileTab}
            onChange={setMobileTab}
            size="compact"
            className="w-full"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {mobileTab === 0 && <CanvasLeftPanel {...leftProps} />}
          {mobileTab === 1 && (
            <CanvasCenterPanel
              pipeline={state}
              isDone={isDone}
              evaluateResult={evaluateResult}
              selectedCandidateId={selectedCandidateId}
              onSelectCandidate={setSelectedCandidateId}
              onClearEvaluate={() => setEvaluateResult(null)}
              onReset={handleReset}
            />
          )}
          {mobileTab === 2 && (
            <CanvasRightPanel
              pipeline={state}
              isDone={isDone}
              selectedCandidateId={selectedCandidateId}
              lastRunParams={lastRunParams}
              onAction={submitAction}
              onReset={handleReset}
              onViewCriticDetail={setCriticDetailCandidate}
            />
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
        onClose={() => submitAction('approve')}
      />

      {criticDetailCandidate && (
        <CriticDetailModal
          candidate={criticDetailCandidate}
          onClose={() => setCriticDetailCandidate(null)}
          crossLayerSignals={state.crossLayerSignals ?? undefined}
        />
      )}

      <OnboardingTour />

      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#FAF7F2',
            color: '#334155',
            border: '1px solid #E8E0D4',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          },
          success: { iconTheme: { primary: '#5F8A50', secondary: '#FAF7F2' } },
          error: { iconTheme: { primary: '#C65D4D', secondary: '#FAF7F2' } },
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
