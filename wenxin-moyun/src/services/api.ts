import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import { getGuestHeaders } from '../utils/guestSession';
import { apiCache, staticCache, cacheKeys } from '../utils/cache';
import { getItem, removeItem } from '../utils/storageUtils';
import { createLogger } from '../utils/logger';

const logger = createLogger('API');

// Guest session structure validation
interface GuestSessionSuggestions {
  show_login_prompt?: boolean;
  primary_scenario?: {
    type: string;
  };
}

interface GuestSessionData {
  suggestions?: GuestSessionSuggestions;
}

// Validate parsed guest session structure
const isValidGuestSession = (data: unknown): data is GuestSessionData => {
  if (!data || typeof data !== 'object') {
    return false;
  }
  const session = data as Record<string, unknown>;
  // suggestions is optional, but if present must be an object
  if (session.suggestions !== undefined && typeof session.suggestions !== 'object') {
    return false;
  }
  return true;
};

// API base configuration - uses unified config
import { API_BASE_URL, API_VERSION } from '../config/api';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 60000; // 60s for Render cold starts

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: Number(API_TIMEOUT),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      // Add guest headers if not authenticated
      const guestHeaders = getGuestHeaders();
      Object.assign(config.headers, guestHeaders);
    }
    return config;
  },
  (error) => {
    // Ensure we reject with a proper Error object
    if (error instanceof Error) {
      return Promise.reject(error);
    }
    return Promise.reject(new Error(String(error)));
  }
);

// Store for pending requests to retry after login
let pendingRequests: Array<() => void> = [];
let loginModalCallback: ((trigger: string) => void) | null = null;

