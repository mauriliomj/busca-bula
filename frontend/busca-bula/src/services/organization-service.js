import httpClient from './http-client'

export async function fetchCurrentOrganization() {
  const { data } = await httpClient.get('/organizations/current')
  return { nome: data.name, subdominio: data.slug }
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
