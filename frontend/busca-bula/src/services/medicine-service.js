import httpClient from './http-client'

export async function searchMedicines({ termo, classeTerapeutica, incluirInativos, pagina, itensPorPagina = 20 }) {
  const { data } = await httpClient.get('/medicines', {
    params: {
      q: termo || undefined,
      therapeutic_class: classeTerapeutica || undefined,
      include_inactive: incluirInativos || undefined,
      page: pagina,
      page_size: itensPorPagina,
    },
  })
  return {
    itens: data.items.map(mapMedicineSummary),
    total: data.total,
    pagina: data.page,
    itensPorPagina: data.page_size,
    aproximado: data.approximate,
  }
}

export async function fetchTherapeuticClasses() {
  const { data } = await httpClient.get('/medicines/therapeutic-classes')
  return data.map((item) => ({ nome: item.name, quantidade: item.medicines_count }))
}

export async function fetchMedicine(registro) {
  const { data } = await httpClient.get(`/medicines/${registro}`)
  return {
    ...mapMedicineSummary(data),
    cnpjDetentor: data.holder_cnpj,
    processo: data.process_number,
    validadeDoRegistro: data.registration_expires_on,
    bula: data.leaflet
      ? {
          idNoBulario: data.leaflet.bulario_product_id,
          empresa: data.leaflet.company_name,
          expediente: data.leaflet.expedient_number,
          publicadaEm: data.leaflet.published_at,
        }
      : null,
    apresentacoes: data.presentations.map((item) => ({
      codigoGgrem: item.ggrem_code,
      descricao: item.presentation,
      codigosDeBarras: item.ean_codes,
      tipo: item.product_type,
      tarja: item.prescription_label,
      usoHospitalar: item.hospital_restricted,
      comercializado: item.marketed,
      precosMaximos: item.consumer_prices,
    })),
    aliquotasDisponiveis: data.consumer_price_tax_rates,
    textoDaBulaDisponivel: data.leaflet_text_available,
  }
}

export async function fetchMedicineLeaflet(registro) {
  const { data } = await httpClient.get(`/medicines/${registro}/leaflet`)
  return {
    origem: data.source,
    atribuicao: data.attribution ? { texto: data.attribution.text, url: data.attribution.url } : null,
    desatualizada: data.is_outdated,
    publicadaEm: data.published_at,
    secoes: data.sections.map((section) => ({
      numero: section.number,
      titulo: section.title,
      conteudo: section.content,
    })),
  }
}

function mapMedicineSummary(medicine) {
  return {
    registro: medicine.registration_number,
    nome: medicine.product_name,
    principioAtivo: medicine.active_ingredient,
    classeTerapeutica: medicine.therapeutic_class,
    categoria: medicine.regulatory_category,
    detentor: medicine.holder_name,
    ativo: medicine.is_active,
    temBula: medicine.has_leaflet ?? Boolean(medicine.leaflet),
  }
}
