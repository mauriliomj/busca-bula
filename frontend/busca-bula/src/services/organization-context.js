const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'localhost'

export function resolveOrganizationSlug() {
  const hostname = window.location.hostname.toLowerCase()
  const suffix = `.${baseDomain}`
  if (!hostname.endsWith(suffix)) return null
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
