/**
 * VULCA Design System — "The Digital Curator"
 * Bridges Tech Trust (Blue) with Cultural Artistry (Bronze & Cream).
 */

export const iosColors = {
  // Digital Curator Color Palette
  blue: '#1275E2',       // Tech Trust Blue — primary
  green: '#5F8A50',      // Sage Green — success
  indigo: '#0C4F9C',     // Deep Blue — primary dark
  orange: '#B8923D',     // Amber Gold — warning
  pink: '#9B6B56',       // Terracotta
  purple: '#C87F4A',     // Warm Bronze — secondary / cultural accent
  red: '#C65D4D',        // Coral Red — error
  teal: '#6B8E7A',       // Patina Green — info
  yellow: '#D4A84B',     // Warm Gold
  
  // Gray Scale
  gray: {
    50: '#F2F2F7',
    100: '#E5E5EA',
    200: '#D1D1D6',
    300: '#C7C7CC',
    400: '#AEAEB2',
    500: '#8E8E93',
    600: '#636366',
    700: '#48484A',
    800: '#3A3A3C',
    900: '#2C2C2E',
  },
  
  // Semantic Colors
  background: {
    primary: '#ffffff',          // surface-container-lowest
    secondary: '#f6f3ee',        // surface-container-low
    tertiary: '#ffffff',
    grouped: '#fcf9f4',          // surface (bg-base)
  },
  
  backgroundDark: {
    primary: '#000000',
    secondary: '#1C1C1E',
    tertiary: '#2C2C2E',
    grouped: '#000000',
  },
  
  label: {
    primary: 'rgba(0, 0, 0, 1.0)',
    secondary: 'rgba(60, 60, 67, 0.6)',
    tertiary: 'rgba(60, 60, 67, 0.3)',
    quaternary: 'rgba(60, 60, 67, 0.18)',
  },
  
  labelDark: {
    primary: 'rgba(255, 255, 255, 1.0)',
    secondary: 'rgba(235, 235, 245, 0.6)',
    tertiary: 'rgba(235, 235, 245, 0.3)',
    quaternary: 'rgba(235, 235, 245, 0.18)',
  },
  
  separator: {
    light: 'rgba(60, 60, 67, 0.29)',
    dark: 'rgba(84, 84, 88, 0.65)',
  },
};

export const iosShadows = {
  sm: '0 2px 12px rgba(28, 28, 25, 0.04)',
  md: '0 4px 24px rgba(28, 28, 25, 0.06)',
  lg: '0 8px 40px rgba(28, 28, 25, 0.06)',
  xl: '0 12px 56px rgba(28, 28, 25, 0.08)',
  '2xl': '0 20px 80px rgba(28, 28, 25, 0.10)',
};

export const iosRadius = {
  xs: '4px',
  sm: '8px',       // 0.5rem
  md: '12px',      // 0.75rem
  lg: '16px',      // 1rem — cards
  xl: '24px',      // 1.5rem — buttons
  '2xl': '32px',   // 2rem
  full: '9999px',
};

export const iosTypography = {
  largeTitle: {
    fontSize: '34px',
    fontWeight: '700',
    lineHeight: '41px',
    letterSpacing: '0.374px',
  },
  title1: {
    fontSize: '28px',
    fontWeight: '700',
    lineHeight: '34px',
    letterSpacing: '0.364px',
  },
  title2: {
    fontSize: '22px',
    fontWeight: '700',
    lineHeight: '28px',
    letterSpacing: '0.352px',
  },
  title3: {
    fontSize: '20px',
    fontWeight: '600',
    lineHeight: '25px',
    letterSpacing: '0.38px',
  },
  headline: {
    fontSize: '17px',
    fontWeight: '600',
    lineHeight: '22px',
    letterSpacing: '-0.408px',
  },
  body: {
    fontSize: '17px',
    fontWeight: '400',
    lineHeight: '22px',
    letterSpacing: '-0.408px',
  },
  callout: {
    fontSize: '16px',
    fontWeight: '400',
    lineHeight: '21px',
    letterSpacing: '-0.32px',
  },
  subheadline: {
    fontSize: '15px',
    fontWeight: '400',
    lineHeight: '20px',
    letterSpacing: '-0.24px',
  },
  footnote: {
    fontSize: '13px',
    fontWeight: '400',
    lineHeight: '18px',
    letterSpacing: '-0.078px',
  },
  caption1: {
    fontSize: '12px',
    fontWeight: '400',
    lineHeight: '16px',
    letterSpacing: '0px',
  },
  caption2: {
    fontSize: '11px',
    fontWeight: '400',
    lineHeight: '13px',
    letterSpacing: '0.066px',
  },
};

