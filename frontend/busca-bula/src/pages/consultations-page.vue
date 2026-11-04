<script setup>
import { onMounted, ref } from 'vue'
import { ChevronRight, FileText, History, Pill, ShieldCheck, Trash2, X } from 'lucide-vue-next'
import MemberLayout from '../components/member-layout.vue'
import {
  clearConsultationHistory,
  fetchConsultationHistory,
  removeConsultation,
  updateConsultationConsent
} from '../services/consultation-service'
import { extractErrorMessage } from '../services/http-client'

const historico = ref(null)
const carregando = ref(true)
const processando = ref(false)
const concordo = ref(false)
const erro = ref('')

const formatadorDeData = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

async function executar(acao, mensagemDeFalha) {
  erro.value = ''
  processando.value = true
  try {
    await acao()
  } catch (falha) {
    erro.value = extractErrorMessage(falha, mensagemDeFalha)
  } finally {
    processando.value = false
  }
}

async function carregarHistorico() {
  await executar(async () => {
    historico.value = await fetchConsultationHistory()
  }, 'Não foi possível carregar o histórico.')
  carregando.value = false
}

function ativarHistorico() {
  executar(async () => {
    historico.value = await updateConsultationConsent(true)
  }, 'Não foi possível ativar o histórico.')
}

function desativarHistorico() {
  const confirmado = window.confirm('Desativar o histórico? Todas as consultas guardadas serão apagadas.')
  if (!confirmado) return
  executar(async () => {
    historico.value = await updateConsultationConsent(false)
    concordo.value = false
  }, 'Não foi possível desativar o histórico.')
}

function limparHistorico() {
  if (!window.confirm('Apagar todas as consultas do histórico?')) return
  executar(async () => {
    await clearConsultationHistory()
    historico.value = { ...historico.value, consultas: [] }
  }, 'Não foi possível limpar o histórico.')
}

function removerConsulta(consulta) {
  executar(async () => {
    await removeConsultation(consulta.id)
    historico.value = {
      ...historico.value,
      consultas: historico.value.consultas.filter((item) => item.id !== consulta.id)
    }
  }, 'Não foi possível remover a consulta.')
}

onMounted(carregarHistorico)
</script>

<template>
  <MemberLayout
    ativo="consultas"
    titulo="Minhas Consultas"
    descricao="Os medicamentos que você abriu no Busca Bula, para encontrá-los de novo rapidamente."
    :icone="History"
  >
    <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>
    <p v-if="carregando" class="empty-state">Carregando histórico...</p>

    <section v-else-if="historico && !historico.ativado" class="consent-card">
      <h2 class="card-title"><ShieldCheck :size="18" />O histórico está desativado</h2>
      <p>
        Ao ativar, o Busca Bula passa a guardar o nome e o princípio ativo de cada medicamento que você abrir, com a data
        da consulta. Essas informações podem indicar algo sobre a sua saúde, por isso só são guardadas com a sua
        autorização.
      </p>
      <ul class="consent-points">
        <li>Ficam no banco de dados da sua organização e não são compartilhadas com outras organizações.</li>
        <li>Você pode remover uma consulta, limpar tudo ou desativar quando quiser.</li>
        <li>Ao desativar o histórico ou excluir sua conta, todas as consultas são apagadas.</li>
      </ul>
      <label class="consent-check">
        <input v-model="concordo" type="checkbox" />
        <span>Autorizo o Busca Bula a guardar o histórico dos medicamentos que eu consultar.</span>
      </label>
      <button class="primary-button" type="button" :disabled="!concordo || processando" @click="ativarHistorico">
        <History :size="15" />Ativar histórico
      </button>
    </section>

    <template v-else-if="historico">
      <div class="history-toolbar">
        <p class="consent-info">
          <ShieldCheck :size="15" />
          Histórico autorizado em {{ formatadorDeData.format(new Date(historico.consentidoEm)) }}
        </p>
        <div class="toolbar-actions">
          <button
            v-if="historico.consultas.length"
            class="text-button"
            type="button"
            :disabled="processando"
            @click="limparHistorico"
          >
            <Trash2 :size="14" />Limpar histórico
          </button>
          <button class="text-button danger" type="button" :disabled="processando" @click="desativarHistorico">
            <X :size="14" />Desativar e apagar
          </button>
        </div>
      </div>

      <p v-if="!historico.consultas.length" class="empty-state">
        Nenhuma consulta ainda. Os medicamentos que você abrir pela <RouterLink :to="{ name: 'search' }">busca</RouterLink> aparecem aqui.
      </p>

      <ul v-else class="history-list">
        <li v-for="consulta in historico.consultas" :key="consulta.id" class="history-item">
          <RouterLink class="history-link" :to="{ name: 'medicine', params: { registro: consulta.registro } }">
            <span class="history-icon"><Pill :size="18" /></span>
            <span class="history-body">
              <span class="history-name">{{ consulta.nome }}</span>
              <span v-if="consulta.principioAtivo" class="history-ingredient">{{ consulta.principioAtivo }}</span>
              <span class="history-date"><FileText :size="12" />{{ formatadorDeData.format(new Date(consulta.consultadoEm)) }}</span>
            </span>
            <ChevronRight :size="18" class="history-arrow" />
          </RouterLink>
          <button
            class="remove-button"
            type="button"
            :aria-label="`Remover ${consulta.nome} do histórico`"
            :disabled="processando"
            @click="removerConsulta(consulta)"
          >
            <X :size="16" />
          </button>
        </li>
      </ul>
    </template>
  </MemberLayout>
