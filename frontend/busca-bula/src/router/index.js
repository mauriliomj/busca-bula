import { createRouter, createWebHistory } from 'vue-router'
import {
  MEMBER_ROLES,
  ORGANIZATION_ADMIN_ROLES,
  PLATFORM_ADMIN_ROLES,
  PLATFORM_CONTEXT,
  TENANT_CONTEXT,
  authorizeNavigation,
} from './guards'

const routes = [
  {
    path: '/',
    name: 'search',
    component: () => import('../pages/search-page.vue'),
    meta: { context: TENANT_CONTEXT, title: 'Buscar medicamentos' },
  },
  {
    path: '/medicine/:registro(\\d{9})',
    name: 'medicine',
    component: () => import('../pages/medicine-page.vue'),
    meta: { context: TENANT_CONTEXT, roles: MEMBER_ROLES, title: 'Medicamento' },
  },
  {
    path: '/consultations',
    name: 'consultations',
    component: () => import('../pages/consultations-page.vue'),
    meta: { context: TENANT_CONTEXT, roles: MEMBER_ROLES, title: 'Minhas Consultas' },
  },
  {
    path: '/user',
    name: 'user',
    component: () => import('../pages/user-page.vue'),
    meta: { context: TENANT_CONTEXT, roles: MEMBER_ROLES, title: 'Meu Perfil' },
  },
  {
    path: '/members',
    name: 'members',
    component: () => import('../pages/members-page.vue'),
    meta: { context: TENANT_CONTEXT, roles: ORGANIZATION_ADMIN_ROLES, title: 'Membros' },
  },
  {
    path: '/org',
    name: 'org',
    component: () => import('../pages/org-page.vue'),
    meta: { context: PLATFORM_CONTEXT, roles: PLATFORM_ADMIN_ROLES, title: 'Organizações' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/login-page.vue'),
    meta: { guestOnly: true, title: 'Entrar' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../pages/register-page.vue'),
    meta: { context: TENANT_CONTEXT, guestOnly: true, title: 'Criar conta' },
  },
  { path: '/search', redirect: (to) => ({ name: 'search', query: to.query }) },
  { path: '/:caminho(.*)*', redirect: { name: 'search' } },
]

const APP_NAME = 'Busca Bula'

function scrollBehavior(to, from, savedPosition) {
  if (savedPosition) return savedPosition
  if (to.hash && document.querySelector(to.hash)) return { el: to.hash, top: 90, behavior: 'smooth' }
  if (to.path === from.path) return false
  return { top: 0 }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior,
})

router.beforeEach(authorizeNavigation)

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · ${APP_NAME}` : APP_NAME
})

export default router
