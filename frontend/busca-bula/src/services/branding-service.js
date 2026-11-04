import httpClient from './http-client'
import { buildBrandColorsPayload, mapBranding } from './organization-service'

export async function fetchOwnBranding() {
  const { data } = await httpClient.get('/organization/branding')
  return mapBranding(data)
}

export async function updateOwnBrandColors(cores) {
  const { data } = await httpClient.put('/organization/branding', buildBrandColorsPayload(cores))
  return mapBranding(data)
}

export async function uploadOwnLogo(arquivo) {
  const { data } = await httpClient.put('/organization/branding/logo', arquivo, {
    headers: { 'Content-Type': arquivo.type },
  })
  return mapBranding(data)
}

export async function removeOwnLogo() {
  const { data } = await httpClient.delete('/organization/branding/logo')
  return mapBranding(data)
}
