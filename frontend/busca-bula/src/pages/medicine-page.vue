<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  ArrowLeft,
  Barcode,
  BookOpen,
  CircleCheck,
  CircleSlash,
  ExternalLink,
  FileText,
  Pill,
  ShieldAlert,
  TriangleAlert
} from 'lucide-vue-next'
import MemberLayout from '../components/member-layout.vue'
import { requireMemberSession } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
import { fetchMedicine, fetchMedicineLeaflet } from '../services/medicine-service'

const ALIQUOTA_PADRAO = '18%'
const BULARIO_ELETRONICO_URL = 'https://consultas.anvisa.gov.br/#/bulario/'

const registro = new URLSearchParams(window.location.search).get('registro') || ''
const medicamento = ref(null)
const carregando = ref(true)
const erro = ref('')
const aliquota = ref(ALIQUOTA_PADRAO)
const bula = ref(null)
const erroDaBula = ref('')

const formatadorDeMoeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const formatadorDeData = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' })
const formatadorDeMesAno = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })

const voltarPara = computed(() => {
  const anterior = document.referrer ? new URL(document.referrer) : null
  return anterior && anterior.origin === window.location.origin && anterior.pathname === '/search'
    ? `${anterior.pathname}${anterior.search}`
    : '/search'
})

const informacoes = computed(() => {
  if (!medicamento.value) return []
  const item = medicamento.value
  return [
    { rotulo: 'Princípio ativo', valor: item.principioAtivo },
    { rotulo: 'Classe terapêutica', valor: item.classeTerapeutica },
    { rotulo: 'Categoria', valor: item.categoria },
    { rotulo: 'Detentor do registro', valor: item.detentor },
    { rotulo: 'Número de registro', valor: item.registro },
    {
      rotulo: 'Validade do registro',
      valor: item.validadeDoRegistro ? formatadorDeMesAno.format(new Date(item.validadeDoRegistro)) : null
    }
  ].filter((informacao) => informacao.valor)
})

const apresentacoesComPreco = computed(() =>
  (medicamento.value?.apresentacoes ?? []).map((apresentacao) => ({
    ...apresentacao,
    precoSelecionado: apresentacao.precosMaximos[aliquota.value] ?? null
  }))
)

function formatarPreco(apresentacao) {
  if (apresentacao.usoHospitalar) return 'Uso hospitalar'
  return apresentacao.precoSelecionado === null ? '—' : formatadorDeMoeda.format(apresentacao.precoSelecionado)
}

async function carregarBula() {
  try {
    bula.value = await fetchMedicineLeaflet(registro)
  } catch (falha) {
    erroDaBula.value = extractErrorMessage(falha, 'Não foi possível carregar o texto da bula.')
  }
}

async function carregarMedicamento() {
  if (!/^\d{9}$/.test(registro)) {
    erro.value = 'Medicamento não encontrado.'
    carregando.value = false
    return
  }
  try {
    medicamento.value = await fetchMedicine(registro)
    const aliquotas = medicamento.value.aliquotasDisponiveis
    if (aliquotas.length && !aliquotas.includes(aliquota.value)) aliquota.value = aliquotas[0]
    if (medicamento.value.textoDaBulaDisponivel) carregarBula()
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível carregar o medicamento.')
  } finally {
    carregando.value = false
  }
}

onMounted(() => {
  if (requireMemberSession()) carregarMedicamento()
})
</script>

