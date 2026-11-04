import httpClient from './http-client'

export async function listMembers() {
  const { data } = await httpClient.get('/members')
  return data.map((member) => ({
    id: member.id,
    papel: member.role,
    nome: member.name,
    email: member.email,
    cidade: member.city ?? '',
    estado: member.state ?? '',
    cadastradoEm: member.created_at,
  }))
}

export async function removeMember(id) {
  await httpClient.delete(`/members/${id}`)
}
