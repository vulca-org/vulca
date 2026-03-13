import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

// Mock framer-motion before importing component
vi.mock('framer-motion', () => {
  const createMotionComponent = (tag: string) => {
    return ({ children, ...props }: Record<string, unknown>) => {
      // Filter out framer-motion-specific props
      const {
        initial, animate, exit, whileHover, whileTap,
        variants, transition, layout, layoutId,
        onAnimationComplete, onAnimationStart,
        ...domProps
      } = props
      const Component = tag as unknown as React.ElementType
      return <Component {...domProps}>{children as React.ReactNode}</Component>
    }
  }
  return {
    motion: {
      div: createMotionComponent('div'),
      span: createMotionComponent('span'),
      button: createMotionComponent('button'),
      p: createMotionComponent('p'),
      a: createMotionComponent('a'),
      ul: createMotionComponent('ul'),
      li: createMotionComponent('li'),
      h1: createMotionComponent('h1'),
      h2: createMotionComponent('h2'),
      h3: createMotionComponent('h3'),
      section: createMotionComponent('section'),
      nav: createMotionComponent('nav'),
      main: createMotionComponent('main'),
      img: createMotionComponent('img'),
    },
    AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    useAnimation: () => ({ start: vi.fn(), stop: vi.fn() }),
    useInView: () => true,
  }
})

import React from 'react'
import { EmojiIcon, StatusEmoji, RankEmoji, TypeEmoji } from '@/components/ios'

