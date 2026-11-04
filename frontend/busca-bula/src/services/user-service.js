import httpClient from './http-client'

export async function fetchCurrentUser() {
  const { data } = await httpClient.get('/users/me')
  return mapUserToProfile(data)
}

export async function updateCurrentUser(perfil) {
  const { data } = await httpClient.put('/users/me', {
    name: perfil.nome,
    email: perfil.email,
    age: perfil.idade === '' ? null : Number(perfil.idade),
    gender: emptyToNull(perfil.sexo),
    phone: emptyToNull(perfil.celular),
    address: emptyToNull(perfil.endereco),
    city: emptyToNull(perfil.cidade),
    state: emptyToNull(perfil.estado),
  })
  return mapUserToProfile(data)
}

export async function changeCurrentUserPassword(senhaAtual, novaSenha) {
  await httpClient.put('/users/me/password', {
    current_password: senhaAtual,
    new_password: novaSenha,
  })
}

export async function deleteCurrentUser(senha) {
  await httpClient.delete('/users/me', { data: { password: senha } })
}

function emptyToNull(valor) {
  const texto = String(valor ?? '').trim()
  return texto === '' ? null : texto
}

function mapUserToProfile(user) {
  return {
    nome: user.name ?? '',
    idade: user.age ?? '',
    sexo: user.gender ?? '',
    email: user.email ?? '',
    celular: user.phone ?? '',
    endereco: user.address ?? '',
    cidade: user.city ?? '',
    estado: user.state ?? '',
  }
}
