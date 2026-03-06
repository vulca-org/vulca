/**
 * VULCA Prototype Pipeline — three-column Playground layout.
 *
 * Left (300px):  Config + monitoring (Template, Form, Topology, Progress, Scout)
 * Center (flex): Canvas (Candidates, Round Timeline)
 * Right (380px): Analysis (Radar, Scores, Rationale, FixIt, Queen)
 *
 * Mobile (< lg): Single column with IOSSegmentedControl tab switching.
 *
 * The usePrototypePipeline hook and backend API are untouched — only rendering changes.
 */

import { useState, useCallback } from 'react';
import { usePrototypePipeline } from '../../hooks/usePrototypePipeline';
import type { CreateRunParams } from '../../hooks/usePrototypePipeline';
import { IOSCard, IOSCardContent, IOSButton, IOSSegmentedControl, IOSAlert } from '../../components/ios';
import { PROTOTYPE_DIM_LABELS } from '../../utils/vulca-dimensions';
import type { PrototypeDimension } from '../../utils/vulca-dimensions';

// Existing components — unchanged
import RunConfigForm from '../../components/prototype/RunConfigForm';
import type { RunConfigParams } from '../../components/prototype/RunConfigForm';
import PipelineProgress from '../../components/prototype/PipelineProgress';
import CandidateGallery from '../../components/prototype/CandidateGallery';
import CriticScoreTable from '../../components/prototype/CriticScoreTable';
import CriticRadarChart from '../../components/prototype/CriticRadarChart';
import QueenDecisionPanel from '../../components/prototype/QueenDecisionPanel';
import RoundTimeline from '../../components/prototype/RoundTimeline';
import TopologyViewer from '../../components/prototype/TopologyViewer';

// Newly extracted components
import PlaygroundHeader from '../../components/prototype/PlaygroundHeader';
import ScoutEvidenceCard from '../../components/prototype/ScoutEvidenceCard';
import FixItPlanCard from '../../components/prototype/FixItPlanCard';
import CriticRationaleCard from '../../components/prototype/CriticRationaleCard';
import HitlOverlay from '../../components/prototype/HitlOverlay';

// M3: Pipeline Editor + Batch
import { PipelineEditor, NodeParamPanel } from '../../components/prototype/editor';
import type { AgentNodeId, StageStatus, ReportOutput } from '../../components/prototype/editor';
import BatchInputPanel from '../../components/prototype/BatchInputPanel';

// M7: Community Canvas modes
import ComparePanel from '../../components/prototype/ComparePanel';
import TraditionBuilder from '../../components/prototype/TraditionBuilder';
import TraditionExplorer from '../../components/prototype/TraditionExplorer';

type PlaygroundMode = 'edit' | 'run' | 'build' | 'explore' | 'compare';

function formatDimension(dim: string): string {
  return PROTOTYPE_DIM_LABELS[dim as PrototypeDimension]?.short || dim.replace(/_/g, ' ');
}

