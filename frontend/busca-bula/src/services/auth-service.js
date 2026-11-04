import httpClient from './http-client'
import { isPlatformContext } from './organization-context'
import {
  clearAccessToken,
  hasValidAccessToken,
  readAccessTokenPayload,
  saveAccessToken,
} from './token-storage'

export const PLATFORM_ADMIN_ROLE = 'platform_admin'
export const ORGANIZATION_ADMIN_ROLE = 'org_admin'

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
  clearAccessToken()
}

export function isAuthenticated() {
  return hasValidAccessToken()
}

export function currentUserRole() {
  return readAccessTokenPayload()?.role ?? null
}

export function homePathForRole(role) {
  return homePaths[role] ?? '/user'
}
