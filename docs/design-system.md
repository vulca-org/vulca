# VULCA Design System — Art Professional v1.0

Gallery-inspired warm color palette. iOS Human Interface Guidelines adapted with art-professional tones.

**Stack**: Tailwind CSS 4.1 + Framer Motion 12.23 + iOS HIG

---

## Color Palette

### Primary Colors

| Name | Light | Dark | Usage |
|------|-------|------|-------|
| **Ink Slate** | `#334155` | `#94A3B8` | Primary / text |
| **Warm Bronze** | `#C87F4A` | `#DDA574` | Accent / highlight |
| **Sage Green** | `#5F8A50` | `#87A878` | Success / positive |
| **Amber Gold** | `#B8923D` | `#D4A84B` | Warning / attention |
| **Coral Red** | `#C65D4D` | `#C97064` | Error / destructive |
| **Terracotta** | `#9B6B56` | `#C49976` | Secondary accent |
| **Patina Green** | `#6B8E7A` | — | Info / teal |

**Rule**: No blue, purple, or indigo from the standard iOS palette.

### Backgrounds

| Layer | Light | Dark | When |
|-------|-------|------|------|
| base | `#FAF7F2` | `#0F0D0B` | Page background |
| surface | `#FFFFFF` | `#1A1614` | Cards, panels |
| elevated | `#FFFFFF` | `#211D1A` | Floating elements |
| overlay | `#FFFFFF` | `#2A2521` | Dropdowns, menus |
| hover | `#F5F0E8` | `#342E28` | Interactive hover |
| active | `#EDE6DB` | `#3E3731` | Press / active state |

### Text

| Level | Light | Dark |
|-------|-------|------|
| primary | `#1E1B18` | `#F5F0EB` |
| secondary | `#524B44` | `#A89E94` |
| tertiary | `#7A726A` | `#7A726A` |
| muted | `#A89E94` | `#524B44` |

### Borders

| Level | Light | Dark |
|-------|-------|------|
| subtle | `#F0EBE3` | `#251F1B` |
| default | `#C9C2B8` | `#4A433C` |
| strong | `#9B9387` | `#6B6259` |
| focus | `#C87F4A` | `#DDA574` |

### Gradients

```
Brand:  linear-gradient(135deg, #334155, #C87F4A)  // Ink Slate → Warm Bronze
Gold:   linear-gradient(135deg, #D4A84B, #C87F4A)
Silver: linear-gradient(135deg, #94A3B8, #64748B)
Bronze: linear-gradient(135deg, #C87F4A, #9B6B56)
```

---

## Typography

### Font Stack

```
-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif
```

### Scale (iOS HIG)

| Style | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|-------------|----------------|
| Large Title | 34px | 700 | 41px | 0.374px |
| Title 1 | 28px | 700 | 34px | 0.364px |
| Title 2 | 22px | 700 | 28px | 0.352px |
| Title 3 | 20px | 600 | 25px | 0.38px |
| Headline | 17px | 600 | 22px | -0.408px |
| Body | 17px | 400 | 22px | -0.408px |
| Callout | 16px | 400 | 21px | -0.32px |
| Subheadline | 15px | 400 | 20px | -0.24px |
| Footnote | 13px | 400 | 18px | -0.078px |
| Caption 1 | 12px | 400 | 16px | 0px |
| Caption 2 | 11px | 400 | 13px | 0.066px |

### Responsive Headings

| Class | Desktop | Tablet (<1024px) | Mobile (<640px) |
|-------|---------|------------------|-----------------|
| `.text-large-title` | 60px | 48px | 36px |
| `.text-page-title` | 48px | 42px | 32px |
| `.text-h1` | 36px | 30px | 24px |
| `.text-h2` | 30px | 24px | 20px |
| `.text-h3` | 24px | 20px | 18px |

---

## Spacing

```
xs: 4px    sm: 8px    md: 12px   lg: 16px
xl: 20px   2xl: 24px  3xl: 32px  4xl: 40px
```

## Border Radius

```
xs: 4px   sm: 6px   md: 8px    lg: 12px
xl: 14px  2xl: 20px  full: 9999px
```

## Breakpoints

```
xs: 475px   sm: 640px   md: 768px   lg: 1024px
xl: 1280px  2xl: 1536px  3xl: 1920px
```

---

## Components

### IOSButton

```tsx
<IOSButton variant="primary" size="md">Label</IOSButton>
```

| Variant | Usage |
|---------|-------|
| `primary` | Main CTA (Ink Slate bg) |
| `secondary` | Secondary action (bordered) |
| `destructive` | Delete/danger (Coral Red) |
| `glass` | Glass morphism overlay |
| `text` | Text-only link style |

| Size | Height | Padding |
|------|--------|---------|
| `sm` | 44px min | `px-4 py-2.5` |
| `md` | 44px min | `px-5 py-3` |
| `lg` | 52px min | `px-7 py-4` |

Interaction: `whileTap={{ scale: 0.96 }}`, ripple effect, haptic feedback.

### IOSCard

```tsx
<IOSCard variant="elevated" padding="md" interactive>
  <IOSCardHeader title="Title" />
  <IOSCardContent>...</IOSCardContent>
  <IOSCardFooter>...</IOSCardFooter>
</IOSCard>
```