export const iosTransitions = {
  default: '200ms ease-in-out',
  fast: '100ms ease-in-out',
  slow: '300ms ease-in-out',
  spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
};

export const iosSpacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '20px',
  '2xl': '24px',
  '3xl': '32px',
  '4xl': '40px',
};

/**
 * Liquid Glass Effect System
 * Advanced glass morphism effects based on iOS design language
 */
export const liquidGlass = {
  // Backdrop blur intensities
  blur: {
    light: 'backdrop-blur-sm backdrop-saturate-200',
    medium: 'backdrop-blur-md backdrop-saturate-150', 
    heavy: 'backdrop-blur-lg backdrop-saturate-180',
    ultra: 'backdrop-blur-xl backdrop-saturate-200'
  },
  
  // Transparency levels with iOS-accurate opacity
  opacity: {
    ultraThin: 'bg-white/[0.08] dark:bg-white/[0.05]',
    thin: 'bg-white/[0.15] dark:bg-white/[0.1]',
    regular: 'bg-white/[0.25] dark:bg-white/[0.18]',
    thick: 'bg-white/[0.4] dark:bg-white/[0.3]',
    material: 'bg-white/[0.6] dark:bg-black/[0.6]'
  },
  
  // Dynamic borders with subtle glass effect
  borders: {
    subtle: 'border border-white/[0.08] dark:border-white/[0.05]',
    regular: 'border border-white/[0.12] dark:border-white/[0.08]',
    prominent: 'border border-white/[0.18] dark:border-white/[0.12]',
    material: 'border border-white/[0.25] dark:border-white/[0.15]'
  },
  
  // Liquid glass container styles
  containers: {
    card: 'bg-white/[0.25] dark:bg-white/[0.18] backdrop-blur-md backdrop-saturate-150 border border-white/[0.12] dark:border-white/[0.08]',
    sheet: 'bg-white/[0.4] dark:bg-black/[0.6] backdrop-blur-xl backdrop-saturate-200 border-t border-white/[0.18] dark:border-white/[0.12]',
    overlay: 'bg-white/[0.15] dark:bg-white/[0.1] backdrop-blur-lg backdrop-saturate-180',
    navigation: 'bg-white/[0.6] dark:bg-black/[0.8] backdrop-blur-xl backdrop-saturate-200 border-t border-white/[0.18] dark:border-white/[0.12]'
  },
  
  // Dynamic reflections and highlights
  reflections: {
    subtle: 'relative before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/[0.05] before:to-transparent before:pointer-events-none',
    regular: 'relative before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/[0.1] before:to-transparent before:pointer-events-none',
    prominent: 'relative before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/[0.15] before:via-transparent before:to-white/[0.05] before:pointer-events-none'
  },
  
  // Liquid glass shadows
  shadows: {
    soft: '0 8px 32px rgba(0, 0, 0, 0.12)',
    medium: '0 16px 48px rgba(0, 0, 0, 0.15)',
    strong: '0 24px 64px rgba(0, 0, 0, 0.18)',
    floating: '0 32px 80px rgba(0, 0, 0, 0.2)'
  }
};