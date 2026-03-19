/** @type {import('tailwindcss').Config} */

/**
 * VULCA Design System — "The Digital Curator"
 *
 * Bridges "Tech Trust" (Blue) with "Cultural Artistry" (Bronze & Cream).
 * Reference: vulca_ethos/DESIGN.md
 *
 * Version: Digital Curator v2.0 (2026-03-19)
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
        // ── Digital Curator Color System ──────────────────────────

        // Primary: Tech Trust Blue — the engine
        primary: {
          50: '#EEF4FC',
          100: '#D5E6FA',
          200: '#AAC8F4',
          300: '#7FAAEE',
          400: '#4A8CE8',
          500: '#1275E2',
          600: '#0F62BF',
          700: '#0C4F9C',
          800: '#093D79',
          900: '#062A56',
          DEFAULT: '#1275E2',
        },
        // Secondary: Cultural Artistry Bronze — the human element
        secondary: {
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
        // Success: Sage Green
        success: {
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
        // Warning: Amber Gold
        warning: {
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
        // Error: Coral Red
        error: {
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

        // Warm Bronze alias (direct access)
        bronze: {
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
        // Blue: proper blue scale (restored)
        blue: {
          50: '#EEF4FC',
          100: '#D5E6FA',
          200: '#AAC8F4',
          300: '#7FAAEE',
          400: '#4A8CE8',
          500: '#1275E2',
          600: '#0F62BF',
          700: '#0C4F9C',
          800: '#093D79',
          900: '#062A56',
          DEFAULT: '#1275E2',
        },
        // Slate: neutral cool gray (standard Tailwind)
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

        // ── Surface System (Warm Gallery-White) ──────────────────
        // Three-tier layering: surface → container-low → container-lowest
        'surface': '#fcf9f4',
        'surface-dim': '#e8e4df',
        'surface-bright': '#fdfaf5',
        'surface-container-lowest': '#ffffff',
        'surface-container-low': '#f6f3ee',
        'surface-container': '#f0ede8',
        'surface-container-high': '#eae7e2',
        'surface-container-highest': '#e4e1dc',

        // ── On-colors (text on surfaces) ─────────────────────────
        'on-surface': '#1c1c19',
        'on-surface-variant': '#4a4740',
        'on-primary': '#ffffff',
        'on-secondary': '#ffffff',
        'on-error': '#ffffff',

        // ── Outline (No-Line Rule: prefer tonal shifts) ──────────
        'outline': '#7a7770',
        'outline-variant': '#c9c5be',

        // Gray scale
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
        neutral: {
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
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
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
        'ios-focus': '0 0 0 3px rgba(18,117,226,0.3)',
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
        // Legacy aliases
        'ios-sm': '0.5rem',
        'ios': '0.75rem',
        'ios-md': '1rem',
        'ios-lg': '1rem',
        'ios-xl': '1.5rem',
        'ios-2xl': '2rem',
        'ios-3xl': '3rem',
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