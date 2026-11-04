<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Building2, Palette, Search, Trash2, UserRound, Users } from 'lucide-vue-next'
import AppShell from '../components/app-shell.vue'
import BrandingEditor from '../components/branding-editor.vue'
import { removeOwnLogo, updateOwnBrandColors, uploadOwnLogo } from '../services/branding-service'
import { extractErrorMessage } from '../services/http-client'
import { listMembers, removeMember } from '../services/member-service'
import {
  loadCurrentOrganization,
  updateCurrentOrganizationBranding,
  useCurrentOrganization
} from '../services/organization-branding'

const SECAO_POR_ANCORA = { '#identidade-visual': 'marca' }

const route = useRoute()
const membros = ref([])
const organizacao = useCurrentOrganization()
const secaoAtual = computed(() => SECAO_POR_ANCORA[route.hash] || 'membros')
const carregando = ref(true)
const erro = ref('')
const busca = ref('')
const removendo = ref(null)

const descricaoPapel = {
  org_admin: 'Administrador',
  member: 'Membro'
}

const cabecalhos = {
  membros: { titulo: 'Membros', descricao: 'Acompanhe quem usa o Busca Bula pela sua organização.', icone: Users },
  marca: { titulo: 'Identidade visual', descricao: 'Personalize a logo e as cores que seus clientes veem no app.', icone: Palette }
}

const navegacao = [
  { chave: 'membros', rotulo: 'Membros', icone: Users, to: { name: 'members' } },
  { chave: 'marca', rotulo: 'Identidade visual', rotuloCurto: 'Marca', icone: Palette, to: { name: 'members', hash: '#identidade-visual' } },
  { chave: 'buscar', rotulo: 'Buscar medicamentos', rotuloCurto: 'Buscar', icone: Search, to: { name: 'search' } },
  { chave: 'perfil', rotulo: 'Meu Perfil', rotuloCurto: 'Perfil', icone: UserRound, to: { name: 'user' } }
]

const cabecalho = computed(() => cabecalhos[secaoAtual.value])

const marcaAtual = computed(() => ({
  logoUrl: organizacao.value?.logoUrl ?? null,
  corPrimaria: organizacao.value?.corPrimaria ?? null,
  corSecundaria: organizacao.value?.corSecundaria ?? null
}))

const membrosFiltrados = computed(() => {
  const termo = busca.value.trim().toLowerCase()
  if (!termo) return membros.value
  return membros.value.filter(
    (membro) => membro.nome.toLowerCase().includes(termo) || membro.email.toLowerCase().includes(termo)
  )
})

const totalDeMembros = computed(() => membros.value.filter((membro) => membro.papel === 'member').length)

function formatarData(data) {
  return new Date(data).toLocaleDateString('pt-BR')
}

function formatarLocalidade(membro) {
  return [membro.cidade, membro.estado].filter(Boolean).join(' / ') || '—'
}

async function carregarPainel() {
  carregando.value = true
  erro.value = ''
  try {
    const [, listaMembros] = await Promise.all([loadCurrentOrganization(), listMembers()])
    membros.value = listaMembros
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível carregar os membros.')
  } finally {
    carregando.value = false
  }
}

async function remover(membro) {
  if (!window.confirm(`Remover ${membro.nome}? Todos os dados desse membro serão apagados.`)) return
  erro.value = ''
  removendo.value = membro.id
  try {
    await removeMember(membro.id)
    membros.value = membros.value.filter((item) => item.id !== membro.id)
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível remover o membro.')
  } finally {
    removendo.value = null
  }
}

onMounted(carregarPainel)
</script>

