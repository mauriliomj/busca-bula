import httpClient from './http-client'

export async function fetchCurrentOrganization() {
  const { data } = await httpClient.get('/organizations/current')
  return { nome: data.name, subdominio: data.slug, ...mapBranding(data) }
}

export function mapBranding(branding) {
  return {
    logoUrl: branding.logo_url,
    corPrimaria: branding.primary_color,
    corSecundaria: branding.secondary_color,
  }
}

export function buildBrandColorsPayload(cores) {
  return {
    primary_color: cores.corPrimaria || null,
    secondary_color: cores.corSecundaria || null,
  }
}

export async function fetchOrganizationBranding(id) {
  const { data } = await httpClient.get(`/platform/organizations/${id}/branding`)
  return mapBranding(data)
}

export async function updateOrganizationBrandColors(id, cores) {
  const { data } = await httpClient.put(`/platform/organizations/${id}/branding`, buildBrandColorsPayload(cores))
  return mapBranding(data)
}

export async function uploadOrganizationLogo(id, arquivo) {
  const { data } = await httpClient.put(`/platform/organizations/${id}/branding/logo`, arquivo, {
    headers: { 'Content-Type': arquivo.type },
  })
  return mapBranding(data)
}

export async function removeOrganizationLogo(id) {
  const { data } = await httpClient.delete(`/platform/organizations/${id}/branding/logo`)
  return mapBranding(data)
}

export async function listOrganizations() {
  const { data } = await httpClient.get('/platform/organizations')
  return data.map(mapOrganization)
}

export async function createOrganization(formulario) {
  const { data } = await httpClient.post('/platform/organizations', {
    name: formulario.nome,
    slug: formulario.subdominio,
    admin_name: formulario.adminNome,
    admin_email: formulario.adminEmail,
    admin_password: formulario.adminSenha,
  })
  return mapOrganization(data)
}

export async function updateOrganization(id, alteracoes) {
  const { data } = await httpClient.patch(`/platform/organizations/${id}`, {
    name: alteracoes.nome,
    is_active: alteracoes.ativa,
  })
  return mapOrganization(data)
}

export async function deleteOrganization(id) {
  await httpClient.delete(`/platform/organizations/${id}`)
}

function mapOrganization(organization) {
  return {
    id: organization.id,
    nome: organization.name,
    subdominio: organization.slug,
    status: organization.status,
    criadaEm: organization.created_at,
  }
}
