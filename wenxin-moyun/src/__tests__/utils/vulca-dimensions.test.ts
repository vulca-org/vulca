import { describe, it, expect } from 'vitest'
import {
  VULCA_47_DIMENSIONS,
  DIMENSION_CATEGORIES,
  DIMENSION_KEYS,
  DIMENSION_LABELS,
  PROTOTYPE_DIMENSIONS,
  PROTOTYPE_DIM_LABELS,
  getDimensionLabel,
  getDimensionCategory,
  getDimensionCategoryColor,
  formatDimensionName,
} from '../../utils/vulca-dimensions'

describe('VULCA_47_DIMENSIONS constant', () => {
  it('should contain exactly 47 dimensions', () => {
    expect(Object.keys(VULCA_47_DIMENSIONS)).toHaveLength(47)
  })

  it('should have string labels for every dimension', () => {
    for (const [key, label] of Object.entries(VULCA_47_DIMENSIONS)) {
      expect(typeof key).toBe('string')
      expect(typeof label).toBe('string')
      expect(label.length).toBeGreaterThan(0)
    }
  })

  it('should include known dimensions', () => {
    expect(VULCA_47_DIMENSIONS.originality).toBe('Originality')
    expect(VULCA_47_DIMENSIONS.emotional_depth).toBe('Emotional Depth')
    expect(VULCA_47_DIMENSIONS.legacy_creation).toBe('Legacy Creation')
  })
})

describe('DIMENSION_CATEGORIES', () => {
  it('should define 6 categories', () => {
    expect(Object.keys(DIMENSION_CATEGORIES)).toHaveLength(6)
  })

  it('should have expected category keys', () => {
    const keys = Object.keys(DIMENSION_CATEGORIES)
    expect(keys).toContain('creativity')
    expect(keys).toContain('technical')
    expect(keys).toContain('emotional')
    expect(keys).toContain('contextual')
    expect(keys).toContain('innovation')
    expect(keys).toContain('impact')
  })

  it('should have ranges covering all 47 dimensions (0-46)', () => {
    const allIndices = new Set<number>()
    for (const cat of Object.values(DIMENSION_CATEGORIES)) {
      for (let i = cat.range[0]; i <= cat.range[1]; i++) {
        allIndices.add(i)
      }
    }
    expect(allIndices.size).toBe(47)
    expect(Math.min(...allIndices)).toBe(0)
    expect(Math.max(...allIndices)).toBe(46)
  })

  it('should have color fields for light and dark mode', () => {
    for (const cat of Object.values(DIMENSION_CATEGORIES)) {
      expect(cat.color).toBeTruthy()
      expect(cat.colorLight).toBeTruthy()
      expect(cat.colorDark).toBeTruthy()
    }
  })
})

describe('DIMENSION_KEYS and DIMENSION_LABELS', () => {
  it('DIMENSION_KEYS should have 47 entries', () => {
    expect(DIMENSION_KEYS).toHaveLength(47)
  })

  it('DIMENSION_LABELS should have 47 entries', () => {
    expect(DIMENSION_LABELS).toHaveLength(47)
  })

  it('should be consistent with VULCA_47_DIMENSIONS', () => {
    expect(DIMENSION_KEYS).toEqual(Object.keys(VULCA_47_DIMENSIONS))
    expect(DIMENSION_LABELS).toEqual(Object.values(VULCA_47_DIMENSIONS))
  })
})

describe('PROTOTYPE_DIMENSIONS', () => {
  it('should define 5 L1-L5 dimensions', () => {
    expect(PROTOTYPE_DIMENSIONS).toHaveLength(5)
  })

  it('should contain expected layer names', () => {
    expect(PROTOTYPE_DIMENSIONS).toContain('visual_perception')
    expect(PROTOTYPE_DIMENSIONS).toContain('technical_analysis')
    expect(PROTOTYPE_DIMENSIONS).toContain('cultural_context')
    expect(PROTOTYPE_DIMENSIONS).toContain('critical_interpretation')
    expect(PROTOTYPE_DIMENSIONS).toContain('philosophical_aesthetic')
  })

  it('should have labels for every prototype dimension', () => {
    for (const dim of PROTOTYPE_DIMENSIONS) {
      const label = PROTOTYPE_DIM_LABELS[dim]
      expect(label).toBeDefined()
      expect(label.short).toBeTruthy()
      expect(label.full).toBeTruthy()
      expect(label.complete).toBeTruthy()
      expect(label.layer).toMatch(/^L[1-5]$/)
      expect(label.color).toMatch(/^bg-/)
    }
  })
})

