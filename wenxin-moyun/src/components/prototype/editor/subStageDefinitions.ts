/**
 * Static definitions for Draft 6 sub-stages + Critic 5 L1-L5 sub-stages.
 */

export interface SubStageDef {
  id: string;
  label: string;
  icon: string;
  parentAgent: 'draft' | 'critic';
  order: number;
}

export const DRAFT_SUB_STAGES: SubStageDef[] = [
  { id: 'mood_palette', label: 'Mood Palette', icon: '🎨', parentAgent: 'draft', order: 0 },
  { id: 'composition_sketch', label: 'Composition', icon: '📐', parentAgent: 'draft', order: 1 },
  { id: 'element_studies', label: 'Elements', icon: '🔍', parentAgent: 'draft', order: 2 },
  { id: 'style_reference', label: 'Style Ref', icon: '🖌️', parentAgent: 'draft', order: 3 },
  { id: 'storyboard', label: 'Storyboard', icon: '📋', parentAgent: 'draft', order: 4 },
  { id: 'final_render', label: 'Final Render', icon: '✨', parentAgent: 'draft', order: 5 },
];

export const CRITIC_SUB_STAGES: SubStageDef[] = [
  { id: 'L1_visual_perception', label: 'L1 Visual', icon: '👁️', parentAgent: 'critic', order: 0 },
  { id: 'L2_technique_analysis', label: 'L2 Technique', icon: '🔧', parentAgent: 'critic', order: 1 },
  { id: 'L3_cultural_context', label: 'L3 Cultural', icon: '🏛️', parentAgent: 'critic', order: 2 },
  { id: 'L4_creative_expression', label: 'L4 Creative', icon: '💡', parentAgent: 'critic', order: 3 },
  { id: 'L5_holistic_integration', label: 'L5 Holistic', icon: '🌟', parentAgent: 'critic', order: 4 },
];

export function getSubStagesFor(agentId: string): SubStageDef[] {
  if (agentId === 'draft') return DRAFT_SUB_STAGES;
  if (agentId === 'critic') return CRITIC_SUB_STAGES;
  return [];
}