| Variant | Visual |
|---------|--------|
| `flat` | No shadow, minimal |
| `elevated` | Shadow + white bg |
| `glass` | Glass morphism |
| `bordered` | Border + no shadow |

### IOSAlert

```tsx
<IOSAlert
  visible={show}
  onClose={close}
  type="error"
  title="Title"
  message="Message"
  actions={[
    { label: 'OK', onPress: handler, style: 'default' },
    { label: 'Cancel', onPress: close, style: 'cancel' },
  ]}
/>
```

Types: `info` | `success` | `warning` | `error`

### IOSSegmentedControl

```tsx
<IOSSegmentedControl
  segments={['Tab 1', 'Tab 2']}
  selectedIndex={0}
  onChange={setIndex}
  size="compact"
/>
```

Sizes: `compact` (44px) | `regular` (44px) | `large` (48px)

### IOSToggle

```tsx
<IOSToggle checked={on} onChange={setOn} color="green" size="md" label="Label" />
```

### IOSSlider

```tsx
<IOSSlider value={val} onChange={setVal} min={0} max={100} showValue label="Volume" />
```

### IOSSheet

Bottom sheet with drag-to-dismiss. Heights: `small` (40vh) | `medium` (60vh) | `large` (90vh).

---

## Glass Morphism

### Blur Levels

| Level | Effect |
|-------|--------|
| light | `backdrop-blur-sm backdrop-saturate-200` |
| medium | `backdrop-blur-md backdrop-saturate-150` |
| heavy | `backdrop-blur-lg backdrop-saturate-180` |
| ultra | `backdrop-blur-xl backdrop-saturate-200` |

### Glass Containers

```css
/* Card glass */
bg-white/25 dark:bg-white/18 backdrop-blur-md backdrop-saturate-150
border border-white/12 dark:border-white/8

/* Sheet glass */
bg-white/40 dark:bg-black/60 backdrop-blur-xl backdrop-saturate-200
border-t border-white/18

/* Navigation glass */
bg-white/60 dark:bg-black/80 backdrop-blur-xl backdrop-saturate-200
```

### CSS Classes

- `.ios-glass` — Standard glass (blur 30px, saturate 200%)
- `.liquid-glass-container` — Enhanced glass (blur 20px, inner shadow)
- `.liquid-glass-hero` — Maximum glass (blur 40px)

---

## Animation

### Spring Physics

| Preset | Stiffness | Damping | Use |
|--------|-----------|---------|-----|
| default | 400 | 30 | General interactions |
| bounce | 300 | 20 | Playful feedback |
| smooth | 500 | 40 | Subtle transitions |
| modal | 300 | 25 | Modal presentations |

### Interaction

```tsx
// Button
whileTap={{ scale: 0.96 }}  // 100ms ease-out
whileHover={{ y: -1 }}       // 200ms ease-out

// Card
whileHover={{ scale: 1.02, rotateX: -2 }}
```

### Entrance

| Pattern | Initial | Animate | Duration |
|---------|---------|---------|----------|
| fadeIn | opacity: 0 | opacity: 1 | 200ms |
| fadeInUp | opacity: 0, y: 10 | opacity: 1, y: 0 | 300ms |
| fadeInScale | opacity: 0, scale: 0.95 | opacity: 1, scale: 1 | 200ms |
| slideInRight | x: 100% | x: 0 | spring |

### Stagger

- List items: 50ms between each
- Grid items: 100ms between each
- Page hero elements: 200ms between each

---

## Dark Mode

**Mechanism**: CSS class-based (`<html class="dark">`).

- Reads `localStorage.getItem('theme')`, falls back to `prefers-color-scheme`
- 300ms transition on toggle (`background-color`, `color`, `border-color`)
- Respects `prefers-reduced-motion`
- Meta `theme-color` updates: light `#FAF7F2`, dark `#0F0D0B`

---

## Chart Colors

### 6D Dimension Mapping

| Dimension | Light | Dark |
|-----------|-------|------|
| Creativity | `#C87F4A` | `#DDA574` |
| Technical | `#5F8A50` | `#87A878` |
| Emotional | `#B35A50` | `#C97064` |
| Contextual | `#64748B` | `#94A3B8` |
| Innovation | `#B8923D` | `#D4A84B` |
| Impact | `#9B6B56` | `#C49976` |

### Palette (8 colors)

Light: `#C87F4A #9B6B56 #5F8A50 #B8923D #64748B #B35A50 #8F7860 #4A7A46`

Dark: `#DDA574 #C49976 #87A878 #D4A84B #94A3B8 #C97064 #B8A089 #7A9B76`

---

## Key Files

| File | Purpose |
|------|---------|
| `src/components/ios/utils/iosTheme.ts` | Core design tokens |
| `src/components/ios/utils/animations.ts` | Motion presets |
| `src/config/theme.ts` | Light/dark theme objects |
| `src/config/chartTheme.ts` | Chart-specific colors |
| `src/index.css` | CSS variables + utility classes |
| `tailwind.config.js` | Tailwind extensions |
| `src/components/ios/index.ts` | Component barrel export |