<template>
  <MemberLayout
    ativo="buscar"
    :titulo="medicamento?.nome || 'Medicamento'"
    :descricao="medicamento?.principioAtivo || ''"
    :icone="Pill"
  >
    <a :href="voltarPara" class="back-link"><ArrowLeft :size="15" />Voltar para a busca</a>

    <p v-if="carregando" class="empty-state">Carregando medicamento...</p>
    <p v-else-if="erro" class="error-message" role="alert">{{ erro }}</p>

    <template v-else-if="medicamento">
      <div class="detail-grid">
        <section class="detail-card">
          <h2 class="card-title"><Pill :size="17" />Registro na ANVISA</h2>
          <p class="registration-status" :class="{ inactive: !medicamento.ativo }">
            <component :is="medicamento.ativo ? CircleCheck : CircleSlash" :size="15" />
            {{ medicamento.ativo ? 'Registro ativo' : 'Registro inativo' }}
          </p>
          <dl class="info-list">
            <div v-for="informacao in informacoes" :key="informacao.rotulo">
              <dt>{{ informacao.rotulo }}</dt>
              <dd>{{ informacao.valor }}</dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <h2 class="card-title"><FileText :size="17" />Bula do paciente</h2>
          <p v-if="medicamento.bula" class="leaflet-text">
            Bula publicada no Bulário Eletrônico da ANVISA
            <template v-if="medicamento.bula.publicadaEm">
              em {{ formatadorDeData.format(new Date(medicamento.bula.publicadaEm)) }}
            </template>.
          </p>
          <p v-else-if="!medicamento.textoDaBulaDisponivel" class="leaflet-text">
            Não há bula do paciente publicada no Bulário Eletrônico para este registro.
          </p>

          <a v-if="medicamento.textoDaBulaDisponivel" class="primary-link" href="#bula">
            <BookOpen :size="15" />Ler a bula
          </a>
          <template v-else-if="medicamento.bula">
            <p class="leaflet-hint">O texto desta bula ainda não está disponível no Busca Bula.</p>
            <a class="outline-button" :href="BULARIO_ELETRONICO_URL" target="_blank" rel="noopener">
              Abrir o Bulário Eletrônico<ExternalLink :size="14" />
            </a>
          </template>
        </section>
      </div>

      <section v-if="medicamento.textoDaBulaDisponivel" id="bula" class="detail-card leaflet-card">
        <h2 class="card-title"><BookOpen :size="17" />Bula do paciente</h2>

        <p v-if="erroDaBula" class="error-message" role="alert">{{ erroDaBula }}</p>
        <p v-else-if="!bula" class="empty-state">Carregando bula...</p>

        <template v-else>
          <p v-if="bula.desatualizada" class="outdated-note" role="note">
            <TriangleAlert :size="16" />
            <span>
              A ANVISA publicou uma versão mais recente desta bula
              <template v-if="bula.publicadaEm">em {{ formatadorDeData.format(new Date(bula.publicadaEm)) }}</template>.
              Confira a versão atual no
              <a :href="BULARIO_ELETRONICO_URL" target="_blank" rel="noopener">Bulário Eletrônico</a>.
            </span>
          </p>

          <details v-for="secao in bula.secoes" :key="secao.numero" class="leaflet-section" :open="secao.numero === 1">
            <summary>
              <span class="section-number">{{ secao.numero }}</span>
              <span class="section-title">{{ secao.titulo }}</span>
            </summary>
            <p class="section-content">{{ secao.conteudo }}</p>
          </details>

          <p v-if="bula.atribuicao" class="attribution">
            {{ bula.atribuicao.texto }}
            <a :href="bula.atribuicao.url" target="_blank" rel="noopener">Ver fonte</a>
          </p>
          <p v-else class="attribution">Texto extraído do PDF da bula do paciente publicado no Bulário Eletrônico da ANVISA.</p>
        </template>
      </section>

      <section class="detail-card presentations-card">
        <div class="presentations-header">
          <h2 class="card-title"><Barcode :size="17" />Apresentações e preço máximo</h2>
          <label v-if="medicamento.aliquotasDisponiveis.length" class="tax-select">
            <span>ICMS</span>
            <select v-model="aliquota" aria-label="Alíquota de ICMS usada no preço máximo">
              <option v-for="opcao in medicamento.aliquotasDisponiveis" :key="opcao" :value="opcao">{{ opcao }}</option>
            </select>
          </label>
        </div>

        <p v-if="!apresentacoesComPreco.length" class="empty-state">
          Este registro não aparece na tabela de preços da CMED.
        </p>

        <template v-else>
          <p class="price-note">
            Preço máximo ao consumidor (PMC) definido pela CMED com ICMS de {{ aliquota }}. A alíquota varia por estado:
            confira a aplicada a medicamentos no seu.
          </p>
          <table class="presentations-table">
            <thead>
              <tr>
                <th>Apresentação</th>
                <th>Código de barras</th>
                <th>Tarja</th>
                <th class="numeric">PMC</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apresentacao in apresentacoesComPreco" :key="apresentacao.codigoGgrem">
                <td data-label="Apresentação">
                  {{ apresentacao.descricao || '—' }}
                  <span v-if="apresentacao.comercializado === false" class="not-marketed">Sem comercialização informada à CMED</span>
                </td>
                <td data-label="Código de barras" class="barcodes">{{ apresentacao.codigosDeBarras.join(', ') || '—' }}</td>
                <td data-label="Tarja">
                  <span v-if="apresentacao.tarja" class="label-badge">
                    <ShieldAlert v-if="apresentacao.tarja.includes('Preta') || apresentacao.tarja.includes('Vermelha')" :size="12" />
                    {{ apresentacao.tarja }}
                  </span>
                  <span v-else>—</span>
                </td>
                <td data-label="PMC" class="numeric">{{ formatarPreco(apresentacao) }}</td>
              </tr>
            </tbody>
          </table>
        </template>
      </section>
    </template>
  </MemberLayout>
</template>

<style scoped>
.back-link { display: inline-flex; align-items: center; gap: 6px; font-size: .85rem; font-weight: 600; color: var(--teal); margin-bottom: 18px; }
.back-link:hover { color: var(--teal-dark); }
.empty-state { font-size: .9rem; color: var(--muted); }
.error-message { color: var(--danger); font-size: .9rem; font-weight: 600; }

