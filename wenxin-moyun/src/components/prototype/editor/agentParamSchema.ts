/**
 * Schema-driven parameter definitions for each agent node.
 * NodeParamPanel iterates these to render controls dynamically.
 */

import type { AgentNodeId } from './types';

export interface ParamDef {
  id: string;
  label: string;
  type: 'number' | 'select' | 'toggle' | 'slider';
  default: unknown;
  min?: number;
  max?: number;
  step?: number;
  options?: { label: string; value: string }[];
  /** Maps to the corresponding field in CreateRunRequest / node_params */
  requestField?: string;
  description?: string;
}

export const AGENT_PARAM_SCHEMA: Record<AgentNodeId, ParamDef[]> = {
  scout: [
    {
      id: 'max_evidence',
      label: 'Max Evidence',
      type: 'number',
      default: 5,
      min: 1,
      max: 20,
      description: 'Maximum evidence items to retrieve',
    },
    {
      id: 'cache_ttl',
      label: 'Cache TTL (s)',
      type: 'number',
      default: 300,
      min: 0,
      max: 3600,
      step: 60,
      description: 'Evidence cache duration in seconds',
    },
  ],

  router: [],

  draft: [
    {
      id: 'n_candidates',
      label: 'Candidates',
      type: 'slider',
      default: 4,
      min: 1,
      max: 8,
      step: 1,
      requestField: 'n_candidates',
      description: 'Number of images to generate per round',
    },
    {
      id: 'seed_base',
      label: 'Seed Base',
      type: 'number',
      default: 42,
      min: 0,
      max: 99999,
      description: 'Base seed for reproducibility',
    },
    {
      id: 'enhance_prompt',
      label: 'Enhance Prompt',
      type: 'toggle',
      default: true,
      description: 'Use PromptEnhancer before generation',
    },
  ],

  critic: [
    {
      id: 'enable_agent_critic',
      label: 'LLM Scoring',
      type: 'toggle',
      default: false,
      requestField: 'enable_agent_critic',
      description: 'Use VLM-based scoring instead of rules',
    },
    {
      id: 'w_l1',
      label: 'L1 Weight',
      type: 'slider',
      default: 0.20,
      min: 0,
      max: 1,
      step: 0.05,
      description: 'Technique & Composition',
    },
    {
      id: 'w_l2',
      label: 'L2 Weight',
      type: 'slider',
      default: 0.20,
      min: 0,
      max: 1,
      step: 0.05,
      description: 'Aesthetic Quality',
    },
    {
      id: 'w_l3',
      label: 'L3 Weight',
      type: 'slider',
      default: 0.20,
      min: 0,
      max: 1,
      step: 0.05,
      description: 'Cultural Authenticity',
    },
    {
      id: 'w_l4',
      label: 'L4 Weight',
      type: 'slider',
      default: 0.20,
      min: 0,
      max: 1,
      step: 0.05,
      description: 'Prompt Fidelity',
    },
    {
      id: 'w_l5',
      label: 'L5 Weight',
      type: 'slider',
      default: 0.20,
      min: 0,
      max: 1,
      step: 0.05,
      description: 'Cultural Depth',
    },
  ],

  queen: [
    {
      id: 'max_rounds',
      label: 'Max Rounds',
      type: 'slider',
      default: 3,
      min: 1,
      max: 5,
      step: 1,
      requestField: 'max_rounds',
      description: 'Maximum Queen rerun rounds',
    },
    {
      id: 'accept_threshold',
      label: 'Accept Threshold',
      type: 'slider',
      default: 0.85,
      min: 0.5,
      max: 1.0,
      step: 0.05,
      description: 'Score threshold for auto-accept',
    },
    {
      id: 'enable_hitl',
      label: 'HITL Review',
      type: 'toggle',
      default: false,
      requestField: 'enable_hitl',
      description: 'Pause for human review at Queen stage',
    },
  ],

  archivist: [],
};
