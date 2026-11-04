<script setup>
import { onMounted, ref } from 'vue'
import {
  Accessibility,
  Building2,
  CheckCircle,
  ExternalLink,
  Globe,
  LockKeyhole,
  LogOut,
  Mail,
  Plus,
  Power,
  ShieldCheck,
  User,
  UserRound
} from 'lucide-vue-next'
import { PLATFORM_ADMIN_ROLE, currentUserRole, isAuthenticated, logoutUser } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
import { buildOrganizationHostname, buildOrganizationUrl, isPlatformContext } from '../services/organization-context'
import { createOrganization, listOrganizations, updateOrganization } from '../services/organization-service'

const organizacoes = ref([])
const carregando = ref(true)
const erroLista = ref('')
const criando = ref(false)
const erroCriacao = ref('')
const mensagem = ref('')
const subdominioEditado = ref(false)

const formulario = ref(criarFormularioVazio())

const descricaoStatus = {
  active: 'Ativa',
  inactive: 'Inativa',
  provisioning: 'Criando'
}

const menuItems = [
  { label: 'Organizações', icon: Building2, href: '/org', active: true },
  { label: 'Sair', icon: LogOut, href: '/login', sair: true }
]

function criarFormularioVazio() {
  return { nome: '', subdominio: '', adminNome: '', adminEmail: '', adminSenha: '' }
}

function gerarSubdominio(nome) {
  return nome
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+/, '')
    .slice(0, 40)
    .replace(/-+$/, '')
}

function atualizarSubdominioPeloNome() {
  if (!subdominioEditado.value) formulario.value.subdominio = gerarSubdominio(formulario.value.nome)
}

function normalizarSubdominioDigitado() {
  subdominioEditado.value = true
  formulario.value.subdominio = formulario.value.subdominio.toLowerCase().replace(/[^a-z0-9-]/g, '')
}

async function carregarOrganizacoes() {
  carregando.value = true
  erroLista.value = ''
  try {
    organizacoes.value = await listOrganizations()
  } catch (falha) {
    erroLista.value = extractErrorMessage(falha, 'Não foi possível carregar as organizações.')
  } finally {
    carregando.value = false
  }
}

async function criarOrganizacao() {
  erroCriacao.value = ''
  mensagem.value = ''
  criando.value = true
  try {
    const organizacao = await createOrganization(formulario.value)
    organizacoes.value = [organizacao, ...organizacoes.value]
    mensagem.value = `${organizacao.nome} criada em ${buildOrganizationHostname(organizacao.subdominio)}`
    formulario.value = criarFormularioVazio()
    subdominioEditado.value = false
  } catch (falha) {
    erroCriacao.value = extractErrorMessage(falha, 'Não foi possível criar a organização.')
  } finally {
    criando.value = false
  }
}

async function alternarStatus(organizacao) {
  erroLista.value = ''
  try {
    const atualizada = await updateOrganization(organizacao.id, { ativa: organizacao.status !== 'active' })
    organizacoes.value = organizacoes.value.map((item) => (item.id === atualizada.id ? atualizada : item))
  } catch (falha) {
    erroLista.value = extractErrorMessage(falha, 'Não foi possível alterar o status da organização.')
  }
}

function sair() {
  logoutUser()
}

onMounted(() => {
  if (!isPlatformContext() || !isAuthenticated() || currentUserRole() !== PLATFORM_ADMIN_ROLE) {
    window.location.href = '/login'
    return
  }
  carregarOrganizacoes()
})
</script>

