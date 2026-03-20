/**
 * Canvas right panel — critic scores, radar, queen decision, feedback.
 */

import { IOSCard, IOSCardContent, IOSButton } from '@/components/ios';
import { formatDimension } from '@/utils/formatDimension';
import type { PipelineState, ScoredCandidate } from '@/hooks/usePrototypePipeline';
import type { RunConfigParams } from './RunConfigForm';

import CriticScoreTable from './CriticScoreTable';
import CriticRadarChart from './CriticRadarChart';
import CriticRationaleCard from './CriticRationaleCard';
import FixItPlanCard from './FixItPlanCard';
import QueenDecisionPanel from './QueenDecisionPanel';
import FeedbackCollector from './FeedbackCollector';
import EvolutionBadge from './editor/EvolutionBadge';

export interface CanvasRightPanelProps {
  pipeline: PipelineState;
  isDone: boolean;
  selectedCandidateId: string | null;
  lastRunParams: RunConfigParams | null;
  onAction: (action: string, payload?: Record<string, unknown>) => void;
  onReset: () => void;
  onViewCriticDetail: (candidate: ScoredCandidate) => void;
}

export default function CanvasRightPanel({
  pipeline,
  isDone,
  selectedCandidateId,
  lastRunParams,
  onAction,
  onReset,
  onViewCriticDetail,
}: CanvasRightPanelProps) {
  return (
    <>
      {/* Critic Scores */}
      {pipeline.scoredCandidates.length > 0 && (
        <>
          <IOSCard variant="elevated" padding="md" animate={false}>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Critic L1-L5</h3>
              {pipeline.agentMode && (
                <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
                  pipeline.agentMode === 'agent_llm'
                    ? 'bg-[#5F8A50]/10 text-[#5F8A50] dark:bg-[#5F8A50]/15 dark:text-[#87A878]'
                    : pipeline.agentMode === 'agent_fallback_rules'
                    ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {pipeline.agentMode === 'agent_llm' ? 'LLM' : pipeline.agentMode === 'agent_fallback_rules' ? 'Rules Fallback' : 'Rules'}
                </span>
              )}
            </div>
            <IOSCardContent>
              {pipeline.agentMode === 'agent_fallback_rules' && (
                <div className="mb-3 rounded-lg border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/10 p-2 text-[11px] text-yellow-800 dark:text-yellow-300">
                  No LLM API key found — scores are rules-only.
                </div>
              )}

              {/* HITL Constraints */}
              {pipeline.hitlConstraints && (
                <div className="mb-3 rounded-lg border border-surface-container-high dark:border-cultural-bronze-500/20 bg-surface dark:bg-cultural-bronze-500/5 p-2">
                  <div className="text-[11px] font-semibold text-on-surface dark:text-cultural-bronze-400 mb-1.5">
                    Your Preferences
                  </div>
                  <div className="space-y-1.5 text-[11px]">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Locked: </span>
                      {pipeline.hitlConstraints.locked_dimensions.length > 0 ? (
                        pipeline.hitlConstraints.locked_dimensions.map(dim => (
                          <span key={dim} className="mr-1 px-1.5 py-0.5 rounded bg-[#5F8A50]/10 dark:bg-[#5F8A50]/15 text-[#5F8A50] dark:text-[#87A878]">
                            {formatDimension(dim)}
                          </span>
                        ))
                      ) : <span className="text-gray-400">—</span>}
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Rerun: </span>
                      {pipeline.hitlConstraints.rerun_dimensions.length > 0 ? (
                        pipeline.hitlConstraints.rerun_dimensions.map(dim => (
                          <span key={dim} className="mr-1 px-1.5 py-0.5 rounded bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 text-[#C87F4A] dark:text-[#DDA574]">
                            {formatDimension(dim)}
                          </span>
                        ))
                      ) : <span className="text-gray-400">—</span>}
                    </div>
                    <div className="text-gray-600 dark:text-gray-300">
                      {pipeline.hitlConstraints.applied_scores} scores applied to {pipeline.hitlConstraints.candidates_touched} candidates
                    </div>
                  </div>
                </div>
              )}

              {/* Radar Chart */}
              {pipeline.rounds.length > 0 && (
                <div className="mb-3">
                  <CriticRadarChart
                    rounds={pipeline.rounds}
                    dynamicWeights={pipeline.dynamicWeights}
                  />
                </div>
              )}

              {/* View Details button */}
              {pipeline.scoredCandidates.length > 0 && (
                <div className="mb-3 flex justify-end">
                  <IOSButton
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      const best = pipeline.scoredCandidates.find(sc => sc.candidate_id === pipeline.bestCandidateId)
                        ?? pipeline.scoredCandidates[0];
                      onViewCriticDetail(best);
                    }}
                  >
                    View Details
                  </IOSButton>
                </div>
              )}

              {/* Score Table */}
              <CriticScoreTable
                scoredCandidates={pipeline.scoredCandidates}
                bestCandidateId={pipeline.bestCandidateId}
                crossLayerSignals={pipeline.crossLayerSignals ?? undefined}
                evaluationSummary={pipeline.evaluationSummary}
              />
            </IOSCardContent>
          </IOSCard>

          <CriticRationaleCard scoredCandidates={pipeline.scoredCandidates} />
        </>
      )}

      {/* FixItPlan */}
      {pipeline.fixItPlan && <FixItPlanCard fixItPlan={pipeline.fixItPlan} />}

      {/* Queen Decision */}
      {(pipeline.decision || pipeline.finalDecision) && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Queen Decision</h3>
            <QueenDecisionPanel
              decision={pipeline.decision}
              finalDecision={pipeline.finalDecision}
              status={pipeline.status}
              scoredCandidates={pipeline.scoredCandidates}
              selectedCandidateId={selectedCandidateId}
              onAction={onAction}
            />
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Evolution Suggestion */}
      {isDone && pipeline.evolutionSuggestion && (
        <IOSCard variant="elevated" padding="md" animate={false}>
          <IOSCardContent>
            <div className="flex items-center gap-2 mb-2">
              <EvolutionBadge suggestion={pipeline.evolutionSuggestion} />
              <h3 className="text-sm font-semibold text-[#B8923D] dark:text-[#DDA574]">Evolution Insight</h3>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
              {pipeline.evolutionSuggestion}
            </p>
          </IOSCardContent>
        </IOSCard>
      )}

      {/* Feedback Collector */}
      {isDone && pipeline.taskId && (
        <FeedbackCollector
          sessionId={pipeline.taskId}
          evaluationId={pipeline.taskId}
          candidateId={pipeline.bestCandidateId ?? undefined}
          tradition={lastRunParams?.tradition}
          scoresSnapshot={
            pipeline.scoredCandidates.length > 0
              ? Object.fromEntries(
                  (pipeline.scoredCandidates.find(sc => sc.candidate_id === pipeline.bestCandidateId)
                    ?? pipeline.scoredCandidates[0]
                  ).dimension_scores.map(ds => [ds.dimension, ds.score])
                )
              : undefined
          }
          onCreateAnother={onReset}
        />
      )}
    </>
  );
}
