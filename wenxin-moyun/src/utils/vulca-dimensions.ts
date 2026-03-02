// VULCA 47 Dimensions Definition - Based on EMNLP2025-VULCA Core Framework
// 47维度分为6个主要类别，与后端算法完全一致

export const VULCA_47_DIMENSIONS = {
  // 创造力与创新类别 (Creativity & Innovation) - dim_0 to dim_7
  originality: 'Originality',                    // 原创性
  imagination: 'Imagination',                    // 想象力
  innovation_depth: 'Innovation Depth',          // 创新深度
  artistic_vision: 'Artistic Vision',            // 艺术视野
  conceptual_novelty: 'Conceptual Novelty',      // 概念新颖性
  creative_synthesis: 'Creative Synthesis',      // 创意综合
  ideation_fluency: 'Ideation Fluency',          // 构思流畅性
  divergent_thinking: 'Divergent Thinking',      // 发散思维
  
  // 技术卓越类别 (Technical Excellence) - dim_8 to dim_15
  skill_mastery: 'Skill Mastery',                // 技能掌握
  precision: 'Precision',                        // 精确度
  craft_excellence: 'Craft Excellence',          // 工艺卓越
  technical_proficiency: 'Technical Proficiency', // 技术熟练度
  execution_quality: 'Execution Quality',        // 执行质量
  methodological_rigor: 'Methodological Rigor',  // 方法严谨性
  tool_expertise: 'Tool Expertise',              // 工具专业性
  procedural_knowledge: 'Procedural Knowledge',  // 程序知识
  
  // 情感表达类别 (Emotional Expression) - dim_16 to dim_23
  emotional_depth: 'Emotional Depth',            // 情感深度
  sentiment_expression: 'Sentiment Expression',  // 情感表达
  affective_resonance: 'Affective Resonance',    // 情感共鸣
  mood_conveyance: 'Mood Conveyance',            // 情绪传达
  feeling_authenticity: 'Feeling Authenticity',  // 情感真实性
  empathy_evocation: 'Empathy Evocation',        // 共情唤起
  psychological_insight: 'Psychological Insight', // 心理洞察
  emotional_intelligence: 'Emotional Intelligence', // 情商
  
  // 情境感知类别 (Contextual Awareness) - dim_24 to dim_31
  cultural_awareness: 'Cultural Awareness',      // 文化意识
  historical_grounding: 'Historical Grounding',  // 历史根基
  situational_relevance: 'Situational Relevance', // 情境相关性
  environmental_sensitivity: 'Environmental Sensitivity', // 环境敏感性
  social_consciousness: 'Social Consciousness',  // 社会意识
  temporal_awareness: 'Temporal Awareness',      // 时间意识
  spatial_understanding: 'Spatial Understanding', // 空间理解
  contextual_integration: 'Contextual Integration', // 情境整合
  
  // 创新突破类别 (Innovation & Breakthrough) - dim_32 to dim_39
  breakthrough_thinking: 'Breakthrough Thinking', // 突破性思维
  paradigm_shifting: 'Paradigm Shifting',        // 范式转换
  novel_approaches: 'Novel Approaches',          // 新颖方法
  experimental_courage: 'Experimental Courage',  // 实验勇气
  boundary_pushing: 'Boundary Pushing',          // 边界推动
  revolutionary_concepts: 'Revolutionary Concepts', // 革命性概念
  transformative_ideas: 'Transformative Ideas',  // 变革性理念
  disruptive_creativity: 'Disruptive Creativity', // 颠覆性创造
  
  // 影响力类别 (Impact & Influence) - dim_40 to dim_46
  audience_engagement: 'Audience Engagement',    // 受众参与
  lasting_impression: 'Lasting Impression',      // 持久印象
  influence_scope: 'Influence Scope',            // 影响范围
  transformative_power: 'Transformative Power',  // 变革力量
  memorable_quality: 'Memorable Quality',        // 难忘品质
  viral_potential: 'Viral Potential',            // 传播潜力
  legacy_creation: 'Legacy Creation'             // 遗产创造
};

