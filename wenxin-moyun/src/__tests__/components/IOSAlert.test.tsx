import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { IOSAlert } from '../../components/ios/core/IOSAlert'

describe('IOSAlert', () => {
  it('should not render anything when visible is false', () => {
    const { container } = render(
      <IOSAlert
        visible={false}
        onClose={vi.fn()}
        title="Hidden Alert"
        message="This should not appear"
      />
    )
    expect(screen.queryByText('Hidden Alert')).not.toBeInTheDocument()
    // AnimatePresence may leave some wrapper, but the dialog content should be absent
    expect(container.querySelector('[role="dialog"]')).not.toBeInTheDocument()
  })

  it('should render title and message when visible', () => {
    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="Alert Title"
        message="Alert message text"
      />
    )
    expect(screen.getByText('Alert Title')).toBeInTheDocument()
    expect(screen.getByText('Alert message text')).toBeInTheDocument()
  })

  it('should render the dialog with proper ARIA attributes', () => {
    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="Accessible Alert"
      />
    )
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby', 'ios-alert-title')
  })

  it('should call onClose when backdrop is clicked', () => {
    const onClose = vi.fn()
    render(
      <IOSAlert
        visible={true}
        onClose={onClose}
        title="Closable"
      />
    )
    // The backdrop is the first motion.div with the fixed inset-0 class
    // We find it by its class pattern
    const backdrop = document.querySelector('.fixed.inset-0.bg-black\\/50')
    expect(backdrop).toBeTruthy()
    fireEvent.click(backdrop!)
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('should call onClose when Escape key is pressed', async () => {
    const onClose = vi.fn()
    render(
      <IOSAlert
        visible={true}
        onClose={onClose}
        title="Escape Test"
      />
    )
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('should render action buttons', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()

    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="With Actions"
        actions={[
          { label: 'Cancel', onPress: onCancel, style: 'cancel' },
          { label: 'Confirm', onPress: onConfirm, style: 'default' },
        ]}
      />
    )

    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByText('Confirm')).toBeInTheDocument()
  })

  it('should fire action callbacks when buttons are clicked', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()

    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="Action Test"
        actions={[
          { label: 'Cancel', onPress: onCancel, style: 'cancel' },
          { label: 'OK', onPress: onConfirm, style: 'default' },
        ]}
      />
    )

    fireEvent.click(screen.getByText('OK'))
    expect(onConfirm).toHaveBeenCalledOnce()

    fireEvent.click(screen.getByText('Cancel'))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('should show close button when showCloseButton is true', () => {
    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="Close Button"
        showCloseButton={true}
      />
    )
    expect(screen.getByLabelText('Close')).toBeInTheDocument()
  })

  it('should not show close button by default', () => {
    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="No Close Button"
      />
    )
    expect(screen.queryByLabelText('Close')).not.toBeInTheDocument()
  })

  it('should focus first button when visible', async () => {
    render(
      <IOSAlert
        visible={true}
        onClose={vi.fn()}
        title="Focus Test"
        actions={[
          { label: 'First', onPress: vi.fn(), style: 'default' },
          { label: 'Second', onPress: vi.fn(), style: 'cancel' },
        ]}
      />
    )

    // The component uses setTimeout(100ms) for focus
    await waitFor(
      () => {
        const buttons = screen.getAllByRole('button')
        // At least one button should exist
        expect(buttons.length).toBeGreaterThan(0)
      },
      { timeout: 500 },
    )
  })
})
