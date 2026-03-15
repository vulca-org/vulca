/**
 * DataType color mapping — Art Professional palette.
 * Frontend mirror of backend DataType enum with socket colors.
 */

export type DataType =
  | 'pipeline_input'
  | 'evidence'
  | 'evidence_pack'
  | 'draft_candidates'
  | 'critique'
  | 'plan_state'
  | 'queen_decision'
  | 'pipeline_output'
  | 'archive'
  | 'skill_results'
  | 'image'
  | 'text'
  | 'sketch'
  | 'mask'
  | 'audio'
  | 'video'
  | 'model_3d'
  | 'config'
  | 'style'
  | 'scores'
  | 'decision';

export const SOCKET_COLORS: Record<DataType, string> = {
  pipeline_input: '#334155',
  evidence: '#6B7B8D',
  evidence_pack: '#6B7B8D',
  draft_candidates: '#C87F4A',
  critique: '#B8923D',
  plan_state: '#8B7355',
  queen_decision: '#9B6A8C',
  pipeline_output: '#334155',
  archive: '#5F8A50',
  skill_results: '#5F8A50',
  image: '#C87F4A',
  text: '#6B7B8D',
  sketch: '#B8923D',
  mask: '#8B7355',
  audio: '#9B6A8C',
  video: '#C65D4D',
  model_3d: '#6B8E7A',
  config: '#334155',
  style: '#DDA574',
  scores: '#C65D4D',
  decision: '#9B6A8C',
};

export function getSocketColor(dataType: DataType | string): string {
  return SOCKET_COLORS[dataType as DataType] ?? '#6B7B8D';
}

/** DataType display labels */
export const DATA_TYPE_LABELS: Record<DataType, string> = {
  pipeline_input: 'Pipeline Input',
  evidence: 'Evidence',
  evidence_pack: 'Evidence Pack',
  draft_candidates: 'Draft Candidates',
  critique: 'Critique',
  plan_state: 'Plan State',
  queen_decision: 'Queen Decision',
  pipeline_output: 'Pipeline Output',
  archive: 'Archive',
  skill_results: 'Skill Results',
  image: 'Image',
  text: 'Text',
  sketch: 'Sketch',
  mask: 'Mask',
  audio: 'Audio',
  video: 'Video',
  model_3d: '3D Model',
  config: 'Config',
  style: 'Style',
  scores: 'Scores',
  decision: 'Decision',
};
