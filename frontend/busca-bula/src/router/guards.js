import {
  MEMBER_ROLE,
  ORGANIZATION_ADMIN_ROLE,
  PLATFORM_ADMIN_ROLE,
  currentUserRole,
  homePathForRole,
  resolvePostLoginPath,
} from '../services/auth-service'
import { isPlatformContext } from '../services/organization-context'
import { ensureSession } from '../services/session-service'

export const TENANT_CONTEXT = 'tenant'
export const PLATFORM_CONTEXT = 'platform'
export const MEMBER_ROLES = [MEMBER_ROLE, ORGANIZATION_ADMIN_ROLE]
export const ORGANIZATION_ADMIN_ROLES = [ORGANIZATION_ADMIN_ROLE]
export const PLATFORM_ADMIN_ROLES = [PLATFORM_ADMIN_ROLE]

function redirectForContext(context) {
  const platform = isPlatformContext()
  if (context === TENANT_CONTEXT && platform) return { name: 'org' }
  if (context === PLATFORM_CONTEXT && !platform) return { name: 'search' }
  return null
}

export async function authorizeNavigation(to) {
  const contextRedirect = redirectForContext(to.meta.context)
  if (contextRedirect) return contextRedirect

  if (to.meta.guestOnly) {
    if (!(await ensureSession())) return true
    return resolvePostLoginPath(currentUserRole(), to.query.next)
  }

  if (to.meta.roles) {
    if (!(await ensureSession())) return { name: 'login', query: { next: to.fullPath } }
    if (!to.meta.roles.includes(currentUserRole())) return homePathForRole(currentUserRole())
  }

  return true
}
