const baseDomain = (import.meta.env.VITE_BASE_DOMAIN || 'localhost').toLowerCase()
const defaultOrganization = (import.meta.env.VITE_DEFAULT_ORGANIZATION || '').trim().toLowerCase() || null

export function resolveOrganizationSlug() {
  const hostname = window.location.hostname.toLowerCase()
  if (hostname === baseDomain) return null
  const suffix = `.${baseDomain}`
  if (!hostname.endsWith(suffix)) return defaultOrganization
  const subdomains = hostname.slice(0, -suffix.length).split('.')
  return subdomains[subdomains.length - 1] || null
}

export function isPlatformContext() {
  return resolveOrganizationSlug() === null
}

export function buildOrganizationUrl(slug) {
  const { protocol, port } = window.location
  return `${protocol}//${slug}.${baseDomain}${port ? `:${port}` : ''}`
}

export function buildOrganizationHostname(slug) {
  return `${slug}.${baseDomain}`
}