// Set login modal callback
export const setLoginModalCallback = (callback: (trigger: string) => void) => {
  loginModalCallback = callback;
};

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Check for guest session info in response headers
    const guestSessionHeader = response.headers['x-guest-session'];
    if (guestSessionHeader && typeof guestSessionHeader === 'string') {
      try {
        const parsed = JSON.parse(guestSessionHeader);

        // Validate parsed structure before using
        if (!isValidGuestSession(parsed)) {
          logger.warn('Invalid guest session structure received');
          return response;
        }

        const guestSession = parsed;

        // Store guest session info for tracking
        sessionStorage.setItem('guest_session', guestSessionHeader);

        // Check trigger scenarios
        if (guestSession.suggestions?.show_login_prompt && loginModalCallback) {
          const primaryScenario = guestSession.suggestions.primary_scenario;
          if (primaryScenario && typeof primaryScenario.type === 'string') {
            // Delay slightly to not interrupt user flow
            const callback = loginModalCallback; // Capture reference
            setTimeout(() => {
              callback(primaryScenario.type);
            }, 500);
          }
        }
      } catch (error) {
        logger.warn('Failed to parse guest session header:', error);
      }
    }
    return response;
  },
  (error: AxiosError) => {
    // Handle guest limit reached (429 Too Many Requests)
    if (error.response?.status === 429) {
      const guestSessionHeader = error.response.headers['x-guest-session'];
      if (guestSessionHeader && typeof guestSessionHeader === 'string') {
        try {
          const parsed = JSON.parse(guestSessionHeader);
          // Validate structure before storing
          if (isValidGuestSession(parsed)) {
            sessionStorage.setItem('guest_session', guestSessionHeader);
          } else {
            logger.warn('Invalid guest session structure in 429 response');
          }
        } catch (e) {
          logger.warn('Failed to parse guest session from error:', e);
        }
      }
      
      if (loginModalCallback) {
        loginModalCallback('limit_reached');
        
        // Store request to retry after login
        const originalRequest = error.config;
        if (originalRequest) {
          return new Promise((resolve) => {
            pendingRequests.push(() => {
              resolve(apiClient(originalRequest));
            });
          });
        }
      }
    }
    
    // Handle authentication errors (401 Unauthorized)
    if (error.response?.status === 401) {
      if (!getItem('access_token')) {
        // Guest user hit protected endpoint
        if (loginModalCallback) {
          loginModalCallback('auth_required');
        }
      } else {
        // Token expired or invalid
        removeItem('access_token');
        if (window.location.pathname !== '/login') {
          window.location.href = `/login?from=${encodeURIComponent(window.location.pathname)}`;
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Retry pending requests after successful login
export const retryPendingRequests = () => {
  pendingRequests.forEach(callback => callback());
  pendingRequests = [];
};

export default apiClient;

// Cold-start wake-up for Render free tier (sleeps after 15min inactivity)
let wakeUpPromise: Promise<void> | null = null;

export const wakeUpBackend = (): Promise<void> => {
  if (wakeUpPromise) return wakeUpPromise;
  wakeUpPromise = (async () => {
    try {
      // Fire a lightweight health check to trigger cold start
      await axios.get(`${API_BASE_URL}/health`, { timeout: 60000 });
      logger.log('Backend is awake');
    } catch {
      logger.warn('Backend wake-up ping failed (may still be starting)');
    } finally {
      // Allow retry after 30s
      setTimeout(() => { wakeUpPromise = null; }, 30000);
    }
  })();
  return wakeUpPromise;
};

// Cache version control for data updates
// Uses build time from vite.config.ts to auto-invalidate cache on new deploys
declare const __APP_VERSION__: string;
declare const __BUILD_TIME__: string;
const CACHE_VERSION = `${__APP_VERSION__}-${__BUILD_TIME__?.slice(0, 10) || 'dev'}`;
const VERSION_KEY = 'cache_version';
const EXPECTED_MODEL_COUNT = 42; // Expected number of real models (init_db.py)

type ApiQueryParams = Record<string, string | number | boolean | null | undefined>;

interface AxiosErrorWithCode extends AxiosError {
  code?: string;
}

// Cache management utilities
export const cacheUtils = {
  // Get cache statistics for debugging
  getStats: () => {
    return {
      api: apiCache.getStats(),
      static: staticCache.getStats(),
      version: localStorage.getItem(VERSION_KEY),
      expectedModels: EXPECTED_MODEL_COUNT,
    };
  },
  
  // Clear all caches
  clearAll: () => {
    apiCache.clear();
    staticCache.clear();
    localStorage.removeItem('models_cache');
    sessionStorage.removeItem('models_data');
  },
  
  // Clear model-specific cache
  clearModelCache: () => {
    staticCache.invalidatePattern(/^models/);
    staticCache.invalidatePattern(/^leaderboard/);
    localStorage.removeItem('models_cache');
    sessionStorage.removeItem('models_data');
  },
  
  // Check and update cache version
  checkVersion: () => {
    const currentVersion = localStorage.getItem(VERSION_KEY);
    if (currentVersion !== CACHE_VERSION) {
      logger.log(`Cache: Version update detected (${currentVersion} → ${CACHE_VERSION}), clearing caches`);
      cacheUtils.clearAll();
      localStorage.setItem(VERSION_KEY, CACHE_VERSION);
      return true; // Version was updated
    }
    return false; // No version change
  },
  
  // Validate model data integrity
  validateModelData: (models: Array<Record<string, unknown>>) => {
    if (!Array.isArray(models)) {
      logger.warn('Cache: Invalid model data format');
      return false;
    }
    
    const modelCount = models.length;
    if (modelCount !== EXPECTED_MODEL_COUNT) {
      logger.warn(`Cache: Model count mismatch (${modelCount} !== ${EXPECTED_MODEL_COUNT}), clearing cache`);
      cacheUtils.clearModelCache();
      return false;
    }
    
    // Check for real data indicators
    const realModels = models.filter(model => 
      model.score_highlights ||
      model.benchmark_responses ||
      model.data_source === 'real'
    );
    
    if (realModels.length === 0) {
      logger.warn('Cache: No real model data detected, clearing cache');
      cacheUtils.clearModelCache();
      return false;
    }
    
    logger.log(`Cache: Model data validated (${modelCount} models, ${realModels.length} with real data)`);
    return true;
  },
  
  // Warm up essential caches with version check
  warmUp: async () => {
    try {
      // Wake up backend first (Render cold start)
      await wakeUpBackend();

      // Check version first
      cacheUtils.checkVersion();

      // Preload commonly accessed data
      const results = await Promise.allSettled([
        modelsApi.getModels(true), // Force refresh for models
        galleryApi.getArtworks(),
      ]);
      
      // Validate models data
      if (results[0].status === 'fulfilled') {
        const modelsResponse = results[0].value;
        if (modelsResponse.data) {
          cacheUtils.validateModelData(modelsResponse.data);
        }
      }
      
      logger.log('Cache: Warmed up successfully');
    } catch (error) {
      logger.warn('Cache: Warm up failed:', error);
    }
  },
};

// Sensitive patterns that should not be exposed to users
const SENSITIVE_PATTERNS = [
  /sql/i,                    // SQL-related errors
  /database/i,               // Database errors
  /select|insert|update|delete|from|where/i,  // SQL keywords
  /\/[a-z]+\/[a-z]+/i,       // File paths like /app/src
  /traceback/i,              // Python tracebacks
  /stack trace/i,            // Stack traces
  /internal server/i,        // Internal server errors
  /password|secret|key|token/i,  // Credential-related
  /connection refused/i,     // Infrastructure errors
  /postgres|mysql|sqlite/i,  // Database names
];

// Check if error message contains sensitive information
const containsSensitiveInfo = (message: string): boolean => {
  return SENSITIVE_PATTERNS.some(pattern => pattern.test(message));
};

// API error handler with network detection and security filtering
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    // Network errors (no response)
    if (!error.response) {
      // Add network error flag for offline detection
      const networkError = error as AxiosErrorWithCode;
      networkError.code = 'NETWORK_ERROR';

      if (networkError.code === 'ECONNABORTED') {
        return 'Request timeout - please check your connection';
      }
      if (error.message?.includes('Network Error') || networkError.code === 'ERR_NETWORK') {
        return 'Network error - please check your internet connection';
      }
      return 'Unable to connect to server';
    }

    const status = error.response?.status;

    // 500+ server errors - hide details for security
    if (status && status >= 500) {
      logger.error('Server error:', error.response?.data);
      return 'Server error - our team has been notified';
    }

    // 4xx client errors - filter sensitive info
    if (error.response?.data?.detail) {
      const detail = String(error.response.data.detail);

      // Filter out sensitive information
      if (containsSensitiveInfo(detail)) {
        logger.warn('Filtered sensitive error:', detail);
        return 'An error occurred while processing your request';
      }

      return detail;
    }

    // Fallback to error message with filtering
    if (error.message) {
      if (containsSensitiveInfo(error.message)) {
        return 'An error occurred';
      }
      return error.message;
    }
  }
  return 'An unexpected error occurred';
};

// Check if error is a network/offline error
export const isNetworkError = (error: unknown): boolean => {
  if (axios.isAxiosError(error)) {
    return !error.response || 
           error.code === 'ECONNABORTED' ||
           error.code === 'ERR_NETWORK' ||
           error.message?.includes('Network Error') ||
           error.message?.includes('fetch');
  }
  return false;
};

// Gallery API endpoints with intelligent caching
export const galleryApi = {
  // Get artworks with optional filtering (cached)
  getArtworks: async (params?: {
    type?: string;
    model_id?: string;
    page?: number;
    page_size?: number;
  }) => {
    const cacheKey = cacheKeys.artworks(params);
    return apiCache.get(
      cacheKey,
      () => apiClient.get('/artworks/', { params })
    );
  },

  // Get single artwork by ID (cached)
  getArtwork: async (id: string) => {
    const cacheKey = cacheKeys.artwork(id);
    return apiCache.get(
      cacheKey,
      () => apiClient.get(`/artworks/${id}`)
    );
  },

  // Like an artwork (invalidates cache)
  likeArtwork: async (id: string) => {
    const result = await apiClient.post(`/artworks/${id}/like`);
    // Invalidate artwork cache to reflect new like count
    apiCache.invalidate(cacheKeys.artwork(id));
    apiCache.invalidatePattern(/^artworks/); // Invalidate lists
    return result;
  },

  // Record a view for an artwork (invalidates cache)
  viewArtwork: async (id: string) => {
    const result = await apiClient.post(`/artworks/${id}/view`);
    // Invalidate artwork cache to reflect new view count
    apiCache.invalidate(cacheKeys.artwork(id));
    return result;
  },

  // Share an artwork (no cache invalidation needed)
  shareArtwork: (id: string) => {
    return apiClient.post(`/artworks/${id}/share`);
  },
};

// Models API with caching and force refresh
export const modelsApi = {
  // Get all models (static cache - changes infrequently)
  getModels: async (forceRefresh = false, params?: ApiQueryParams) => {
    const cacheKey = cacheKeys.models(params);
    
    if (forceRefresh) {
      // Clear cache and fetch fresh data
      staticCache.invalidate(cacheKey);
      logger.log('Models API: Force refresh requested, bypassing cache');
    }
    
    const result = await staticCache.get(
      cacheKey,
      async () => {
        logger.log('Models API: Fetching fresh data from server');
        return apiClient.get('/models/', { params });
      }
    );
    
    // Validate data after fetch
    if (result.data) {
      cacheUtils.validateModelData(result.data);
    }
    
    return result;
  },

  // Get single model (static cache with force refresh support)
  getModel: async (id: string, forceRefresh = false) => {
    const cacheKey = cacheKeys.model(id);
    
    if (forceRefresh) {
      staticCache.invalidate(cacheKey);
      logger.log(`Models API: Force refresh for model ${id}`);
    }
    
    return staticCache.get(
      cacheKey,
      () => apiClient.get(`/models/${id}`)
    );
  },
};

// Leaderboard API with static caching
export const leaderboardApi = {
  // Get leaderboard data from models endpoint (static cache - updates infrequently)
  getLeaderboard: async (category?: string) => {
    const cacheKey = cacheKeys.leaderboard(category);
    return staticCache.get(
      cacheKey,
      () => apiClient.get('/models/', { params: { is_active: true } })
    );
  },
};

// Evaluations API with caching
export const evaluationsApi = {
  // Get evaluations list (cached)
  getEvaluations: async (params?: ApiQueryParams) => {
    const cacheKey = cacheKeys.evaluations(params);
    return apiCache.get(
      cacheKey,
      () => apiClient.get('/evaluations/', { params })
    );
  },

  // Get single evaluation (cached)
  getEvaluation: async (id: string) => {
    const cacheKey = cacheKeys.evaluation(id);
    return apiCache.get(
      cacheKey,
      () => apiClient.get(`/evaluations/${id}`)
    );
  },

  // Create evaluation (invalidates cache)
  createEvaluation: async (data: Record<string, unknown>) => {
    const result = await apiClient.post('/evaluations/', data);
    // Invalidate evaluations list cache
    apiCache.invalidatePattern(/^evaluations/);
    return result;
  },
};

// Battles API with real-time caching
export const battlesApi = {
  // Get battles (short cache due to real-time nature)
  getBattles: async (params?: ApiQueryParams) => {
    const cacheKey = cacheKeys.battles(params);
    return apiCache.get(
      cacheKey,
      () => apiClient.get('/battles/', { params }),
      60000 // 1 minute TTL for battles
    );
  },

  // Vote on battle (invalidates cache)
  voteBattle: async (battleId: string, choice: string) => {
    const result = await apiClient.post(`/battles/${battleId}/vote`, { choice });
    // Invalidate battles cache to reflect new votes
    apiCache.invalidatePattern(/^battles/);
    // Also invalidate leaderboard as it might change
    staticCache.invalidatePattern(/^leaderboard/);
    return result;
  },
};

// Leads API for demo requests and sales inquiries
export interface LeadSubmitData {
  name: string;
  email: string;
  organization?: string;
  role?: string;
  use_case: 'ai_labs' | 'research' | 'museums' | 'enterprise' | 'other';
  timeline?: string;
  message?: string;
  source_page: 'book_demo' | 'pricing' | 'product' | 'solutions' | 'contact' | 'other';
}

export interface LeadSubmitResponse {
  success: boolean;
  message: string;
  lead_id: string;
}

export const leadsApi = {
  // Submit a new lead (public endpoint, no auth required)
  submitLead: async (data: LeadSubmitData): Promise<LeadSubmitResponse> => {
    const response = await apiClient.post('/leads/', data);
    return response.data;
  },
};
