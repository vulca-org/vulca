// Use crypto.randomUUID() instead of uuid package for React 19 compatibility
import { getItem, setItem, removeItem } from './storageUtils';

export interface GuestSession {
  id: string;
  dailyUsage: number;
  lastReset: string;
  evaluations: string[];
  createdAt: string;
}

const GUEST_SESSION_KEY = 'wenxin_guest_session';
const DAILY_LIMIT = 10;

// UUID v4 format validation regex
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/**
 * Validate UUID v4 format
 */
function isValidUUID(id: string): boolean {
  return typeof id === 'string' && UUID_REGEX.test(id);
}

/**
 * Get or create guest session
 */
export function getGuestSession(): GuestSession {
  const stored = getItem(GUEST_SESSION_KEY);

  if (stored) {
    try {
      const session: GuestSession = JSON.parse(stored);

      // Validate session structure and UUID format
      if (!isValidUUID(session.id)) {
        console.warn('Invalid guest session ID, creating new session');
        removeItem(GUEST_SESSION_KEY);
        // Fall through to create new session
      } else {
        // Check if we need to reset daily usage
        const today = new Date().toDateString();
        if (session.lastReset !== today) {
          session.dailyUsage = 0;
          session.lastReset = today;
          setItem(GUEST_SESSION_KEY, JSON.stringify(session));
        }

        return session;
      }
    } catch {
      // Invalid stored session, create new one
    }
  }
  
  // Create new guest session
  const newSession: GuestSession = {
    id: crypto.randomUUID(),
    dailyUsage: 0,
    lastReset: new Date().toDateString(),
    evaluations: [],
    createdAt: new Date().toISOString()
  };
  
  setItem(GUEST_SESSION_KEY, JSON.stringify(newSession));
  return newSession;
}

/**
 * Update guest session
 */
export function updateGuestSession(updates: Partial<GuestSession>): GuestSession {
  const session = getGuestSession();
  const updated = { ...session, ...updates };
  setItem(GUEST_SESSION_KEY, JSON.stringify(updated));
  return updated;
}

/**
 * Check if guest has reached daily limit
 */
export function hasReachedDailyLimit(): boolean {
  const session = getGuestSession();
  return session.dailyUsage >= DAILY_LIMIT;
}

/**
 * Get remaining daily usage for guest
 */
export function getRemainingUsage(): number {
  const session = getGuestSession();
  return Math.max(0, DAILY_LIMIT - session.dailyUsage);
}

/**
 * Increment guest daily usage
 */
export function incrementGuestUsage(): GuestSession {
  const session = getGuestSession();
  return updateGuestSession({
    dailyUsage: session.dailyUsage + 1
  });
}

/**
 * Add evaluation to guest session
 */
export function addEvaluationToGuest(evaluationId: string): GuestSession {
  const session = getGuestSession();
  const updatedEvaluations = [...session.evaluations, evaluationId];
  
  return updateGuestSession({
    evaluations: updatedEvaluations,
    dailyUsage: session.dailyUsage + 1
  });
}

/**
 * Clear guest session (for testing or logout)
 */
export function clearGuestSession(): void {
  removeItem(GUEST_SESSION_KEY);
}

/**
 * Check if user is in guest mode
 */
export function isGuestMode(): boolean {
  const token = getItem('access_token');
  return !token;
}

/**
 * Get guest session for API headers
 */
export function getGuestHeaders(): Record<string, string> {
  if (!isGuestMode()) {
    return {};
  }
  
  const session = getGuestSession();
  return {
    'X-Guest-ID': session.id
  };
}
