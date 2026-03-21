/**
 * SSE hook for the VULCA prototype pipeline.
 *
 * Connects to GET /api/v1/prototype/runs/{taskId}/events and
 * provides reactive state for pipeline progress, candidates, scores, etc.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { API_PREFIX } from '../config/api';

export interface PipelineEvent {
  event_type: string;
  stage: string;
  round_num: number;
  payload: Record<string, unknown>;
  timestamp_ms: number;
}

export interface DraftCandidate {
  candidate_id: string;
  image_path: string;
  image_url?: string;
  prompt: string;
  seed: number;
  model_ref: string;
}

export interface AgentMetadata {
  mode: string;
  rule_score: number;
  agent_score: number;
  confidence: number;
  model_used: string;
  tool_calls_made: number;
  llm_calls_made: number;
  cost_usd: number;
  latency_ms: number;
  fallback_used: boolean;
}

export interface DimensionScore {
  dimension: string;
  score: number;
  rationale: string;
  summary?: string;
  agent_metadata?: AgentMetadata;
}

export interface ScoredCandidate {
  candidate_id: string;
  dimension_scores: DimensionScore[];
  weighted_total: number;
  gate_passed: boolean;
  risk_tags: string[];
}

export interface QueenDecision {
  action: string;
  reason: string;
  rerun_dimensions: string[];
  preserve_dimensions: string[];
  round: number;
  budget_state: BudgetState | null;
}

export interface BudgetState {
  rounds_used: number;
  max_rounds: number;
  total_cost_usd: number;
  candidates_generated: number;
}

export interface CrossLayerSignal {
  source_layer: string;
  target_layer: string;
  signal_type: string;
  message: string;
  strength: number;
}

export interface FixItPlanItem {
  target_layer: string;
  issue: string;
  prompt_delta: string;
  mask_region_hint: string;
  reference_suggestion: string;
  priority: number;
}

export interface FixItPlan {
  overall_strategy: string;
  items: FixItPlanItem[];
  estimated_improvement: number;
  source_scores: Record<string, number>;
}

export interface RoundData {
  round: number;
  candidates: DraftCandidate[];
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  weightedTotal: number | null;
  decision: QueenDecision | null;
  dynamicWeights: Record<string, number> | null;
  crossLayerSignals: CrossLayerSignal[] | null;
  fixItPlan: FixItPlan | null;
}

export interface HitlConstraints {
  locked_dimensions: string[];
  rerun_dimensions: string[];
  preserved_dimensions: string[];
  applied_scores: number;
  candidates_touched: number;
}

export interface HitlWaitInfo {
  /** Which stage is waiting for human input: 'scout' | 'draft' | 'critic' | 'queen' */
  stage: string;
  /** Optional payload from the backend (queen_decision, plan_state, etc.) */
  payload: Record<string, unknown>;
}

export interface PipelineState {
  taskId: string | null;
  status: 'idle' | 'running' | 'waiting_human' | 'completed' | 'failed';
  currentStage: string;
  currentRound: number;
  events: PipelineEvent[];

  // Scout
  evidence: Record<string, unknown> | null;

  // Draft
  candidates: DraftCandidate[];

  // Critic
  scoredCandidates: ScoredCandidate[];
  bestCandidateId: string | null;
  hitlConstraints: HitlConstraints | null;
  dynamicWeights: Record<string, number> | null;
  crossLayerSignals: CrossLayerSignal[] | null;
  fixItPlan: FixItPlan | null;
  agentMode: string | null;  // 'rule_only' | 'agent_llm' | 'agent_fallback_rules'
  evaluationSummary: string | null;

  // Queen
  decision: QueenDecision | null;

  // Round-by-round history
  rounds: RoundData[];

  // HITL — multi-stage wait info
  hitlWaitInfo: HitlWaitInfo | null;

  // Sub-stages (e.g. draft sub-steps)
  subStages: SubStageInfo[];

  // Report
  reportOutput: Record<string, unknown> | null;

  // Final
  finalDecision: string | null;
  totalCostUsd: number;
  totalRounds: number;
  totalLatencyMs: number;
  error: string | null;

  // Evolution
  evolutionSuggestion: string | null;

  // Best image URL (resolved from status API after completion)
  bestImageUrl: string | null;
}

