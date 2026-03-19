/**
 * Canvas left sidebar panel — config, controls, monitoring.
 * Reads shared state from useCanvasStore; pipeline state via props.
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { IOSCard, IOSCardContent } from '@/components/ios';
import { useCanvasStore } from '@/store/canvasStore';
import type { CreationMode } from '@/store/canvasStore';
import type { PipelineState } from '@/hooks/usePrototypePipeline';
import type { RunConfigParams } from '@/components/prototype/RunConfigForm';
import { isGuestMode } from '@/utils/guestSession';

import PlaygroundHeader from './PlaygroundHeader';
import IntentBar from './IntentBar';
import ScoutEvidenceCard from './ScoutEvidenceCard';
import RunConfigForm from './RunConfigForm';
import PipelineProgress from './PipelineProgress';
import TopologyViewer from './TopologyViewer';
import RunHistoryPanel from './RunHistoryPanel';
import CreationModeSelector from './CreationModeSelector';
import EvolutionInsightsPanel from './EvolutionInsightsPanel';
import BatchInputPanel from './BatchInputPanel';
import { formatTradition } from '@/utils/formatTradition';

export interface EditorRunParams {
  template: string;
  customNodes?: string[];
  customEdges?: [string, string][];
  nodeParams?: Record<string, Record<string, unknown>>;
}

export interface CanvasLeftPanelProps {
  pipeline: PipelineState;
  isRunning: boolean;
  isDone: boolean;
  evaluateLoading: boolean;
  lastRunParams: RunConfigParams | null;
  activeTemplate: string;
  completedStages: string[];
  stageDurations: Record<string, number>;
  // Handlers
  onIntentSubmit: (intent: string, imageFile?: File) => Promise<void>;
  onIntentChange: (text: string) => void;
  onStartRun: (params: RunConfigParams) => void;
  onFork: (params: { subject: string; tradition: string }) => void;
}

export default function CanvasLeftPanel({
  pipeline,
  isRunning,
  isDone,
  evaluateLoading,
  lastRunParams,
  activeTemplate,
  completedStages,
  stageDurations,
  onIntentSubmit,
  onIntentChange,
  onStartRun,
  onFork,
}: CanvasLeftPanelProps) {
  const {
    playgroundMode, setPlaygroundMode,
    currentSubject, currentTradition, traditionClassifying,
    creationMode, setCreationMode,
  } = useCanvasStore();

  const navigate = useNavigate();
  const guest = isGuestMode();

  const handleAuthRequired = useCallback((mode: CreationMode) => {
    const label = mode === 'guided' ? 'Guided' : 'Generate';
    toast(`Please sign in to use ${label} mode`, {
      icon: '🔒',
      duration: 3000,
    });
    navigate('/login');
  }, [navigate]);

  return (
    <>
      <div className="space-y-2">
        {/* Row 1: Title + Status badge */}
        <PlaygroundHeader status={pipeline.status} taskId={pipeline.taskId} />

        {/* Row 2: Mode tabs */}
        <div data-tour-modes className="flex gap-1.5">
          {([
            { mode: 'edit' as const, label: 'Edit' },
            { mode: 'run' as const, label: 'Run' },
            { mode: 'traditions' as const, label: 'Traditions' },
          ]).map(({ mode, label }) => (
            <button
              key={mode}
              onClick={() => setPlaygroundMode(mode)}
              className={[
                'px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors',
                playgroundMode === mode
                  ? 'border-secondary-200 dark:border-secondary-500 text-secondary-500 dark:text-secondary-400 bg-secondary-50 dark:bg-secondary-500/10'
                  : 'border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800',
              ].join(' ')}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Quick intent bar */}
      <div data-tour-intent>
        <IntentBar onSubmit={onIntentSubmit} onIntentChange={onIntentChange} disabled={isRunning || evaluateLoading} initialValue={currentSubject} />
      </div>

      {/* Tradition indicator */}
      <div data-tour-tradition>
        {currentSubject.trim() && (
          <div className="flex items-center gap-2 px-1 text-xs">
            <span className="text-gray-400 dark:text-gray-500">Tradition:</span>
            <span className="font-medium text-[#C87F4A] dark:text-[#DDA574]">
              {formatTradition(currentTradition)}
            </span>
            {traditionClassifying && (
              <span className="inline-block w-3 h-3 border-2 border-[#C87F4A]/30 border-t-[#C87F4A] rounded-full animate-spin" />
            )}
          </div>
        )}
      </div>

      {/* Creation Mode — unified Preview / Guided / Generate selector */}
      <div data-tour-hitl>
        <CreationModeSelector
          value={creationMode}
          onChange={setCreationMode}
          disabled={isRunning}
          nCandidates={lastRunParams?.n_candidates || 2}
          isGuest={guest}
          onAuthRequired={handleAuthRequired}
        />
      </div>

      {/* Detailed config (collapsible) */}
      <details className="group">
        <summary className="cursor-pointer text-xs font-medium text-gray-500 dark:text-gray-400 px-1 py-1 select-none">
          Advanced Config
        </summary>
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <RunConfigForm
              onSubmit={onStartRun}
              disabled={isRunning}
              initialValues={isDone ? lastRunParams ?? undefined : undefined}
            />
          </IOSCardContent>
        </IOSCard>
      </details>

      {pipeline.taskId && (
        <IOSCard variant="elevated" padding="sm" animate={false}>
          <IOSCardContent>
            <TopologyViewer
              template={activeTemplate}
              currentStage={pipeline.currentStage}
              status={pipeline.status}
              completedStages={completedStages}
              stageDurations={stageDurations}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {pipeline.taskId && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Progress</h3>
              <span className="text-[10px] font-mono text-gray-400">{pipeline.taskId.slice(0, 8)}</span>
            </div>
            <PipelineProgress
              currentStage={pipeline.currentStage}
              currentRound={pipeline.currentRound}
              status={pipeline.status}
              events={pipeline.events}
              subStages={pipeline.subStages}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {pipeline.evidence ? (
        <ScoutEvidenceCard evidence={pipeline.evidence} />
      ) : pipeline.currentStage === 'scout' && pipeline.status === 'running' ? (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#C87F4A]/10 dark:bg-[#C87F4A]/20 flex items-center justify-center animate-pulse">
                <span className="text-sm">🔍</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 animate-pulse">
                  Scout analyzing cultural context...
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                  Gathering references, terminology, and tradition signals
                </p>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>
      ) : null}

      {/* Run History Panel */}
      <RunHistoryPanel onFork={onFork} />

      {/* Self-evolution insights — shows how the system learns */}
      <EvolutionInsightsPanel />

      {/* M3: Batch input panel for batch_eval template in edit mode */}
      {playgroundMode === 'edit' && activeTemplate === 'batch_eval' && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <BatchInputPanel
              tradition={lastRunParams?.tradition || 'default'}
              provider={lastRunParams?.provider || 'auto'}
              template="batch_eval"
              disabled={isRunning}
            />
          </IOSCardContent>
        </IOSCard>
      )}
    </>
  );
}
