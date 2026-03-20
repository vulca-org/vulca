/** @type {import('tailwindcss').Config} */

/**
 * VULCA Design System — "The Digital Curator" v2.1
 *
 * Architecture: MD3 base tokens (from design HTML) + Cultural extensions
 * Source of truth: /tmp/design-v2/stitch/vulca_canvas_workspace_functional_apple_v1/code.html
 *
 * Version: Digital Curator v2.1 (2026-03-20)
 */

export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ═══════════════════════════════════════════════════════════
        // MD3 BASE TOKENS (from design HTML, 46 tokens)
        // These are the canonical Material Design 3 tokens generated
        // by Stitch for Canvas/Gallery/SignIn pages.
        // ═══════════════════════════════════════════════════════════

        // ── Primary (Tech Trust Blue) ───────────────────────────
        // Used for high-priority actions and active states
        primary: {
          50: '#E8F0FB',
          100: '#C7DAF5',
          200: '#91B5EB',
          300: '#5B90E1',
          400: '#2570D4',
          500: '#005ab4',
          600: '#004D9A',
          700: '#003F80',
          800: '#003166',
          900: '#00234D',
          DEFAULT: '#005ab4',
        },
        'primary-container': '#0873df',
        'primary-fixed': '#d6e3ff',
        'primary-fixed-dim': '#aac7ff',
        'on-primary': '#ffffff',
        'on-primary-container': '#fefcff',
        'on-primary-fixed': '#001b3e',
        'on-primary-fixed-variant': '#00458d',

        // ── Secondary (MD3 blue-grey) ───────────────────────────
        // Supporting UI elements, chips, subtle accents
        secondary: '#465f89',
        'secondary-container': '#b7cfff',
        'secondary-fixed': '#d6e3ff',
        'secondary-fixed-dim': '#afc7f7',
        'on-secondary': '#ffffff',
        'on-secondary-container': '#405882',
        'on-secondary-fixed': '#001b3e',
        'on-secondary-fixed-variant': '#2e4770',

        // ── Tertiary (MD3 orange) ───────────────────────────────
        // Highlights, badges, accent elements
        tertiary: '#964400',
        'tertiary-container': '#bd5700',
        'tertiary-fixed': '#ffdbc9',
        'tertiary-fixed-dim': '#ffb68c',
        'on-tertiary': '#ffffff',
        'on-tertiary-container': '#fffbff',
        'on-tertiary-fixed': '#321200',
        'on-tertiary-fixed-variant': '#763400',

        // ── Error (MD3 red) ─────────────────────────────────────
        error: '#ba1a1a',
        'error-container': '#ffdad6',
        'on-error': '#ffffff',
        'on-error-container': '#93000a',

        // ── Surface System (Cool White) ─────────────────────────
        // Three-tier layering: surface → container-low → container-lowest
        'surface': '#f9f9ff',
        'surface-dim': '#d8dae3',
        'surface-bright': '#f9f9ff',
        'surface-container-lowest': '#ffffff',
        'surface-container-low': '#f2f3fd',
        'surface-container': '#ecedf7',
        'surface-container-high': '#e6e8f1',
        'surface-container-highest': '#e0e2ec',
        'surface-tint': '#005db8',
        'surface-variant': '#e0e2ec',
        'background': '#f9f9ff',

        // ── On-colors (text on surfaces) ────────────────────────
        'on-surface': '#181c22',
        'on-surface-variant': '#414753',
        'on-background': '#181c22',

        // ── Outline ─────────────────────────────────────────────
        'outline': '#717785',
        'outline-variant': '#c1c6d5',

        // ── Inverse (for dark-on-light scenarios) ───────────────
        'inverse-surface': '#2d3038',
        'inverse-on-surface': '#eff0fa',
        'inverse-primary': '#aac7ff',

        // ═══════════════════════════════════════════════════════════
        // CULTURAL EXTENSIONS (VULCA-specific palette)
        // The "human element" — warm, artisanal tones that bridge
        // tech trust with cultural artistry.
        // ═══════════════════════════════════════════════════════════

        // Cultural Bronze — the warm accent, storytelling elements
        'cultural-bronze': {
          50: '#FDF8F4',
          100: '#FAEFE6',
          200: '#F4DCC9',
          300: '#EBC4A1',
          400: '#DDA574',
          500: '#C87F4A',
          600: '#A86838',
          700: '#8F5530',
          800: '#6D4127',
          900: '#4A2C1A',
          DEFAULT: '#C87F4A',
        },
        // Cultural Sage — growth, nature, success states
        'cultural-sage': {
          50: '#F0F7ED',
          100: '#E1EFDB',
          200: '#C3DFB7',
          300: '#A5CF93',
          400: '#7FB86A',
          500: '#5F8A50',
          600: '#4C6E40',
          700: '#395330',
          800: '#263720',
          900: '#131C10',
          DEFAULT: '#5F8A50',
        },
        // Cultural Amber — warmth, attention, warning states
        'cultural-amber': {
          50: '#FDF8ED',
          100: '#FAF1DB',
          200: '#F5E3B7',
          300: '#F0D593',
          400: '#D4A84B',
          500: '#B8923D',
          600: '#937531',
          700: '#6E5825',
          800: '#4A3B19',
          900: '#251E0C',
          DEFAULT: '#B8923D',
        },
        // Cultural Coral — urgency, passion, cultural error states
        'cultural-coral': {
          50: '#FCF0EF',
          100: '#F9E1DF',
          200: '#F3C3BF',
          300: '#EDA59F',
          400: '#D98070',
          500: '#C65D4D',
          600: '#A84A3D',
          700: '#8A3D32',
          800: '#6B2F27',
          900: '#4D211C',
          DEFAULT: '#C65D4D',
        },

        // ── Neutral scales ──────────────────────────────────────
        // Standard Tailwind gray/slate for general UI needs
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#020617',
        },
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
          900: '#1C1C1E',
          950: '#000000',
        },
      },
      fontFamily: {
        // Dual-typeface: Noto Serif (gallery voice) + Inter (tech clarity)
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ["'Noto Serif'", 'Georgia', 'serif'],
        headline: ["'Noto Serif'", 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        label: ['Inter', 'system-ui', 'sans-serif'],
        text: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-in-up': 'fadeInUp 1s cubic-bezier(0.2,0.8,0.2,1) forwards',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'float': 'float 6s ease-in-out infinite',
        'soft-float': 'softFloat 3s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'blink': 'blink 1s step-end infinite',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(40px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        softFloat: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0,90,180,0.2)' },
          '50%': { boxShadow: '0 0 24px 8px rgba(0,90,180,0.15)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '24px',
        '3xl': '40px',
      },
      boxShadow: {
        // Ambient shadows — warm, soft-box lighting (6% on-surface opacity)
        'ambient-sm': '0 2px 12px rgba(28,28,25,0.04)',
        'ambient-md': '0 4px 24px rgba(28,28,25,0.06)',
        'ambient-lg': '0 8px 40px rgba(28,28,25,0.06)',
        'ambient-xl': '0 12px 56px rgba(28,28,25,0.08)',
        'ambient-2xl': '0 20px 80px rgba(28,28,25,0.10)',
        // Legacy aliases
        'ios-sm': '0 2px 12px rgba(28,28,25,0.04)',
        'ios-md': '0 4px 24px rgba(28,28,25,0.06)',
        'ios-lg': '0 8px 40px rgba(28,28,25,0.06)',
        'ios-xl': '0 12px 56px rgba(28,28,25,0.08)',
        'ios-2xl': '0 20px 80px rgba(28,28,25,0.10)',
        'ios-inner': 'inset 0 1px 3px rgba(28,28,25,0.04)',
        'ios-focus': '0 0 0 3px rgba(0,90,180,0.3)',
      },
      borderRadius: {
        // Digital Curator: Apple-style organic radii
        'DEFAULT': '1rem',      // 16px — cards, modules
        'sm': '0.5rem',         // 8px — small elements
        'md': '0.75rem',        // 12px — medium elements
        'lg': '1rem',           // 16px — standard
        'xl': '1.5rem',         // 24px — buttons, inputs
        '2xl': '2rem',          // 32px — large containers
        '3xl': '3rem',          // 48px — hero sections
      },
      transitionTimingFunction: {
        'ios': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'ios-spring': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
      },
    },
  },
  plugins: [],
}
