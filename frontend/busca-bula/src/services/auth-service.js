import httpClient from './http-client'
import { isPlatformContext } from './organization-context'
import { closeSession } from './session-service'
import { readAccessTokenPayload, saveAccessToken } from './token-storage'

export const PLATFORM_ADMIN_ROLE = 'platform_admin'
export const ORGANIZATION_ADMIN_ROLE = 'org_admin'
export const MEMBER_ROLE = 'member'

const homePaths = {
  [PLATFORM_ADMIN_ROLE]: '/org',
  [ORGANIZATION_ADMIN_ROLE]: '/members',
}

export async function registerUser(formulario) {
  const { data } = await httpClient.post('/auth/register', {
    name: formulario.nome,
    age: Number(formulario.idade),
    gender: formulario.sexo,
    email: formulario.email,
    phone: formulario.celular,
    address: formulario.endereco,
    city: formulario.cidade,
    state: formulario.estado,
    password: formulario.senha,
  })
  return data
}

export async function loginUser(email, senha) {
  const loginPath = isPlatformContext() ? '/platform/auth/login' : '/auth/login'
  const { data } = await httpClient.post(loginPath, { email, password: senha })
  saveAccessToken(data.access_token)
  return data.role
}

export function logoutUser() {
  return closeSession()
}

export function currentUserRole() {
  return readAccessTokenPayload()?.role ?? null
}

export function homePathForRole(role) {
  return homePaths[role] ?? '/'
}

export function sanitizeNextPath(next) {
  return typeof next === 'string' && next.startsWith('/') && !next.startsWith('//') ? next : null
}

export function resolvePostLoginPath(role, next) {
  const safeNext = sanitizeNextPath(next)
  return safeNext && role !== PLATFORM_ADMIN_ROLE ? safeNext : homePathForRole(role)
}
