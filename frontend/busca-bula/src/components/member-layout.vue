<script setup>
import { computed } from 'vue'
import { FileText, Search, UserRound, Users } from 'lucide-vue-next'
import AppShell from './app-shell.vue'
import { ORGANIZATION_ADMIN_ROLE, currentUserRole } from '../services/auth-service'

defineProps({
  ativo: { type: String, required: true },
  titulo: { type: String, required: true },
  descricao: { type: String, default: '' },
  icone: { type: [Object, Function], required: true }
})

const navegacao = computed(() => [
  { chave: 'buscar', rotulo: 'Buscar', icone: Search, to: { name: 'search' } },
  { chave: 'consultas', rotulo: 'Minhas Consultas', rotuloCurto: 'Consultas', icone: FileText, to: { name: 'consultations' } },
  ...(currentUserRole() === ORGANIZATION_ADMIN_ROLE
    ? [{ chave: 'membros', rotulo: 'Membros', icone: Users, to: { name: 'members' } }]
    : []),
  { chave: 'perfil', rotulo: 'Meu Perfil', rotuloCurto: 'Perfil', icone: UserRound, to: { name: 'user' } }
])
</script>

<template>
  <AppShell
    :navegacao="navegacao"
    :ativo="ativo"
    :titulo="titulo"
    :descricao="descricao"
    :icone="icone"
    :inicio="{ name: 'search' }"
    rotulo-do-menu="Menu do usuário"
  >
    <slot />

    <p class="medical-disclaimer">
      O conteúdo do Busca Bula é informativo e não substitui a orientação de um médico ou farmacêutico.
    </p>
  </AppShell>
</template>

<style scoped>
.medical-disclaimer { margin-top: 28px; font-size: .78rem; color: var(--muted); text-align: center; }
</style>