</template>

<style scoped>
.error-message { color: var(--danger); font-size: .88rem; font-weight: 600; margin-bottom: 12px; }
.empty-state { font-size: .9rem; color: var(--muted); margin-top: 8px; }
.empty-state a { color: var(--teal); font-weight: 600; }

.consent-card { background: #fff; border-radius: 16px; padding: 18px 16px; box-shadow: var(--card-shadow); max-width: 720px; display: flex; flex-direction: column; gap: 14px; }
.consent-card p { font-size: .9rem; color: var(--text); }
.card-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); }
.card-title svg { color: var(--teal); flex: none; }
.consent-points { padding-left: 20px; display: flex; flex-direction: column; gap: 6px; font-size: .88rem; color: var(--text); }
.consent-check { display: flex; align-items: flex-start; gap: 12px; font-size: .9rem; font-weight: 600; color: var(--navy); cursor: pointer; }
.consent-check input { accent-color: var(--teal); width: 20px; height: 20px; margin-top: 1px; flex: none; }
.primary-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 48px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .95rem; padding: 0 26px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.primary-button:hover { background: var(--teal-dark); }
.primary-button:disabled { background: #9aafc0; cursor: not-allowed; }

.history-toolbar { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.consent-info { display: inline-flex; align-items: center; gap: 8px; font-size: .82rem; color: var(--muted); }
.consent-info svg { color: var(--teal); flex: none; }
.toolbar-actions { display: flex; flex-wrap: wrap; gap: 4px 16px; }
.text-button { display: inline-flex; align-items: center; gap: 6px; min-height: 44px; background: none; border: 0; color: var(--muted); font-weight: 600; font-size: .85rem; cursor: pointer; }
.text-button:hover { color: var(--navy); }
.text-button.danger { color: var(--danger); }
.text-button:disabled { opacity: .5; cursor: not-allowed; }

.history-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.history-item { display: flex; align-items: center; gap: 4px; background: #fff; border-radius: 14px; padding: 4px 4px 4px 2px; box-shadow: var(--card-shadow); }
.history-link { flex: 1; min-width: 0; display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 10px; }
.history-link:hover { background: var(--bg-soft); }
.history-icon { width: 38px; height: 38px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.history-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.history-name { font-weight: 700; color: var(--navy); overflow-wrap: anywhere; }
.history-ingredient { font-size: .82rem; color: var(--text); overflow-wrap: anywhere; }
.history-date { display: inline-flex; align-items: center; gap: 5px; font-size: .75rem; color: var(--muted); }
.history-arrow { display: none; color: var(--muted); flex: none; }
.remove-button { width: 44px; height: 44px; border-radius: 50%; border: 0; background: none; color: var(--muted); display: grid; place-items: center; cursor: pointer; flex: none; }
.remove-button:hover { background: var(--bg-soft); color: var(--danger); }

@media (min-width: 640px) {
  .consent-card { padding: 24px 26px; }
  .primary-button { align-self: flex-start; }
  .history-toolbar { flex-direction: row; align-items: center; justify-content: space-between; flex-wrap: wrap; }
  .history-item { gap: 8px; padding: 6px 10px 6px 6px; }
  .history-link { gap: 14px; padding: 10px 12px; }
  .history-arrow { display: block; }
}
</style>
