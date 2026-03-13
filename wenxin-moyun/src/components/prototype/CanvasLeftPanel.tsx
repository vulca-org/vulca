/**
 * Canvas left sidebar panel — config, controls, monitoring.
 * Reads shared state from useCanvasStore; pipeline state via props.
 */

import { IOSCard, IOSCardContent, IOSToggle } from '@/components/ios';
import { useCanvasStore } from '@/store/canvasStore';
import type { PipelineState } from '@/hooks/usePrototypePipeline';
import type { RunConfigParams } from '@/components/prototype/RunConfigForm';

import PlaygroundHeader from './PlaygroundHeader';
import IntentBar from './IntentBar';
import ScoutEvidenceCard from './ScoutEvidenceCard';
import RunConfigForm from './RunConfigForm';
import PipelineProgress from './PipelineProgress';
import TopologyViewer from './TopologyViewer';
import RunHistoryPanel from './RunHistoryPanel';
import ProviderQuickSwitch from './ProviderQuickSwitch';
import BatchInputPanel from './BatchInputPanel';

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
    enableHitl, setEnableHitl,
    currentProvider, setCurrentProvider,
  } = useCanvasStore();

  return (
    <>
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <PlaygroundHeader status={pipeline.status} taskId={pipeline.taskId} />
        </div>
        <div data-tour-modes className="flex gap-1 shrink-0">
          {([
            { mode: 'edit' as const, label: 'Edit' },
            { mode: 'run' as const, label: 'Run' },
            { mode: 'traditions' as const, label: 'Traditions' },
          ]).map(({ mode, label }) => (
            <button
              key={mode}
              onClick={() => setPlaygroundMode(mode)}
              className={[
                'px-2 py-1 text-[11px] font-medium rounded-lg border transition-colors',
                playgroundMode === mode
                  ? 'border-[#C9C2B8] dark:border-[#C87F4A] text-[#C87F4A] dark:text-[#DDA574] bg-[#FAF7F2] dark:bg-[#C87F4A]/10'
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
              {currentTradition.replace(/_/g, ' ')}
            </span>
            {traditionClassifying && (
              <span className="inline-block w-3 h-3 border-2 border-[#C87F4A]/30 border-t-[#C87F4A] rounded-full animate-spin" />
            )}
          </div>
        )}
      </div>

      {/* HITL toggle */}
      <div data-tour-hitl className="flex items-center justify-between px-1">
        <IOSToggle
          checked={enableHitl}
          onChange={setEnableHitl}
          disabled={isRunning}
          size="sm"
          color="orange"
          label="Human-in-the-Loop"
          description="Pause at each stage for human review"
        />
      </div>

      {/* Provider Quick Switch (WU-3) */}
      <ProviderQuickSwitch
        value={currentProvider}
        onChange={setCurrentProvider}
        disabled={isRunning}
        nCandidates={lastRunParams?.n_candidates || 4}
      />

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

      {/* WU-2: Run History Panel */}
      <RunHistoryPanel onFork={onFork} />

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
