<script setup>
import { computed, onMounted, ref } from 'vue'
import { Accessibility, Building2, LogOut, Palette, Search, Trash2, UserRound, Users } from 'lucide-vue-next'
import BrandingEditor from '../components/branding-editor.vue'
import { ORGANIZATION_ADMIN_ROLE, currentUserRole, isAuthenticated, logoutUser } from '../services/auth-service'
import { removeOwnLogo, updateOwnBrandColors, uploadOwnLogo } from '../services/branding-service'
import { extractErrorMessage } from '../services/http-client'
import { listMembers, removeMember } from '../services/member-service'
import {
  loadCurrentOrganization,
  updateCurrentOrganizationBranding,
  useCurrentOrganization
} from '../services/organization-branding'
import { isPlatformContext } from '../services/organization-context'

const SECAO_POR_ANCORA = { '#identidade-visual': 'marca' }

const membros = ref([])
const organizacao = useCurrentOrganization()
const secaoAtual = ref(SECAO_POR_ANCORA[window.location.hash] || 'membros')
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

const menuItems = computed(() => [
  { label: 'Membros', icon: Users, href: '#membros', secao: 'membros' },
  { label: 'Identidade visual', icon: Palette, href: '#identidade-visual', secao: 'marca' },
  { label: 'Meu Perfil', icon: UserRound, href: '/user' },
  { label: 'Sair', icon: LogOut, href: '/login', sair: true }
].map((item) => ({ ...item, active: item.secao === secaoAtual.value })))

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

function selecionarItem(item) {
  if (item.sair) logoutUser()
  if (item.secao) secaoAtual.value = item.secao
}

onMounted(() => {
  if (isPlatformContext() || !isAuthenticated() || currentUserRole() !== ORGANIZATION_ADMIN_ROLE) {
    window.location.href = '/login'
    return
  }
  carregarPainel()
})
</script>

<template>
  <div class="members-page">
    <header class="header">
      <div class="header-inner">
        <a href="/members" class="logo" aria-label="Busca Bula – painel da organização">
          <img v-if="organizacao?.logoUrl" :src="organizacao.logoUrl" :alt="organizacao.nome" class="org-logo" />
          <template v-else>
            <svg width="44" height="44" viewBox="0 0 48 48" aria-hidden="true">
              <rect x="14" y="4" width="28" height="36" rx="4" fill="#0f9e94" />
              <rect x="18" y="8" width="20" height="28" rx="2" fill="#d9f1ee" />
              <circle cx="20" cy="26" r="11" fill="#fff" stroke="#123a5c" stroke-width="3.5" />
              <path d="M13 34 5 43" stroke="#123a5c" stroke-width="4.5" stroke-linecap="round" />
              <path d="M15.5 22h9M15.5 26h9M15.5 30h6" stroke="#0f9e94" stroke-width="2.2" stroke-linecap="round" />
            </svg>
            <span>Busca <em>Bula</em></span>
          </template>
        </a>

        <div class="header-actions">
          <button class="icon-btn" type="button" aria-label="Opções de acessibilidade">
            <Accessibility :size="22" />
          </button>
          <span class="header-user"><Building2 :size="17" />{{ organizacao?.nome || 'Organização' }}</span>
        </div>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <nav class="menu" aria-label="Menu da organização">
          <a
            v-for="item in menuItems"
            :key="item.label"
            :href="item.href"
            class="menu-item"
            :class="{ active: item.active }"
            :aria-current="item.active ? 'page' : undefined"
            @click="selecionarItem(item)"
          >
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </a>
        </nav>
      </aside>

      <main class="main-content">
        <div class="page-heading">
          <div class="heading-icon"><component :is="cabecalho.icone" :size="27" /></div>
          <div>
            <h1>{{ cabecalho.titulo }}</h1>
            <p>{{ cabecalho.descricao }}</p>
          </div>
        </div>

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
      </main>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
</style>

