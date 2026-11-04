import axios from 'axios'
import { resolveOrganizationSlug } from './organization-context'
import { clearAccessToken, readAccessToken } from './token-storage'

const httpClient = axios.create({ baseURL: '/api' })

httpClient.interceptors.request.use((config) => {
  const token = readAccessToken()
  const slug = resolveOrganizationSlug()
  if (token) config.headers.Authorization = `Bearer ${token}`
  if (slug) config.headers['X-Organization'] = slug
  return config
})

httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && readAccessToken()) {
      clearAccessToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export function extractErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage
}

export default httpClient
