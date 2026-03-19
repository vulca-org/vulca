import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ThemeProvider } from '../../contexts/ThemeContext'
import { useTheme } from '../../contexts/useTheme'
import { themes, generateCSSVariables } from '../../config/theme'

// Mock storageUtils so we can control localStorage behavior
const mockStorage: Record<string, string> = {}
vi.mock('../../utils/storageUtils', () => ({
  getItem: vi.fn((key: string) => mockStorage[key] ?? null),
  setItem: vi.fn((key: string, value: string) => { mockStorage[key] = value }),
  removeItem: vi.fn((key: string) => { delete mockStorage[key] }),
}))

// Import the mocked functions for assertion
import { getItem, setItem } from '../../utils/storageUtils'

// Helper component that exposes theme context for testing
function ThemeConsumer() {
  const { theme, toggleTheme, setTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button data-testid="toggle-btn" onClick={toggleTheme}>Toggle</button>
      <button data-testid="set-dark-btn" onClick={() => setTheme('dark')}>Set Dark</button>
      <button data-testid="set-light-btn" onClick={() => setTheme('light')}>Set Light</button>
    </div>
  )
}

// Mock matchMedia
let matchMediaMatches = false
let matchMediaListeners: Array<(e: MediaQueryListEvent) => void> = []

function createMockMatchMedia(matches: boolean) {
  return (query: string): MediaQueryList => ({
    matches,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn((_event: string, handler: (e: MediaQueryListEvent) => void) => {
      matchMediaListeners.push(handler)
    }),
    removeEventListener: vi.fn((_event: string, handler: (e: MediaQueryListEvent) => void) => {
      matchMediaListeners = matchMediaListeners.filter(h => h !== handler)
    }),
    dispatchEvent: vi.fn(),
  })
}