.detail-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 20px; align-items: start; margin-bottom: 20px; }
.detail-card { background: #fff; border-radius: 16px; padding: 22px 24px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); min-width: 0; }
.card-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 14px; }
.card-title svg { color: var(--teal); }

.registration-status { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; font-size: .78rem; font-weight: 700; background: var(--mint); color: var(--teal-dark); margin-bottom: 14px; }
.registration-status.inactive { background: var(--bg-soft); color: var(--muted); }
.info-list { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; }
.info-list dt { font-size: .75rem; font-weight: 600; color: var(--muted); }
.info-list dd { font-size: .9rem; color: var(--navy); overflow-wrap: anywhere; }

.leaflet-text { font-size: .9rem; color: var(--text); }
.leaflet-hint { font-size: .8rem; color: var(--muted); margin: 8px 0 16px; }
.outline-button { display: inline-flex; align-items: center; gap: 8px; border: 1.5px solid var(--teal); color: var(--teal); font-weight: 600; font-size: .85rem; padding: 9px 18px; border-radius: 999px; transition: all .2s; }
.outline-button:hover { background: var(--teal); color: #fff; }
.primary-link { display: inline-flex; align-items: center; gap: 8px; margin-top: 14px; background: var(--teal); color: #fff; font-weight: 700; font-size: .88rem; padding: 10px 22px; border-radius: 999px; transition: background .2s; }
.primary-link:hover { background: var(--teal-dark); }

.leaflet-card { margin-bottom: 20px; scroll-margin-top: 90px; }
.outdated-note { display: flex; align-items: flex-start; gap: 10px; background: #fff4e0; color: #7a4d00; border-radius: 12px; padding: 12px 14px; font-size: .85rem; margin-bottom: 14px; }
.outdated-note svg { flex: none; margin-top: 1px; color: #9a6100; }
.outdated-note a { color: inherit; font-weight: 700; text-decoration: underline; }
.leaflet-section { border-top: 1px solid var(--line); }
.leaflet-section:last-of-type { border-bottom: 1px solid var(--line); }
.leaflet-section summary { display: flex; align-items: center; gap: 12px; padding: 14px 4px; cursor: pointer; list-style: none; font-weight: 700; color: var(--navy); font-size: .92rem; }
.leaflet-section summary::-webkit-details-marker { display: none; }
.leaflet-section summary::after { content: '+'; margin-left: auto; font-size: 1.2rem; font-weight: 600; color: var(--teal); }
.leaflet-section[open] summary::after { content: '–'; }
.section-number { width: 26px; height: 26px; border-radius: 50%; background: var(--mint); color: var(--teal-dark); display: grid; place-items: center; font-size: .78rem; flex: none; }
.section-content { white-space: pre-line; font-size: .9rem; line-height: 1.65; color: var(--text); padding: 0 4px 18px 42px; overflow-wrap: anywhere; }
.attribution { margin-top: 14px; font-size: .75rem; color: var(--muted); }
.attribution a { color: var(--teal); font-weight: 600; }

.presentations-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 4px; }
.presentations-header .card-title { margin-bottom: 0; }
.tax-select { display: inline-flex; align-items: center; gap: 8px; font-size: .8rem; font-weight: 600; color: var(--navy); }
.tax-select select { border: 1px solid var(--line); border-radius: 10px; padding: 7px 10px; font-size: .85rem; color: var(--navy); background: #fff; }
.price-note { font-size: .8rem; color: var(--muted); margin: 10px 0 14px; }

.presentations-table { width: 100%; border-collapse: collapse; font-size: .85rem; }
.presentations-table th { text-align: left; font-size: .72rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 0 10px 10px; border-bottom: 1px solid var(--line); }
.presentations-table td { padding: 12px 10px; border-bottom: 1px solid var(--line); color: var(--navy); vertical-align: top; }
.presentations-table tr:last-child td { border-bottom: 0; }
.presentations-table .numeric { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 700; }
.barcodes { font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.not-marketed { display: block; font-size: .72rem; color: var(--muted); margin-top: 2px; }
.label-badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; background: var(--bg-soft); font-size: .72rem; font-weight: 600; color: var(--navy); white-space: nowrap; }

@media (max-width: 900px) {
  .detail-grid { grid-template-columns: 1fr; }
  .presentations-table thead { display: none; }
  .presentations-table tr { display: grid; gap: 4px; padding: 12px 0; border-bottom: 1px solid var(--line); }
  .presentations-table td { padding: 0; border: 0; }
  .presentations-table .numeric { text-align: left; }
  .presentations-table td[data-label]::before { content: attr(data-label) ': '; color: var(--muted); font-size: .75rem; font-weight: 600; }
}
@media (max-width: 520px) {
  .info-list { grid-template-columns: 1fr; }
}
</style>