describe('EmojiIcon', () => {
  it('should render an emoji for a known category and name', () => {
    render(<EmojiIcon category="status" name="completed" />)
    expect(screen.getByText('✅')).toBeInTheDocument()
  })

  it('should render fallback emoji for an unknown name', () => {
    render(<EmojiIcon category="status" name="nonexistent" />)
    // fallback is ✨
    expect(screen.getByText('✨')).toBeInTheDocument()
  })

  it('should render different emojis for different categories', () => {
    const { unmount } = render(<EmojiIcon category="rank" name="1" />)
    expect(screen.getByText('🥇')).toBeInTheDocument()
    unmount()

    render(<EmojiIcon category="evaluationType" name="painting" />)
    expect(screen.getByText('🎨')).toBeInTheDocument()
  })

  it('should apply default size (md) class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-6')
    expect(span?.className).toContain('h-6')
  })

  it('should apply xs size class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="xs" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-4')
    expect(span?.className).toContain('h-4')
  })

  it('should apply sm size class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="sm" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-5')
    expect(span?.className).toContain('h-5')
  })

  it('should apply lg size class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="lg" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-8')
    expect(span?.className).toContain('h-8')
  })

  it('should apply xl size class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="xl" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-10')
    expect(span?.className).toContain('h-10')
  })

  it('should apply 2xl size class', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="2xl" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-12')
    expect(span?.className).toContain('h-12')
  })

  it('should apply inline font size for different sizes', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" size="lg" />)
    const span = container.querySelector('span')
    expect(span?.style.fontSize).toBe('28px')
  })

  it('should forward custom className', () => {
    const { container } = render(<EmojiIcon category="status" name="pending" className="my-class" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('my-class')
  })

  it('should fire onClick callback when clicked', () => {
    const handleClick = vi.fn()
    const { container } = render(<EmojiIcon category="status" name="completed" onClick={handleClick} />)
    // The inner div (motion.div) has class "inline-flex items-center justify-center"
    // The outer div has class "relative inline-flex"
    const innerDiv = container.querySelector('.relative.inline-flex > div')
    expect(innerDiv).not.toBeNull()
    if (innerDiv) fireEvent.click(innerDiv)
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('should apply cursor-pointer class when interactive', () => {
    const { container } = render(<EmojiIcon category="status" name="completed" interactive />)
    const motionDiv = container.querySelector('.cursor-pointer')
    expect(motionDiv).toBeInTheDocument()
  })

  it('should not apply cursor-pointer when not interactive', () => {
    const { container } = render(<EmojiIcon category="status" name="completed" />)
    const motionDiv = container.querySelector('.cursor-pointer')
    expect(motionDiv).toBeNull()
  })

  it('should render tooltip text when showTooltip is true and hovered', () => {
    const { container } = render(<EmojiIcon category="status" name="completed" showTooltip />)
    // Target the inner motion.div (direct child of .relative.inline-flex)
    const innerDiv = container.querySelector('.relative.inline-flex > div')
    expect(innerDiv).not.toBeNull()
    if (innerDiv) {
      fireEvent.mouseEnter(innerDiv)
    }
    // The tooltip should show the name
    expect(screen.getByText('completed')).toBeInTheDocument()
  })

  it('should hide tooltip when mouse leaves', () => {
    const { container } = render(<EmojiIcon category="status" name="completed" showTooltip />)
    const innerDiv = container.querySelector('.relative.inline-flex > div')
    expect(innerDiv).not.toBeNull()
    if (innerDiv) {
      fireEvent.mouseEnter(innerDiv)
      expect(screen.getByText('completed')).toBeInTheDocument()
      fireEvent.mouseLeave(innerDiv)
    }
    // After leaving, tooltip text should be removed
    expect(screen.queryByText('completed')).not.toBeInTheDocument()
  })

  it('should not render tooltip when showTooltip is false', () => {
    const { container } = render(<EmojiIcon category="status" name="completed" />)
    const motionDiv = container.querySelector('.inline-flex')
    if (motionDiv) {
      fireEvent.mouseEnter(motionDiv)
    }
    // Name should not appear as tooltip text (only as emoji)
    const elements = screen.queryAllByText('completed')
    expect(elements).toHaveLength(0)
  })
})

describe('StatusEmoji', () => {
  it('should render the correct emoji for each status', () => {
    const statuses = [
      { status: 'pending' as const, emoji: '⏱️' },
      { status: 'processing' as const, emoji: '⚙️' },
      { status: 'completed' as const, emoji: '✅' },
      { status: 'failed' as const, emoji: '❌' },
      { status: 'warning' as const, emoji: '⚠️' },
    ]

    statuses.forEach(({ status, emoji }) => {
      const { unmount } = render(<StatusEmoji status={status} />)
      expect(screen.getByText(emoji)).toBeInTheDocument()
      unmount()
    })
  })

  it('should accept size prop', () => {
    const { container } = render(<StatusEmoji status="completed" size="lg" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-8')
  })

  it('should default to animated=true', () => {
    // StatusEmoji defaults animated=true; the component should render without error
    const { container } = render(<StatusEmoji status="completed" />)
    expect(container.firstChild).toBeTruthy()
  })

  it('should accept animated=false', () => {
    const { container } = render(<StatusEmoji status="completed" animated={false} />)
    expect(container.firstChild).toBeTruthy()
  })
})

describe('RankEmoji', () => {
  it('should render gold medal for rank 1', () => {
    render(<RankEmoji rank={1} />)
    expect(screen.getByText('🥇')).toBeInTheDocument()
  })

  it('should render silver medal for rank 2', () => {
    render(<RankEmoji rank={2} />)
    expect(screen.getByText('🥈')).toBeInTheDocument()
  })

  it('should render bronze medal for rank 3', () => {
    render(<RankEmoji rank={3} />)
    expect(screen.getByText('🥉')).toBeInTheDocument()
  })

  it('should render trophy for ranks 4-10', () => {
    render(<RankEmoji rank={5} />)
    expect(screen.getByText('🏆')).toBeInTheDocument()
  })

  it('should render rocket for ranks above 10', () => {
    render(<RankEmoji rank={15} />)
    expect(screen.getByText('🚀')).toBeInTheDocument()
  })

  it('should accept size prop', () => {
    const { container } = render(<RankEmoji rank={1} size="xl" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-10')
  })
})

describe('TypeEmoji', () => {
  it('should render correct emoji for each evaluation type', () => {
    const types = [
      { type: 'poem' as const, emoji: '📝' },
      { type: 'painting' as const, emoji: '🎨' },
      { type: 'story' as const, emoji: '📖' },
      { type: 'music' as const, emoji: '🎵' },
      { type: 'general' as const, emoji: '✨' },
    ]

    types.forEach(({ type, emoji }) => {
      const { unmount } = render(<TypeEmoji type={type} />)
      expect(screen.getByText(emoji)).toBeInTheDocument()
      unmount()
    })
  })

  it('should accept size prop', () => {
    const { container } = render(<TypeEmoji type="painting" size="sm" />)
    const span = container.querySelector('span')
    expect(span?.className).toContain('w-5')
  })
})
