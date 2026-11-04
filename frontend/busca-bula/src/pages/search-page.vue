<script setup>
import { computed, onMounted, ref } from 'vue'
import { ChevronLeft, ChevronRight, FileText, Pill, Search, TriangleAlert } from 'lucide-vue-next'
import MemberLayout from '../components/member-layout.vue'
import { requireMemberSession } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
import { fetchTherapeuticClasses, searchMedicines } from '../services/medicine-service'

const ITENS_POR_PAGINA = 20

const parametrosIniciais = new URLSearchParams(window.location.search)
const termo = ref(parametrosIniciais.get('q') || '')
const classeTerapeutica = ref(parametrosIniciais.get('classe') || '')
const incluirInativos = ref(parametrosIniciais.get('inativos') === '1')
const pagina = ref(Number(parametrosIniciais.get('pagina')) || 1)

const classes = ref([])
const resultado = ref(null)
const buscando = ref(false)
const erro = ref('')
const formatadorDeNumero = new Intl.NumberFormat('pt-BR')

const totalDePaginas = computed(() =>
  resultado.value ? Math.max(1, Math.ceil(resultado.value.total / resultado.value.itensPorPagina)) : 1
)

const resumoDoResultado = computed(() => {
  if (!resultado.value) return ''
  const total = resultado.value.total
  const quantidade = `${formatadorDeNumero.format(total)} ${total === 1 ? 'medicamento encontrado' : 'medicamentos encontrados'}`
  return resultado.value.aproximado ? `${quantidade} com nome parecido` : quantidade
})

function atualizarEndereco() {
  const parametros = new URLSearchParams()
  if (termo.value.trim()) parametros.set('q', termo.value.trim())
  if (classeTerapeutica.value) parametros.set('classe', classeTerapeutica.value)
  if (incluirInativos.value) parametros.set('inativos', '1')
  if (pagina.value > 1) parametros.set('pagina', String(pagina.value))
  const consulta = parametros.toString()
  window.history.replaceState(null, '', `/search${consulta ? `?${consulta}` : ''}`)
}

async function executarBusca() {
  if (!termo.value.trim() && !classeTerapeutica.value) {
    resultado.value = null
    return
  }
  erro.value = ''
  buscando.value = true
  atualizarEndereco()
  try {
    resultado.value = await searchMedicines({
      termo: termo.value.trim(),
      classeTerapeutica: classeTerapeutica.value,
      incluirInativos: incluirInativos.value,
      pagina: pagina.value,
      itensPorPagina: ITENS_POR_PAGINA
    })
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível buscar agora. Tente novamente.')
  } finally {
    buscando.value = false
  }
}

function buscarDoInicio() {
  pagina.value = 1
  executarBusca()
}