<style scoped>
.members-page {
  --navy: var(--brand-secondary, #123a5c);
  --teal: var(--brand-primary, #0f9e94);
  --teal-dark: var(--brand-primary-dark, #0b857c);
  --mint: var(--brand-primary-soft, #d9f1ee);
  --bg-soft: #eef7f8;
  --text: #2b4a63;
  --muted: #6b8497;
  --line: #dfe9ee;
  --danger: #c0392b;
  min-height: 100vh;
  background: var(--bg-soft);
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}
:where(.members-page *, .members-page *::before, .members-page *::after) { box-sizing: border-box; margin: 0; padding: 0; }
.members-page a { color: inherit; text-decoration: none; }
.members-page button, .members-page input { font: inherit; }
.members-page :focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; border-radius: 6px; }

.header { background: #fff; box-shadow: 0 1px 0 var(--line); position: sticky; top: 0; z-index: 10; }
.header-inner { width: min(1200px, 100% - 48px); margin-inline: auto; height: 70px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.5rem; color: var(--navy); letter-spacing: -.02em; }
.logo em { font-style: normal; color: var(--teal); }
.org-logo { max-height: 48px; max-width: 220px; object-fit: contain; }
.header-actions { display: flex; align-items: center; gap: 16px; }
.icon-btn { width: 38px; height: 38px; border-radius: 50%; border: 2px solid var(--navy); background: none; color: var(--navy); display: grid; place-items: center; cursor: pointer; }
.header-user { display: inline-flex; align-items: center; gap: 8px; background: var(--navy); color: #fff; font-weight: 600; font-size: .85rem; padding: 10px 20px; border-radius: 999px; }

.layout { width: min(1200px, 100% - 48px); margin-inline: auto; display: grid; grid-template-columns: 220px 1fr; gap: 28px; padding: 32px 0 48px; align-items: start; }
.layout > * { min-width: 0; }
.sidebar { background: #fff; border-radius: 16px; padding: 14px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.menu { display: flex; flex-direction: column; gap: 4px; }
.menu-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 10px; font-size: .88rem; font-weight: 500; color: var(--navy); transition: background .2s; }
.menu-item:hover { background: var(--bg-soft); }
.menu-item.active { background: var(--teal); color: #fff; font-weight: 700; }

.page-heading { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.heading-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.page-heading h1 { font-size: 1.7rem; color: var(--navy); font-weight: 800; letter-spacing: -.02em; }
.page-heading p { font-size: .9rem; color: var(--muted); }

.table-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.table-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 18px; }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); }
.section-title svg { color: var(--teal); }
.branding-card { max-width: 720px; }
.branding-title { margin-bottom: 20px; }

.input-wrapper { display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fff; padding: 0 14px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.input-wrapper svg { flex: none; }
.input-wrapper input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 11px 0; font-size: .88rem; color: var(--navy); }
.input-wrapper input::placeholder { color: #8aa0b0; }
.search-input { width: min(320px, 100%); }

.empty-state { font-size: .88rem; color: var(--muted); padding: 18px 0; }
.error-message { color: var(--danger); font-size: .85rem; font-weight: 600; margin-bottom: 8px; }
.members-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.members-table th { text-align: left; font-size: .75rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 0 10px 10px; border-bottom: 1px solid var(--line); }
.members-table td { padding: 14px 10px; border-bottom: 1px solid var(--line); color: var(--navy); vertical-align: middle; }
.members-table tr:last-child td { border-bottom: 0; }
.member-name { font-weight: 600; }
.role-badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: .75rem; font-weight: 700; background: var(--bg-soft); color: var(--muted); }
.role-badge.org_admin { background: var(--mint); color: var(--teal-dark); }
.actions-cell { text-align: right; }
.remove-button { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1.5px solid var(--danger); color: var(--danger); font-weight: 600; font-size: .8rem; padding: 6px 14px; border-radius: 999px; cursor: pointer; transition: all .2s; white-space: nowrap; }
.remove-button:hover { background: var(--danger); color: #fff; }
.remove-button:disabled { opacity: .5; cursor: not-allowed; }

.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

@media (max-width: 1000px) {
  .layout { grid-template-columns: 1fr; }
  .menu { flex-direction: row; overflow-x: auto; }
  .menu-item { white-space: nowrap; }
}
@media (max-width: 640px) {
  .header-user { display: none; }
  .members-table thead { display: none; }
  .members-table tr { display: grid; gap: 6px; padding: 12px 0; border-bottom: 1px solid var(--line); }
  .members-table td { padding: 0; border: 0; }
  .actions-cell { text-align: left; }
}
@media (prefers-reduced-motion: reduce) {
  .members-page * { transition: none !important; }
}
</style>
