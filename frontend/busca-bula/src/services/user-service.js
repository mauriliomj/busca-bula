import httpClient from './http-client'

export async function fetchCurrentUser() {
  const { data } = await httpClient.get('/users/me')
  return {
    nome: data.name ?? '',
    idade: data.age ?? '',
    sexo: data.gender ?? '',
    email: data.email ?? '',
    celular: data.phone ?? '',
    endereco: data.address ?? '',
    cidade: data.city ?? '',
    estado: data.state ?? '',
  }
}
