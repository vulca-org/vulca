import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { IOSButton } from '@/components/ios'

describe('IOSButton', () => {
  it('should render children text', () => {
    render(<IOSButton>Click Me</IOSButton>)
    expect(screen.getByText('Click Me')).toBeInTheDocument()
  })

  it('should render as a button element', () => {
    render(<IOSButton>Test</IOSButton>)
    expect(screen.getByRole('button', { name: 'Test' })).toBeInTheDocument()
  })

  it('should fire onClick callback when clicked', () => {
    const handleClick = vi.fn()
    render(<IOSButton onClick={handleClick}>Click</IOSButton>)
    fireEvent.click(screen.getByRole('button', { name: 'Click' }))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('should not fire onClick when disabled', () => {
    const handleClick = vi.fn()
    render(<IOSButton onClick={handleClick} disabled>Disabled</IOSButton>)
    fireEvent.click(screen.getByRole('button', { name: 'Disabled' }))
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('should have disabled attribute when disabled prop is true', () => {
    render(<IOSButton disabled>Disabled</IOSButton>)
    expect(screen.getByRole('button', { name: 'Disabled' })).toBeDisabled()
  })

  it('should render emoji when provided', () => {
    render(<IOSButton emoji="fire">With Emoji</IOSButton>)
    expect(screen.getByText('fire')).toBeInTheDocument()
  })

  it('should apply primary variant classes by default', () => {
    render(<IOSButton>Primary</IOSButton>)
    const button = screen.getByRole('button', { name: 'Primary' })
    // Primary variant has bg-slate-700
    expect(button.className).toContain('bg-slate-700')
  })

  it('should apply destructive variant classes', () => {
    render(<IOSButton variant="destructive">Delete</IOSButton>)
    const button = screen.getByRole('button', { name: 'Delete' })
    expect(button.className).toContain('bg-red-600')
  })

  it('should apply secondary variant classes', () => {
    render(<IOSButton variant="secondary">Secondary</IOSButton>)
    const button = screen.getByRole('button', { name: 'Secondary' })
    expect(button.className).toContain('bg-gray-100')
  })

  it('should apply size classes', () => {
    const { rerender } = render(<IOSButton size="sm">Small</IOSButton>)
    expect(screen.getByRole('button').className).toContain('text-sm')

    rerender(<IOSButton size="lg">Large</IOSButton>)
    expect(screen.getByRole('button').className).toContain('text-lg')
  })

  it('should forward custom className', () => {
    render(<IOSButton className="my-custom-class">Custom</IOSButton>)
    expect(screen.getByRole('button').className).toContain('my-custom-class')
  })

  it('should have displayName set', () => {
    expect(IOSButton.displayName).toBe('IOSButton')
  })

  it('should support data-testid prop', () => {
    render(<IOSButton data-testid="my-btn">Test</IOSButton>)
    expect(screen.getByTestId('my-btn')).toBeInTheDocument()
  })
})