// 维度类别定义 - with dark mode color support
export const DIMENSION_CATEGORIES = {
  creativity: {
    name: 'Creativity & Innovation',
    name_zh: '创造力与创新',
    range: [0, 7],
    color: '#FF6B6B',
    colorLight: '#FF6B6B',
    colorDark: '#FF8A8A'  // Brighter for dark mode
  },
  technical: {
    name: 'Technical Excellence',
    name_zh: '技术卓越',
    range: [8, 15],
    color: '#4ECDC4',
    colorLight: '#4ECDC4',
    colorDark: '#6EE7DF'  // Brighter for dark mode
  },
  emotional: {
    name: 'Emotional Expression',
    name_zh: '情感表达',
    range: [16, 23],
    color: '#45B7D1',
    colorLight: '#45B7D1',
    colorDark: '#67C9E0'  // Brighter for dark mode
  },
  contextual: {
    name: 'Contextual Awareness',
    name_zh: '情境感知',
    range: [24, 31],
    color: '#96CEB4',
    colorLight: '#96CEB4',
    colorDark: '#B2DECA'  // Brighter for dark mode
  },
  innovation: {
    name: 'Innovation & Breakthrough',
    name_zh: '创新突破',
    range: [32, 39],
    color: '#FFEAA7',
    colorLight: '#FFEAA7',
    colorDark: '#FFF0C0'  // Brighter for dark mode
  },
  impact: {
    name: 'Impact & Influence',
    name_zh: '影响力',
    range: [40, 46],
    color: '#DDA0DD',
    colorLight: '#DDA0DD',
    colorDark: '#E8B8E8'  // Brighter for dark mode
  }
};

/**
 * Get the appropriate color for a dimension category based on theme
 * @param categoryKey - The category key (creativity, technical, etc.)
 * @param isDarkMode - Whether dark mode is active
 * @returns The color string for the current theme
 */
export const getDimensionCategoryColor = (categoryKey: string, isDarkMode: boolean): string => {
  const category = DIMENSION_CATEGORIES[categoryKey as keyof typeof DIMENSION_CATEGORIES];
  if (!category) return isDarkMode ? '#A0AEC0' : '#718096';
  return isDarkMode ? category.colorDark : category.colorLight;
};

// Helper function to convert camelCase to snake_case
const camelToSnakeCase = (str: string): string => {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase().replace(/^_/, '');
};

