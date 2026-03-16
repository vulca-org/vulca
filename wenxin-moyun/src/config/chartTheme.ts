/**
 * Art Professional Chart Theme
 * Warm, professional chart colors with light/dark mode support.
 * See docs/design-system.md for full spec.
 */

import { ORGANIZATION_COLORS, getOrganizationColor } from '../constants/organizationColors';

// ============= Art Professional Color System =============

export const iosSystemColors = {
  // Primary warm palette
  bronze: '#C87F4A',      // Warm Bronze — primary accent
  terracotta: '#9B6B56',  // Terracotta — secondary accent
  sage: '#5F8A50',        // Sage Green
  amber: '#B8923D',       // Amber Gold
  slate: '#64748B',       // Ink Slate
  coral: '#C65D4D',       // Coral Red (unified)
  ochre: '#8F7860',       // Ochre
  olive: '#4A7A46',       // Olive Green
  // Legacy compatibility aliases
  blue: '#64748B',        // Mapped to Ink Slate
  green: '#5F8A50',
  orange: '#C87F4A',
  red: '#C65D4D',
  purple: '#9B6B56',
  teal: '#4A7A46',
  indigo: '#64748B',
  pink: '#C65D4D',
  yellow: '#B8923D',
};

// Dark mode (lighter variants)
export const iosDarkSystemColors = {
  bronze: '#DDA574',      // Light Bronze
  terracotta: '#C49976',  // Light Terracotta
  sage: '#87A878',        // Light Sage
  amber: '#D4A84B',       // Light Amber
  slate: '#94A3B8',       // Light Slate
  coral: '#C97064',       // Light Coral
  ochre: '#B8A089',       // Light Ochre
  olive: '#7A9B76',       // Light Olive
  // Legacy compatibility
  blue: '#94A3B8',
  green: '#87A878',
  orange: '#DDA574',
  red: '#C97064',
  purple: '#C49976',
  teal: '#7A9B76',
  indigo: '#94A3B8',
  pink: '#C97064',
  yellow: '#D4A84B',
};

// ============= Light Mode Chart Config =============

export const chartColorsLight = {
  // Art Professional color sequence
  primary: [
    iosSystemColors.bronze,      // #C87F4A Warm Bronze
    iosSystemColors.terracotta,  // #9B6B56 Terracotta
    iosSystemColors.sage,        // #5F8A50 Sage Green
    iosSystemColors.amber,       // #B8923D Amber Gold
    iosSystemColors.slate,       // #64748B Ink Slate
    iosSystemColors.coral,       // #C65D4D Coral Red
    iosSystemColors.ochre,       // #8F7860 Ochre
    iosSystemColors.olive,       // #4A7A46 Olive
  ],

  // Warm gradient pairs
  gradients: {
    primaryToSuccess: [iosSystemColors.slate, iosSystemColors.sage],
    primaryToAccent: [iosSystemColors.slate, iosSystemColors.bronze],
    successToWarning: [iosSystemColors.sage, iosSystemColors.amber],
    purpleToBlue: [iosSystemColors.terracotta, iosSystemColors.slate],
  },

  // Semantic colors
  semantic: {
    success: '#5F8A50',       // Sage Green
    warning: '#B8923D',       // Amber Gold
    error: '#C65D4D',         // Coral Red (unified)
    info: '#64748B',          // Ink Slate
    neutral: '#7A726A',       // Warm Gray
  },

  // Grid and axis colors — WCAG AA optimized
  grid: {
    line: '#999999',        // contrast 3.5:1
    text: '#636366',        // iOS Gray 600 - 5.34:1 ✓
    subText: '#707070',     // contrast 4.5:1
    axis: '#808080',        // contrast 4.0:1
  },

  // Background
  background: {
    card: '#FFFFFF',
    hover: '#F2F2F7',       // iOS Gray 50
    disabled: '#E5E5EA',    // iOS Gray 100
    tooltip: 'rgba(0, 0, 0, 0.85)',
  },

  // Tooltip
  tooltip: {
    background: 'rgba(0, 0, 0, 0.85)',
    text: '#FFFFFF',
    border: 'rgba(0, 0, 0, 0.1)',
  },
};

