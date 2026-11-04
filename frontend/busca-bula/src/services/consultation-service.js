import httpClient from './http-client'

const HISTORY_PATH = '/users/me/consultations'

export async function fetchConsultationHistory() {
  const { data } = await httpClient.get(HISTORY_PATH)
  return mapHistory(data)
}

export async function updateConsultationConsent(ativado) {
  const { data } = await httpClient.put(`${HISTORY_PATH}/consent`, { enabled: ativado })
  return mapHistory(data)
}

export async function removeConsultation(id) {
  await httpClient.delete(`${HISTORY_PATH}/${id}`)
}

export async function clearConsultationHistory() {
  await httpClient.delete(HISTORY_PATH)
}

function mapHistory(history) {
  return {
    ativado: history.enabled,
    consentidoEm: history.consented_at,
    consultas: history.items.map((item) => ({
      id: item.id,
      registro: item.registration_number,
      nome: item.product_name,
      principioAtivo: item.active_ingredient,
      consultadoEm: item.consulted_at,
    })),
  }
}
