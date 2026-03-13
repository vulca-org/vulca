import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { IOSSegmentedControl } from '@/components/ios'
import type { SegmentItem } from '@/components/ios'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, style, ...props }: any) => {
      const {
        whileTap, whileHover, transition, animate, initial,
        ...domProps
      } = props
      return <div style={style} {...domProps}>{children}</div>
    },
    button: ({ children, ...props }: any) => {
      const {
        whileTap, whileHover, transition, animate, initial,
        ...domProps
      } = props
      return <button {...domProps}>{children}</button>
    },
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

// Mock iosTheme utility
vi.mock('../../components/ios/utils/iosTheme', () => ({
  liquidGlass: {
    opacity: { regular: 'opacity-class' },
    borders: { regular: 'border-class', subtle: 'border-subtle' },
  },
}))

// Mock animations utility
vi.mock('../../components/ios/utils/animations', () => ({
  iosAnimations: {
    spring: { type: 'spring', stiffness: 400, damping: 30 },
  },
}))

// Mock EmojiIcon
vi.mock('@/components/ios/core/EmojiIcon', () => ({
  EmojiIcon: ({ category, name, size }: any) => (
    <span data-testid={`emoji-${name}`}>{name}</span>
  ),
}))

describe('IOSSegmentedControl', () => {
  it('should render all segment labels from string array', () => {
    render(
      <IOSSegmentedControl
        segments={['Tab 1', 'Tab 2', 'Tab 3']}
        selectedIndex={0}
        onChange={vi.fn()}
      />
    )
    expect(screen.getByText('Tab 1')).toBeInTheDocument()
    expect(screen.getByText('Tab 2')).toBeInTheDocument()
    expect(screen.getByText('Tab 3')).toBeInTheDocument()
  })

  it('should render segment labels from SegmentItem objects', () => {
    const segments: SegmentItem[] = [
      { id: 'a', label: 'Alpha' },
      { id: 'b', label: 'Beta' },
    ]
    render(
      <IOSSegmentedControl
        segments={segments}
        selectedIndex={0}
        onChange={vi.fn()}
      />
    )
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.getByText('Beta')).toBeInTheDocument()
  })

  it('should call onChange with correct index when segment is clicked', () => {
    const handleChange = vi.fn()
    render(
      <IOSSegmentedControl
        segments={['One', 'Two', 'Three']}
        selectedIndex={0}
        onChange={handleChange}
      />
    )
    fireEvent.click(screen.getByText('Two'))
    expect(handleChange).toHaveBeenCalledWith(1, expect.objectContaining({ label: 'Two' }))
  })

  it('should highlight the selected segment with selected class', () => {
    render(
      <IOSSegmentedControl
        segments={['First', 'Second']}
        selectedIndex={1}
        onChange={vi.fn()}
      />
    )
    const secondBtn = screen.getByText('Second').closest('button') as HTMLElement
    // The selected segment gets the selected style class (e.g., shadow-sm for 'filled')
    expect(secondBtn.className).toContain('shadow-sm')
  })

  it('should apply compact size classes', () => {
    const { container } = render(
      <IOSSegmentedControl
        segments={['A', 'B']}
        selectedIndex={0}
        onChange={vi.fn()}
        size="compact"
      />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('h-11')
  })

  it('should apply large size classes', () => {
    const { container } = render(
      <IOSSegmentedControl
        segments={['A', 'B']}
        selectedIndex={0}
        onChange={vi.fn()}
        size="large"
      />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('h-12')
  })

  it('should apply plain style classes', () => {
    const { container } = render(
      <IOSSegmentedControl
        segments={['X', 'Y']}
        selectedIndex={0}
        onChange={vi.fn()}
        style="plain"
      />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('bg-transparent')
  })

  it('should not trigger onChange when segment is disabled', () => {
    const handleChange = vi.fn()
    const segments: SegmentItem[] = [
      { id: 'a', label: 'Active' },
      { id: 'b', label: 'Disabled', disabled: true },
    ]
    render(
      <IOSSegmentedControl
        segments={segments}
        selectedIndex={0}
        onChange={handleChange}
      />
    )
    fireEvent.click(screen.getByText('Disabled'))
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('should not trigger onChange when entire control is disabled', () => {
    const handleChange = vi.fn()
    render(
      <IOSSegmentedControl
        segments={['One', 'Two']}
        selectedIndex={0}
        onChange={handleChange}
        disabled
      />
    )
    fireEvent.click(screen.getByText('Two'))
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('should render icon in segments when provided', () => {
    const segments: SegmentItem[] = [
      { id: 'a', label: 'With Icon', icon: <span data-testid="seg-icon">IC</span> },
    ]
    render(
      <IOSSegmentedControl
        segments={segments}
        selectedIndex={0}
        onChange={vi.fn()}
      />
    )
    expect(screen.getByTestId('seg-icon')).toBeInTheDocument()
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSSegmentedControl
        segments={['A', 'B']}
        selectedIndex={0}
        onChange={vi.fn()}
        className="my-segmented"
      />
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toContain('my-segmented')
  })
})
