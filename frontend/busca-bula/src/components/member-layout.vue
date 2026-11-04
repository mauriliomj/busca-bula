<script setup>
import { computed } from 'vue'
import { Accessibility, FileText, House, LogOut, Search, UserRound, Users } from 'lucide-vue-next'
import { ORGANIZATION_ADMIN_ROLE, currentUserRole, logoutUser } from '../services/auth-service'
import { useCurrentOrganization } from '../services/organization-branding'

const props = defineProps({
  ativo: { type: String, required: true },
  titulo: { type: String, required: true },
  descricao: { type: String, default: '' },
  icone: { type: [Object, Function], required: true }
})

const organizacao = useCurrentOrganization()

const menuItems = computed(() => [
  { chave: 'inicio', label: 'Início', icon: House, href: '/medicine-leaflet' },
  { chave: 'buscar', label: 'Buscar', icon: Search, href: '/search' },
  { chave: 'consultas', label: 'Minhas Consultas', icon: FileText, href: '/consultations' },
  ...(currentUserRole() === ORGANIZATION_ADMIN_ROLE
    ? [{ chave: 'membros', label: 'Membros', icon: Users, href: '/members' }]
    : []),
  { chave: 'perfil', label: 'Meu Perfil', icon: UserRound, href: '/user' },
  { chave: 'sair', label: 'Sair', icon: LogOut, href: '/login', sair: true }
].map((item) => ({ ...item, active: item.chave === props.ativo })))

function selecionarItem(item) {
  if (item.sair) logoutUser()
}
</script>

<template>
  <div class="member-layout">
    <header class="header">
      <div class="header-inner">
        <a href="/medicine-leaflet" class="logo" aria-label="Busca Bula – início">
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
          <a href="/user" class="header-user"><UserRound :size="17" />Minha conta</a>
        </div>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <nav class="menu" aria-label="Menu do usuário">
          <a
            v-for="item in menuItems"
            :key="item.chave"
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
          <div class="heading-icon"><component :is="icone" :size="27" /></div>
          <div>
            <h1>{{ titulo }}</h1>
            <p v-if="descricao">{{ descricao }}</p>
          </div>
        </div>

        <slot />

        <p class="medical-disclaimer">
          O conteúdo do Busca Bula é informativo e não substitui a orientação de um médico ou farmacêutico.
        </p>
      </main>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
</style>

<style scoped>
.member-layout {
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
:where(.member-layout *, .member-layout *::before, .member-layout *::after) { box-sizing: border-box; margin: 0; padding: 0; }
:where(.member-layout) :where(a) { color: inherit; text-decoration: none; }
:where(.member-layout) :where(button, input, select) { font: inherit; }
.member-layout :focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; border-radius: 6px; }

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

.medical-disclaimer { margin-top: 28px; font-size: .78rem; color: var(--muted); text-align: center; }

@media (max-width: 1000px) {
  .layout { grid-template-columns: 1fr; }
  .menu { flex-direction: row; overflow-x: auto; }
  .menu-item { white-space: nowrap; }
}
@media (max-width: 640px) {
  .header-user { display: none; }
  .page-heading { align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  .member-layout * { transition: none !important; }
}
</style>
