<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Accessibility, LogIn, LogOut } from 'lucide-vue-next'
import BrandLogo from './brand-logo.vue'
import { logoutUser } from '../services/auth-service'
import { readAccessToken } from '../services/token-storage'

const props = defineProps({
  navegacao: { type: Array, required: true },
  ativo: { type: String, required: true },
  titulo: { type: String, required: true },
  descricao: { type: String, default: '' },
  icone: { type: [Object, Function], required: true },
  inicio: { type: [String, Object], required: true },
  identificacao: { type: Object, default: null },
  rotuloDoMenu: { type: String, default: 'Menu principal' }
})

const route = useRoute()
const router = useRouter()

const autenticado = computed(() => Boolean(readAccessToken()))
const entrar = computed(() => ({ name: 'login', query: route.fullPath === '/' ? {} : { next: route.fullPath } }))

const itens = computed(() => props.navegacao.map((item) => ({ ...item, ativo: item.chave === props.ativo })))

async function sair() {
  await logoutUser()
  router.replace({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-inner">
        <RouterLink :to="inicio" class="logo-link" aria-label="Ir para o início">
          <BrandLogo />
        </RouterLink>

        <div class="header-actions">
          <span v-if="identificacao" class="header-identity">
            <component :is="identificacao.icone" :size="17" />{{ identificacao.texto }}
          </span>
          <button class="icon-button" type="button" aria-label="Opções de acessibilidade">
            <Accessibility :size="21" />
          </button>
          <button v-if="autenticado" class="session-button" type="button" @click="sair">
            <LogOut :size="18" /><span>Sair</span>
          </button>
          <RouterLink v-else :to="entrar" class="session-button login">
            <LogIn :size="18" /><span>Entrar</span>
          </RouterLink>
        </div>
      </div>
    </header>

    <div class="layout">
      <nav class="app-nav" :aria-label="rotuloDoMenu">
        <RouterLink
          v-for="item in itens"
          :key="item.chave"
          :to="item.to"
          class="nav-item"
          :class="{ active: item.ativo }"
          :aria-current="item.ativo ? 'page' : undefined"
        >
          <component :is="item.icone" :size="20" />
          <span class="nav-label">{{ item.rotulo }}</span>
          <span class="nav-label-short" aria-hidden="true">{{ item.rotuloCurto || item.rotulo }}</span>
        </RouterLink>
      </nav>

      <main class="main-content">
        <div class="page-heading">
          <div class="heading-icon"><component :is="icone" :size="24" /></div>
          <div class="heading-text">
            <h1>{{ titulo }}</h1>
            <p v-if="descricao">{{ descricao }}</p>
          </div>
        </div>

        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell { min-height: 100dvh; }

.app-header { background: #fff; box-shadow: 0 1px 0 var(--line); position: sticky; top: 0; z-index: 20; padding-top: var(--safe-top); }
.header-inner { width: min(1200px, 100% - 32px); margin-inline: auto; height: var(--header-height); display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.logo-link { min-width: 0; display: flex; }
.header-actions { display: flex; align-items: center; gap: 8px; flex: none; }
.header-identity { display: none; align-items: center; gap: 8px; background: var(--navy); color: #fff; font-weight: 600; font-size: .85rem; padding: 9px 18px; border-radius: 999px; max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.icon-button { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--navy); background: none; color: var(--navy); display: grid; place-items: center; cursor: pointer; }
.session-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-width: 44px; height: 44px; padding: 0 10px; border: 0; border-radius: 999px; background: none; color: var(--navy); font-weight: 600; font-size: .85rem; cursor: pointer; }
.session-button:hover { background: var(--bg-soft); }
.session-button span { display: none; }
.session-button.login { background: var(--teal); color: #fff; padding: 0 16px; }
.session-button.login span { display: inline; }
.session-button.login:hover { background: var(--teal-dark); }

.layout { width: min(1200px, 100% - 32px); margin-inline: auto; padding: 20px 0 calc(var(--bottom-nav-height) + var(--safe-bottom) + 24px); }
.layout > * { min-width: 0; }

.app-nav { position: fixed; inset: auto 0 0 0; z-index: 20; display: flex; background: #fff; box-shadow: 0 -1px 0 var(--line), 0 -6px 18px rgba(18, 58, 92, .06); padding: 0 4px var(--safe-bottom); }
.nav-item { flex: 1; min-width: 0; height: var(--bottom-nav-height); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; color: var(--muted); font-size: .7rem; font-weight: 600; transition: color .2s; }
.nav-item.active { color: var(--teal); }
.nav-label { display: none; }
.nav-label-short { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.page-heading { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.heading-icon { width: 48px; height: 48px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.heading-text { min-width: 0; }
.page-heading h1 { font-size: 1.35rem; line-height: 1.25; color: var(--navy); font-weight: 800; letter-spacing: -.02em; overflow-wrap: anywhere; }
.page-heading p { font-size: .88rem; color: var(--muted); }

@media (min-width: 640px) {
  .session-button span { display: inline; }
  .session-button { padding: 0 16px; }
}

@media (min-width: 1000px) {
  .header-inner, .layout { width: min(1200px, 100% - 48px); }
  .header-identity { display: inline-flex; }
  .layout { display: grid; grid-template-columns: 220px 1fr; gap: 28px; padding: 32px 0 48px; align-items: start; }
  .app-nav { position: sticky; top: calc(var(--header-height) + 24px); inset: auto; flex-direction: column; gap: 4px; padding: 14px; border-radius: 16px; box-shadow: var(--card-shadow); }
  .nav-item { flex: none; height: auto; flex-direction: row; justify-content: flex-start; gap: 12px; padding: 12px 14px; border-radius: 10px; font-size: .88rem; font-weight: 500; color: var(--navy); }
  .nav-item:hover { background: var(--bg-soft); }
  .nav-item.active { background: var(--teal); color: #fff; font-weight: 700; }
  .nav-label { display: inline; }
  .nav-label-short { display: none; }
  .page-heading { gap: 16px; margin-bottom: 24px; }
  .heading-icon { width: 56px; height: 56px; }
  .page-heading h1 { font-size: 1.7rem; }
  .page-heading p { font-size: .9rem; }
}
</style>
