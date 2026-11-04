<script setup>
import { computed, ref, watch } from 'vue'
import { NavigationFailureType, isNavigationFailure, useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, FileText, Pill, Search, TriangleAlert } from 'lucide-vue-next'
import MemberLayout from '../components/member-layout.vue'
import { extractErrorMessage } from '../services/http-client'
import { fetchTherapeuticClasses, searchMedicines } from '../services/medicine-service'
import { ensureSession } from '../services/session-service'

const ITENS_POR_PAGINA = 20
const EXEMPLOS = ['Dipirona', 'Paracetamol', 'Amoxicilina', 'Losartana']

const route = useRoute()
const router = useRouter()

const termo = ref('')
const classeTerapeutica = ref('')
const incluirInativos = ref(false)
const pagina = ref(1)

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

function lerConsulta(query) {
  termo.value = typeof query.q === 'string' ? query.q : ''
  classeTerapeutica.value = typeof query.classe === 'string' ? query.classe : ''
  incluirInativos.value = query.inativos === '1'
  pagina.value = Math.max(1, Number(query.pagina) || 1)
}

function montarConsulta(destino) {
  const consulta = {}
  if (termo.value.trim()) consulta.q = termo.value.trim()
  if (classeTerapeutica.value) consulta.classe = classeTerapeutica.value
  if (incluirInativos.value) consulta.inativos = '1'
  if (destino > 1) consulta.pagina = String(destino)
  return consulta
}

function temCriterio() {
  return Boolean(termo.value.trim() || classeTerapeutica.value)
}

async function carregarClasses() {
  if (classes.value.length) return
  try {
    classes.value = await fetchTherapeuticClasses()
  } catch {
    classes.value = []
  }
}