describe('ThemeContext', () => {
  beforeEach(() => {
    // Clear mock storage
    Object.keys(mockStorage).forEach(key => delete mockStorage[key])

    // Reset call counts but preserve mock implementations
    vi.mocked(getItem).mockClear()
    vi.mocked(setItem).mockClear()

    // Re-apply implementations (clearAllMocks would strip them)
    vi.mocked(getItem).mockImplementation((key: string) => mockStorage[key] ?? null)
    vi.mocked(setItem).mockImplementation((key: string, value: string) => { mockStorage[key] = value })

    // Reset matchMedia
    matchMediaMatches = false
    matchMediaListeners = []
    window.matchMedia = createMockMatchMedia(matchMediaMatches)

    // Clean up document state
    document.documentElement.classList.remove('light', 'dark', 'theme-transition')
    const styleEl = document.getElementById('theme-variables')
    if (styleEl) styleEl.remove()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  // --- Default Initialization ---

  it('should default to light theme when no saved preference and system prefers light', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  it('should default to dark theme when system prefers dark', () => {
    window.matchMedia = createMockMatchMedia(true)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
  })

  // --- localStorage Persistence ---

  it('should restore saved theme from localStorage', () => {
    mockStorage['theme'] = 'dark'

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
    expect(getItem).toHaveBeenCalledWith('theme')
  })

  it('should save theme to localStorage on change', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    // Initial save (light)
    expect(setItem).toHaveBeenCalledWith('theme', 'light')

    // Toggle to dark
    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    expect(setItem).toHaveBeenCalledWith('theme', 'dark')
  })

  // --- Theme Toggle ---

  it('should toggle from light to dark', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
  })

  it('should toggle from dark to light', () => {
    mockStorage['theme'] = 'dark'

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  it('should cycle light -> dark -> light on successive toggles', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')

    act(() => { screen.getByTestId('toggle-btn').click() })
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')

    act(() => { screen.getByTestId('toggle-btn').click() })
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  // --- setTheme ---

  it('should set theme directly via setTheme', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    act(() => {
      screen.getByTestId('set-dark-btn').click()
    })

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
  })

  // --- Document Class Manipulation ---

  it('should add "light" class to documentElement for light theme', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(document.documentElement.classList.contains('light')).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('should add "dark" class to documentElement for dark theme', () => {
    mockStorage['theme'] = 'dark'

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(document.documentElement.classList.contains('light')).toBe(false)
  })

  it('should swap classes when toggling theme', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(document.documentElement.classList.contains('light')).toBe(true)

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(document.documentElement.classList.contains('light')).toBe(false)
  })

  // --- CSS Variable Generation ---

  it('should inject a style element with theme CSS variables', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    const styleEl = document.getElementById('theme-variables')
    expect(styleEl).not.toBeNull()
    expect(styleEl?.tagName).toBe('STYLE')
    expect(styleEl?.textContent).toContain(':root')
  })

  it('should include theme-specific CSS variables in the style element', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    const styleEl = document.getElementById('theme-variables')
    // Light theme bg.base is #fcf9f4
    expect(styleEl?.textContent).toContain('#fcf9f4')
  })

  it('should update CSS variables when theme changes', () => {
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    const styleEl = document.getElementById('theme-variables')
    expect(styleEl?.textContent).toContain('#fcf9f4') // light bg.base

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    // Dark theme bg.base is #0F0D0B
    expect(styleEl?.textContent).toContain('#0F0D0B')
    // Light bg color should no longer be present
    expect(styleEl?.textContent).not.toContain('#fcf9f4')
  })

  // --- Transition Animation ---

  it('should add theme-transition class during toggle and remove it after timeout', () => {
    vi.useFakeTimers()
    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    expect(document.documentElement.classList.contains('theme-transition')).toBe(true)

    act(() => {
      vi.advanceTimersByTime(300)
    })

    expect(document.documentElement.classList.contains('theme-transition')).toBe(false)
  })

  // --- System Preference Change Listener ---

  it('should follow system preference change when no manual theme is saved', () => {
    // No saved theme
    window.matchMedia = createMockMatchMedia(false)
    // Override getItem to always return null (no saved preference)
    vi.mocked(getItem).mockReturnValue(null)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')

    // Simulate system preference change to dark
    act(() => {
      matchMediaListeners.forEach(listener => {
        listener({ matches: true } as MediaQueryListEvent)
      })
    })

    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
  })

  it('should ignore system preference change when user has manually set theme', () => {
    mockStorage['theme'] = 'light'

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')

    // Simulate system preference change to dark
    act(() => {
      matchMediaListeners.forEach(listener => {
        listener({ matches: true } as MediaQueryListEvent)
      })
    })

    // Should remain light because user had manually saved a preference
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  // --- useTheme hook error ---

  it('should throw when useTheme is used outside ThemeProvider', () => {
    // Suppress React error boundary console output
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => {
      render(<ThemeConsumer />)
    }).toThrow('useTheme must be used within a ThemeProvider')

    consoleSpy.mockRestore()
  })

  // --- Meta theme-color ---

  it('should update meta theme-color when theme changes', () => {
    // Create a meta tag for theme-color
    const meta = document.createElement('meta')
    meta.setAttribute('name', 'theme-color')
    meta.setAttribute('content', '#ffffff')
    document.head.appendChild(meta)

    window.matchMedia = createMockMatchMedia(false)

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    )

    // Light theme bg.base
    expect(meta.getAttribute('content')).toBe(themes.light.bg.base)

    act(() => {
      screen.getByTestId('toggle-btn').click()
    })

    // Dark theme bg.base
    expect(meta.getAttribute('content')).toBe(themes.dark.bg.base)

    // Clean up
    meta.remove()
  })
})

// --- generateCSSVariables unit tests ---

describe('generateCSSVariables', () => {
  it('should generate CSS variables from theme object', () => {
    const result = generateCSSVariables(themes.dark)
    expect(result).toContain('--bg-base: #0F0D0B')
    expect(result).toContain('--text-primary: #F5F0EB')
  })

  it('should not include arrays in CSS variables', () => {
    const result = generateCSSVariables(themes.dark)
    // chart.series is an array and should be excluded
    expect(result).not.toContain('--chart-series')
  })

  it('should handle nested objects', () => {
    const result = generateCSSVariables(themes.light)
    expect(result).toContain('--bg-surface: #ffffff')
    expect(result).toContain('--semantic-primary: #1275E2')
    expect(result).toContain('--border-default: #e4e1dc')
  })

  it('should produce different variables for dark vs light themes', () => {
    const darkVars = generateCSSVariables(themes.dark)
    const lightVars = generateCSSVariables(themes.light)
    // Both should have the same variable names but different values
    expect(darkVars).toContain('--bg-base: #0F0D0B')
    expect(lightVars).toContain('--bg-base: #fcf9f4')
  })
})
