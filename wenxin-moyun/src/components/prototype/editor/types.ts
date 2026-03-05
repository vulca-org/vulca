/**
 * M3 Pipeline Editor — type definitions
 * Shared between PipelineEditor, AgentNode, NodeParamPanel, etc.
 */

export type AgentNodeId =
  | 'scout'
  | 'router'
  | 'draft'
  | 'critic'
  | 'queen'
  | 'archivist';

export const ALL_AGENT_IDS: AgentNodeId[] = [
  'scout', 'router', 'draft', 'critic', 'queen', 'archivist',
];

export interface AgentNodeData {
  agentId: AgentNodeId;
  label: string;
  icon: string;
  description: string;
  params: Record<string, unknown>;
  validationError?: string;
}

/** Serialisable topology state (for localStorage & API) */
export interface TopologyState {
  nodes: AgentNodeId[];
  edges: [string, string][];
  enableLoop: boolean;
}

/** localStorage saved template */
export interface SavedTemplate {
  id: string;
  name: string;
  createdAt: number;
  topology: TopologyState;
  nodeParams: Record<string, Record<string, unknown>>;
}

/** Agent metadata mirroring backend /agents response */
export const AGENT_META: Record<AgentNodeId, { label: string; icon: string; description: string }> = {
  scout:     { label: 'Scout',     icon: '\uD83D\uDD0D', description: 'Evidence retrieval' },
  router:    { label: 'Router',    icon: '\uD83D\uDEA6', description: 'Cultural routing' },
  draft:     { label: 'Draft',     icon: '\uD83C\uDFA8', description: 'Image generation' },
  critic:    { label: 'Critic',    icon: '\uD83D\uDCCA', description: 'Multi-dim scoring' },
  queen:     { label: 'Queen',     icon: '\uD83D\uDC51', description: 'Accept / rerun gate' },
  archivist: { label: 'Archivist', icon: '\uD83D\uDCBE', description: 'Result archival' },
};

/** Fixed initial positions for the 6 nodes (horizontal layout) */
export const INITIAL_POSITIONS: Record<AgentNodeId, { x: number; y: number }> = {
  scout:     { x: 0,    y: 0 },
  router:    { x: 220,  y: 0 },
  draft:     { x: 440,  y: 0 },
  critic:    { x: 660,  y: 0 },
  queen:     { x: 880,  y: 0 },
  archivist: { x: 1100, y: 0 },
};
