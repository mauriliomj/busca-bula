<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Building2,
  CalendarDays,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Map,
  MapPin,
  Phone,
  UserRound,
  VenusAndMars
} from 'lucide-vue-next'
import AuthLayout from '../components/auth-layout.vue'
import { loginUser, registerUser, resolvePostLoginPath } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'

const route = useRoute()
const router = useRouter()

const estados = [
  { sigla: 'AC', nome: 'Acre' },
  { sigla: 'AL', nome: 'Alagoas' },
  { sigla: 'AP', nome: 'Amapá' },
  { sigla: 'AM', nome: 'Amazonas' },
  { sigla: 'BA', nome: 'Bahia' },
  { sigla: 'CE', nome: 'Ceará' },
  { sigla: 'DF', nome: 'Distrito Federal' },
  { sigla: 'ES', nome: 'Espírito Santo' },
  { sigla: 'GO', nome: 'Goiás' },
  { sigla: 'MA', nome: 'Maranhão' },
  { sigla: 'MT', nome: 'Mato Grosso' },
  { sigla: 'MS', nome: 'Mato Grosso do Sul' },
  { sigla: 'MG', nome: 'Minas Gerais' },
  { sigla: 'PA', nome: 'Pará' },
  { sigla: 'PB', nome: 'Paraíba' },
  { sigla: 'PR', nome: 'Paraná' },
  { sigla: 'PE', nome: 'Pernambuco' },
  { sigla: 'PI', nome: 'Piauí' },
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'RN', nome: 'Rio Grande do Norte' },
  { sigla: 'RS', nome: 'Rio Grande do Sul' },
  { sigla: 'RO', nome: 'Rondônia' },
  { sigla: 'RR', nome: 'Roraima' },
  { sigla: 'SC', nome: 'Santa Catarina' },
  { sigla: 'SP', nome: 'São Paulo' },
  { sigla: 'SE', nome: 'Sergipe' },
  { sigla: 'TO', nome: 'Tocantins' }
]

const mostrarSenha = ref(false)
const enviando = ref(false)
const erro = ref('')

const formulario = ref({
  nome: '',
  idade: '',
  sexo: '',
  email: '',
  celular: '',
  endereco: '',
  cidade: '',
  estado: '',
  senha: ''
})

const entrar = computed(() => ({ name: 'login', query: route.query.next ? { next: route.query.next } : {} }))

async function cadastrar() {
  erro.value = ''
  enviando.value = true
  try {
    await registerUser(formulario.value)
    const papel = await loginUser(formulario.value.email, formulario.value.senha)
    await router.replace(resolvePostLoginPath(papel, route.query.next))
  } catch (falha) {
    erro.value = extractErrorMessage(falha, 'Não foi possível concluir o cadastro. Tente novamente.')
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <AuthLayout
    largo
    destaque="Tenha acesso rápido e seguro às bulas de medicamentos."
    resumo="Cadastre-se para consultar informações oficiais da ANVISA de forma simples, rápida e confiável."
  >
    <h1>Criar conta</h1>
    <p class="subtitle">Preencha os dados abaixo para começar a usar o Busca Bula.</p>

    <form @submit.prevent="cadastrar">
      <div class="form-row">
        <div class="form-group">
          <label for="nome">Nome completo</label>
          <div class="input-container">
            <UserRound :size="18" />
            <input id="nome" v-model="formulario.nome" type="text" placeholder="Digite seu nome completo" autocomplete="name" required>
          </div>
        </div>

        <div class="form-group">
          <label for="idade">Idade</label>
          <div class="input-container">
            <CalendarDays :size="18" />
            <input id="idade" v-model="formulario.idade" type="number" inputmode="numeric" placeholder="Ex.: 25" min="1" max="120" required>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="sexo">Sexo</label>
        <div class="input-container">
          <VenusAndMars :size="18" />
          <select id="sexo" v-model="formulario.sexo" required>
            <option value="" disabled>Selecione seu sexo</option>
            <option value="feminino">Feminino</option>
            <option value="masculino">Masculino</option>
            <option value="outro">Outro</option>
            <option value="nao-informar">Prefiro não informar</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="email">E-mail</label>
          <div class="input-container">
            <Mail :size="18" />
            <input id="email" v-model="formulario.email" type="email" inputmode="email" placeholder="Digite seu e-mail" autocomplete="email" autocapitalize="off" required>
          </div>
        </div>

        <div class="form-group">
          <label for="celular">Celular</label>
          <div class="input-container">
            <Phone :size="18" />
            <input id="celular" v-model="formulario.celular" type="tel" inputmode="tel" placeholder="(11) 91234-5678" autocomplete="tel" required>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="endereco">Endereço</label>
        <div class="input-container">
          <MapPin :size="18" />
          <input id="endereco" v-model="formulario.endereco" type="text" placeholder="Digite seu endereço completo" autocomplete="street-address" required>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="cidade">Cidade</label>
          <div class="input-container">
            <Building2 :size="18" />
            <input id="cidade" v-model="formulario.cidade" type="text" placeholder="Digite sua cidade" autocomplete="address-level2" required>
          </div>
        </div>

        <div class="form-group">
          <label for="estado">Estado</label>
          <div class="input-container">
            <Map :size="18" />
            <select id="estado" v-model="formulario.estado" autocomplete="address-level1" required>
              <option value="" disabled>Selecione</option>
              <option v-for="estado in estados" :key="estado.sigla" :value="estado.sigla">{{ estado.nome }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="senha">Senha</label>
        <div class="input-container">
          <LockKeyhole :size="18" />
          <input
            id="senha"
            v-model="formulario.senha"
            :type="mostrarSenha ? 'text' : 'password'"
            placeholder="Crie uma senha com 8 caracteres ou mais"
            minlength="8"
            autocomplete="new-password"
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

      <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>

      <button type="submit" class="submit-button" :disabled="enviando">
        {{ enviando ? 'Cadastrando...' : 'Cadastrar' }} <span aria-hidden="true">→</span>
      </button>

      <p class="alternate-link">
        Já tem uma conta? <RouterLink :to="entrar">Entrar</RouterLink>
      </p>
    </form>
  </AuthLayout>
</template>
