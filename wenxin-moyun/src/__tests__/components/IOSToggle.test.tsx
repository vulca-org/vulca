import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { IOSToggle } from '@/components/ios'

// Mock framer-motion to avoid animation complexity in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => {
      const { whileTap, transition, animate, initial, ...domProps } = props
      return <div {...domProps}>{children}</div>
    },
    button: ({ children, ...props }: any) => {
      const { whileTap, transition, animate, initial, ...domProps } = props
      return <button {...domProps}>{children}</button>
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

describe('IOSToggle', () => {
  it('should render without crashing', () => {
    const { container } = render(
      <IOSToggle checked={false} onChange={vi.fn()} />
    )
    expect(container.firstChild).toBeTruthy()
  })

  it('should display label text when provided', () => {
    render(
      <IOSToggle checked={false} onChange={vi.fn()} label="Enable Notifications" />
    )
    expect(screen.getByText('Enable Notifications')).toBeInTheDocument()
  })

  it('should display description when provided', () => {
    render(
      <IOSToggle
        checked={false}
        onChange={vi.fn()}
        label="Dark Mode"
        description="Switch to dark theme"
      />
    )
    expect(screen.getByText('Switch to dark theme')).toBeInTheDocument()
  })

  it('should call onChange when clicked (toggling checked state)', () => {
    const handleChange = vi.fn()
    const { container } = render(
      <IOSToggle checked={false} onChange={handleChange} />
    )
    // Click the toggle wrapper (motion.div rendered as div)
    fireEvent.click(container.firstChild as HTMLElement)
    expect(handleChange).toHaveBeenCalledWith(true)
  })

  it('should call onChange with false when checked and clicked', () => {
    const handleChange = vi.fn()
    const { container } = render(
      <IOSToggle checked={true} onChange={handleChange} />
    )
    fireEvent.click(container.firstChild as HTMLElement)
    expect(handleChange).toHaveBeenCalledWith(false)
  })

  it('should NOT call onChange when disabled', () => {
    const handleChange = vi.fn()
    const { container } = render(
      <IOSToggle checked={false} onChange={handleChange} disabled />
    )
    fireEvent.click(container.firstChild as HTMLElement)
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('should apply opacity-50 class when disabled', () => {
    const { container } = render(
      <IOSToggle checked={false} onChange={vi.fn()} disabled />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('opacity-50')
  })

  it('should apply correct color class when checked (green)', () => {
    const { container } = render(
      <IOSToggle checked={true} onChange={vi.fn()} color="green" />
    )
    // The inner track div should have the emerald color
    const trackDiv = container.querySelector('.bg-emerald-600')
    expect(trackDiv).toBeTruthy()
  })

  it('should apply correct color class when checked (orange)', () => {
    const { container } = render(
      <IOSToggle checked={true} onChange={vi.fn()} color="orange" />
    )
    const trackDiv = container.querySelector('.bg-amber-600')
    expect(trackDiv).toBeTruthy()
  })

  it('should apply correct color class when checked (red)', () => {
    const { container } = render(
      <IOSToggle checked={true} onChange={vi.fn()} color="red" />
    )
    const trackDiv = container.querySelector('.bg-rose-600')
    expect(trackDiv).toBeTruthy()
  })

  it('should apply correct color class when checked (primary)', () => {
    const { container } = render(
      <IOSToggle checked={true} onChange={vi.fn()} color="primary" />
    )
    const trackDiv = container.querySelector('.bg-slate-600')
    expect(trackDiv).toBeTruthy()
  })

  it('should apply bg-gray-300 when unchecked', () => {
    const { container } = render(
      <IOSToggle checked={false} onChange={vi.fn()} color="green" />
    )
    const trackDiv = container.querySelector('.bg-gray-300')
    expect(trackDiv).toBeTruthy()
  })

  it('should apply size classes for sm', () => {
    const { container } = render(
      <IOSToggle checked={false} onChange={vi.fn()} size="sm" />
    )
    // sm size uses w-10 h-6 for the track
    expect(container.querySelector('.w-10')).toBeTruthy()
    expect(container.querySelector('.h-6')).toBeTruthy()
  })

  it('should apply size classes for lg', () => {
    const { container } = render(
      <IOSToggle checked={false} onChange={vi.fn()} size="lg" />
    )
    // lg size uses w-14 h-8 for the track
    expect(container.querySelector('.w-14')).toBeTruthy()
    expect(container.querySelector('.h-8')).toBeTruthy()
  })

  it('should render left icon when provided', () => {
    render(
      <IOSToggle
        checked={false}
        onChange={vi.fn()}
        leftIcon={<span data-testid="left-icon">L</span>}
      />
    )
    expect(screen.getByTestId('left-icon')).toBeInTheDocument()
  })

  it('should render right icon when provided', () => {
    render(
      <IOSToggle
        checked={false}
        onChange={vi.fn()}
        rightIcon={<span data-testid="right-icon">R</span>}
      />
    )
    expect(screen.getByTestId('right-icon')).toBeInTheDocument()
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSToggle
        checked={false}
        onChange={vi.fn()}
        className="my-custom-toggle"
      />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('my-custom-toggle')
  })

  it('should also call onChange when label is clicked', () => {
    const handleChange = vi.fn()
    render(
      <IOSToggle checked={false} onChange={handleChange} label="Click Label" />
    )
    fireEvent.click(screen.getByText('Click Label'))
    expect(handleChange).toHaveBeenCalledWith(true)
  })
})
