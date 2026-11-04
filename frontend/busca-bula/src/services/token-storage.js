const ACCESS_TOKEN_KEY = 'busca-bula.access-token'

export function readAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function saveAccessToken(token) {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAccessToken() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
}

export function readAccessTokenPayload() {
  const token = readAccessToken()
  if (!token) return null
  try {
    const encodedPayload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(encodedPayload))
  } catch {
    return null
  }
}

export function hasValidAccessToken() {
  const payload = readAccessTokenPayload()
  return Boolean(payload) && payload.exp * 1000 > Date.now()
}
