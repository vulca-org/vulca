import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { IOSSheet } from '@/components/ios'

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => {
      const {
        whileTap, whileHover, transition, animate, initial, exit,
        drag, dragConstraints, dragElastic, dragControls, onDragEnd,
        ...domProps
      } = props
      return <div {...domProps}>{children}</div>
    },
  },
  AnimatePresence: ({ children, mode }: any) => <>{children}</>,
  useDragControls: () => ({
    start: vi.fn(),
  }),
}))

// Mock iosTheme utility
vi.mock('../../components/ios/utils/iosTheme', () => ({
  liquidGlass: {
    containers: { sheet: 'glass-sheet-class' },
    shadows: { strong: '0 0 0 rgba(0,0,0,0)' },
  },
}))

// Mock createPortal to render in-place instead of into document.body
vi.mock('react-dom', async () => {
  const actual = await vi.importActual<typeof import('react-dom')>('react-dom')
  return {
    ...actual,
    createPortal: (node: any) => node,
  }
})

describe('IOSSheet', () => {
  it('should render children when visible', () => {
    render(
      <IOSSheet visible={true} onClose={vi.fn()}>
        <p>Sheet Content</p>
      </IOSSheet>
    )
    expect(screen.getByText('Sheet Content')).toBeInTheDocument()
  })

  it('should not render children when not visible', () => {
    render(
      <IOSSheet visible={false} onClose={vi.fn()}>
        <p>Hidden Content</p>
      </IOSSheet>
    )
    expect(screen.queryByText('Hidden Content')).not.toBeInTheDocument()
  })

  it('should call onClose when backdrop is clicked and allowDismiss is true', () => {
    const onClose = vi.fn()
    render(
      <IOSSheet visible={true} onClose={onClose} allowDismiss={true}>
        <p>Content</p>
      </IOSSheet>
    )
    // Backdrop is the first fixed div with bg-black class
    const backdrop = document.querySelector('.fixed.inset-0') as HTMLElement
    expect(backdrop).toBeTruthy()
    // Click directly on the backdrop (target === currentTarget)
    fireEvent.click(backdrop)
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('should NOT call onClose when backdrop is clicked and allowDismiss is false', () => {
    const onClose = vi.fn()
    render(
      <IOSSheet visible={true} onClose={onClose} allowDismiss={false}>
        <p>Content</p>
      </IOSSheet>
    )
    const backdrop = document.querySelector('.fixed.inset-0') as HTMLElement
    if (backdrop) {
      fireEvent.click(backdrop)
    }
    expect(onClose).not.toHaveBeenCalled()
  })

  it('should render drag handle when showHandle is true (default)', () => {
    const { container } = render(
      <IOSSheet visible={true} onClose={vi.fn()}>
        <p>Content</p>
      </IOSSheet>
    )
    // The handle is a small rounded div (w-9 h-1)
    const handle = container.querySelector('.w-9.h-1')
    expect(handle).toBeTruthy()
  })

  it('should NOT render drag handle when showHandle is false', () => {
    const { container } = render(
      <IOSSheet visible={true} onClose={vi.fn()} showHandle={false}>
        <p>Content</p>
      </IOSSheet>
    )
    const handle = container.querySelector('.w-9.h-1')
    expect(handle).toBeFalsy()
  })

  it('should forward custom className to sheet container', () => {
    const { container } = render(
      <IOSSheet visible={true} onClose={vi.fn()} className="my-sheet-class">
        <p>Content</p>
      </IOSSheet>
    )
    // The sheet container div should contain the custom class
    const sheet = container.querySelector('.my-sheet-class')
    expect(sheet).toBeTruthy()
  })

  it('should render content accessible in the DOM', () => {
    render(
      <IOSSheet visible={true} onClose={vi.fn()}>
        <h2>Sheet Title</h2>
        <p>Some descriptive text</p>
      </IOSSheet>
    )
    expect(screen.getByText('Sheet Title')).toBeInTheDocument()
    expect(screen.getByText('Some descriptive text')).toBeInTheDocument()
  })
})