describe('getDimensionLabel', () => {
  it('should return label for snake_case keys', () => {
    expect(getDimensionLabel('originality')).toBe('Originality')
    expect(getDimensionLabel('innovation_depth')).toBe('Innovation Depth')
    expect(getDimensionLabel('creative_synthesis')).toBe('Creative Synthesis')
  })

  it('should return label for dim_N backend format', () => {
    expect(getDimensionLabel('dim_0')).toBe('Originality')
    expect(getDimensionLabel('dim_46')).toBe('Legacy Creation')
  })

  it('should return fallback for unknown dim_N indices', () => {
    // dim_99 is out of range; falls through to underscore formatting
    const result = getDimensionLabel('dim_99')
    expect(result).toBe('Dim 99')
  })

  it('should handle camelCase keys via conversion', () => {
    // camelToSnakeCase: innovationDepth -> innovation_depth
    expect(getDimensionLabel('innovationDepth')).toBe('Innovation Depth')
  })

  it('should format unknown snake_case keys nicely', () => {
    expect(getDimensionLabel('some_unknown_dim')).toBe('Some Unknown Dim')
  })

  it('should format unknown PascalCase keys nicely', () => {
    expect(getDimensionLabel('SomeUnknownDim')).toBe('Some Unknown Dim')
  })

  it('should return original key for plain unknown keys', () => {
    expect(getDimensionLabel('unknown')).toBe('unknown')
  })
})

describe('getDimensionCategory', () => {
  it('should return correct category for direct keys', () => {
    expect(getDimensionCategory('originality')).toBe('creativity')
    expect(getDimensionCategory('skill_mastery')).toBe('technical')
    expect(getDimensionCategory('emotional_depth')).toBe('emotional')
    expect(getDimensionCategory('cultural_awareness')).toBe('contextual')
    expect(getDimensionCategory('breakthrough_thinking')).toBe('innovation')
    expect(getDimensionCategory('audience_engagement')).toBe('impact')
  })

  it('should return correct category for dim_N format', () => {
    expect(getDimensionCategory('dim_0')).toBe('creativity')
    expect(getDimensionCategory('dim_8')).toBe('technical')
    expect(getDimensionCategory('dim_16')).toBe('emotional')
    expect(getDimensionCategory('dim_24')).toBe('contextual')
    expect(getDimensionCategory('dim_32')).toBe('innovation')
    expect(getDimensionCategory('dim_40')).toBe('impact')
  })

  it('should return null for unknown keys', () => {
    expect(getDimensionCategory('nonexistent')).toBeNull()
    expect(getDimensionCategory('dim_99')).toBeNull()
  })
})

describe('getDimensionCategoryColor', () => {
  it('should return light color when isDarkMode is false', () => {
    expect(getDimensionCategoryColor('creativity', false)).toBe('#FF6B6B')
    expect(getDimensionCategoryColor('technical', false)).toBe('#4ECDC4')
  })

  it('should return dark color when isDarkMode is true', () => {
    expect(getDimensionCategoryColor('creativity', true)).toBe('#FF8A8A')
    expect(getDimensionCategoryColor('technical', true)).toBe('#6EE7DF')
  })

  it('should return fallback for unknown category', () => {
    expect(getDimensionCategoryColor('nonexistent', false)).toBe('#718096')
    expect(getDimensionCategoryColor('nonexistent', true)).toBe('#A0AEC0')
  })
})

describe('formatDimensionName', () => {
  it('should return empty string for empty input', () => {
    expect(formatDimensionName('')).toBe('')
  })

  it('should return already-spaced text as-is', () => {
    expect(formatDimensionName('Innovation Depth')).toBe('Innovation Depth')
  })

  it('should convert snake_case to Title Case', () => {
    expect(formatDimensionName('innovation_depth')).toBe('Innovation Depth')
    expect(formatDimensionName('creative_synthesis')).toBe('Creative Synthesis')
  })

  it('should convert PascalCase to spaced form', () => {
    expect(formatDimensionName('InnovationDepth')).toBe('Innovation Depth')
    expect(formatDimensionName('CreativeSynthesis')).toBe('Creative Synthesis')
  })

  it('should convert camelCase to spaced form', () => {
    expect(formatDimensionName('innovationDepth')).toBe('Innovation Depth')
    expect(formatDimensionName('creativeSynthesis')).toBe('Creative Synthesis')
  })

  it('should handle single word', () => {
    expect(formatDimensionName('originality')).toBe('Originality')
  })
})
