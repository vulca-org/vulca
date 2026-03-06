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
  | 'archivist'
  | 'upload'
  | 'identify'
  | 'report';

export const ALL_AGENT_IDS: AgentNodeId[] = [
  'scout', 'router', 'draft', 'critic', 'queen', 'archivist',
  'upload', 'identify', 'report',
];

/** Report output embedded in ReportNode data */
export interface ReportOutput {
  weighted_total: number;
  summary: string;
  dimension_scores: { dimension: string; label: string; score: number }[];
  tradition: string;
  risk_flags: string[];
}

export interface AgentNodeData {
  [key: string]: unknown;
  agentId: AgentNodeId;
  label: string;
  icon: string;
  description: string;
  params: Record<string, unknown>;
  validationError?: string;
  status?: 'idle' | 'running' | 'done' | 'error' | 'skipped';
  duration?: number;
  reportOutput?: ReportOutput;
}

/** StickyNote data — decorative canvas annotation */
export interface StickyNoteData {
  [key: string]: unknown;
  text: string;
  color: 'yellow' | 'blue' | 'pink' | 'green';
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
  upload:    { label: 'Upload',    icon: '\uD83D\uDCE4', description: 'Image input' },
  identify:  { label: 'Identify',  icon: '\uD83D\uDD0E', description: 'Tradition detection' },
  report:    { label: 'Report',    icon: '\uD83D\uDCCA', description: 'Result summary' },
};

/** Fixed initial positions for nodes (horizontal layout) */
export const INITIAL_POSITIONS: Record<AgentNodeId, { x: number; y: number }> = {
  scout:     { x: 0,    y: 0 },
  router:    { x: 220,  y: 0 },
  draft:     { x: 440,  y: 0 },
  critic:    { x: 660,  y: 0 },
  queen:     { x: 880,  y: 0 },
  archivist: { x: 1100, y: 0 },
  upload:    { x: -220, y: 0 },
  identify:  { x: -110, y: 120 },
  report:    { x: 1320, y: 0 },
};
