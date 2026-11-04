import axios from 'axios'
import { resolveOrganizationSlug } from './organization-context'
import { clearAccessToken, readAccessToken, saveAccessToken } from './token-storage'

const API_BASE_URL = '/api'
const SESSION_REFRESH_PATH = '/auth/refresh'

const httpClient = axios.create({ baseURL: API_BASE_URL })
const sessionClient = axios.create({ baseURL: API_BASE_URL })

let pendingRefresh = null
let sessionExpiredHandler = () => {}

function applyOrganizationHeader(config) {
  const slug = resolveOrganizationSlug()
  if (slug) config.headers['X-Organization'] = slug
  return config
}

function applyAuthorizationHeader(config) {
  const token = readAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
}

httpClient.interceptors.request.use((config) => applyAuthorizationHeader(applyOrganizationHeader(config)))
sessionClient.interceptors.request.use(applyOrganizationHeader)

export function refreshAccessToken() {
  if (!resolveOrganizationSlug() || !readAccessToken()) return Promise.resolve(null)
  if (!pendingRefresh) {
    pendingRefresh = sessionClient
      .post(SESSION_REFRESH_PATH)
      .then(({ data }) => {
        saveAccessToken(data.access_token)
        return data
      })
      .catch(() => {
        clearAccessToken()
        return null
      })
      .finally(() => {
        pendingRefresh = null
      })
  }
  return pendingRefresh
}

export function onSessionExpired(handler) {
  sessionExpiredHandler = handler
}

function wasSentWithAccessToken(config) {
  return Boolean(config?.headers?.Authorization)
}

httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    if (response?.status !== 401 || !wasSentWithAccessToken(config) || config.sessionRetried) {
      return Promise.reject(error)
    }
    const session = await refreshAccessToken()
    if (session) return httpClient.request({ ...config, sessionRetried: true })
    clearAccessToken()
    sessionExpiredHandler()
    return Promise.reject(error)
  }
)

export function extractErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage
}

export default httpClient
