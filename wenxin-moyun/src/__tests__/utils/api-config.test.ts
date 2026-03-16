import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('API config module', () => {
  // We need to isolate module state between tests since the module caches
  // its computed values at import time.

  beforeEach(() => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '5173', protocol: 'http:', host: 'localhost:5173' } })
    // Reset import.meta.env stubs
    vi.stubEnv('VITE_API_BASE_URL', '')
    vi.stubEnv('VITE_API_VERSION', '')
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
    vi.resetModules()
  })

  it('should use localhost:8001 when hostname is localhost on Vite port', async () => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '5173', protocol: 'http:', host: 'localhost:5173' } })
    const mod = await import('../../config/api')
    expect(mod.API_BASE_URL).toBe('http://localhost:8001')
  })

  it('should use same-origin when served from backend (local app mode)', async () => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '8001', protocol: 'http:', host: 'localhost:8001' } })
    const mod = await import('../../config/api')
    expect(mod.API_BASE_URL).toBe('http://localhost:8001')
  })

  it('should use production URL when hostname is not localhost', async () => {
    // In production, VITE_API_BASE_URL is injected by CI secrets
    vi.stubEnv('VITE_API_BASE_URL', 'https://my-api.run.app')
    vi.stubGlobal('window', { location: { hostname: 'vulcaart.art' } })
    const mod = await import('../../config/api')
    expect(mod.API_BASE_URL).toBe('https://my-api.run.app')
  })

  it('should construct API_PREFIX with version', async () => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '5173', protocol: 'http:', host: 'localhost:5173' } })
    const mod = await import('../../config/api')
    expect(mod.API_PREFIX).toBe(`${mod.API_BASE_URL}/api/${mod.API_VERSION}`)
  })

  it('should default API_VERSION to v1', async () => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '5173', protocol: 'http:', host: 'localhost:5173' } })
    const mod = await import('../../config/api')
    expect(mod.API_VERSION).toBe('v1')
  })

  it('getWebSocketBaseUrl should convert http to ws', async () => {
    vi.stubGlobal('window', { location: { hostname: 'localhost', port: '5173', protocol: 'http:', host: 'localhost:5173' } })
    const mod = await import('../../config/api')
    const wsUrl = mod.getWebSocketBaseUrl()
    expect(wsUrl).toMatch(/^ws:\/\//)
    expect(wsUrl).not.toMatch(/^http/)
  })

  it('getWebSocketBaseUrl should convert https to wss', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://my-api.run.app')
    vi.stubGlobal('window', { location: { hostname: 'vulcaart.art' } })
    const mod = await import('../../config/api')
    const wsUrl = mod.getWebSocketBaseUrl()
    expect(wsUrl).toMatch(/^wss:\/\//)
    expect(wsUrl).not.toMatch(/^https/)
  })
})
