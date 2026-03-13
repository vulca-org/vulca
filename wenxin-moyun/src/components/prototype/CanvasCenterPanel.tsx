/**
 * Canvas center panel — candidates, timeline, results.
 */

import { IOSCard, IOSCardContent, IOSButton } from '@/components/ios';
import type { PipelineState } from '@/hooks/usePrototypePipeline';

import CandidateGallery from './CandidateGallery';
import RoundTimeline from './RoundTimeline';
import FinalResultPanel from './FinalResultPanel';

export interface CanvasCenterPanelProps {
  pipeline: PipelineState;
  isDone: boolean;
  evaluateResult: Record<string, unknown> | null;
  selectedCandidateId: string | null;
  onSelectCandidate: (id: string | null) => void;
  onClearEvaluate: () => void;
  onReset: () => void;
}

export default function CanvasCenterPanel({
  pipeline,
  isDone,
  evaluateResult,
  selectedCandidateId,
  onSelectCandidate,
  onClearEvaluate,
  onReset,
}: CanvasCenterPanelProps) {
  return (
    <>
      {/* Evaluate result (from IntentBar image upload) */}
      {evaluateResult && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Evaluation Result</h3>
            <div className="space-y-2 text-sm">
              {evaluateResult.weighted_total != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Weighted Total</span>
                  <span className="font-mono font-semibold">{Number(evaluateResult.weighted_total).toFixed(2)}</span>
                </div>
              )}
              {evaluateResult.summary ? (
                <p className="text-gray-600 dark:text-gray-400 text-xs">{String(evaluateResult.summary)}</p>
              ) : null}
              {evaluateResult.scores && typeof evaluateResult.scores === 'object' ? (
                <div className="grid grid-cols-2 gap-1 text-xs">
                  {Object.entries(evaluateResult.scores as Record<string, number>).map(([dim, score]) => (
                    <div key={dim} className="flex justify-between px-2 py-1 bg-gray-50 dark:bg-gray-800 rounded">
                      <span className="text-gray-500">{dim.replace(/_/g, ' ')}</span>
                      <span className="font-mono">{Number(score).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              ) : null}
              {evaluateResult.risk_level ? (
                <div className="flex justify-between">
                  <span className="text-gray-500">Risk</span>
                  <span>{String(evaluateResult.risk_level)}</span>
                </div>
              ) : null}
              <IOSButton variant="secondary" size="sm" onClick={onClearEvaluate}>
                Clear
              </IOSButton>
            </div>
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Candidate Gallery */}
      {pipeline.candidates.length > 0 ? (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Candidates
              <span className="ml-2 text-xs font-normal text-gray-500">R{pipeline.currentRound}</span>
            </h3>
            {pipeline.status === 'waiting_human' && (
              <span className="text-[11px] text-[#C87F4A] dark:text-[#DDA574]">Click to select</span>
            )}
          </div>
          <IOSCardContent>
            <CandidateGallery
              candidates={pipeline.candidates}
              bestCandidateId={pipeline.bestCandidateId}
              selectedCandidateId={selectedCandidateId}
              onSelect={onSelectCandidate}
              scoredCandidates={pipeline.scoredCandidates}
              rounds={pipeline.rounds}
            />
          </IOSCardContent>
        </IOSCard>
      ) : pipeline.taskId && pipeline.currentStage === 'draft' ? (
        /* Skeleton loading state during Draft generation */
        <IOSCard variant="elevated" padding="md" animate={false}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Candidates
              <span className="ml-2 text-xs font-normal text-gray-500">R{pipeline.currentRound}</span>
            </h3>
          </div>
          <IOSCardContent>
            <div className="grid grid-cols-2 gap-3">
              {[0, 1, 2, 3].map(i => (
                <div key={i} className="animate-pulse">
                  <div className="aspect-square rounded-xl bg-stone-200 dark:bg-stone-700" />
                  <div className="mt-2 h-3 w-3/4 rounded bg-stone-200 dark:bg-stone-700" />
                </div>
              ))}
            </div>
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-4">
              Generating candidates...
            </p>
          </IOSCardContent>
        </IOSCard>
      ) : (
        /* Empty state */
        !pipeline.taskId && (
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
      {(pipeline.rounds.length > 0 || (pipeline.status === 'running' && pipeline.currentRound > 0)) && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <RoundTimeline
              rounds={pipeline.rounds}
              currentRound={pipeline.currentRound}
              status={pipeline.status}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Final Results */}
      {pipeline.status === 'completed' && pipeline.scoredCandidates.length > 0 && (
        <FinalResultPanel
          candidates={pipeline.candidates}
          scoredCandidates={pipeline.scoredCandidates}
          bestCandidateId={pipeline.bestCandidateId}
          finalDecision={pipeline.finalDecision}
          totalRounds={pipeline.totalRounds}
          totalLatencyMs={pipeline.totalLatencyMs}
          totalCostUsd={pipeline.totalCostUsd}
          rounds={pipeline.rounds}
          onNewRun={onReset}
        />
      )}

      {/* Fallback: completed but no scores, or failed */}
      {isDone && (pipeline.status === 'failed' || (pipeline.status === 'completed' && pipeline.scoredCandidates.length === 0)) && (
        <div className={`rounded-xl p-4 ${
          pipeline.status === 'completed'
            ? 'bg-[#5F8A50]/5 dark:bg-[#5F8A50]/10 border border-[#5F8A50]/20 dark:border-[#4A7040]'
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold">
              {pipeline.status === 'completed' ? 'Pipeline Complete' : 'Pipeline Failed'}
            </h3>
            <div className="text-right text-xs text-gray-600 dark:text-gray-400 space-y-0.5">
              {pipeline.totalRounds > 0 && <div>Rounds: {pipeline.totalRounds}</div>}
              {pipeline.totalLatencyMs > 0 && <div>{(pipeline.totalLatencyMs / 1000).toFixed(1)}s</div>}
              {pipeline.totalCostUsd > 0 && <div>${pipeline.totalCostUsd.toFixed(4)}</div>}
            </div>
          </div>
          {pipeline.error && (
            <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/30 rounded-lg text-xs text-red-700 dark:text-red-300">
              {pipeline.error}
            </div>
          )}
          <div className="flex gap-2 mt-3">
            <IOSButton variant="secondary" size="sm" onClick={onReset}>New Run</IOSButton>
            {pipeline.status === 'failed' && (
              <IOSButton variant="primary" size="sm" onClick={onReset}>Retry</IOSButton>
            )}
          </div>
        </div>
      )}
    </>
  );
}
