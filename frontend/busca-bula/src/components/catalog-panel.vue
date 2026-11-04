<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { CircleAlert, CircleCheck, Database, FileText, LoaderCircle, Pill, RefreshCw, Tags } from 'lucide-vue-next'
import { fetchCatalogSummary, startCatalogImport } from '../services/catalog-service'
import { extractErrorMessage } from '../services/http-client'

const INTERVALO_DE_ATUALIZACAO = 5000

const FONTES = {
  medicines: { nome: 'Catálogo de medicamentos', origem: 'ANVISA – dados abertos' },
  leaflets: { nome: 'Índice de bulas', origem: 'ANVISA – Bulário Eletrônico' },
  prices: { nome: 'Tabela de preços', origem: 'CMED' }
}

const SITUACOES = {
  running: { rotulo: 'Sincronizando', icone: LoaderCircle },
  succeeded: { rotulo: 'Concluída', icone: CircleCheck },
  failed: { rotulo: 'Falhou', icone: CircleAlert }
}

const resumo = ref(null)
const carregando = ref(true)
const iniciando = ref(false)
const erro = ref('')
let temporizador = null

const formatadorDeNumero = new Intl.NumberFormat('pt-BR')
const formatadorDePercentual = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const formatadorDeData = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

const indicadores = computed(() => {
  if (!resumo.value) return []
  return [
    {
      rotulo: 'Medicamentos registrados',
      valor: resumo.value.totalDeMedicamentos,
      detalhe: `${formatarNumero(resumo.value.medicamentosAtivos)} com registro ativo`,
      icone: Pill
    },
    {
      rotulo: 'Bulas indexadas',
      valor: resumo.value.totalDeBulas,
      detalhe: 'Bula do paciente no Bulário Eletrônico',
      icone: FileText
    },
    {
      rotulo: 'Apresentações com preço',
      valor: resumo.value.totalDeApresentacoes,
      detalhe: 'Preço máximo ao consumidor (CMED)',
      icone: Tags
    }
  ]
})

const medidores = computed(() => {
  if (!resumo.value) return []
  const { cobertura, medicamentosAtivos } = resumo.value
  return [
    {
      rotulo: 'Ativos com bula',
      percentual: cobertura.percentualComBula,
      quantidade: cobertura.ativosComBula,
      total: medicamentosAtivos
    },
    {
      rotulo: 'Ativos com preço',
      percentual: cobertura.percentualComPreco,
      quantidade: cobertura.ativosComPreco,
      total: medicamentosAtivos
    }
  ]
})

const linhasDeImportacao = computed(() =>
  Object.keys(FONTES).map((fonte) => ({
    fonte,
    ...FONTES[fonte],
    importacao: resumo.value?.importacoes.find((item) => item.fonte === fonte) ?? null
  }))
)

function formatarNumero(valor) {
  return valor === null || valor === undefined ? '—' : formatadorDeNumero.format(valor)
}

function formatarData(valor) {
  return valor ? formatadorDeData.format(new Date(valor)) : '—'
}

function formatarDuracao(importacao) {
  if (!importacao.finalizadaEm) return '—'
  const segundos = Math.round((new Date(importacao.finalizadaEm) - new Date(importacao.iniciadaEm)) / 1000)
  return segundos < 60 ? `${segundos} s` : `${Math.floor(segundos / 60)} min ${segundos % 60} s`
}

function agendarAtualizacao() {
  clearTimeout(temporizador)
  if (resumo.value?.sincronizando) temporizador = setTimeout(carregarResumo, INTERVALO_DE_ATUALIZACAO)
}

async function carregarResumo() {
  try {
    resumo.value = await fetchCatalogSummary()
    erro.value = ''
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível carregar o catálogo.')
  } finally {
    carregando.value = false
    agendarAtualizacao()
  }
}

async function sincronizar() {
  erro.value = ''
  iniciando.value = true
  try {
    await startCatalogImport()
    await carregarResumo()
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível iniciar a sincronização.')
  } finally {
    iniciando.value = false
  }
}

onMounted(carregarResumo)
onBeforeUnmount(() => clearTimeout(temporizador))
</script>