<template>
  <div class="org-page">
    <header class="header">
      <div class="header-inner">
        <a href="/org" class="logo" aria-label="Busca Bula – painel da plataforma">
          <svg width="44" height="44" viewBox="0 0 48 48" aria-hidden="true">
            <rect x="14" y="4" width="28" height="36" rx="4" fill="#0f9e94" />
            <rect x="18" y="8" width="20" height="28" rx="2" fill="#d9f1ee" />
            <circle cx="20" cy="26" r="11" fill="#fff" stroke="#123a5c" stroke-width="3.5" />
            <path d="M13 34 5 43" stroke="#123a5c" stroke-width="4.5" stroke-linecap="round" />
            <path d="M15.5 22h9M15.5 26h9M15.5 30h6" stroke="#0f9e94" stroke-width="2.2" stroke-linecap="round" />
          </svg>
          <span>Busca <em>Bula</em></span>
        </a>

        <div class="header-actions">
          <button class="icon-btn" type="button" aria-label="Opções de acessibilidade">
            <Accessibility :size="22" />
          </button>
          <span class="header-user"><ShieldCheck :size="17" />Plataforma</span>
        </div>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <nav class="menu" aria-label="Menu da plataforma">
          <a
            v-for="item in menuItems"
            :key="item.label"
            :href="item.href"
            class="menu-item"
            :class="{ active: item.active }"
            :aria-current="item.active ? 'page' : undefined"
            @click="item.sair && sair()"
          >
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </a>
        </nav>
      </aside>

      <main class="main-content">
        <div class="page-heading">
          <div class="heading-icon"><Building2 :size="27" /></div>
          <div>
            <h1>Organizações</h1>
            <p>Gerencie as farmácias e planos de saúde que oferecem o Busca Bula aos seus clientes.</p>
          </div>
        </div>

        <div class="content-grid">
          <section class="table-card">
            <h2 class="section-title"><Building2 :size="17" />Organizações cadastradas</h2>

            <p v-if="erroLista" class="error-message" role="alert">{{ erroLista }}</p>
            <p v-if="carregando" class="empty-state">Carregando organizações...</p>
            <p v-else-if="!organizacoes.length" class="empty-state">Nenhuma organização cadastrada ainda.</p>

            <table v-else class="org-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Endereço</th>
                  <th>Status</th>
                  <th><span class="visually-hidden">Ações</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="organizacao in organizacoes" :key="organizacao.id">
                  <td class="org-name">{{ organizacao.nome }}</td>
                  <td>
                    <a
                      class="org-link"
                      :href="buildOrganizationUrl(organizacao.subdominio)"
                      target="_blank"
                      rel="noopener"
                    >
                      {{ buildOrganizationHostname(organizacao.subdominio) }}
                      <ExternalLink :size="13" />
                    </a>
                  </td>
                  <td>
                    <span class="status-badge" :class="organizacao.status">
                      {{ descricaoStatus[organizacao.status] || organizacao.status }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button
                      v-if="organizacao.status !== 'provisioning'"
                      class="status-button"
                      type="button"
                      @click="alternarStatus(organizacao)"
                    >
                      <Power :size="14" />
                      {{ organizacao.status === 'active' ? 'Desativar' : 'Ativar' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </section>

          <aside class="form-card">
            <h2 class="section-title"><Plus :size="17" />Nova organização</h2>

            <form class="org-form" @submit.prevent="criarOrganizacao">
              <div class="field">
                <label for="nome">Nome da organização</label>
                <div class="input-wrapper">
                  <Building2 :size="16" />
                  <input
                    id="nome"
                    v-model="formulario.nome"
                    type="text"
                    placeholder="Ex.: Farmácia Central"
                    required
                    @input="atualizarSubdominioPeloNome"
                  />
                </div>
              </div>

              <div class="field">
                <label for="subdominio">Subdomínio</label>
                <div class="input-wrapper">
                  <Globe :size="16" />
                  <input
                    id="subdominio"
                    v-model="formulario.subdominio"
                    type="text"
                    placeholder="farmacia-central"
                    minlength="3"
                    maxlength="40"
                    required
                    @input="normalizarSubdominioDigitado"
                  />
                </div>
                <small v-if="formulario.subdominio" class="field-hint">
                  {{ buildOrganizationHostname(formulario.subdominio) }}
                </small>
              </div>

              <h3 class="subsection-title"><UserRound :size="15" />Administrador da organização</h3>

              <div class="field">
                <label for="admin-nome">Nome</label>
                <div class="input-wrapper">
                  <User :size="16" />
                  <input id="admin-nome" v-model="formulario.adminNome" type="text" placeholder="Nome completo" required />
                </div>
              </div>

              <div class="field">
                <label for="admin-email">E-mail</label>
                <div class="input-wrapper">
                  <Mail :size="16" />
                  <input id="admin-email" v-model="formulario.adminEmail" type="email" placeholder="admin@organizacao.com.br" required />
                </div>
              </div>

              <div class="field">
                <label for="admin-senha">Senha</label>
                <div class="input-wrapper">
                  <LockKeyhole :size="16" />
                  <input
                    id="admin-senha"
                    v-model="formulario.adminSenha"
                    type="password"
                    placeholder="Mínimo de 8 caracteres"
                    minlength="8"
                    autocomplete="new-password"
                    required
                  />
                </div>
              </div>

              <button class="save-button" type="submit" :disabled="criando">
                <Plus :size="15" />{{ criando ? 'Criando banco da organização...' : 'Criar organização' }}
              </button>

              <p v-if="erroCriacao" class="error-message" role="alert">{{ erroCriacao }}</p>
              <p v-if="mensagem" class="success-message" role="status"><CheckCircle :size="15" />{{ mensagem }}</p>
            </form>
          </aside>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
</style>

<style scoped>
.org-page {
  --navy: #123a5c;
  --teal: #0f9e94;
  --teal-dark: #0b857c;
  --mint: #d9f1ee;
  --bg-soft: #eef7f8;
  --text: #2b4a63;
  --muted: #6b8497;
  --line: #dfe9ee;
  --danger: #c0392b;
  --danger-soft: #fbe9e7;
  min-height: 100vh;
  background: var(--bg-soft);
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}
.org-page *, .org-page *::before, .org-page *::after { box-sizing: border-box; margin: 0; padding: 0; }
.org-page a { color: inherit; text-decoration: none; }
.org-page button, .org-page input { font: inherit; }
.org-page :focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; border-radius: 6px; }

.header { background: #fff; box-shadow: 0 1px 0 var(--line); position: sticky; top: 0; z-index: 10; }
.header-inner { width: min(1200px, 100% - 48px); margin-inline: auto; height: 70px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.5rem; color: var(--navy); letter-spacing: -.02em; }
.logo em { font-style: normal; color: var(--teal); }
.header-actions { display: flex; align-items: center; gap: 16px; }
.icon-btn { width: 38px; height: 38px; border-radius: 50%; border: 2px solid var(--navy); background: none; color: var(--navy); display: grid; place-items: center; cursor: pointer; }
.header-user { display: inline-flex; align-items: center; gap: 8px; background: var(--navy); color: #fff; font-weight: 600; font-size: .85rem; padding: 10px 20px; border-radius: 999px; }

.layout { width: min(1200px, 100% - 48px); margin-inline: auto; display: grid; grid-template-columns: 220px 1fr; gap: 28px; padding: 32px 0 48px; align-items: start; }
.sidebar { background: #fff; border-radius: 16px; padding: 14px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.menu { display: flex; flex-direction: column; gap: 4px; }
.menu-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 10px; font-size: .88rem; font-weight: 500; color: var(--navy); transition: background .2s; }
.menu-item:hover { background: var(--bg-soft); }
.menu-item.active { background: var(--teal); color: #fff; font-weight: 700; }

.page-heading { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.heading-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.page-heading h1 { font-size: 1.7rem; color: var(--navy); font-weight: 800; letter-spacing: -.02em; }
.page-heading p { font-size: .9rem; color: var(--muted); }

.content-grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }
.table-card, .form-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 18px; }
.section-title svg { color: var(--teal); }
.subsection-title { display: flex; align-items: center; gap: 8px; font-size: .85rem; font-weight: 700; color: var(--navy); margin-top: 6px; }
.subsection-title svg { color: var(--teal); }

.empty-state { font-size: .88rem; color: var(--muted); padding: 18px 0; }
.org-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.org-table th { text-align: left; font-size: .75rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 0 10px 10px; border-bottom: 1px solid var(--line); }
.org-table td { padding: 14px 10px; border-bottom: 1px solid var(--line); color: var(--navy); vertical-align: middle; }
.org-table tr:last-child td { border-bottom: 0; }
.org-name { font-weight: 600; }
.org-link { display: inline-flex; align-items: center; gap: 6px; color: var(--teal) !important; font-weight: 600; word-break: break-all; }
.org-link:hover { color: var(--teal-dark) !important; }
.status-badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: .75rem; font-weight: 700; background: var(--bg-soft); color: var(--muted); }
.status-badge.active { background: var(--mint); color: var(--teal-dark); }
.status-badge.inactive { background: var(--danger-soft); color: var(--danger); }
.actions-cell { text-align: right; }
.status-button { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1.5px solid var(--teal); color: var(--teal); font-weight: 600; font-size: .8rem; padding: 6px 14px; border-radius: 999px; cursor: pointer; transition: all .2s; white-space: nowrap; }
.status-button:hover { background: var(--teal); color: #fff; }

.org-form { display: flex; flex-direction: column; gap: 14px; }
.field label { display: block; font-size: .8rem; font-weight: 600; color: var(--navy); margin-bottom: 6px; }
.field-hint { display: block; margin-top: 6px; font-size: .75rem; color: var(--muted); }
.input-wrapper { display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fff; padding: 0 14px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.input-wrapper svg { flex: none; }
.input-wrapper input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 12px 0; font-size: .9rem; color: var(--navy); }
.input-wrapper input::placeholder { color: #8aa0b0; }

.save-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .9rem; padding: 13px 28px; border-radius: 999px; cursor: pointer; transition: background .2s; margin-top: 6px; }
.save-button:hover { background: var(--teal-dark); }
.save-button:disabled { background: #9aafc0; cursor: not-allowed; }
.success-message { display: inline-flex; align-items: center; gap: 8px; color: var(--teal-dark); font-size: .85rem; font-weight: 600; }
.error-message { color: var(--danger); font-size: .85rem; font-weight: 600; margin-bottom: 8px; }

.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

@media (max-width: 1000px) {
  .layout { grid-template-columns: 1fr; }
  .menu { flex-direction: row; overflow-x: auto; }
  .menu-item { white-space: nowrap; }
  .content-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .header-user { display: none; }
  .org-table thead { display: none; }
  .org-table tr { display: grid; gap: 6px; padding: 12px 0; border-bottom: 1px solid var(--line); }
  .org-table td { padding: 0; border: 0; }
  .actions-cell { text-align: left; }
}
@media (prefers-reduced-motion: reduce) {
  .org-page * { transition: none !important; }
}
</style>