const INITIAL_STATE: PipelineState = {
  taskId: null,
  status: 'idle',
  currentStage: '',
  currentRound: 0,
  events: [],
  evidence: null,
  candidates: [],
  scoredCandidates: [],
  bestCandidateId: null,
  hitlConstraints: null,
  dynamicWeights: null,
  crossLayerSignals: null,
  fixItPlan: null,
  agentMode: null,
  evaluationSummary: null,
  decision: null,
  rounds: [],
  hitlWaitInfo: null,
  subStages: [],
  reportOutput: null,
  finalDecision: null,
  totalCostUsd: 0,
  totalRounds: 0,
  totalLatencyMs: 0,
  error: null,
  evolutionSuggestion: null,
  bestImageUrl: null,
};

export interface SubStageInfo {
  name: string;
  displayName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  durationMs?: number;
  /** Text/JSON content produced by this sub-stage */
  data?: string;
  /** Path to visual artifact (NB2-rendered image) */
  imagePath?: string;
  /** Artifact type: "text" | "json" | "image" */
  artifactType?: string;
}

export interface CreateRunParams {
  subject: string;
  tradition: string;
  intent?: string;
  provider?: string;
  n_candidates?: number;
  max_rounds?: number;
  enable_hitl?: boolean;
  enable_agent_critic?: boolean;
  enable_parallel_critic?: boolean;
  use_graph?: boolean;
  template?: string;
  media_type?: string;
  // M3: custom topology
  custom_nodes?: string[];
  custom_edges?: [string, string][];
  node_params?: Record<string, Record<string, unknown>>;
  reference_image_base64?: string;
}

