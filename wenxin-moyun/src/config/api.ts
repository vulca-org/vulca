/**
 * Unified API URL configuration
 *
 * Single source of truth for backend API URLs.
 * Update PRODUCTION_API_URL here when migrating to a new backend host.
 */

// Set VITE_API_BASE_URL in env or CI secrets; fallback to localhost for development
const PRODUCTION_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// Detect environment:
// 1. Local app mode: served from backend (localhost but NOT Vite dev ports)
// 2. Production: non-localhost hostname
// 3. Vite dev: localhost on Vite ports (5173-5175)
const isLocalApp = typeof window !== 'undefined'
  && window.location.hostname === 'localhost'
  && !['5173', '5174', '5175'].includes(window.location.port);

const isProduction = typeof window !== 'undefined'
  && window.location.hostname !== 'localhost';

/** Base URL for the backend API (no trailing slash) */
export const API_BASE_URL = isLocalApp
  ? `${window.location.protocol}//${window.location.host}`  // same-origin
  : isProduction
    ? PRODUCTION_API_URL
    : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001');

/** API version path segment */
export const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

/** Full versioned API prefix, e.g. https://vulca-api.onrender.com/api/v1 */
export const API_PREFIX = `${API_BASE_URL}/api/${API_VERSION}`;

/**
 * Convert the HTTP(S) base URL to a WebSocket URL.
 * https:// -> wss://, http:// -> ws://
 */
export const getWebSocketBaseUrl = (): string =>
  API_BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://');