<template>
  <div class="catalog-panel">
    <div class="panel-toolbar">
      <p class="toolbar-text">
        Dados públicos da ANVISA e da CMED, compartilhados por todas as organizações em modo somente leitura.
      </p>
      <button
        class="sync-button"
        type="button"
        :disabled="iniciando || carregando || resumo?.sincronizando"
        @click="sincronizar"
      >
        <RefreshCw :size="15" :class="{ spinning: resumo?.sincronizando }" />
        {{ resumo?.sincronizando ? 'Sincronizando...' : 'Sincronizar agora' }}
      </button>
    </div>

    <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>
    <p v-if="carregando" class="empty-state">Carregando catálogo...</p>

    <template v-else-if="resumo">
      <section class="kpi-row" aria-label="Totais do catálogo">
        <article v-for="indicador in indicadores" :key="indicador.rotulo" class="stat-tile">
          <p class="stat-label"><component :is="indicador.icone" :size="15" />{{ indicador.rotulo }}</p>
          <p class="stat-value">{{ formatarNumero(indicador.valor) }}</p>
          <p class="stat-detail">{{ indicador.detalhe }}</p>
        </article>
      </section>

      <section class="panel-card" aria-labelledby="titulo-cobertura">
        <h3 id="titulo-cobertura" class="card-title"><Database :size="16" />Cobertura dos medicamentos ativos</h3>
        <div class="meters">
          <div v-for="medidor in medidores" :key="medidor.rotulo" class="meter">
            <div class="meter-header">
              <span class="meter-label">{{ medidor.rotulo }}</span>
              <span class="meter-value">{{ formatadorDePercentual.format(medidor.percentual) }}%</span>
            </div>
            <div
              class="meter-track"
              role="meter"
              :aria-label="medidor.rotulo"
              aria-valuemin="0"
              aria-valuemax="100"
              :aria-valuenow="medidor.percentual"
            >
              <div class="meter-fill" :style="{ width: `${Math.min(medidor.percentual, 100)}%` }" />
            </div>
            <p class="meter-detail">
              {{ formatarNumero(medidor.quantidade) }} de {{ formatarNumero(medidor.total) }} registros ativos
            </p>
          </div>
        </div>
      </section>

      <section class="panel-card" aria-labelledby="titulo-importacoes">
        <h3 id="titulo-importacoes" class="card-title"><RefreshCw :size="16" />Última sincronização por fonte</h3>
        <table class="imports-table">
          <thead>
            <tr>
              <th>Fonte</th>
              <th>Situação</th>
              <th>Início</th>
              <th>Duração</th>
              <th class="numeric">Linhas lidas</th>
              <th class="numeric">Registros</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="linha in linhasDeImportacao" :key="linha.fonte">
              <td>
                <span class="source-name">{{ linha.nome }}</span>
                <span class="source-origin">{{ linha.origem }}</span>
              </td>
              <td>
                <span v-if="linha.importacao" class="status-badge" :class="linha.importacao.situacao">
                  <component
                    :is="SITUACOES[linha.importacao.situacao].icone"
                    :size="13"
                    :class="{ spinning: linha.importacao.situacao === 'running' }"
                  />
                  {{ SITUACOES[linha.importacao.situacao].rotulo }}
                </span>
                <span v-else class="status-badge">Nunca sincronizada</span>
                <span v-if="linha.importacao?.erro" class="import-error">{{ linha.importacao.erro }}</span>
              </td>
              <td data-label="Início">{{ formatarData(linha.importacao?.iniciadaEm) }}</td>
              <td data-label="Duração">{{ linha.importacao ? formatarDuracao(linha.importacao) : '—' }}</td>
              <td class="numeric" data-label="Linhas lidas">{{ formatarNumero(linha.importacao?.linhasLidas) }}</td>
              <td class="numeric" data-label="Registros">{{ formatarNumero(linha.importacao?.registrosImportados) }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<style scoped>
.catalog-panel { display: flex; flex-direction: column; gap: 20px; }
.catalog-panel button { font-family: inherit; }
.panel-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.toolbar-text { font-size: .85rem; color: var(--muted); max-width: 560px; }
.sync-button { display: inline-flex; align-items: center; gap: 8px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .88rem; padding: 12px 24px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.sync-button:hover { background: var(--teal-dark); }
.sync-button:disabled { background: #9aafc0; cursor: not-allowed; }

.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-tile, .panel-card { background: #fff; border-radius: 16px; padding: 20px 22px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.stat-label { display: flex; align-items: center; gap: 8px; font-size: .8rem; font-weight: 600; color: var(--muted); }
.stat-label svg { color: var(--teal); }
.stat-value { font-size: 2rem; font-weight: 800; color: var(--navy); letter-spacing: -.02em; margin: 6px 0 2px; }
.stat-detail { font-size: .78rem; color: var(--muted); }

.card-title { display: flex; align-items: center; gap: 10px; font-size: .95rem; font-weight: 700; color: var(--navy); margin-bottom: 18px; }
.card-title svg { color: var(--teal); }

.meters { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.meter-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
.meter-label { font-size: .85rem; font-weight: 600; color: var(--navy); }
.meter-value { font-size: 1.1rem; font-weight: 800; color: var(--navy); }
.meter-track { height: 10px; border-radius: 999px; background: var(--mint); overflow: hidden; }
.meter-fill { height: 100%; border-radius: 999px; background: var(--teal); transition: width .4s; }
.meter-detail { font-size: .75rem; color: var(--muted); margin-top: 6px; }

.imports-table { width: 100%; border-collapse: collapse; font-size: .85rem; }
.imports-table th { text-align: left; font-size: .72rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 0 10px 10px; border-bottom: 1px solid var(--line); }
.imports-table td { padding: 12px 10px; border-bottom: 1px solid var(--line); color: var(--navy); vertical-align: top; }
.imports-table tr:last-child td { border-bottom: 0; }
.imports-table .numeric { text-align: right; font-variant-numeric: tabular-nums; }
.source-name { display: block; font-weight: 600; }
.source-origin { display: block; font-size: .75rem; color: var(--muted); }
.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; font-size: .75rem; font-weight: 700; background: var(--bg-soft); color: var(--muted); white-space: nowrap; }
.status-badge.succeeded { background: var(--mint); color: var(--teal-dark); }
.status-badge.failed { background: #fbe9e7; color: #c0392b; }
.status-badge.running { background: #fff4e0; color: #9a6100; }
.import-error { display: block; margin-top: 6px; font-size: .75rem; color: #c0392b; max-width: 280px; word-break: break-word; }

.empty-state { font-size: .88rem; color: var(--muted); }
.error-message { color: #c0392b; font-size: .85rem; font-weight: 600; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .kpi-row, .meters { grid-template-columns: 1fr; }
  .imports-table thead { display: none; }
  .imports-table tr { display: grid; gap: 4px; padding: 10px 0; border-bottom: 1px solid var(--line); }
  .imports-table td { padding: 0; border: 0; }
  .imports-table .numeric { text-align: left; }
  .imports-table td[data-label]::before { content: attr(data-label) ': '; color: var(--muted); font-size: .75rem; font-weight: 600; }
}
@media (prefers-reduced-motion: reduce) {
  .spinning { animation: none; }
  .meter-fill, .sync-button { transition: none; }
}
</style>
