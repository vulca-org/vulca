import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock storageUtils before importing guestSession
const mockStorage: Record<string, string> = {}

vi.mock('../../utils/storageUtils', () => ({
  getItem: vi.fn((key: string) => mockStorage[key] ?? null),
  setItem: vi.fn((key: string, value: string) => {
    mockStorage[key] = value
  }),
  removeItem: vi.fn((key: string) => {
    delete mockStorage[key]
  }),
}))

import {
  getGuestSession,
  updateGuestSession,
  hasReachedDailyLimit,
  getRemainingUsage,
  incrementGuestUsage,
  addEvaluationToGuest,
  clearGuestSession,
  isGuestMode,
  getGuestHeaders,
} from '../../utils/guestSession'
import type { GuestSession } from '../../utils/guestSession'
import { getItem, setItem, removeItem } from '../../utils/storageUtils'

const GUEST_SESSION_KEY = 'wenxin_guest_session'

describe('guestSession', () => {
  beforeEach(() => {
    // Clear mock storage
    Object.keys(mockStorage).forEach((k) => delete mockStorage[k])
    vi.clearAllMocks()

    // Provide crypto.randomUUID in test env
    if (!globalThis.crypto?.randomUUID) {
      vi.stubGlobal('crypto', {
        ...globalThis.crypto,
        randomUUID: () => '12345678-1234-4123-8123-123456789abc',
      })
    }
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('getGuestSession', () => {
    it('should create a new session when none exists', () => {
      const session = getGuestSession()

      expect(session.id).toBeTruthy()
      expect(session.dailyUsage).toBe(0)
      expect(session.evaluations).toEqual([])
      expect(session.createdAt).toBeTruthy()
      expect(session.lastReset).toBe(new Date().toDateString())
      expect(setItem).toHaveBeenCalledWith(
        GUEST_SESSION_KEY,
        expect.any(String),
      )
    })

    it('should return existing valid session from storage', () => {
      const existingSession: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 2,
        lastReset: new Date().toDateString(),
        evaluations: ['eval-1'],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(existingSession)

      const session = getGuestSession()

      expect(session.id).toBe('aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee')
      expect(session.dailyUsage).toBe(2)
      expect(session.evaluations).toEqual(['eval-1'])
    })

    it('should reset daily usage when lastReset is a different day', () => {
      const existingSession: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 3,
        lastReset: 'Thu Jan 01 2020', // past date
        evaluations: ['eval-1'],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(existingSession)

      const session = getGuestSession()

      expect(session.dailyUsage).toBe(0)
      expect(session.lastReset).toBe(new Date().toDateString())
      // Should persist the reset
      expect(setItem).toHaveBeenCalled()
    })

    it('should create new session when stored session has invalid UUID', () => {
      const badSession = {
        id: 'not-a-uuid',
        dailyUsage: 1,
        lastReset: new Date().toDateString(),
        evaluations: [],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(badSession)

      const session = getGuestSession()

      // Should have created a new session with valid UUID
      expect(session.id).not.toBe('not-a-uuid')
      expect(removeItem).toHaveBeenCalledWith(GUEST_SESSION_KEY)
    })

    it('should create new session when stored data is invalid JSON', () => {
      mockStorage[GUEST_SESSION_KEY] = '{invalid json}'

      const session = getGuestSession()

      expect(session.id).toBeTruthy()
      expect(session.dailyUsage).toBe(0)
    })

    it('should generate a valid UUID v4 for new sessions', () => {
      const session = getGuestSession()
      const uuidV4Regex =
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      expect(session.id).toMatch(uuidV4Regex)
    })
  })

  describe('updateGuestSession', () => {
    it('should merge updates into the current session', () => {
      // First create a session
      getGuestSession()

      const updated = updateGuestSession({ dailyUsage: 5 })

      expect(updated.dailyUsage).toBe(5)
      // Other fields should be preserved
      expect(updated.id).toBeTruthy()
      expect(updated.evaluations).toEqual([])
    })
  })

  describe('hasReachedDailyLimit', () => {
    it('should return false when usage is below limit', () => {
      getGuestSession() // creates with dailyUsage=0
      expect(hasReachedDailyLimit()).toBe(false)
    })

    it('should return true when usage equals daily limit (10)', () => {
      const session: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 10,
        lastReset: new Date().toDateString(),
        evaluations: [],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(session)

      expect(hasReachedDailyLimit()).toBe(true)
    })

    it('should return true when usage exceeds daily limit', () => {
      const session: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 15,
        lastReset: new Date().toDateString(),
        evaluations: [],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(session)

      expect(hasReachedDailyLimit()).toBe(true)
    })
  })

  describe('getRemainingUsage', () => {
    it('should return 10 for a fresh session', () => {
      getGuestSession()
      expect(getRemainingUsage()).toBe(10)
    })

    it('should return 0 when limit is reached', () => {
      const session: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 10,
        lastReset: new Date().toDateString(),
        evaluations: [],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(session)

      expect(getRemainingUsage()).toBe(0)
    })

    it('should never return negative values', () => {
      const session: GuestSession = {
        id: 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        dailyUsage: 10,
        lastReset: new Date().toDateString(),
        evaluations: [],
        createdAt: new Date().toISOString(),
      }
      mockStorage[GUEST_SESSION_KEY] = JSON.stringify(session)

      expect(getRemainingUsage()).toBe(0)
    })
  })

  describe('incrementGuestUsage', () => {
    it('should increment dailyUsage by 1', () => {
      getGuestSession()

      const updated = incrementGuestUsage()
      expect(updated.dailyUsage).toBe(1)

      const updated2 = incrementGuestUsage()
      expect(updated2.dailyUsage).toBe(2)
    })
  })

  describe('addEvaluationToGuest', () => {
    it('should add evaluation ID and increment usage', () => {
      getGuestSession()

      const updated = addEvaluationToGuest('eval-123')

      expect(updated.evaluations).toContain('eval-123')
      expect(updated.dailyUsage).toBe(1)
    })

    it('should accumulate multiple evaluations', () => {
      getGuestSession()

      addEvaluationToGuest('eval-1')
      const updated = addEvaluationToGuest('eval-2')

      expect(updated.evaluations).toContain('eval-1')
      expect(updated.evaluations).toContain('eval-2')
      expect(updated.dailyUsage).toBe(2)
    })
  })

  describe('clearGuestSession', () => {
    it('should remove session from storage', () => {
      getGuestSession()
      clearGuestSession()

      expect(removeItem).toHaveBeenCalledWith(GUEST_SESSION_KEY)
    })
  })

  describe('isGuestMode', () => {
    it('should return true when no access_token exists', () => {
      expect(isGuestMode()).toBe(true)
    })

    it('should return false when access_token exists', () => {
      mockStorage['access_token'] = 'some-jwt-token'
      expect(isGuestMode()).toBe(false)
    })
  })

  describe('getGuestHeaders', () => {
    it('should return X-Guest-ID header when in guest mode', () => {
      const headers = getGuestHeaders()

      expect(headers).toHaveProperty('X-Guest-ID')
      expect(headers['X-Guest-ID']).toBeTruthy()
    })

    it('should return empty object when not in guest mode', () => {
      mockStorage['access_token'] = 'some-jwt-token'

      const headers = getGuestHeaders()

      expect(headers).toEqual({})
    })
  })
})
