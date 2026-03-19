import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useFeedback } from '../../hooks/useFeedback'

// Mock API config
vi.mock('../../config/api', () => ({
  API_PREFIX: 'http://localhost:8001/api/v1',
  getProtoAuthHeaders: () => ({ Authorization: 'Bearer test-token' }),
}))

describe('useFeedback', () => {
  let fetchSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    fetchSpy = vi.spyOn(globalThis, 'fetch')
  })

  afterEach(() => {
    fetchSpy.mockRestore()
    vi.restoreAllMocks()
  })

  // --- Initial State ---

  it('should have correct initial state', () => {
    const { result } = renderHook(() => useFeedback())

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.isSubmitted).toBe(false)
    expect(result.current.error).toBeNull()
    expect(typeof result.current.submit).toBe('function')
    expect(typeof result.current.reset).toBe('function')
  })

  // --- Submit: loading state ---

  it('should set isSubmitting during request', async () => {
    // Never resolve so we can observe loading state
    fetchSpy.mockImplementation(
      () => new Promise<Response>(() => {})
    )

    const { result } = renderHook(() => useFeedback())

    act(() => {
      result.current.submit('eval-1', 'good')
    })

    await waitFor(() => {
      expect(result.current.isSubmitting).toBe(true)
    })
  })

  // --- Successful submit ---

  it('should set isSubmitted to true on successful submit', async () => {
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-1', 'excellent', 'Great work!')
    })

    expect(result.current.isSubmitted).toBe(true)
    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.error).toBeNull()
  })

  // --- Failed submit ---

  it('should set error message on failed submit', async () => {
    fetchSpy.mockResolvedValueOnce(
      new Response('', {
        status: 500,
        statusText: 'Internal Server Error',
      })
    )

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-1', 'bad')
    })

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.isSubmitted).toBe(false)
    expect(result.current.error).toContain('Failed to submit feedback')
  })

  it('should set error message on network failure', async () => {
    fetchSpy.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-1', 'bad')
    })

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.error).toBe('Network error')
  })

  // --- Reset ---

  it('should reset to initial state', async () => {
    // First trigger a successful submit
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-1', 'good')
    })

    expect(result.current.isSubmitted).toBe(true)

    // Now reset
    act(() => {
      result.current.reset()
    })

    expect(result.current.isSubmitting).toBe(false)
    expect(result.current.isSubmitted).toBe(false)
    expect(result.current.error).toBeNull()
  })

  // --- Request payload ---

  it('should send correct payload to API', async () => {
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-42', 'thumbs_up', 'Nice output', 'implicit')
    })

    expect(fetchSpy).toHaveBeenCalledOnce()
    const [url, options] = fetchSpy.mock.calls[0]
    expect(url).toBe('http://localhost:8001/api/v1/feedback')
    expect(options).toMatchObject({
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer test-token',
      },
    })

    const body = JSON.parse(options!.body as string)
    expect(body.evaluation_id).toBe('eval-42')
    expect(body.rating).toBe('thumbs_up')
    expect(body.comment).toBe('Nice output')
    expect(body.feedback_type).toBe('implicit')
  })

  it('should use default comment and feedback_type when not provided', async () => {
    fetchSpy.mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    const { result } = renderHook(() => useFeedback())

    await act(async () => {
      await result.current.submit('eval-99', 'ok')
    })

    const body = JSON.parse(fetchSpy.mock.calls[0][1]!.body as string)
    expect(body.comment).toBe('')
    expect(body.feedback_type).toBe('explicit')
  })
})
