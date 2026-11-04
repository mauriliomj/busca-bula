import httpClient, { refreshAccessToken } from './http-client'
import { isPlatformContext } from './organization-context'
import { clearAccessToken, hasValidAccessToken } from './token-storage'

export async function ensureSession() {
  if (hasValidAccessToken()) return true
  return Boolean(await refreshAccessToken())
}

export async function closeSession() {
  if (!isPlatformContext()) await httpClient.post('/auth/logout').catch(() => null)
  clearAccessToken()
}