// Helper function to get dimension label with robust fallback
export const getDimensionLabel = (key: string): string => {
  // Handle backend format "dim_0", "dim_1", etc.
  if (key.startsWith('dim_')) {
    const index = parseInt(key.replace('dim_', ''));
    const dimensionKeys = Object.keys(VULCA_47_DIMENSIONS);
    if (index >= 0 && index < dimensionKeys.length) {
      const actualKey = dimensionKeys[index];
      return VULCA_47_DIMENSIONS[actualKey as keyof typeof VULCA_47_DIMENSIONS];
    }
  }
  
  // Direct lookup for proper keys (snake_case)
  const directResult = VULCA_47_DIMENSIONS[key as keyof typeof VULCA_47_DIMENSIONS];
  if (directResult) return directResult;
  
  // Try converting camelCase to snake_case and lookup
  if (key !== key.toLowerCase()) {
    const snakeKey = camelToSnakeCase(key);
    const snakeResult = VULCA_47_DIMENSIONS[snakeKey as keyof typeof VULCA_47_DIMENSIONS];
    if (snakeResult) return snakeResult;
  }
  
  // Try lowercase version for snake_case keys
  const lowerKey = key.toLowerCase();
  const lowerResult = VULCA_47_DIMENSIONS[lowerKey as keyof typeof VULCA_47_DIMENSIONS];
  if (lowerResult) return lowerResult;
  
  // Enhanced fallback: format the key nicely using same logic as VULCAVisualization
  // Handle snake_case: innovation_depth -> Innovation Depth
  if (key.includes('_')) {
    return key.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  // Handle camelCase/PascalCase: InnovationDepth -> Innovation Depth
  if (key !== key.toLowerCase()) {
    // Strategy: Add space before each uppercase letter (except at start)
    let result = key.replace(/([A-Z])/g, (match, p1, offset) => {
      return offset > 0 ? ' ' + p1 : p1;
    });
    
    // Handle consecutive capitals (e.g., "XMLParser" -> "XML Parser")
    result = result.replace(/([A-Z])([A-Z])([a-z])/g, '$1 $2$3');
    
    // Ensure first letter is uppercase
    result = result.charAt(0).toUpperCase() + result.slice(1);
    
    // Clean up any multiple spaces
    return result.replace(/\s+/g, ' ').trim();
  }
  
  // Last resort: return original key
  return key;
};

// 8个文化视角定义 - Based on EMNLP2025-VULCA Cultural Perspectives
export const CULTURAL_PERSPECTIVES = {
  western: {
    name: 'Western',
    name_zh: '西方视角',
    description: 'Individualism, Innovation, Direct Communication',
    core_values: {
      individualism: 0.8,
      innovation: 0.9,
      directness: 0.7,
      analytical: 0.85,
      competition: 0.75
    }
  },
  eastern: {
    name: 'Eastern',
    name_zh: '东方视角',
    description: 'Harmony, Tradition, Holistic Thinking',
    core_values: {
      harmony: 0.9,
      tradition: 0.85,
      holistic: 0.9,
      cooperation: 0.8,
      indirect_communication: 0.75
    }
  },
  african: {
    name: 'African',
    name_zh: '非洲视角',
    description: 'Community, Rhythm, Storytelling, Ubuntu',
    core_values: {
      community: 0.95,
      rhythm: 0.9,
      storytelling: 0.85,
      ubuntu: 0.9,
      ancestral_wisdom: 0.8
    }
  },
  latin_american: {
    name: 'Latin American',
    name_zh: '拉美视角',
    description: 'Passion, Family, Magical Realism',
    core_values: {
      passion: 0.9,
      family: 0.85,
      magical_realism: 0.85,
      celebration: 0.8,
      social_orientation: 0.75
    }
  },
  middle_eastern: {
    name: 'Middle Eastern',
    name_zh: '中东视角',
    description: 'Hospitality, Tradition, Honor, Spirituality',
    core_values: {
      hospitality: 0.9,
      tradition: 0.85,
      honor: 0.8,
      spirituality: 0.85,
      community_values: 0.8
    }
  },
  south_asian: {
    name: 'South Asian',
    name_zh: '南亚视角',
    description: 'Spirituality, Family, Karma, Festival Culture',
    core_values: {
      spirituality: 0.9,
      family: 0.85,
      karma: 0.85,
      festival_culture: 0.8,
      hierarchical_structure: 0.75
    }
  },
  oceanic: {
    name: 'Oceanic',
    name_zh: '大洋洲视角',
    description: 'Nature, Navigation, Oral Tradition',
    core_values: {
      nature_connection: 0.95,
      navigation: 0.85,
      oral_tradition: 0.8,
      ocean_culture: 0.9,
      island_community: 0.85
    }
  },
  indigenous: {
    name: 'Indigenous',
    name_zh: '原住民视角',
    description: 'Land Connection, Ancestral Wisdom, Circular Time',
    core_values: {
      land_connection: 0.95,
      ancestral_wisdom: 0.9,
      circular_time: 0.85,
      nature_spirituality: 0.9,
      oral_history: 0.85
    }
  }
};

// Get dimension category for a given dimension key
export const getDimensionCategory = (key: string): string | null => {
  const keys = Object.keys(VULCA_47_DIMENSIONS);
  let index = keys.indexOf(key);
  
  // Handle backend format "dim_0", "dim_1", etc.
  if (index === -1 && key.startsWith('dim_')) {
    const dimIndex = parseInt(key.replace('dim_', ''));
    if (dimIndex >= 0 && dimIndex < keys.length) {
      index = dimIndex;
    }
  }
  
  if (index === -1) return null;
  
  for (const [categoryKey, category] of Object.entries(DIMENSION_CATEGORIES)) {
    if (index >= category.range[0] && index <= category.range[1]) {
      return categoryKey;
    }
  }
  return null;
};

// Get all dimension keys
export const DIMENSION_KEYS = Object.keys(VULCA_47_DIMENSIONS);

// Get all dimension labels
export const DIMENSION_LABELS = Object.values(VULCA_47_DIMENSIONS);

// Get all cultural perspective keys
export const CULTURAL_PERSPECTIVE_KEYS = Object.keys(CULTURAL_PERSPECTIVES);

/**
 * Format dimension name from any format (snake_case, camelCase, PascalCase)
 * to Title Case with proper spacing
 * @example formatDimensionName('innovation_depth') => 'Innovation Depth'
 * @example formatDimensionName('InnovationDepth') => 'Innovation Depth'
 * @example formatDimensionName('innovationDepth') => 'Innovation Depth'
 */
export const formatDimensionName = (text: string): string => {
  if (!text) return '';

  // If already has proper spacing (contains space and doesn't have underscore), return as-is
  if (text.includes(' ') && !text.includes('_')) {
    return text;
  }

  // Handle snake_case: innovation_depth -> Innovation Depth
  if (text.includes('_')) {
    return text.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  // Handle camelCase/PascalCase: InnovationDepth -> Innovation Depth
  const result = text
    // Insert space before uppercase letters that follow lowercase letters or digits
    .replace(/([a-z\d])([A-Z])/g, '$1 $2')
    // Insert space between consecutive uppercase letters followed by lowercase
    .replace(/([A-Z]+)([A-Z][a-z\d]+)/g, '$1 $2');

  // Ensure first letter is uppercase and clean up multiple spaces
  return (result.charAt(0).toUpperCase() + result.slice(1))
    .replace(/\s+/g, ' ')
    .trim();
};

// ─── L1-L5 Five-Layer Definitions (VULCA Prototype) ──────────────

export const PROTOTYPE_DIMENSIONS = [
  'visual_perception',
  'technical_analysis',
  'cultural_context',
  'critical_interpretation',
  'philosophical_aesthetic',
] as const;

export type PrototypeDimension = typeof PROTOTYPE_DIMENSIONS[number];

export const PROTOTYPE_DIM_LABELS: Record<PrototypeDimension, {
  short: string;
  full: string;
  complete: string;
  layer: string;
  color: string;
}> = {
  visual_perception:       { short: 'L1 Visual',    full: 'Visual Perception',       complete: 'L1 Visual Perception',       layer: 'L1', color: 'bg-blue-400' },
  technical_analysis:      { short: 'L2 Technical', full: 'Technical Analysis',      complete: 'L2 Technical Analysis',      layer: 'L2', color: 'bg-cyan-400' },
  cultural_context:        { short: 'L3 Cultural',  full: 'Cultural Context',        complete: 'L3 Cultural Context',        layer: 'L3', color: 'bg-emerald-400' },
  critical_interpretation: { short: 'L4 Critical',  full: 'Critical Interpretation', complete: 'L4 Critical Interpretation', layer: 'L4', color: 'bg-amber-400' },
  philosophical_aesthetic: { short: 'L5 Aesthetic',  full: 'Philosophical Aesthetic', complete: 'L5 Philosophical Aesthetic', layer: 'L5', color: 'bg-purple-400' },
};