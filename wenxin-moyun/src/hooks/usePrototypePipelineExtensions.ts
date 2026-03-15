/**
 * Extension hook for skill/processing/flow events from the pipeline.
 * Supplements usePrototypePipeline with Phase 5 event handling.
 */

import { useState, useCallback } from 'react';

interface SkillEvent {
  skillName: string;
  status: 'started' | 'completed' | 'error';
  resultsCount?: number;
  durationMs?: number;
}

interface FlowEvent {
  nodeType: string;
  decision?: boolean;
  iteration?: number;
  maxIterations?: number;
}

interface PipelineExtensionState {
  skillEvents: SkillEvent[];
  flowEvents: FlowEvent[];
  processingStatus: Record<string, 'idle' | 'running' | 'done' | 'error'>;
}

const INITIAL_EXTENSION_STATE: PipelineExtensionState = {
  skillEvents: [],
  flowEvents: [],
  processingStatus: {},
};

const MAX_EVENTS = 50;

export function usePrototypePipelineExtensions() {
  const [extState, setExtState] = useState<PipelineExtensionState>(INITIAL_EXTENSION_STATE);

  const processExtensionEvent = useCallback((eventType: string, payload: Record<string, unknown>) => {
    setExtState((prev) => {
      const update = { ...prev };

      switch (eventType) {
        case 'skill_started':
          update.skillEvents = [
            ...prev.skillEvents.slice(-MAX_EVENTS + 1),
            { skillName: payload.skill_name as string, status: 'started' },
          ];
          break;

        case 'skill_completed':
          update.skillEvents = [
            ...prev.skillEvents.slice(-MAX_EVENTS + 1),
            {
              skillName: payload.skill_name as string,
              status: 'completed',
              resultsCount: payload.results_count as number,
              durationMs: payload.duration_ms as number,
            },
          ];
          break;

        case 'processing_started':
          update.processingStatus = {
            ...prev.processingStatus,
            [payload.node_name as string]: 'running',
          };
          break;

        case 'processing_completed':
          update.processingStatus = {
            ...prev.processingStatus,
            [payload.node_name as string]: 'done',
          };
          break;

        case 'flow_decision':
        case 'flow_gate_evaluation':
          update.flowEvents = [
            ...prev.flowEvents.slice(-MAX_EVENTS + 1),
            {
              nodeType: (payload.node_type as string) || 'gate',
              decision: payload.passed as boolean,
              iteration: payload.iteration as number,
              maxIterations: payload.max_iterations as number,
            },
          ];
          break;
      }

      return update;
    });
  }, []);

  const resetExtensions = useCallback(() => {
    setExtState(INITIAL_EXTENSION_STATE);
  }, []);

  return { extState, processExtensionEvent, resetExtensions };
}
