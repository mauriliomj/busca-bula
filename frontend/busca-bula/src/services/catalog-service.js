import httpClient from './http-client'

export async function fetchCatalogSummary() {
  const { data } = await httpClient.get('/platform/catalog')
  return {
    totalDeMedicamentos: data.medicines_total,
    medicamentosAtivos: data.active_medicines_total,
    totalDeBulas: data.leaflets_total,
    totalDeApresentacoes: data.presentations_total,
    cobertura: {
      ativosComBula: data.coverage.active_medicines_with_leaflet,
      ativosComPreco: data.coverage.active_medicines_with_price,
      percentualComBula: data.coverage.leaflet_percentage,
      percentualComPreco: data.coverage.price_percentage,
    },
    importacoes: data.latest_imports.map(mapCatalogImport),
    sincronizando: data.is_importing,
  }
}

export async function startCatalogImport() {
  const { data } = await httpClient.post('/platform/catalog/imports')
  return data.map(mapCatalogImport)
}

function mapCatalogImport(catalogImport) {
  return {
    id: catalogImport.id,
    fonte: catalogImport.source,
    situacao: catalogImport.status,
    iniciadaEm: catalogImport.started_at,
    finalizadaEm: catalogImport.finished_at,
    linhasLidas: catalogImport.rows_read,
    registrosImportados: catalogImport.rows_loaded,
    erro: catalogImport.error_message,
  }
}
