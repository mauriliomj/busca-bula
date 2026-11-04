<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff, LockKeyhole, Mail } from 'lucide-vue-next'
import AuthLayout from '../components/auth-layout.vue'
import { loginUser, resolvePostLoginPath } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
import { loadCurrentOrganization } from '../services/organization-branding'
import { isPlatformContext } from '../services/organization-context'

const route = useRoute()
const router = useRouter()

const areaDaPlataforma = isPlatformContext()
const email = ref('')
const senha = ref('')
const mostrarSenha = ref(false)
const enviando = ref(false)
const erro = ref('')
const organizacao = ref(null)
const organizacaoIndisponivel = ref(false)

const subtitulo = computed(() => {
  if (areaDaPlataforma) return 'Área administrativa da plataforma Busca Bula.'
  if (organizacao.value) return `Informe seu e-mail para acessar sua conta ${organizacao.value.nome}.`
  return 'Informe seu e-mail para acessar sua conta.'
})

const cadastro = computed(() => ({ name: 'register', query: route.query.next ? { next: route.query.next } : {} }))

async function carregarOrganizacao() {
  try {
    organizacao.value = await loadCurrentOrganization()
  } catch (falha) {
    organizacaoIndisponivel.value = true
    erro.value = extractErrorMessage(falha, 'Não foi possível carregar a organização.')
  }
}

async function entrar() {
  erro.value = ''
  enviando.value = true
  try {
    const papel = await loginUser(email.value, senha.value)
    await router.replace(resolvePostLoginPath(papel, route.query.next))
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível entrar. Tente novamente.')
  } finally {
    enviando.value = false
  }
}

onMounted(() => {
  if (!areaDaPlataforma) carregarOrganizacao()
})
</script>

<template>
  <AuthLayout
    destaque="Acesse suas bulas de forma rápida e segura."
    resumo="Encontre informações oficiais sobre medicamentos em poucos cliques."
  >
    <h1>Entrar</h1>
    <p class="subtitle">{{ subtitulo }}</p>

    <form @submit.prevent="entrar">
      <div class="form-group">
        <label for="email">E-mail</label>
        <div class="input-container">
          <Mail :size="18" :stroke-width="1.8" />
          <input
            id="email"
            v-model="email"
            type="email"
            inputmode="email"
            placeholder="Digite seu e-mail"
            autocomplete="username"
            autocapitalize="off"
            required
          >
        </div>
      </div>

      <div class="form-group">
        <label for="senha">Senha</label>
        <div class="input-container">
          <LockKeyhole :size="18" :stroke-width="1.8" />
          <input
            id="senha"
            v-model="senha"
            :type="mostrarSenha ? 'text' : 'password'"
            placeholder="Digite sua senha"
            autocomplete="current-password"
            required
          >
          <button
            type="button"
            class="toggle-password"
            :aria-label="mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'"
            @click="mostrarSenha = !mostrarSenha"
          >
            <EyeOff v-if="mostrarSenha" :size="18" />
            <Eye v-else :size="18" />
          </button>
        </div>
      </div>

      <button type="submit" class="submit-button" :disabled="enviando || organizacaoIndisponivel">
        {{ enviando ? 'Entrando...' : 'Entrar' }} <span aria-hidden="true">→</span>
      </button>

      <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>

      <p v-if="!areaDaPlataforma && !organizacaoIndisponivel" class="alternate-link">
        Não tem uma conta? <RouterLink :to="cadastro">Cadastre-se</RouterLink>
      </p>
    </form>
  </AuthLayout>
</template>
