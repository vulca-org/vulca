import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import {
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardFooter,
} from '@/components/ios'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => {
      const {
        whileTap, whileHover, transition, animate, initial,
        drag, dragConstraints, dragElastic, onDrag,
        ...domProps
      } = props
      return <div {...domProps}>{children}</div>
    },
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}))

describe('IOSCard', () => {
  it('should render children content', () => {
    render(<IOSCard>Card Content</IOSCard>)
    expect(screen.getByText('Card Content')).toBeInTheDocument()
  })

  it('should apply elevated variant classes by default', () => {
    const { container } = render(<IOSCard>Default</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('shadow-sm')
    expect(card.className).toContain('border')
  })

  it('should apply flat variant classes', () => {
    const { container } = render(<IOSCard variant="flat">Flat</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('bg-white')
    // flat has no shadow
    expect(card.className).not.toContain('shadow-sm')
  })

  it('should apply glass variant classes', () => {
    const { container } = render(<IOSCard variant="glass">Glass</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('backdrop-blur-xl')
  })

  it('should apply bordered variant classes', () => {
    const { container } = render(<IOSCard variant="bordered">Bordered</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('border')
  })

  it('should apply padding none class', () => {
    const { container } = render(<IOSCard padding="none">NoPad</IOSCard>)
    const card = container.firstChild as HTMLElement
    // padding none = empty string, so no p-* class
    expect(card.className).not.toContain('p-3')
    expect(card.className).not.toContain('p-4')
    expect(card.className).not.toContain('p-6')
  })

  it('should apply padding sm class', () => {
    const { container } = render(<IOSCard padding="sm">SmPad</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('p-3')
  })

  it('should apply padding lg class', () => {
    const { container } = render(<IOSCard padding="lg">LgPad</IOSCard>)
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('p-6')
  })

  it('should apply radius classes', () => {
    const { container: c1 } = render(<IOSCard radius="sm">Sm</IOSCard>)
    expect((c1.firstChild as HTMLElement).className).toContain('rounded-md')

    const { container: c2 } = render(<IOSCard radius="xl">Xl</IOSCard>)
    expect((c2.firstChild as HTMLElement).className).toContain('rounded-2xl')
  })

  it('should fire onClick when interactive', () => {
    const handleClick = vi.fn()
    const { container } = render(
      <IOSCard interactive onClick={handleClick}>
        Interactive Card
      </IOSCard>
    )
    fireEvent.click(container.firstChild as HTMLElement)
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('should not fire onClick when not interactive', () => {
    const handleClick = vi.fn()
    const { container } = render(
      <IOSCard onClick={handleClick}>
        Non-Interactive
      </IOSCard>
    )
    fireEvent.click(container.firstChild as HTMLElement)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('should apply cursor-pointer when interactive', () => {
    const { container } = render(
      <IOSCard interactive>Interactive</IOSCard>
    )
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('cursor-pointer')
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSCard className="my-card-class">Custom</IOSCard>
    )
    const card = container.firstChild as HTMLElement
    expect(card.className).toContain('my-card-class')
  })
})

describe('IOSCardHeader', () => {
  it('should render title', () => {
    render(<IOSCardHeader title="Header Title" />)
    expect(screen.getByText('Header Title')).toBeInTheDocument()
  })

  it('should render subtitle when provided', () => {
    render(<IOSCardHeader title="Title" subtitle="Subtitle text" />)
    expect(screen.getByText('Subtitle text')).toBeInTheDocument()
  })

  it('should not render subtitle when not provided', () => {
    const { container } = render(<IOSCardHeader title="Title Only" />)
    // Only the title h3 and its wrapper should exist — no <p> tag
    const paragraphs = container.querySelectorAll('p')
    expect(paragraphs.length).toBe(0)
  })

  it('should render action node when provided', () => {
    render(
      <IOSCardHeader
        title="With Action"
        action={<button data-testid="action-btn">Act</button>}
      />
    )
    expect(screen.getByTestId('action-btn')).toBeInTheDocument()
  })

  it('should render emoji node when provided', () => {
    render(
      <IOSCardHeader
        title="With Emoji"
        emoji={<span data-testid="emoji-node">E</span>}
      />
    )
    expect(screen.getByTestId('emoji-node')).toBeInTheDocument()
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSCardHeader title="Cls" className="header-custom" />
    )
    expect((container.firstChild as HTMLElement).className).toContain('header-custom')
  })
})

describe('IOSCardContent', () => {
  it('should render children', () => {
    render(<IOSCardContent>Content here</IOSCardContent>)
    expect(screen.getByText('Content here')).toBeInTheDocument()
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSCardContent className="content-custom">Text</IOSCardContent>
    )
    expect((container.firstChild as HTMLElement).className).toContain('content-custom')
  })
})

describe('IOSCardFooter', () => {
  it('should render children', () => {
    render(<IOSCardFooter>Footer content</IOSCardFooter>)
    expect(screen.getByText('Footer content')).toBeInTheDocument()
  })

  it('should render divider border by default', () => {
    const { container } = render(<IOSCardFooter>Footer</IOSCardFooter>)
    const footer = container.firstChild as HTMLElement
    expect(footer.className).toContain('border-t')
  })

  it('should not render divider when divider is false', () => {
    const { container } = render(
      <IOSCardFooter divider={false}>No divider</IOSCardFooter>
    )
    const footer = container.firstChild as HTMLElement
    expect(footer.className).not.toContain('border-t')
  })

  it('should forward custom className', () => {
    const { container } = render(
      <IOSCardFooter className="footer-custom">Ft</IOSCardFooter>
    )
    expect((container.firstChild as HTMLElement).className).toContain('footer-custom')
  })
})