async function executarBusca() {
  if (!temCriterio()) {
    resultado.value = null
    return
  }
  if (!(await ensureSession())) {
    router.replace({ name: 'login', query: { next: route.fullPath } })
    return
  }
  carregarClasses()
  erro.value = ''
  buscando.value = true
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

async function navegarPara(destino) {
  const falha = await router.push({ name: 'search', query: montarConsulta(destino) })
  if (isNavigationFailure(falha, NavigationFailureType.duplicated)) executarBusca()
}

function buscarDoInicio() {
  navegarPara(1)
}

function buscarExemplo(nome) {
  termo.value = nome
  buscarDoInicio()
}

watch(
  () => route.query,
  (query) => {
    lerConsulta(query)
    executarBusca()
  },
  { immediate: true }
)

ensureSession().then((ativa) => {
  if (ativa) carregarClasses()
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
            enterkeyhint="search"
            placeholder="Ex.: dipirona, Novalgina ou código de barras"
            aria-label="Nome, princípio ativo, registro ou código de barras"
          />
        </div>
        <button class="search-button" type="submit" :disabled="buscando">
          {{ buscando ? 'Buscando...' : 'Buscar' }}
        </button>
      </form>

      <div v-if="classes.length" class="filters">
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

    <div v-if="!resultado && !buscando && !erro" class="empty-state">
      <p>Digite o nome do medicamento ou escolha uma classe terapêutica para começar.</p>
      <div class="examples">
        <span>Exemplos:</span>
        <button v-for="exemplo in EXEMPLOS" :key="exemplo" type="button" class="example-chip" @click="buscarExemplo(exemplo)">
          {{ exemplo }}
        </button>
      </div>
    </div>

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
          <RouterLink class="result-card" :to="{ name: 'medicine', params: { registro: medicamento.registro } }">
            <span class="result-icon"><Pill :size="20" /></span>
            <span class="result-body">
              <span class="result-name">{{ medicamento.nome }}</span>
              <span v-if="medicamento.principioAtivo" class="result-ingredient">{{ medicamento.principioAtivo }}</span>
              <span class="result-meta">
                {{ [medicamento.classeTerapeutica, medicamento.detentor].filter(Boolean).join(' · ') }}
              </span>
              <span v-if="medicamento.temBula || !medicamento.ativo" class="result-badges">
                <span v-if="medicamento.temBula" class="badge leaflet"><FileText :size="12" />Bula disponível</span>
                <span v-if="!medicamento.ativo" class="badge inactive">Registro inativo</span>
              </span>
            </span>
            <ChevronRight :size="18" class="result-arrow" />
          </RouterLink>
        </li>
      </ul>

      <nav v-if="totalDePaginas > 1" class="pagination" aria-label="Páginas de resultado">
        <button type="button" :disabled="pagina <= 1 || buscando" @click="navegarPara(pagina - 1)">
          <ChevronLeft :size="16" /><span>Anterior</span>
        </button>
        <span>{{ pagina }} de {{ totalDePaginas }}</span>
        <button type="button" :disabled="pagina >= totalDePaginas || buscando" @click="navegarPara(pagina + 1)">
          <span>Próxima</span><ChevronRight :size="16" />
        </button>
      </nav>
    </template>
  </MemberLayout>
</template>

<style scoped>
.search-card { background: #fff; border-radius: 16px; padding: 16px; box-shadow: var(--card-shadow); display: flex; flex-direction: column; gap: 14px; }
.search-form { display: flex; flex-direction: column; gap: 10px; }
.search-input { flex: 1; min-width: 0; display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 999px; padding: 0 18px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.search-input:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.search-input input:focus-visible { outline: none; }
.search-input input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 13px 0; font-size: 1rem; color: var(--navy); }
.search-button { min-height: 48px; border: 0; border-radius: 999px; background: var(--teal); color: #fff; font-weight: 700; font-size: 1rem; padding: 0 28px; cursor: pointer; transition: background .2s; }
.search-button:hover { background: var(--teal-dark); }
.search-button:disabled { background: #9aafc0; cursor: not-allowed; }

.filters { display: flex; flex-direction: column; gap: 12px; }
.filter-select { display: flex; flex-direction: column; gap: 6px; font-size: .8rem; font-weight: 600; color: var(--navy); min-width: 0; }
.filter-select select { border: 1px solid var(--line); border-radius: 10px; padding: 11px 12px; font-size: 1rem; color: var(--navy); background: #fff; width: 100%; }
.filter-check { display: inline-flex; align-items: center; gap: 10px; min-height: 44px; font-size: .9rem; color: var(--navy); cursor: pointer; }
.filter-check input { accent-color: var(--teal); width: 20px; height: 20px; }

.results-summary { margin: 20px 0 10px; font-size: .85rem; font-weight: 600; color: var(--muted); }
.approximate-note { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: .85rem; color: #9a6100; background: #fff4e0; border-radius: 10px; padding: 10px 14px; }
.empty-state { margin-top: 20px; font-size: .9rem; color: var(--muted); }
.examples { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 12px; }
.examples span { font-weight: 600; color: var(--navy); }
.example-chip { min-height: 40px; padding: 0 16px; border: 1px solid var(--line); border-radius: 999px; background: #fff; color: var(--teal-dark); font-weight: 600; font-size: .88rem; cursor: pointer; transition: border-color .2s; }
.example-chip:hover { border-color: var(--teal); }
.error-message { margin-top: 16px; color: var(--danger); font-size: .9rem; font-weight: 600; }

.results { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.result-card { display: flex; align-items: center; gap: 12px; background: #fff; border-radius: 14px; padding: 14px; box-shadow: var(--card-shadow); border: 1px solid transparent; transition: border-color .2s; }
.result-card:hover { border-color: var(--teal); }
.result-icon { width: 40px; height: 40px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; align-self: flex-start; }
.result-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.result-name { font-weight: 700; color: var(--navy); overflow-wrap: anywhere; }
.result-ingredient { font-size: .85rem; color: var(--text); overflow-wrap: anywhere; }
.result-meta { font-size: .75rem; color: var(--muted); }
.result-badges { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 999px; font-size: .72rem; font-weight: 700; white-space: nowrap; }
.badge.leaflet { background: var(--mint); color: var(--teal-dark); }
.badge.inactive { background: var(--bg-soft); color: var(--muted); }
.result-arrow { color: var(--muted); flex: none; }

.pagination { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 20px; font-size: .88rem; font-weight: 600; color: var(--muted); }
.pagination button { display: inline-flex; align-items: center; justify-content: center; gap: 4px; min-height: 44px; min-width: 44px; border: 1.5px solid var(--teal); background: #fff; color: var(--teal); font-weight: 600; font-size: .88rem; padding: 0 16px; border-radius: 999px; cursor: pointer; }
.pagination button:disabled { opacity: .45; cursor: not-allowed; }

@media (min-width: 640px) {
  .search-card { padding: 22px 24px; gap: 16px; }
  .search-form { flex-direction: row; gap: 12px; }
  .search-input input { font-size: .95rem; }
  .search-button { font-size: .9rem; }
  .filters { flex-direction: row; align-items: flex-end; gap: 20px; flex-wrap: wrap; }
  .filter-select { flex: 1 1 280px; max-width: 460px; }
  .filter-select select { font-size: .88rem; }
  .result-card { gap: 16px; padding: 16px 18px; }
  .result-icon { width: 42px; height: 42px; align-self: center; }
  .pagination { justify-content: center; gap: 16px; }
}
</style>
