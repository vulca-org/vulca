// Art Professional Theme System
// Warm, professional, gallery-inspired visual style.
// See docs/design-system.md for full spec.

export const themes = {
  dark: {
    // Background layers — warm dark tones
    bg: {
      base: '#0F0D0B',      // Warm Black — page background
      surface: '#1A1614',   // Warm Surface — cards/panels
      elevated: '#211D1A',  // Elevated — floating/modal
      overlay: '#2A2521',   // Overlay — dropdown/tooltip
      hover: '#342E28',     // Hover state
      active: '#3E3731',    // Active/pressed state
    },

    // Border system
    border: {
      default: '#4A433C',   // Default border (3.2:1 contrast)
      muted: '#342E28',     // Muted — dividers
      strong: '#6B6259',    // Strong — focus/selected
      subtle: '#251F1B',    // Ultra-subtle
    },

    // Text hierarchy
    text: {
      primary: '#F5F0EB',   // Cream White — headings
      secondary: '#A89E94', // Warm Gray — body
      tertiary: '#7A726A',  // Tertiary — hints
      muted: '#524B44',     // Disabled text
      inverse: '#0F0D0B',   // Inverse text
    },

    // Semantic colors — Art Professional Dark
    semantic: {
      primary: '#94A3B8',   // Ink Slate (light)
      accent: '#DDA574',    // Light Bronze
      green: '#87A878',     // Light Sage
      yellow: '#D4A84B',    // Light Amber
      red: '#C97064',       // Light Coral
      bronze: '#C87F4A',    // Warm Bronze
      terracotta: '#9B6B56',// Terracotta
      sage: '#87A878',      // Light Sage
    },

    // Chart palette — warm tones
    chart: {
      primary: '#C87F4A',   // Warm Bronze
      secondary: '#9B6B56', // Terracotta
      tertiary: '#87A878',  // Light Sage
      quaternary: '#D4A84B',// Light Amber
      series: [
        '#C87F4A', '#9B6B56', '#87A878', '#D4A84B',
        '#94A3B8', '#C97064', '#B8A089', '#7A9B76'
      ]
    },

    // Special purpose
    special: {
      gold: 'linear-gradient(135deg, #D4A84B 0%, #C87F4A 100%)',
      silver: 'linear-gradient(135deg, #94A3B8 0%, #64748B 100%)',
      bronze: 'linear-gradient(135deg, #C87F4A 0%, #9B6B56 100%)',
      gradient: 'linear-gradient(135deg, #334155 0%, #C87F4A 100%)', // Brand gradient
    }
  },

  light: {
    // Background layers — gallery style
    bg: {
      base: '#FAF7F2',      // Cream White
      surface: '#FFFFFF',   // Pure White
      elevated: '#FFFFFF',
      overlay: '#FFFFFF',
      hover: '#F5F0E8',
      active: '#EDE6DB',
    },

    border: {
      default: '#C9C2B8',   // Warm Gray border
      muted: '#E8E0D4',
      strong: '#9B9387',
      subtle: '#F0EBE3',
    },

    text: {
      primary: '#1E1B18',   // Warm Black
      secondary: '#524B44', // Warm Dark Gray
      tertiary: '#7A726A',  // Warm Mid Gray
      muted: '#A89E94',     // Warm Light Gray
      inverse: '#FAF7F2',
    },

    // Semantic colors — Art Professional Light
    semantic: {
      primary: '#334155',   // Ink Slate
      accent: '#C87F4A',    // Warm Bronze
      green: '#5F8A50',     // Sage Green
      yellow: '#B8923D',    // Amber Gold
      red: '#C65D4D',       // Coral Red (unified)
      bronze: '#C87F4A',    // Warm Bronze (unified)
      terracotta: '#7D5645',// Terracotta
      sage: '#5F8A50',      // Sage Green
    },

    chart: {
      primary: '#C87F4A',
      secondary: '#9B6B56',
      tertiary: '#5F8A50',
      quaternary: '#B8923D',
      series: [
        '#C87F4A', '#9B6B56', '#5F8A50', '#B8923D',
        '#334155', '#C65D4D', '#8F7860', '#4A7A46'
      ]
    },

    special: {
      gold: 'linear-gradient(135deg, #D4A84B 0%, #C87F4A 100%)',
      silver: 'linear-gradient(135deg, #94A3B8 0%, #64748B 100%)',
      bronze: 'linear-gradient(135deg, #C87F4A 0%, #9B6B56 100%)',
      gradient: 'linear-gradient(135deg, #334155 0%, #C87F4A 100%)', // Brand gradient
    }
  },
};

// Type exports
export type Theme = typeof themes.dark;
export type ThemeMode = keyof typeof themes;

// Get theme by mode
export function getTheme(mode: ThemeMode): Theme {
  return themes[mode];
}

// CSS variable generator
export function generateCSSVariables(theme: Theme): string {
  const vars: string[] = [];
  function flatten(obj: Record<string, unknown>, prefix = '') {
    for (const [key, value] of Object.entries(obj ?? {})) {
      const varName = prefix ? `${prefix}-${key}` : key;
      if (typeof value === 'string') {
        vars.push(`--${varName}: ${value};`);
      } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        flatten(value as Record<string, unknown>, varName);
      }
    }
  }
  flatten(theme as unknown as Record<string, unknown>);
  return vars.join('\n');
}

// Theme class mapping
export const themeClasses = {
  // Background classes
  'bg-base': 'bg-[var(--bg-base)]',
  'bg-surface': 'bg-[var(--bg-surface)]',
  'bg-elevated': 'bg-[var(--bg-elevated)]',
  'bg-overlay': 'bg-[var(--bg-overlay)]',
  // Text classes
  'text-primary': 'text-[var(--text-primary)]',
  'text-secondary': 'text-[var(--text-secondary)]',
  'text-tertiary': 'text-[var(--text-tertiary)]',
  'text-muted': 'text-[var(--text-muted)]',
  // Border classes
  'border-default': 'border-[var(--border-default)]',
  'border-subtle': 'border-[var(--border-subtle)]',
  'border-strong': 'border-[var(--border-strong)]',
} as const;
