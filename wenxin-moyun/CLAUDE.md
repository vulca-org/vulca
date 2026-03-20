# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VULCA — a **creation organism** where generation, evaluation, refinement, and learning are seamless stages of one creative process. The core product is **Canvas** (unified creation + evaluation), not the leaderboard. React 19 frontend with **Digital Curator design system** (v2.0), FastAPI backend with async AI pipeline (Scout->Draft->Critic->Queen), and production GCP deployment.

### Digital Curator Design System (v2.0, 2026-03-19)

Bridges "Tech Trust" (Blue) with "Cultural Artistry" (Bronze & Cream). Reference: `vulca_ethos/DESIGN.md`.

- **Color System**: Primary Blue `#1275E2` | Bronze `#C87F4A` | Sage Green `#5F8A50` | Amber Gold `#B8923D` | Coral Red `#C65D4D`
- **Surface System**: Gallery White `#fcf9f4` (base) → `#f6f3ee` (sections) → `#ffffff` (cards)
- **Typography**: Noto Serif (headlines ≥24px, "gallery voice") + Inter (body/UI, "tech clarity")
- **Component System**: IOSButton, IOSCard, IOSToggle, IOSSlider, IOSAlert (retained naming)
- **Glass Morphism**: Liquid Glass effects with warm tint (bg-base: #fcf9f4 Gallery White)
- **Dark Mode**: Full dark palette (Light Blue #AAC8F4, Light Bronze #DDA574)
- **No-Line Rule**: No 1px borders — use tonal shifts and negative space
- **Radius**: 16px cards | 24px buttons | 48px hero containers
- **Shadows**: Warm ambient `rgba(28,28,25,0.06)` — never black opacity
- **Canvas V2**: AI Collective sidebar + Artwork HUD + Intelligence Log + L1-L5 Maturity Panel

## Essential Commands

```bash
# Development
npm run dev          # Start dev server on http://localhost:5173 (or next available port)

# Build & Production
npm run build        # TypeScript check + Vite build
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint checks

# Testing (Playwright E2E)
npm run test:e2e              # Run E2E tests headless
npm run test:e2e:ui           # Run tests with UI mode
npm run test:e2e:debug        # Debug tests step by step
npm run test:e2e:headed       # Run tests in headed browser
npm run test:e2e:report       # Show test report
```

## Architecture Overview

### Tech Stack
- **Frontend**: React 19 + TypeScript 5.8
- **Build**: Vite 7.1 
- **Styling**: Tailwind CSS 4.1 with **pure iOS design tokens**
- **Design System**: **Complete iOS Component System** with Fluent Emoji integration
- **Routing**: React Router DOM 7.8
- **State Management**: Zustand 4.4 (lightweight store)
- **Animations**: Framer Motion 12.23 (iOS spring physics)
- **Charts**: Recharts 3.1
- **Icons**: Microsoft Fluent Emoji (60+ SVG)
- **Testing**: Playwright (E2E testing framework)

### Core Type System

All types are defined in `src/types/types.ts`. Key interfaces:
- `Model`: AI model with metrics, works, and metadata
- `ModelMetrics`: 6 evaluation dimensions (rhythm, composition, narrative, emotion, creativity, cultural)
- `Battle`: Model comparison and voting system
- `LeaderboardEntry`: Ranking data with win rates

**Important**: Always use `import type` for TypeScript types to avoid runtime issues.

### Component Architecture

```
Layout (wraps all pages with Header/Footer)
  └── Pages (route-level components)
       └── iOS Components (src/components/ios/)
            ├── Core Components (IOSButton, IOSCard, IOSToggle, IOSSlider, IOSAlert)
            ├── Emoji System (EmojiIcon, StatusEmoji, RankEmoji, TypeEmoji)
            ├── Utils (iosTheme.ts, animations.ts, emojiMap.ts)
            └── Adapter Layer (ChineseButton → IOSButton compatibility)
       └── Feature Components (evaluation/, auth/, charts/)
            └── Legacy Components (being phased out)
       └── Prototype Editor (src/components/prototype/editor/)
            ├── PipelineEditor.tsx          # Main canvas (ReactFlow)
            ├── AgentNode.tsx               # Scout/Draft/Critic/Queen nodes
            ├── SkillNode.tsx + SkillBrowser.tsx  # Skill marketplace
            ├── SubStageNode.tsx            # Sub-stage expansion
            ├── TypedEdge.tsx + TypedHandle.tsx  # 21 DataType connections
            ├── inputNodes/ (7)             # Sketch, Reference, Mask, Text, Script, Model, Audio
            ├── processingNodes/ (7)        # Style, Color, Composition, Upscale, Depth, Edge, Element
            ├── flowNodes/ (5)              # IfElse, Loop, Merge, Split, Gate
            ├── outputNodes/ (4)            # Save, Gallery, Export, Compare
            ├── inlinePreviews/ (3)         # Draft, Critic, Queen inline views
            ├── FrameNode, RerouteNode, StickyNote, ReportNode  # Utility nodes
            ├── CanvasToolbar, NodeSearchPopup, EvolutionBadge  # UI panels
            └── NodeParamPanel, TemplateGallery, TraditionWeightGrid  # Config panels
```

## iOS Component System

### Core Components

**IOSButton** - Native iOS button with glass morphism and haptic feedback simulation
```typescript
<IOSButton 
  variant="primary" // primary | secondary | destructive | glass | text
  size="md"         // sm | md | lg
  emoji="like"      // Fluent Emoji integration
  glassMorphism={true}
  disabled={false}
>
  Button Text
</IOSButton>
```

**IOSCard** - Container with multiple variants and structured content
```typescript
<IOSCard variant="elevated" interactive animate>
  <IOSCardHeader 
    title="Card Title"
    subtitle="Optional subtitle"
    emoji={<TypeEmoji type="painting" size="lg" />}
    action={<StatusEmoji status="completed" animated />}
  />
  <IOSCardContent>
    <p>Card content goes here</p>
  </IOSCardContent>
  <IOSCardFooter>
    <IOSButton>Action</IOSButton>
  </IOSCardFooter>
</IOSCard>
```

**IOSToggle** - iOS-style switches with multiple colors and sizes
```typescript
<IOSToggle
  checked={value}
  onChange={setValue}
  color="green"     // primary | green | orange | red
  size="md"         // sm | md | lg
  label="Enable Feature"
  description="Detailed description"
/>
```

**IOSSlider** - Interactive value sliders with custom formatting
```typescript
<IOSSlider
  value={sliderValue}
  onChange={setSliderValue}
  min={0}
  max={100}
  step={1}
  color="primary"
  showValue={true}
  label="Volume"
  formatValue={(v) => `${v}%`}
/>
```

**IOSAlert** - Modal alerts with backdrop blur and native animations
```typescript
<IOSAlert
  visible={showAlert}
  onClose={() => setShowAlert(false)}
  type="info"       // info | success | warning | error
  title="Alert Title"
  message="Alert message text"
  actions={[
    { label: "Cancel", onPress: onCancel, style: "cancel" },
    { label: "Confirm", onPress: onConfirm, style: "default" }
  ]}
/>
```

### Emoji System

**Fluent Emoji Integration** - 60+ Microsoft Fluent Emoji SVGs with semantic categorization

```typescript
// Status-based emojis
<StatusEmoji status="pending" size="lg" animated />    // ⏱️
<StatusEmoji status="processing" size="md" />          // ⚙️
<StatusEmoji status="completed" size="sm" />           // ✅
<StatusEmoji status="failed" />                        // ❌

// Ranking emojis
<RankEmoji rank={1} size="lg" />                       // 🥇
<RankEmoji rank={2} size="md" />                       // 🥈
<RankEmoji rank={3} size="sm" />                       // 🥉

// Content type emojis
<TypeEmoji type="poem" size="lg" />                    // 📝
<TypeEmoji type="painting" size="md" />                // 🎨
<TypeEmoji type="music" size="sm" />                   // 🎵

// Generic emoji with animation
<EmojiIcon 
  category="actions" 
  name="like" 
  size="md" 
  animated 
  animationType="pulse" 
/>
```

### Theme System

**Art Professional Design Tokens** (`src/components/ios/utils/iosTheme.ts`)
```typescript
export const iosColors = {
  blue: '#334155',      // Ink Slate — primary
  green: '#5F8A50',     // Sage Green — success
  orange: '#B8923D',    // Amber Gold — warning
  purple: '#C87F4A',    // Warm Bronze — accent
  red: '#C65D4D',       // Coral Red — destructive
  teal: '#6B8E7A',      // Patina Green — info
}

export const iosShadows = {
  sm: '0 1px 2px rgba(0,0,0,0.05)',
  md: '0 4px 6px rgba(0,0,0,0.07)',
  lg: '0 10px 15px rgba(0,0,0,0.1)',
  xl: '0 20px 25px rgba(0,0,0,0.15)',
}
```

**iOS Animation Presets** (`src/components/ios/utils/animations.ts`)
```typescript
export const iosAnimations = {
  spring: {
    type: 'spring',
    stiffness: 400,
    damping: 30,
  },
  buttonTap: { scale: 0.96 },
  cardHover: { scale: 1.02, rotateX: -2 },
}
```

### Migration Patterns

**Backward Compatibility** - Seamless migration from Chinese components
```typescript
// Old usage (still works)
import { ChineseButton } from '../components/common/ChineseButton';

// New usage (recommended)
import { IOSButton } from '../components/ios';

// Adapter pattern ensures compatibility
export { IOSButton as ChineseButton } from './core/IOSButton';
```

### Test Page
Visit `/test-ios` to see comprehensive component demonstrations and interactive examples.

## Critical Implementation Details

### React 19 Compatibility
- Uses native `crypto.randomUUID()` for guest session IDs
- Compatible with strict TypeScript 5.8 configuration
- Leverages React 19's improved concurrent features

### Tailwind CSS v4 Setup
```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
plugins: [react(), tailwindcss()]

// index.css - v4 import syntax
@import 'tailwindcss';  // NOT @tailwind directives
```

### State Management Architecture
- **Zustand stores**: UI state, filters, preferences
- **React hooks**: Custom hooks abstract business logic
- **Component state**: Local form state and UI interactions
- **Mock data**: Static data in `src/data/mockData.ts` for development

### Responsive Design System
- **Mobile-first**: 375px baseline with touch-friendly 44px targets
- **Breakpoints**: `md: 768px`, `lg: 1024px`, `xl: 1200px`
- **Dynamic orbs**: Floating background animations preserved across themes
- **Glass morphism**: Uses backdrop-blur and opacity layering

### Routing Structure

**Core (must work):**
- `/` - Home page
- `/canvas` - Creation + evaluation (THE PRODUCT)
- `/gallery` - Creation results display

**Auth (outside Layout):**
- `/login` - User login
- `/register` - User registration (auto-login on success)

**Support:**
- `/vulca` - L1-L5 visualization
- `/methodology`, `/about` - How it works
- `/admin` - System monitoring

**Academic (preserved, deprioritized):**
- `/leaderboard[/:category]` - Model rankings (paper reference)
- `/battle` - Model comparison (paper reference)
- `/model/:id` - Model detail with radar chart and works
- `/evaluations` - Redirects to `/canvas`

### Product Focus

- **Canvas** is the core product page: users create, evaluate, refine, and learn in one unified session
- **Gallery** displays Canvas output (creations, evaluations, community works)
- **Leaderboard** and **Battle** are academic legacy from EMNLP papers — preserved for paper references but not the product focus
- ~25 of the 80+ backend API endpoints serve the leaderboard system; new development should prioritize Canvas and Gallery endpoints
- The creation pipeline (Scout -> Draft -> Critic -> Queen) powers Canvas, not the leaderboard

### Data Flow

Currently using static mock data (`src/data/mockData.ts`). No state management library yet - uses React local state and prop drilling. Data structure is designed to easily transition to API integration.

### Styling Approach

- Tailwind CSS with custom configuration
- Custom utility classes: `gradient-text`, `glass-effect`
- Dark mode CSS classes prepared (not togglable yet)
- Responsive grid system with mobile-first approach

## Common Development Patterns

### Adding New Models
Edit `src/data/mockData.ts` and add to `mockModels` array with all required fields per `Model` interface.

### Creating New Pages
1. Add page component in `src/pages/`
2. Add route in `App.tsx`
3. Update navigation in `Header.tsx` if needed

### Component Conventions
- Use functional components with TypeScript
- Props interfaces defined inline or in component file
- Framer Motion for page transitions
- Tailwind classes for styling (no separate CSS files)

## Known Issues & Solutions

### Module Import Errors
If you encounter "module does not provide export" errors:
1. Clear Vite cache: `rm -rf node_modules/.vite`
2. Use `import type` for TypeScript types
3. Restart dev server

### Port Conflicts
Dev server auto-increments ports if 5173 is taken. Check console output for actual port.

### PostCSS/Tailwind Issues
Configuration uses `@tailwindcss/postcss` plugin. If CSS errors occur, verify `postcss.config.js` has correct plugin path.

## Project Goals & Roadmap

**Current Phase**: Canvas-first creation organism
- ✅ Leaderboard system (academic legacy)
- ✅ Model comparison (academic legacy)
- ✅ Responsive design
- ✅ Art Professional design system
- ✅ Creation pipeline (Scout -> Draft -> Critic -> Queen)
- ✅ Multimodal type system (image, video, 3D, sound)

**Next Phases**:
- Canvas page polish and production readiness
- Gallery with community creation display
- Digestion system integration (cultural emergence)
- Evolved context injection into creation pipeline

## Test Accounts
- Demo: `demo` / `demo123`
- Admin: `admin` / `admin123`

## Key Files
- Application entry: `src/App.tsx`
- Type definitions: `src/types/types.ts`
- Tailwind config: `tailwind.config.js`
- GitHub Actions: `.github/workflows/deploy-gcp.yml`