<template>
  <AppShell
    :navegacao="navegacao"
    :ativo="secaoAtual"
    :titulo="cabecalho.titulo"
    :descricao="cabecalho.descricao"
    :icone="cabecalho.icone"
    :inicio="{ name: 'members' }"
    :identificacao="{ icone: Building2, texto: organizacao?.nome || 'Organização' }"
    rotulo-do-menu="Menu da organização"
  >
    <section v-if="secaoAtual === 'marca'" class="table-card branding-card">
      <h2 class="section-title branding-title"><Palette :size="17" />Logo e cores de {{ organizacao?.nome || 'sua organização' }}</h2>
      <BrandingEditor
        :marca="marcaAtual"
        :nome-da-organizacao="organizacao?.nome || ''"
        :salvar-cores="updateOwnBrandColors"
        :enviar-logo="uploadOwnLogo"
        :remover-logo="removeOwnLogo"
        @atualizada="updateCurrentOrganizationBranding"
      />
    </section>

    <section v-else class="table-card">
      <div class="table-toolbar">
        <h2 class="section-title">
          <Users :size="17" />{{ totalDeMembros }} {{ totalDeMembros === 1 ? 'membro cadastrado' : 'membros cadastrados' }}
        </h2>

        <div class="input-wrapper search-input">
          <Search :size="16" />
          <input v-model="busca" type="search" placeholder="Buscar por nome ou e-mail" aria-label="Buscar membros" />
        </div>
      </div>

      <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>
      <p v-if="carregando" class="empty-state">Carregando membros...</p>
      <p v-else-if="!membrosFiltrados.length" class="empty-state">Nenhum membro encontrado.</p>

      <table v-else class="members-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Cidade</th>
            <th>Papel</th>
            <th>Cadastro</th>
            <th><span class="visually-hidden">Ações</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="membro in membrosFiltrados" :key="membro.id">
            <td class="member-name">{{ membro.nome }}</td>
            <td>{{ membro.email }}</td>
            <td>{{ formatarLocalidade(membro) }}</td>
            <td>
              <span class="role-badge" :class="membro.papel">{{ descricaoPapel[membro.papel] || membro.papel }}</span>
            </td>
            <td>{{ formatarData(membro.cadastradoEm) }}</td>
            <td class="actions-cell">
              <button
                v-if="membro.papel === 'member'"
                class="remove-button"
                type="button"
                :disabled="removendo === membro.id"
                @click="remover(membro)"
              >
                <Trash2 :size="14" />Remover
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </AppShell>
</template>

<style scoped>
.table-card { background: #fff; border-radius: 16px; padding: 18px 16px; box-shadow: var(--card-shadow); }
.table-toolbar { display: flex; flex-direction: column; align-items: stretch; gap: 12px; margin-bottom: 14px; }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); }
.section-title svg { color: var(--teal); flex: none; }
.branding-card { max-width: 720px; }
.branding-title { margin-bottom: 20px; }

.input-wrapper { display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fff; padding: 0 14px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.input-wrapper svg { flex: none; }
.input-wrapper input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 12px 0; font-size: 1rem; color: var(--navy); }
.input-wrapper input::placeholder { color: #8aa0b0; }

.empty-state { font-size: .88rem; color: var(--muted); padding: 18px 0; }
.error-message { color: var(--danger); font-size: .85rem; font-weight: 600; margin-bottom: 8px; }

.members-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.members-table thead { display: none; }
.members-table tr { display: grid; gap: 4px; padding: 14px 0; border-bottom: 1px solid var(--line); }
.members-table tr:last-child { border-bottom: 0; }
.members-table td { color: var(--navy); overflow-wrap: anywhere; }
.members-table td[data-label]::before { content: attr(data-label) ': '; color: var(--muted); font-size: .75rem; font-weight: 600; }
.member-name { font-weight: 700; }
.member-email { color: var(--text); }
.role-badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: .75rem; font-weight: 700; background: var(--bg-soft); color: var(--muted); }
.role-badge.org_admin { background: var(--mint); color: var(--teal-dark); }
.remove-button { display: inline-flex; align-items: center; gap: 6px; min-height: 40px; margin-top: 6px; background: none; border: 1.5px solid var(--danger); color: var(--danger); font-weight: 600; font-size: .85rem; padding: 0 16px; border-radius: 999px; cursor: pointer; transition: all .2s; white-space: nowrap; }
.remove-button:hover { background: var(--danger); color: #fff; }
.remove-button:disabled { opacity: .5; cursor: not-allowed; }

@media (min-width: 640px) {
  .table-card { padding: 24px; }
  .table-toolbar { flex-direction: row; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 18px; }
  .input-wrapper { width: min(320px, 100%); }
  .input-wrapper input { font-size: .9rem; }
}

@media (min-width: 900px) {
  .members-table thead { display: table-header-group; }
  .members-table tr { display: table-row; padding: 0; }
  .members-table th { text-align: left; font-size: .75rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 0 10px 10px; border-bottom: 1px solid var(--line); }
  .members-table td { padding: 14px 10px; border-bottom: 1px solid var(--line); vertical-align: middle; }
  .members-table tr:last-child td { border-bottom: 0; }
  .members-table td[data-label]::before { content: none; }
  .member-name { font-weight: 600; }
  .member-email { color: var(--navy); }
  .actions-cell { text-align: right; }
  .remove-button { min-height: 34px; margin-top: 0; font-size: .8rem; padding: 0 14px; }
}
</style>