function irParaPagina(destino) {
  pagina.value = destino
  executarBusca()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function carregarClasses() {
  try {
    classes.value = await fetchTherapeuticClasses()
  } catch {
    classes.value = []
  }
}

onMounted(() => {
  if (!requireMemberSession()) return
  carregarClasses()
  executarBusca()
})
</script>

<template>
  <MemberLayout
    ativo="buscar"
    titulo="Buscar medicamentos"
    descricao="Pesquise pelo nome comercial, princípio ativo, número de registro ou código de barras da caixa."
    :icone="Search"
  >
    <section class="search-card">
      <form class="search-form" role="search" @submit.prevent="buscarDoInicio">
        <div class="search-input">
          <Search :size="18" />
          <input
            v-model="termo"
            type="search"
            placeholder="Ex.: dipirona, Novalgina ou o código de barras da caixa"
            aria-label="Nome, princípio ativo, registro ou código de barras"
            autofocus
          />
        </div>
        <button class="search-button" type="submit" :disabled="buscando">
          {{ buscando ? 'Buscando...' : 'Buscar' }}
        </button>
      </form>

      <div class="filters">
        <label class="filter-select">
          <span>Classe terapêutica</span>
          <select v-model="classeTerapeutica" @change="buscarDoInicio">
            <option value="">Todas</option>
            <option v-for="classe in classes" :key="classe.nome" :value="classe.nome">
              {{ classe.nome }} ({{ classe.quantidade }})
            </option>
          </select>
        </label>
        <label class="filter-check">
          <input v-model="incluirInativos" type="checkbox" @change="buscarDoInicio" />
          <span>Incluir registros inativos</span>
        </label>
      </div>
    </section>

    <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>

    <p v-if="!resultado && !buscando && !erro" class="empty-state">
      Digite o nome do medicamento ou escolha uma classe terapêutica para começar.
    </p>

    <template v-if="resultado">
      <p class="results-summary" role="status">{{ resumoDoResultado }}</p>

      <p v-if="resultado.aproximado && resultado.total" class="approximate-note">
        <TriangleAlert :size="15" />Não achamos o termo exato. Confira se algum destes é o que você procura.
      </p>

      <p v-if="!resultado.total" class="empty-state">
        Nenhum medicamento encontrado. Confira a grafia ou tente pelo princípio ativo.
      </p>

      <ul class="results">
        <li v-for="medicamento in resultado.itens" :key="medicamento.registro">
          <a class="result-card" :href="`/medicine?registro=${medicamento.registro}`">
            <span class="result-icon"><Pill :size="20" /></span>
            <span class="result-body">
              <span class="result-name">{{ medicamento.nome }}</span>
              <span v-if="medicamento.principioAtivo" class="result-ingredient">{{ medicamento.principioAtivo }}</span>
              <span class="result-meta">
                {{ [medicamento.classeTerapeutica, medicamento.detentor].filter(Boolean).join(' · ') }}
              </span>
            </span>
            <span class="result-badges">
              <span v-if="medicamento.temBula" class="badge leaflet"><FileText :size="12" />Bula disponível</span>
              <span v-if="!medicamento.ativo" class="badge inactive">Registro inativo</span>
              <ChevronRight :size="18" class="result-arrow" />
            </span>
          </a>
        </li>
      </ul>

      <nav v-if="totalDePaginas > 1" class="pagination" aria-label="Páginas de resultado">
        <button type="button" :disabled="pagina <= 1 || buscando" @click="irParaPagina(pagina - 1)">
          <ChevronLeft :size="16" />Anterior
        </button>
        <span>Página {{ pagina }} de {{ totalDePaginas }}</span>
        <button type="button" :disabled="pagina >= totalDePaginas || buscando" @click="irParaPagina(pagina + 1)">
          Próxima<ChevronRight :size="16" />
        </button>
      </nav>
    </template>
  </MemberLayout>
</template>

<style scoped>
.search-card { background: #fff; border-radius: 16px; padding: 22px 24px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); display: flex; flex-direction: column; gap: 16px; }
.search-form { display: flex; gap: 12px; }
.search-input { flex: 1; min-width: 0; display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 999px; padding: 0 18px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.search-input:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.search-input input:focus-visible { outline: none; }
.search-input input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 13px 0; font-size: .95rem; color: var(--navy); }
.search-button { border: 0; border-radius: 999px; background: var(--teal); color: #fff; font-weight: 700; font-size: .9rem; padding: 0 28px; cursor: pointer; transition: background .2s; }
.search-button:hover { background: var(--teal-dark); }
.search-button:disabled { background: #9aafc0; cursor: not-allowed; }

.filters { display: flex; align-items: flex-end; gap: 20px; flex-wrap: wrap; }
.filter-select { display: flex; flex-direction: column; gap: 6px; font-size: .78rem; font-weight: 600; color: var(--navy); min-width: 0; flex: 1 1 280px; max-width: 460px; }
.filter-select select { border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; font-size: .85rem; color: var(--navy); background: #fff; width: 100%; }
.filter-check { display: inline-flex; align-items: center; gap: 8px; font-size: .85rem; color: var(--navy); cursor: pointer; padding-bottom: 10px; }
.filter-check input { accent-color: var(--teal); width: 16px; height: 16px; }

.results-summary { margin: 22px 0 10px; font-size: .85rem; font-weight: 600; color: var(--muted); }
.approximate-note { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: .85rem; color: #9a6100; background: #fff4e0; border-radius: 10px; padding: 10px 14px; }
.empty-state { margin-top: 22px; font-size: .9rem; color: var(--muted); }
.error-message { margin-top: 16px; color: var(--danger); font-size: .85rem; font-weight: 600; }

.results { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.result-card { display: flex; align-items: center; gap: 16px; background: #fff; border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); border: 1px solid transparent; transition: border-color .2s; }
.result-card:hover { border-color: var(--teal); }
.result-icon { width: 42px; height: 42px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.result-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.result-name { font-weight: 700; color: var(--navy); }
.result-ingredient { font-size: .85rem; color: var(--text); }
.result-meta { font-size: .75rem; color: var(--muted); }
.result-badges { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 999px; font-size: .72rem; font-weight: 700; white-space: nowrap; }
.badge.leaflet { background: var(--mint); color: var(--teal-dark); }
.badge.inactive { background: var(--bg-soft); color: var(--muted); }
.result-arrow { color: var(--muted); }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 20px; font-size: .85rem; color: var(--muted); }
.pagination button { display: inline-flex; align-items: center; gap: 4px; border: 1.5px solid var(--teal); background: #fff; color: var(--teal); font-weight: 600; font-size: .82rem; padding: 7px 16px; border-radius: 999px; cursor: pointer; }
.pagination button:disabled { opacity: .45; cursor: not-allowed; }

@media (max-width: 640px) {
  .search-form { flex-direction: column; }
  .search-button { padding: 12px; }
  .result-card { flex-wrap: wrap; }
  .result-badges { width: 100%; justify-content: flex-start; }
  .result-arrow { display: none; }
}
</style>
