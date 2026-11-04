import { ref } from 'vue'
import { buildBrandPalette } from './brand-colors'
import { isPlatformContext } from './organization-context'
import { fetchCurrentOrganization } from './organization-service'

const BRAND_PROPERTIES = ['--brand-primary', '--brand-primary-dark', '--brand-primary-soft', '--brand-secondary']

const currentOrganization = ref(null)
let currentOrganizationRequest = null

export function applyBrandColors(marca) {
  const rootStyle = document.documentElement.style
  BRAND_PROPERTIES.forEach((property) => rootStyle.removeProperty(property))
  const palette = buildBrandPalette(marca?.corPrimaria, marca?.corSecundaria)
  Object.entries(palette).forEach(([property, value]) => rootStyle.setProperty(property, value))
}

export function loadCurrentOrganization() {
  if (isPlatformContext()) return Promise.resolve(null)
  if (!currentOrganizationRequest) {
    currentOrganizationRequest = fetchCurrentOrganization().then((organizacao) => {
      currentOrganization.value = organizacao
      applyBrandColors(organizacao)
      return organizacao
    })
    currentOrganizationRequest.catch(() => {
      currentOrganizationRequest = null
    })
  }
  return currentOrganizationRequest
}

export function useCurrentOrganization() {
  loadCurrentOrganization().catch(() => null)
  return currentOrganization
}

export function updateCurrentOrganizationBranding(marca) {
  if (!currentOrganization.value) return
  currentOrganization.value = { ...currentOrganization.value, ...marca }
  applyBrandColors(currentOrganization.value)
}
