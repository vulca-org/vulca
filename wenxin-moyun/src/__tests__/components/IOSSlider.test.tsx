import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { IOSSlider } from '@/components/ios'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, style, ...props }: any) => {
      const {
        whileTap, whileHover, transition, animate, initial,
        drag, dragConstraints, dragElastic, onDrag,
        ...domProps
      } = props
      return <div style={style} {...domProps}>{children}</div>
    },
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

// Mock animations utility
vi.mock('../../components/ios/utils/animations', () => ({
  iosAnimations: {
    spring: { type: 'spring', stiffness: 400, damping: 30 },
  },
}))

describe('IOSSlider', () => {
  it('should render without crashing', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} />
    )
    expect(container.firstChild).toBeTruthy()
  })

  it('should display label when provided', () => {
    render(
      <IOSSlider value={50} onChange={vi.fn()} label="Volume" />
    )
    expect(screen.getByText('Volume')).toBeInTheDocument()
  })

  it('should display formatted value when label is provided', () => {
    render(
      <IOSSlider value={75} onChange={vi.fn()} label="Brightness" />
    )
    // When label is present, the formatted value is shown next to the label
    expect(screen.getByText('75')).toBeInTheDocument()
  })

  it('should use formatValue function for display', () => {
    render(
      <IOSSlider
        value={42}
        onChange={vi.fn()}
        label="Opacity"
        formatValue={(v) => `${v}%`}
      />
    )
    expect(screen.getByText('42%')).toBeInTheDocument()
  })

  it('should apply size sm classes', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} size="sm" />
    )
    // sm track height is h-1
    expect(container.querySelector('.h-1')).toBeTruthy()
  })

  it('should apply size lg classes', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} size="lg" />
    )
    // lg track height is h-3
    expect(container.querySelector('.h-3')).toBeTruthy()
  })

  it('should apply color classes', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} color="green" />
    )
    expect(container.querySelector('.bg-emerald-600')).toBeTruthy()
  })

  it('should apply primary color by default', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} />
    )
    expect(container.querySelector('.bg-slate-600')).toBeTruthy()
  })

  it('should apply red color class', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} color="red" />
    )
    expect(container.querySelector('.bg-rose-600')).toBeTruthy()
  })

  it('should apply orange color class', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} color="orange" />
    )
    expect(container.querySelector('.bg-amber-600')).toBeTruthy()
  })

  it('should have disabled styling when disabled', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} disabled />
    )
    expect(container.querySelector('.opacity-50')).toBeTruthy()
    expect(container.querySelector('.cursor-not-allowed')).toBeTruthy()
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSSlider value={50} onChange={vi.fn()} className="my-slider" />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('my-slider')
  })

  it('should calculate correct percentage for active track width', () => {
    const { container } = render(
      <IOSSlider value={25} onChange={vi.fn()} min={0} max={100} />
    )
    // The active track is a div with style width: 25%
    const activeTrack = container.querySelector('[style*="width"]') as HTMLElement
    expect(activeTrack).toBeTruthy()
    expect(activeTrack.style.width).toBe('25%')
  })
})