// ============= Dark Mode Chart Config =============

export const chartColorsDark = {
  // Art Professional dark mode color sequence
  primary: [
    iosDarkSystemColors.bronze,      // #DDA574 Light Bronze
    iosDarkSystemColors.terracotta,  // #C49976 Light Terracotta
    iosDarkSystemColors.sage,        // #87A878 Light Sage
    iosDarkSystemColors.amber,       // #D4A84B Light Amber
    iosDarkSystemColors.slate,       // #94A3B8 Light Slate
    iosDarkSystemColors.coral,       // #C97064 Light Coral
    iosDarkSystemColors.ochre,       // #B8A089 Light Ochre
    iosDarkSystemColors.olive,       // #7A9B76 Light Olive
  ],

  // Warm gradient pairs
  gradients: {
    primaryToSuccess: [iosDarkSystemColors.slate, iosDarkSystemColors.sage],
    primaryToAccent: [iosDarkSystemColors.slate, iosDarkSystemColors.bronze],
    successToWarning: [iosDarkSystemColors.sage, iosDarkSystemColors.amber],
    purpleToBlue: [iosDarkSystemColors.terracotta, iosDarkSystemColors.slate],
  },

  // Semantic colors — Art Professional dark
  semantic: {
    success: iosDarkSystemColors.sage,
    warning: iosDarkSystemColors.amber,
    error: iosDarkSystemColors.coral,
    info: iosDarkSystemColors.slate,
    neutral: '#A89E94',
  },

  // Grid and axis colors — WCAG AA optimized
  grid: {
    line: '#555555',        // contrast 3.0:1
    text: '#AEAEB2',        // iOS Gray 400 - 9.04:1 ✓
    subText: '#8E8E93',     // iOS Gray 500 - 5.0:1 ✓
    axis: '#666666',        // contrast 3.5:1
  },

  // Background
  background: {
    card: '#1C1C1E',        // iOS Dark Gray 900
    hover: '#2C2C2E',       // iOS Gray 900
    disabled: '#3A3A3C',    // iOS Dark Gray 800
    tooltip: 'rgba(255, 255, 255, 0.9)',
  },

  // Tooltip
  tooltip: {
    background: 'rgba(255, 255, 255, 0.9)',
    text: '#000000',
    border: 'rgba(255, 255, 255, 0.1)',
  },
};

// ============= Organization Brand Colors =============
// Re-export from centralized constants for backward compatibility
export const organizationColors = ORGANIZATION_COLORS;

// ============= VULCA Dimension Category Colors =============

export const vulcaCategoryColors = {
  creativity: {
    light: iosSystemColors.bronze,      // Warm Bronze — Creativity
    dark: iosDarkSystemColors.bronze,
  },
  technical: {
    light: iosSystemColors.sage,        // Sage Green — Technical
    dark: iosDarkSystemColors.sage,
  },
  emotional: {
    light: iosSystemColors.coral,       // Coral Red — Emotional
    dark: iosDarkSystemColors.coral,
  },
  contextual: {
    light: iosSystemColors.slate,       // Ink Slate — Contextual
    dark: iosDarkSystemColors.slate,
  },
  innovation: {
    light: iosSystemColors.amber,       // Amber Gold — Innovation
    dark: iosDarkSystemColors.amber,
  },
  impact: {
    light: iosSystemColors.terracotta,  // Terracotta — Impact
    dark: iosDarkSystemColors.terracotta,
  },
};

// ============= Chart Common Config =============

export const chartConfig = {
  // Font config — iOS system font
  font: {
    family: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif',
    sizes: {
      title: 17,      // iOS Body
      label: 15,      // iOS Subheadline
      tick: 13,       // iOS Footnote
      legend: 13,     // iOS Footnote
      tooltip: 14,
    },
    weights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },

  // Animation config — iOS style
  animation: {
    duration: 300,
    easing: 'ease-out',
    spring: {
      stiffness: 400,
      damping: 30,
    },
  },

  // Margin config
  margin: {
    top: 20,
    right: 20,
    bottom: 20,
    left: 20,
  },

  // Border radius — iOS style
  borderRadius: {
    sm: 6,
    md: 10,
    lg: 14,
    xl: 20,
  },
};