export default function PrototypePage() {
  const { state, startRun, submitAction, reset } = usePrototypePipeline();
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [activeTemplate, setActiveTemplate] = useState('default');
  const [mobileTab, setMobileTab] = useState(0);
  const [lastRunParams, setLastRunParams] = useState<RunConfigParams | null>(null);

  // M3: playground mode
  const [playgroundMode, setPlaygroundMode] = useState<PlaygroundMode>('edit');
  const [editorNodeParams, setEditorNodeParams] = useState<Record<string, Record<string, unknown>>>({});
  const [selectedEditorNode, setSelectedEditorNode] = useState<AgentNodeId | null>(null);

  const handleNodeParamChange = useCallback((nodeId: AgentNodeId, paramId: string, value: unknown) => {
    setEditorNodeParams(prev => ({
      ...prev,
      [nodeId]: { ...prev[nodeId], [paramId]: value },
    }));
  }, []);

  const isRunning = state.status === 'running' || state.status === 'waiting_human';
  const isDone = state.status === 'completed' || state.status === 'failed';

  /** M3: Run from PipelineEditor */
  const handleEditorRun = useCallback((params: {
    template: string;
    customNodes?: string[];
    customEdges?: [string, string][];
    nodeParams?: Record<string, Record<string, unknown>>;
  }) => {
    // Build CreateRunParams with custom topology
    const runParams: CreateRunParams = {
      subject: lastRunParams?.subject || 'Ink wash landscape with mist and mountains',
      tradition: lastRunParams?.tradition || 'chinese_xieyi',
      provider: lastRunParams?.provider || 'mock',
      n_candidates: lastRunParams?.n_candidates || 4,
      max_rounds: lastRunParams?.max_rounds || 3,
      enable_hitl: lastRunParams?.enable_hitl || false,
      enable_agent_critic: lastRunParams?.enable_agent_critic || false,
      enable_parallel_critic: lastRunParams?.enable_parallel_critic || false,
      use_graph: true, // M3 custom topology forces graph mode
      template: params.template,
      custom_nodes: params.customNodes,
      custom_edges: params.customEdges,
      node_params: params.nodeParams,
    };
    setActiveTemplate(params.template);
    setPlaygroundMode('run');
    startRun(runParams);
  }, [lastRunParams, startRun]);

  const completedStages = state.events
    .filter(e => e.event_type === 'stage_completed')
    .map(e => e.stage)
    .filter((v, i, a) => a.indexOf(v) === i);

  // Compute stage durations from events (started → completed pairs)
  const stageDurations: Record<string, number> = {};
  const stageStarts: Record<string, number> = {};
  for (const e of state.events) {
    if (e.event_type === 'stage_started') {
      stageStarts[e.stage] = e.timestamp_ms;
    } else if (e.event_type === 'stage_completed' && stageStarts[e.stage]) {
      stageDurations[e.stage] = e.timestamp_ms - stageStarts[e.stage];
    }
  }

  // M8: Compute stageStatuses for PipelineEditor node animation
  const stageStatuses: Record<string, StageStatus> = {};
  for (const e of state.events) {
    if (e.event_type === 'stage_started') {
      stageStatuses[e.stage] = { status: 'running' };
    } else if (e.event_type === 'stage_completed') {
      stageStatuses[e.stage] = {
        status: 'done',
        duration: stageStarts[e.stage]
          ? e.timestamp_ms - stageStarts[e.stage]
          : undefined,
      };
    }
  }
  if (state.currentStage && !stageStatuses[state.currentStage]) {
    stageStatuses[state.currentStage] = { status: 'running' };
  }
  if (state.status === 'failed' && state.currentStage) {
    stageStatuses[state.currentStage] = { status: 'error' };
  }

  // M8: Extract reportOutput for ReportNode
  const reportOutput = state.reportOutput as ReportOutput | null;

  const handleStartRun = (params: RunConfigParams) => {
    setActiveTemplate(params.template || 'default');
    setLastRunParams(params);
    startRun(params);
  };

  const handleReset = () => {
    setSelectedCandidateId(null);
    reset();
  };

  // --- Shared panel builders (used by both desktop and mobile) ---

  const leftPanelContent = (
    <>
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <PlaygroundHeader status={state.status} taskId={state.taskId} />
        </div>
        <div className="flex gap-1 shrink-0">
          {([
            { mode: 'edit' as const, label: 'Edit' },
            { mode: 'run' as const, label: 'Run' },
            { mode: 'build' as const, label: 'Build' },
            { mode: 'explore' as const, label: 'Explore' },
            { mode: 'compare' as const, label: 'Compare' },
          ]).map(({ mode, label }) => (
            <button
              key={mode}
              onClick={() => setPlaygroundMode(mode)}
              className={[
                'px-2 py-1 text-[11px] font-medium rounded-lg border transition-colors',
                playgroundMode === mode
                  ? 'border-blue-300 dark:border-blue-600 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800',
              ].join(' ')}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <IOSCard variant="elevated" padding="md" animate={false}>
        <IOSCardContent>
          <RunConfigForm
            onSubmit={handleStartRun}
            disabled={isRunning}
            initialValues={isDone ? lastRunParams ?? undefined : undefined}
          />
        </IOSCardContent>
      </IOSCard>

      {state.taskId && (
        <IOSCard variant="elevated" padding="sm" animate={false}>
          <IOSCardContent>
            <TopologyViewer
              template={activeTemplate}
              currentStage={state.currentStage}
              status={state.status}
              completedStages={completedStages}
              stageDurations={stageDurations}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {state.taskId && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Progress</h3>
              <span className="text-[10px] font-mono text-gray-400">{state.taskId.slice(0, 8)}</span>
            </div>
            <PipelineProgress
              currentStage={state.currentStage}
              currentRound={state.currentRound}
              status={state.status}
              events={state.events}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {state.evidence && <ScoutEvidenceCard evidence={state.evidence} />}

      {/* M3: Batch input panel for batch_eval template in edit mode */}
      {playgroundMode === 'edit' && activeTemplate === 'batch_eval' && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <BatchInputPanel
              tradition={lastRunParams?.tradition || 'default'}
              provider={lastRunParams?.provider || 'mock'}
              template="batch_eval"
              disabled={isRunning}
            />
          </IOSCardContent>
        </IOSCard>
      )}
    </>
  );

  const centerPanelContent = (
    <>
      {/* Candidate Gallery */}
      {state.candidates.length > 0 ? (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Candidates
              <span className="ml-2 text-xs font-normal text-gray-500">R{state.currentRound}</span>
            </h3>
            {state.status === 'waiting_human' && (
              <span className="text-[11px] text-blue-600 dark:text-blue-400">Click to select</span>
            )}
          </div>
          <IOSCardContent>
            <CandidateGallery
              candidates={state.candidates}
              bestCandidateId={state.bestCandidateId}
              selectedCandidateId={selectedCandidateId}
              onSelect={setSelectedCandidateId}
              scoredCandidates={state.scoredCandidates}
              rounds={state.rounds}
            />
          </IOSCardContent>
        </IOSCard>
      ) : (
        /* Empty state */
        !state.taskId && (
          <IOSCard variant="glass" padding="lg" animate={false}>
            <IOSCardContent className="text-center py-12">
              <div className="text-4xl mb-3">🎨</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                VULCA Playground
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                Configure a pipeline run in the left panel to start generating
                and evaluating cultural art with multi-agent scoring.
              </p>
            </IOSCardContent>
          </IOSCard>
        )
      )}

      {/* Round Timeline */}
      {(state.rounds.length > 0 || (state.status === 'running' && state.currentRound > 0)) && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <RoundTimeline
              rounds={state.rounds}
              currentRound={state.currentRound}
              status={state.status}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Final Summary */}
      {isDone && (
        <div className={`rounded-xl p-4 ${
          state.status === 'completed'
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold">
              {state.status === 'completed' ? 'Pipeline Complete' : 'Pipeline Failed'}
            </h3>
            <div className="text-right text-xs text-gray-600 dark:text-gray-400 space-y-0.5">
              {state.totalRounds > 0 && <div>Rounds: {state.totalRounds}</div>}
              {state.totalLatencyMs > 0 && <div>{(state.totalLatencyMs / 1000).toFixed(1)}s</div>}
              {state.totalCostUsd > 0 && <div>${state.totalCostUsd.toFixed(4)}</div>}
            </div>
          </div>
          {state.error && (
            <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/30 rounded-lg text-xs text-red-700 dark:text-red-300">
              {state.error}
            </div>
          )}
          <div className="flex gap-2 mt-3">
            <IOSButton variant="secondary" size="sm" onClick={handleReset}>New Run</IOSButton>
            {state.status === 'failed' && (
              <IOSButton variant="primary" size="sm" onClick={handleReset}>Retry</IOSButton>
            )}
          </div>
        </div>
      )}
    </>
  );

  const rightPanelContent = (
    <>
      {/* Critic Scores Header with Agent Mode Badge */}
      {state.scoredCandidates.length > 0 && (
        <>
          <IOSCard variant="elevated" padding="md" animate={false}>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Critic L1-L5</h3>
              {state.agentMode && (
                <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
                  state.agentMode === 'agent_llm'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : state.agentMode === 'agent_fallback_rules'
                    ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {state.agentMode === 'agent_llm' ? 'LLM' : state.agentMode === 'agent_fallback_rules' ? 'Rules Fallback' : 'Rules'}
                </span>
              )}
            </div>
            <IOSCardContent>
              {state.agentMode === 'agent_fallback_rules' && (
                <div className="mb-3 rounded-lg border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/10 p-2 text-[11px] text-yellow-800 dark:text-yellow-300">
                  No LLM API key found — scores are rules-only.
                </div>
              )}
              {/* HITL Constraints */}
              {state.hitlConstraints && (
                <div className="mb-3 rounded-lg border border-blue-200 dark:border-blue-900/40 bg-blue-50 dark:bg-blue-900/10 p-2">
                  <div className="text-[11px] font-semibold text-blue-800 dark:text-blue-300 mb-1.5">
                    HITL Constraints
                  </div>
                  <div className="space-y-1.5 text-[11px]">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Locked: </span>
                      {state.hitlConstraints.locked_dimensions.length > 0 ? (
                        state.hitlConstraints.locked_dimensions.map(dim => (
                          <span key={dim} className="mr-1 px-1.5 py-0.5 rounded bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
                            {formatDimension(dim)}
                          </span>
                        ))
                      ) : <span className="text-gray-400">—</span>}
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Rerun: </span>
                      {state.hitlConstraints.rerun_dimensions.length > 0 ? (
                        state.hitlConstraints.rerun_dimensions.map(dim => (
                          <span key={dim} className="mr-1 px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">
                            {formatDimension(dim)}
                          </span>
                        ))
                      ) : <span className="text-gray-400">—</span>}
                    </div>
                    <div className="text-gray-600 dark:text-gray-300">
                      Applied: {state.hitlConstraints.applied_scores} | Touched: {state.hitlConstraints.candidates_touched}
                    </div>
                  </div>
                </div>
              )}

              {/* Radar Chart */}
              {state.rounds.length > 0 && (
                <div className="mb-3">
                  <CriticRadarChart
                    rounds={state.rounds}
                    dynamicWeights={state.dynamicWeights}
                  />
                </div>
              )}

              {/* Score Table */}
              <CriticScoreTable
                scoredCandidates={state.scoredCandidates}
                bestCandidateId={state.bestCandidateId}
                crossLayerSignals={state.crossLayerSignals ?? undefined}
              />
            </IOSCardContent>
          </IOSCard>

          <CriticRationaleCard scoredCandidates={state.scoredCandidates} />
        </>
      )}

      {/* FixItPlan */}
      {state.fixItPlan && <FixItPlanCard fixItPlan={state.fixItPlan} />}

      {/* Queen Decision */}
      {(state.decision || state.finalDecision) && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Queen Decision</h3>
            <QueenDecisionPanel
              decision={state.decision}
              finalDecision={state.finalDecision}
              status={state.status}
              scoredCandidates={state.scoredCandidates}
              selectedCandidateId={selectedCandidateId}
              onAction={submitAction}
            />
          </IOSCardContent>
        </IOSCard>
      )}
    </>
  );

  // --- Layout ---

  return (
    <>
      {/* Desktop layout */}
      {playgroundMode === 'edit' ? (
        /* Edit mode: left config + center PipelineEditor */
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            {leftPanelContent}
          </aside>
          <main className="min-h-0 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden relative">
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
        /* Run mode: three-column grid */
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr_380px] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            {leftPanelContent}
          </aside>
          <main className="overflow-y-auto space-y-3 px-1 scrollbar-thin">
            {centerPanelContent}
          </main>
          <aside className="overflow-y-auto space-y-3 pl-1 scrollbar-thin">
            {rightPanelContent}
          </aside>
        </div>
      ) : (
        /* Build / Explore / Compare: left config + full center */
        <div className="hidden lg:grid h-[calc(100vh-64px)] grid-cols-[300px_1fr] gap-4 p-4 overflow-hidden">
          <aside className="overflow-y-auto space-y-3 pr-1 scrollbar-thin">
            {leftPanelContent}
          </aside>
          <main className="overflow-y-auto px-1 scrollbar-thin">
            {playgroundMode === 'build' && <TraditionBuilder />}
            {playgroundMode === 'explore' && <TraditionExplorer />}
            {playgroundMode === 'compare' && <ComparePanel />}
          </main>
        </div>
      )}

      {/* Mobile: tab-based single column */}
      <div className="lg:hidden flex flex-col h-[calc(100vh-64px)]">
        {/* Tab bar */}
        <div className="sticky top-0 z-10 bg-white/80 dark:bg-[#0F0D0B]/80 backdrop-blur-lg px-4 py-2 border-b border-gray-200 dark:border-gray-800">
          <IOSSegmentedControl
            segments={['Config', 'Canvas', 'Analysis']}
            selectedIndex={mobileTab}
            onChange={(idx) => setMobileTab(idx)}
            size="compact"
            className="w-full"
          />
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {mobileTab === 0 && leftPanelContent}
          {mobileTab === 1 && centerPanelContent}
          {mobileTab === 2 && rightPanelContent}
        </div>
      </div>

      {/* HITL Sheet overlay (works for both desktop and mobile) */}
      <HitlOverlay
        hitlWaitInfo={state.hitlWaitInfo}
        evidence={state.evidence}
        candidates={state.candidates}
        scoredCandidates={state.scoredCandidates}
        bestCandidateId={state.bestCandidateId}
        onAction={submitAction}
        onClose={() => {/* Sheet not dismissable during HITL */}}
      />

      {/* Pipeline failure alert */}
      <IOSAlert
        visible={state.status === 'failed' && !!state.error}
        onClose={handleReset}
        type="error"
        title="Pipeline Failed"
        message={state.error || 'An unexpected error occurred.'}
        actions={[
          { label: 'New Run', onPress: handleReset, style: 'default' },
          { label: 'Dismiss', onPress: () => {/* IOSAlert will close */}, style: 'cancel' },
        ]}
      />
    </>
  );
}
