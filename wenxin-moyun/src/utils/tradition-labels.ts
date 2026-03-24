/**
 * Shared tradition display labels used across Gallery, Canvas, and Modal.
 * Single source of truth — covers all 13 YAML traditions + legacy/alias names.
 */

export const TRADITION_LABELS: Record<string, string> = {
  // 13 canonical traditions (from vulca/cultural/ YAML configs)
  chinese_xieyi: 'Chinese Xieyi',
  chinese_gongbi: 'Chinese Gongbi',
  islamic_geometric: 'Islamic Geometric',
  japanese_traditional: 'Japanese Traditional',
  western_academic: 'Western Academic',
  african_traditional: 'African Traditional',
  south_asian: 'South Asian',
  watercolor: 'Watercolor',
  default: 'Default',
  // Aliases / legacy names (from gallery mock data)
  chinese_ink: 'Chinese Ink',
  japanese_ukiyoe: 'Japanese Ukiyo-e',
  persian_miniature: 'Persian Miniature',
  indian_mughal: 'Mughal Painting',
  korean_minhwa: 'Korean Minhwa',
  byzantine_icon: 'Byzantine Icon',
  tibetan_thangka: 'Tibetan Thangka',
  japanese_wabi_sabi: 'Japanese Wabi-Sabi',
};

/** L1-L5 dimension full names */
export const L_LABELS: Record<string, string> = {
  L1: 'Visual Perception',
  L2: 'Technical Analysis',
  L3: 'Cultural Context',
  L4: 'Critical Interpretation',
  L5: 'Philosophical Aesthetic',
};

/** Map dimension aliases to canonical L-labels */
export const DIM_TO_L: Record<string, string> = {
  visual_perception: 'L1', technical_analysis: 'L2', technical_execution: 'L2',
  cultural_context: 'L3', critical_interpretation: 'L4', philosophical_aesthetic: 'L5',
  L1: 'L1', L2: 'L2', L3: 'L3', L4: 'L4', L5: 'L5',
  '1': 'L1', '2': 'L2', '3': 'L3', '4': 'L4', '5': 'L5',
};

/** Resolve tradition name to display label, with fallback */
export function getTraditionLabel(tradition: string): string {
  return TRADITION_LABELS[tradition] ?? tradition.replace(/_/g, ' ');
}
