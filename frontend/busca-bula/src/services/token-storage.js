import { ref } from 'vue'

const ACCESS_TOKEN_KEY = 'busca-bula.access-token'

const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY))

window.addEventListener('storage', (event) => {
  if (event.key === ACCESS_TOKEN_KEY) accessToken.value = event.newValue
})

export function readAccessToken() {
  return accessToken.value
}

export function saveAccessToken(token) {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
  accessToken.value = token
}

export function clearAccessToken() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  accessToken.value = null
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