// ============= Utility Functions =============

/**
 * Get current theme chart colors
 */
export const getChartColors = (isDark: boolean = false) => {
  return isDark ? chartColorsDark : chartColorsLight;
};

/**
 * Get data series color
 */
export const getSeriesColors = (count: number, isDark: boolean = false): string[] => {
  const colors = isDark ? chartColorsDark.primary : chartColorsLight.primary;

  if (count <= colors.length) {
    return colors.slice(0, count);
  }

  // Cycle colors with adjusted opacity if needed
  const result: string[] = [];
  for (let i = 0; i < count; i++) {
    const baseColor = colors[i % colors.length];
    const opacity = i < colors.length ? 1 : 0.7;
    result.push(opacity === 1 ? baseColor : `${baseColor}B3`);
  }
  return result;
};

/**
 * Get organization color
 * Uses centralized organizationColors from constants
 */
export const getOrgColor = (orgName: string): string => {
  return getOrganizationColor(orgName);
};

/**
 * Get VULCA dimension category color
 */
export const getVulcaCategoryColor = (
  category: keyof typeof vulcaCategoryColors,
  isDark: boolean = false
): string => {
  const colors = vulcaCategoryColors[category];
  return colors ? (isDark ? colors.dark : colors.light) : chartColorsLight.primary[0];
};

/**
 * Get gradient CSS
 */
export const getGradientCSS = (
  gradientKey: keyof typeof chartColorsLight.gradients,
  isDark: boolean = false,
  angle: number = 135
): string => {
  const gradients = isDark ? chartColorsDark.gradients : chartColorsLight.gradients;
  const [start, end] = gradients[gradientKey];
  return `linear-gradient(${angle}deg, ${start} 0%, ${end} 100%)`;
};

/**
 * Recharts config generator
 */
export const getRechartsTheme = (isDark: boolean = false) => {
  const colors = getChartColors(isDark);

  return {
    // Axis config
    axis: {
      stroke: colors.grid.axis,
      tick: {
        fill: colors.grid.text,
        fontSize: chartConfig.font.sizes.tick,
        fontFamily: chartConfig.font.family,
      },
    },

    // Grid config
    cartesianGrid: {
      stroke: colors.grid.line,
      strokeDasharray: '3 3',
      strokeOpacity: isDark ? 0.3 : 0.5,
    },

    // Tooltip config
    tooltip: {
      contentStyle: {
        backgroundColor: colors.tooltip.background,
        border: `1px solid ${colors.tooltip.border}`,
        borderRadius: chartConfig.borderRadius.md,
        padding: '12px 16px',
        boxShadow: isDark
          ? '0 10px 40px rgba(0,0,0,0.4)'
          : '0 10px 40px rgba(0,0,0,0.15)',
      },
      labelStyle: {
        color: colors.tooltip.text,
        fontWeight: chartConfig.font.weights.semibold,
        marginBottom: 8,
      },
      itemStyle: {
        color: colors.tooltip.text,
        fontSize: chartConfig.font.sizes.tooltip,
      },
    },

    // Legend config
    legend: {
      wrapperStyle: {
        paddingTop: '20px',
        fontFamily: chartConfig.font.family,
        fontSize: chartConfig.font.sizes.legend,
      },
    },

    // Radar chart config
    radar: {
      polarGrid: {
        stroke: colors.grid.line,
        strokeOpacity: isDark ? 0.3 : 0.5,
      },
      polarAngleAxis: {
        tick: {
          fill: colors.grid.text,
          fontSize: 11,
        },
      },
      polarRadiusAxis: {
        tick: {
          fill: colors.grid.subText,
          fontSize: 10,
        },
        axisLine: {
          stroke: colors.grid.line,
        },
      },
    },
  };
};

// ============= Backward Compat Exports =============

export const chartColors = chartColorsLight;

// Type exports
export type ChartColors = typeof chartColorsLight;
export type OrganizationColorKey = keyof typeof organizationColors;
export type VulcaCategoryKey = keyof typeof vulcaCategoryColors;