export function usePrototypePipeline() {
  const [state, setState] = useState<PipelineState>(INITIAL_STATE);
  const eventSourceRef = useRef<EventSource | null>(null);

  const updateState = useCallback((partial: Partial<PipelineState>) => {
    setState(prev => ({ ...prev, ...partial }));
  }, []);

  const processEvent = useCallback((event: PipelineEvent) => {
    const { event_type, stage, round_num, payload } = event;

    setState(prev => {
      const newEvents = [...prev.events, event];
      const update: Partial<PipelineState> = { events: newEvents };

      switch (event_type) {
        case 'stage_started':
          update.currentStage = stage;
          update.currentRound = round_num;
          update.status = 'running';
          break;

        case 'stage_completed':
          if (stage === 'scout') {
            update.evidence = (payload.evidence as Record<string, unknown>) || null;
          } else if (stage === 'generate' || stage === 'draft') {
            // WU-6: Handle both single-candidate and array formats
            const candidatesRaw = payload.candidates as DraftCandidate[] | undefined;
            const genCandidates: DraftCandidate[] = candidatesRaw ? [...candidatesRaw] : [];

            if (!candidatesRaw && payload.candidate_id) {
              genCandidates.push({
                candidate_id: payload.candidate_id as string,
                image_url: (payload.image_url as string) || '',
                image_path: '',
                prompt: '',
                seed: 0,
                model_ref: '',
              });
            }

            if (genCandidates.length > 0) {
              update.candidates = genCandidates;
            }

            // Set bestImageUrl immediately for real-time display
            const imgUrl = (payload.image_url as string) || '';
            const imgB64 = (payload.image_b64 as string) || '';
            const imgMime = (payload.image_mime as string) || 'image/png';

            if (imgUrl && !imgUrl.startsWith('mock://') && !imgUrl.startsWith('gemini://')) {
              update.bestImageUrl = imgUrl;
            } else if (imgB64) {
              update.bestImageUrl = `data:${imgMime};base64,${imgB64}`;
            }
          } else if (stage === 'draft_refine') {
            // Local inpainting produced refined candidates — update gallery
            update.candidates = (payload.candidates as DraftCandidate[]) || [];
            update.currentStage = 'draft_refine';
          } else if (stage === 'report') {
            const reportOut = payload.report_output as Record<string, unknown> | undefined;
            if (reportOut) {
              update.reportOutput = reportOut;
            }
          } else if (stage === 'critic' || stage === 'evaluate') {
            // Support both old format (critique.scored_candidates) and
            // vulca engine format (flat scores + weighted_total)
            const critique = payload.critique as Record<string, unknown> | undefined;
            if (critique) {
              update.scoredCandidates = (critique.scored_candidates as ScoredCandidate[]) || [];
              update.bestCandidateId = (critique.best_candidate_id as string) || null;
              update.evaluationSummary = (critique.evaluation_summary as string) || null;
            }
            // vulca engine: flat {scores: {L1: 0.75, ...}, weighted_total: 0.754}
            const scores = payload.scores as Record<string, number> | undefined;
            const wt = payload.weighted_total as number | undefined;
            if (scores && typeof wt === 'number') {
              // Map L1-L5 to full dimension names used by frontend components
              const L_TO_DIM: Record<string, string> = {
                L1: 'visual_perception',
                L2: 'technical_analysis',
                L3: 'cultural_context',
                L4: 'critical_interpretation',
                L5: 'philosophical_aesthetic',
              };
              const rationales = payload.rationales as Record<string, string> | undefined;
              const dimScores: DimensionScore[] = Object.entries(scores).map(([dim, score]) => ({
                dimension: L_TO_DIM[dim] || dim,
                score: score as number,
                rationale: rationales?.[`${dim}_rationale`] || '',
              }));
              const candidateId = (payload.candidate_id as string) || prev.bestCandidateId || 'mock';
              update.scoredCandidates = [{
                candidate_id: candidateId,
                dimension_scores: dimScores,
                weighted_total: wt,
                gate_passed: true,
                risk_tags: [],
              }];
              update.bestCandidateId = candidateId;
            }
            const rawConstraints = payload.hitl_constraints as Partial<HitlConstraints> | undefined;
            if (rawConstraints && typeof rawConstraints === 'object' && Object.keys(rawConstraints).length > 0) {
              update.hitlConstraints = {
                locked_dimensions: Array.isArray(rawConstraints.locked_dimensions) ? rawConstraints.locked_dimensions : [],
                rerun_dimensions: Array.isArray(rawConstraints.rerun_dimensions) ? rawConstraints.rerun_dimensions : [],
                preserved_dimensions: Array.isArray(rawConstraints.preserved_dimensions) ? rawConstraints.preserved_dimensions : [],
                applied_scores: typeof rawConstraints.applied_scores === 'number' ? rawConstraints.applied_scores : 0,
                candidates_touched: typeof rawConstraints.candidates_touched === 'number' ? rawConstraints.candidates_touched : 0,
              };
            } else {
              update.hitlConstraints = null;
            }
            // Phase 2 enhanced fields
            update.dynamicWeights = (payload.dynamic_weights as Record<string, number>) || null;
            update.crossLayerSignals = (payload.cross_layer_signals as CrossLayerSignal[]) || null;
            update.fixItPlan = (payload.fix_it_plan as FixItPlan) || null;
            update.agentMode = (payload.agent_mode as string) || null;
          }
          break;

        case 'substage_started': {
          const subName = (payload.substage as string) || (payload.sub_stage_name as string) || (payload.name as string) || '';
          const subDisplay = (payload.display_name as string) || subName;
          // Mark any previously running sub-stage as completed (if backend didn't send explicit complete)
          const updatedSubs = prev.subStages.map(s =>
            s.status === 'running' ? { ...s, status: 'completed' as const } : s
          );
          update.subStages = [
            ...updatedSubs,
            { name: subName, displayName: subDisplay, status: 'running' },
          ];
          break;
        }

        case 'substage_completed': {
          const completedName = (payload.substage as string) || (payload.sub_stage_name as string) || (payload.name as string) || '';
          const dur = (payload.duration_ms as number) || undefined;
          // Extract artifact data if present
          const artifactData = (payload.data as string) || undefined;
          const artifactImagePath = (payload.image_path as string) || undefined;
          const artifactType = (payload.artifact_type as string) || undefined;
          update.subStages = prev.subStages.map(s =>
            s.name === completedName
              ? {
                  ...s,
                  status: 'completed' as const,
                  durationMs: dur ?? s.durationMs,
                  data: artifactData ?? s.data,
                  imagePath: artifactImagePath ?? s.imagePath,
                  artifactType: artifactType ?? s.artifactType,
                }
              : s
          );
          break;
        }

        case 'decision_made': {
          const budgetRaw = payload.budget_state as BudgetState | undefined;
          // Support both old format (action) and vulca engine format (decision)
          const decisionAction = (payload.action as string) || (payload.decision as string) || 'unknown';
          const newDecision: QueenDecision = {
            action: decisionAction,
            reason: (payload.reason as string) || '',
            rerun_dimensions: (payload.rerun_dimensions as string[]) || [],
            preserve_dimensions: (payload.preserve_dimensions as string[]) || [],
            round: (payload.round as number) || round_num,
            budget_state: budgetRaw || null,
          };
          update.decision = newDecision;

          // Build round snapshot
          // vulca engine sends weighted_total directly in decision_made
          const decisionWT = payload.weighted_total as number | undefined;
          const bestTotal = decisionWT != null
            ? decisionWT
            : prev.scoredCandidates.length > 0
              ? Math.max(...prev.scoredCandidates.map(sc => sc.weighted_total))
              : null;
          const roundSnapshot: RoundData = {
            round: round_num,
            candidates: [...prev.candidates],
            scoredCandidates: [...prev.scoredCandidates],
            bestCandidateId: prev.bestCandidateId,
            weightedTotal: bestTotal,
            decision: newDecision,
            dynamicWeights: prev.dynamicWeights,
            crossLayerSignals: prev.crossLayerSignals,
            fixItPlan: prev.fixItPlan,
          };
          update.rounds = [...prev.rounds, roundSnapshot];
          break;
        }

        case 'human_required':
          update.status = 'waiting_human';
          update.hitlWaitInfo = {
            stage: stage || prev.currentStage || 'queen',
            payload: payload as Record<string, unknown>,
          };
          break;

        case 'human_received':
          update.status = 'running';
          update.hitlWaitInfo = null;
          break;

        case 'pipeline_completed':
          update.status = 'completed';
          update.finalDecision = payload.final_decision as string;
          update.totalCostUsd = (payload.total_cost_usd as number) || 0;
          update.totalRounds = (payload.total_rounds as number) || 0;
          update.totalLatencyMs = (payload.total_latency_ms as number) || 0;
          break;

        case 'session_digest':
          if (payload.evolution_suggestion) {
            update.evolutionSuggestion = payload.evolution_suggestion as string;
          }
          break;

        case 'pipeline_failed':
          update.status = 'failed';
          update.error = (payload.error as string) || 'Unknown error';
          break;

        // Phase 5: skill/processing/flow events
        case 'skill_started':
        case 'skill_completed':
        case 'processing_started':
        case 'processing_completed':
        case 'flow_gate_evaluation':
          // Handled by PipelineEditor via stageStatuses — no global state change needed
          break;
      }

      return { ...prev, ...update };
    });
  }, []);

  const startRun = useCallback(async (params: CreateRunParams) => {
    // Close any existing SSE connection before starting a new run
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    // Reset state
    setState({ ...INITIAL_STATE, status: 'running' });

    try {
      const res = await fetch(`${API_PREFIX}/prototype/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        const detail = err.detail || 'Unknown error';
        let errorMsg: string;

        if (res.status === 400 && typeof detail === 'string' && detail.includes('API_KEY')) {
          errorMsg = `Provider configuration error: ${detail}. Switch to "Preview" mode or configure the API key on the server.`;
        } else if (res.status === 429) {
          errorMsg = 'Daily run limit reached. Please try again tomorrow.';
        } else if (res.status === 422) {
          const fields = Array.isArray(detail)
            ? detail.map((d: { loc?: string[]; msg?: string }) => `${d.loc?.join('.')} — ${d.msg}`).join('; ')
            : String(detail);
          errorMsg = `Invalid request: ${fields}`;
        } else if (res.status >= 500) {
          errorMsg = `Server error (${res.status}). Please try again later.`;
        } else {
          errorMsg = `Request failed (${res.status}): ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`;
        }

        updateState({ status: 'failed', error: errorMsg });
        return;
      }

      const data = await res.json();
      const taskId = data.task_id;
      updateState({ taskId });

      // Connect SSE
      const es = new EventSource(`${API_PREFIX}/prototype/runs/${taskId}/events`);
      eventSourceRef.current = es;

      es.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data) as PipelineEvent;
          processEvent(event);

          if (event.event_type === 'pipeline_completed' || event.event_type === 'pipeline_failed' || event.event_type === 'timeout') {
            es.close();
            eventSourceRef.current = null;

            if (event.event_type === 'pipeline_failed') {
              const errMsg = (event.payload as Record<string, unknown>)?.error;
              setState(prev => ({ ...prev, status: 'failed', error: `Pipeline failed: ${errMsg || 'unknown error'}` }));
            } else if (event.event_type === 'timeout') {
              setState(prev => ({ ...prev, status: 'failed', error: 'Pipeline timed out. The server stopped streaming events.' }));
            }

            // Fetch final status to get real image URL (static path, not gemini://)
            if (event.event_type === 'pipeline_completed') {
              fetch(`${API_PREFIX}/prototype/runs/${taskId}`)
                .then(r => r.ok ? r.json() : null)
                .then(status => {
                  if (status?.best_image_url) {
                    setState(prev => ({ ...prev, bestImageUrl: status.best_image_url }));
                  }
                })
                .catch(() => { /* non-critical */ });
            }
          }
        } catch {
          // Skip malformed events
        }
      };

      es.onerror = () => {
        es.close();
        eventSourceRef.current = null;
        // Only set failed if not already completed
        setState(prev => {
          if (prev.status === 'running') {
            return { ...prev, status: 'failed', error: 'Connection to server lost. The pipeline may still be running — check status later.' };
          }
          return prev;
        });
      };
    } catch (err) {
      const msg = err instanceof TypeError
        ? 'Cannot reach server. Please check that the backend is running.'
        : String(err);
      updateState({ status: 'failed', error: msg });
    }
  }, [updateState, processEvent]);

  const reset = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setState(INITIAL_STATE);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  /** Connect to an existing run's SSE stream without creating a new one.
   *  Used by instruct flow where the backend already created the run. */
  const connectToRun = useCallback((taskId: string) => {
    // Close existing
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setState({ ...INITIAL_STATE, status: 'running', taskId });

    const es = new EventSource(`${API_PREFIX}/prototype/runs/${taskId}/events`);
    eventSourceRef.current = es;

    es.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as PipelineEvent;
        processEvent(event);

        if (event.event_type === 'pipeline_completed' || event.event_type === 'pipeline_failed' || event.event_type === 'timeout') {
          es.close();
          eventSourceRef.current = null;

          if (event.event_type === 'pipeline_failed') {
            const errMsg = (event.payload as Record<string, unknown>)?.error;
            setState(prev => ({ ...prev, status: 'failed', error: `Pipeline failed: ${errMsg || 'unknown error'}` }));
          } else if (event.event_type === 'timeout') {
            setState(prev => ({ ...prev, status: 'failed', error: 'Pipeline timed out.' }));
          }

          if (event.event_type === 'pipeline_completed') {
            fetch(`${API_PREFIX}/prototype/runs/${taskId}`)
              .then(r => r.ok ? r.json() : null)
              .then(status => {
                if (status?.best_image_url) {
                  setState(prev => ({ ...prev, bestImageUrl: status.best_image_url }));
                }
              })
              .catch(() => {});
          }
        }
      } catch { /* skip malformed */ }
    };

    es.onerror = () => {
      es.close();
      eventSourceRef.current = null;
      setState(prev => prev.status === 'running' ? { ...prev, status: 'failed', error: 'Connection lost.' } : prev);
    };
  }, [processEvent]);

  const submitAction = useCallback(async (
    action: string,
    options?: { locked_dimensions?: string[]; rerun_dimensions?: string[]; candidate_id?: string; reason?: string },
  ) => {
    if (!state.taskId) return;

    try {
      const res = await fetch(`${API_PREFIX}/prototype/runs/${state.taskId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...options }),
      });

      if (res.ok) {
        const data = await res.json();
        // WU-5: Rerun creates a new pipeline — connect to its SSE stream
        if (data.new_task_id) {
          connectToRun(data.new_task_id);
        }
      } else {
        console.error('Failed to submit action:', await res.text());
      }
    } catch (err) {
      console.error('Submit action error:', err);
    }
  }, [state.taskId, connectToRun]);

  return {
    state,
    startRun,
    connectToRun,
    submitAction,
    reset,
  };
}
