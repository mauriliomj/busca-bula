<script setup>
import { computed, ref, onBeforeUnmount, onMounted } from 'vue'
import {
  House,
  Search,
  FileText,
  UserRound,
  LogOut,
  Accessibility,
  User,
  CalendarDays,
  Venus,
  Mail,
  Phone,
  MapPin,
  MapPinned,
  ShieldCheck,
  LockKeyhole,
  ChevronRight,
  Camera,
  Save,
  CheckCircle,
  Eye,
  Trash2,
  Users
} from 'lucide-vue-next'
import {
  ORGANIZATION_ADMIN_ROLE,
  PLATFORM_ADMIN_ROLE,
  currentUserRole,
  isAuthenticated,
  logoutUser
} from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
import { useCurrentOrganization } from '../services/organization-branding'
import {
  changeCurrentUserPassword,
  deleteCurrentUser,
  fetchCurrentUser,
  updateCurrentUser
} from '../services/user-service'

const perfil = ref({
  nome: '',
  idade: '',
  sexo: '',
  email: '',
  celular: '',
  endereco: '',
  cidade: '',
  estado: ''
})

const estados = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA',
  'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

const administradorDaOrganizacao = currentUserRole() === ORGANIZATION_ADMIN_ROLE
const organizacao = useCurrentOrganization()

const menuItems = computed(() => [
  { label: 'Início', icon: House, href: '#' },
  { label: 'Buscar', icon: Search, href: '#' },
  { label: 'Minhas Consultas', icon: FileText, href: '#' },
  ...(administradorDaOrganizacao ? [{ label: 'Membros', icon: Users, href: '/members' }] : []),
  { label: 'Meu Perfil', icon: UserRound, href: '/user', active: true },
  { label: 'Sair', icon: LogOut, href: '/login', sair: true }
])

const foto = ref('')
const inputFoto = ref(null)
const mensagem = ref('')
const erroPerfil = ref('')
const salvando = ref(false)
const avisoSeguranca = ref('')
const erroSeguranca = ref('')
const painelAberto = ref('')
const processandoSeguranca = ref(false)
const alteracaoSenha = ref(criarAlteracaoSenhaVazia())
const senhaExclusao = ref('')
let timer = null

function criarAlteracaoSenhaVazia() {
  return { atual: '', nova: '', confirmacao: '' }
}

function alternarPainel(painel) {
  painelAberto.value = painelAberto.value === painel ? '' : painel
  erroSeguranca.value = ''
}

function mostrar(alvo, texto) {
  alvo.value = texto
  clearTimeout(timer)
  timer = setTimeout(() => (alvo.value = ''), 3000)
}

async function salvarAlteracoes() {
  erroPerfil.value = ''
  salvando.value = true
  try {
    perfil.value = await updateCurrentUser(perfil.value)
    mostrar(mensagem, 'Alterações salvas!')
  } catch (falha) {
    erroPerfil.value = extractErrorMessage(falha, 'Não foi possível salvar as alterações.')
  } finally {
    salvando.value = false
  }
}

async function alterarSenha() {
  erroSeguranca.value = ''
  if (alteracaoSenha.value.nova !== alteracaoSenha.value.confirmacao) {
    erroSeguranca.value = 'A confirmação não confere com a nova senha.'
    return
  }
  processandoSeguranca.value = true
  try {
    await changeCurrentUserPassword(alteracaoSenha.value.atual, alteracaoSenha.value.nova)
    alteracaoSenha.value = criarAlteracaoSenhaVazia()
    painelAberto.value = ''
    mostrar(avisoSeguranca, 'Senha alterada com sucesso!')
  } catch (falha) {
    erroSeguranca.value = extractErrorMessage(falha, 'Não foi possível alterar a senha.')
  } finally {
    processandoSeguranca.value = false
  }
}

async function excluirConta() {
  erroSeguranca.value = ''
  if (!window.confirm('Excluir sua conta? Todos os seus dados serão apagados e essa ação não pode ser desfeita.')) return
  processandoSeguranca.value = true
  try {
    await deleteCurrentUser(senhaExclusao.value)
    logoutUser()
    window.location.href = '/login'
  } catch (falha) {
    erroSeguranca.value = extractErrorMessage(falha, 'Não foi possível excluir a conta.')
  } finally {
    processandoSeguranca.value = false
  }
}

function sair() {
  logoutUser()
}

async function carregarPerfil() {
  if (!isAuthenticated() || currentUserRole() === PLATFORM_ADMIN_ROLE) {
    window.location.href = '/login'
    return
  }
  perfil.value = await fetchCurrentUser()
}

onMounted(carregarPerfil)

function alterarFoto() {
  inputFoto.value?.click()
}

function selecionarFoto(event) {
  const arquivo = event.target.files[0]
  if (!arquivo || !arquivo.type.startsWith('image/')) return
  if (foto.value) URL.revokeObjectURL(foto.value)
  foto.value = URL.createObjectURL(arquivo)
}

onBeforeUnmount(() => {
  clearTimeout(timer)
  if (foto.value) URL.revokeObjectURL(foto.value)
})
</script>

<template>
  <div class="perfil-page">
    <header class="header">
      <div class="header-inner">
        <a href="#" class="logo" aria-label="Busca Bula – início">
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

        <nav class="top-nav" aria-label="Navegação principal">
          <a href="#">Início</a>
          <a href="#">Sobre</a>
          <a href="#">Ajuda</a>
          <a href="#">Contato</a>
        </nav>

        <div class="header-actions">
          <button class="icon-btn" type="button" aria-label="Opções de acessibilidade">
            <Accessibility :size="22" />
          </button>
          <span class="header-user"><UserRound :size="17" />{{ perfil.nome || 'Usuário' }}</span>
        </div>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <nav class="menu" aria-label="Menu do usuário">
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
          <div class="heading-icon"><UserRound :size="27" /></div>
          <div>
            <h1>Meu Perfil</h1>
            <p>Mantenha seus dados sempre atualizados para uma melhor experiência no Busca Bula.</p>
          </div>
        </div>

        <div class="content-grid">
          <section class="forms-column">
            <form class="profile-form" @submit.prevent="salvarAlteracoes">
              <div class="form-card">
                <h2 class="section-title"><UserRound :size="17" />Dados pessoais</h2>

                <div class="fields-grid personal-grid">
                  <div class="field">
                    <label for="nome">Nome completo</label>
                    <div class="input-wrapper">
                      <User :size="16" />
                      <input id="nome" v-model="perfil.nome" type="text" placeholder="Digite seu nome completo" />
                    </div>
                  </div>

                  <div class="field">
                    <label for="idade">Idade</label>
                    <div class="input-wrapper">
                      <CalendarDays :size="16" />
                      <input id="idade" v-model="perfil.idade" type="number" min="0" max="120" placeholder="Ex.: 25" />
                    </div>
                  </div>

                  <div class="field sex-field">
                    <label for="sexo">Sexo</label>
                    <div class="input-wrapper">
                      <Venus :size="16" />
                      <select id="sexo" v-model="perfil.sexo">
                        <option value="" disabled>Selecione seu sexo</option>
                        <option value="feminino">Feminino</option>
                        <option value="masculino">Masculino</option>
                        <option value="outro">Outro</option>
                        <option value="nao-informar">Prefiro não informar</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-card">
                <h2 class="section-title"><Phone :size="17" />Contato</h2>

                <div class="fields-grid">
                  <div class="field">
                    <label for="email">E-mail</label>
                    <div class="input-wrapper">
                      <Mail :size="16" />
                      <input id="email" v-model="perfil.email" type="email" placeholder="Digite seu e-mail" />
                    </div>
                  </div>

                  <div class="field">
                    <label for="celular">Celular</label>
                    <div class="input-wrapper">
                      <Phone :size="16" />
                      <input id="celular" v-model="perfil.celular" type="tel" placeholder="(11) 91234-5678" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-card address-card">
                <h2 class="section-title"><MapPin :size="17" />Endereço</h2>

                <div class="fields-grid">
                  <div class="field full-width">
                    <label for="endereco">Endereço</label>
                    <div class="input-wrapper">
                      <House :size="16" />
                      <input id="endereco" v-model="perfil.endereco" type="text" placeholder="Digite seu endereço completo" />
                    </div>
                  </div>

                  <div class="field">
                    <label for="cidade">Cidade</label>
                    <div class="input-wrapper">
                      <MapPinned :size="16" />
                      <input id="cidade" v-model="perfil.cidade" type="text" placeholder="Digite sua cidade" />
                    </div>
                  </div>

                  <div class="field">
                    <label for="estado">Estado</label>
                    <div class="input-wrapper">
                      <MapPin :size="16" />
                      <select id="estado" v-model="perfil.estado">
                        <option value="" disabled>Selecione seu estado</option>
                        <option v-for="uf in estados" :key="uf" :value="uf">{{ uf }}</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div class="form-footer">
                  <button class="save-button" type="submit" :disabled="salvando">
                    <Save :size="15" />{{ salvando ? 'Salvando...' : 'Salvar alterações' }}
                  </button>
                  <p v-if="mensagem" class="success-message" role="status">
                    <CheckCircle :size="15" />{{ mensagem }}
                  </p>
                  <p v-if="erroPerfil" class="error-message" role="alert">{{ erroPerfil }}</p>
                </div>
              </div>
            </form>
          </section>

          <aside class="right-column">
            <section class="user-card">
              <div class="avatar-container">
                <div class="avatar">
                  <img v-if="foto" :src="foto" alt="Foto de perfil" />
                  <UserRound v-else :size="42" :stroke-width="1.5" />
                </div>
                <button class="camera-button" type="button" aria-label="Alterar foto de perfil" @click="alterarFoto">
                  <Camera :size="13" />
                </button>
                <input ref="inputFoto" class="hidden-input" type="file" accept="image/*" @change="selecionarFoto" />
              </div>

              <h2>{{ perfil.nome || 'Seu nome' }}</h2>
              <p>{{ perfil.email || 'Seu e-mail' }}</p>

              <button class="edit-photo-button" type="button" @click="alterarFoto">
                <Camera :size="14" />Alterar foto
              </button>
            </section>

            <section class="security-card">
              <h2 class="section-title"><ShieldCheck :size="18" />Segurança</h2>

              <button
                class="security-option"
                :class="{ open: painelAberto === 'senha' }"
                type="button"
                :aria-expanded="painelAberto === 'senha'"
                @click="alternarPainel('senha')"
              >
                <LockKeyhole :size="16" />
                <span>Alterar senha</span>
                <ChevronRight :size="16" class="option-arrow" />
              </button>

              <form v-if="painelAberto === 'senha'" class="security-panel" @submit.prevent="alterarSenha">
                <div class="field">
                  <label for="senha-atual">Senha atual</label>
                  <div class="input-wrapper">
                    <LockKeyhole :size="16" />
                    <input id="senha-atual" v-model="alteracaoSenha.atual" type="password" autocomplete="current-password" required />
                  </div>
                </div>
                <div class="field">
                  <label for="nova-senha">Nova senha</label>
                  <div class="input-wrapper">
                    <LockKeyhole :size="16" />
                    <input id="nova-senha" v-model="alteracaoSenha.nova" type="password" minlength="8" autocomplete="new-password" required />
                  </div>
                </div>
                <div class="field">
                  <label for="confirmacao-senha">Confirmar nova senha</label>
                  <div class="input-wrapper">
                    <LockKeyhole :size="16" />
                    <input id="confirmacao-senha" v-model="alteracaoSenha.confirmacao" type="password" minlength="8" autocomplete="new-password" required />
                  </div>
                </div>
                <button class="save-button" type="submit" :disabled="processandoSeguranca">
                  <Save :size="15" />{{ processandoSeguranca ? 'Salvando...' : 'Salvar nova senha' }}
                </button>
              </form>

              <button
                class="security-option"
                :class="{ open: painelAberto === 'privacidade' }"
                type="button"
                :aria-expanded="painelAberto === 'privacidade'"
                @click="alternarPainel('privacidade')"
              >
                <Eye :size="16" />
                <span>Privacidade dos dados</span>
                <ChevronRight :size="16" class="option-arrow" />
              </button>

              <div v-if="painelAberto === 'privacidade'" class="security-panel">
                <p class="security-text">
                  Seus dados ficam guardados apenas no banco da sua organização e não são compartilhados com outras
                  organizações. Você pode excluir sua conta a qualquer momento, e essa ação não pode ser desfeita.
                </p>

                <p v-if="administradorDaOrganizacao" class="security-text">
                  O administrador da organização não pode excluir a própria conta.
                </p>

                <form v-else class="panel-form" @submit.prevent="excluirConta">
                  <div class="field">
                    <label for="senha-exclusao">Confirme sua senha</label>
                    <div class="input-wrapper">
                      <LockKeyhole :size="16" />
                      <input id="senha-exclusao" v-model="senhaExclusao" type="password" autocomplete="current-password" required />
                    </div>
                  </div>
                  <button class="danger-button" type="submit" :disabled="processandoSeguranca">
                    <Trash2 :size="15" />Excluir minha conta
                  </button>
                </form>
              </div>

              <p v-if="erroSeguranca" class="error-message" role="alert">{{ erroSeguranca }}</p>
              <p v-if="avisoSeguranca" class="security-note" role="status">{{ avisoSeguranca }}</p>
            </section>
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
.perfil-page {
  --navy: var(--brand-secondary, #123a5c);
  --navy-dark: #16384f;
  --teal: var(--brand-primary, #0f9e94);
  --teal-dark: var(--brand-primary-dark, #0b857c);
  --mint: var(--brand-primary-soft, #d9f1ee);
  --bg-soft: #eef7f8;
  --text: #2b4a63;
  --muted: #6b8497;
  --line: #dfe9ee;
  min-height: 100vh;
  background: var(--bg-soft);
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}
.perfil-page *, .perfil-page *::before, .perfil-page *::after { box-sizing: border-box; margin: 0; padding: 0; }
.perfil-page a { color: inherit; text-decoration: none; }
.perfil-page button, .perfil-page input, .perfil-page select { font: inherit; }
.perfil-page :focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; border-radius: 6px; }

.header { background: #fff; box-shadow: 0 1px 0 var(--line); position: sticky; top: 0; z-index: 10; }
.header-inner { width: min(1200px, 100% - 48px); margin-inline: auto; height: 70px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.5rem; color: var(--navy); letter-spacing: -.02em; }
.logo em { font-style: normal; color: var(--teal); }
.org-logo { max-height: 48px; max-width: 220px; object-fit: contain; }
.top-nav { display: flex; gap: 30px; }
.top-nav a { font-size: .9rem; font-weight: 500; color: var(--navy); }
.top-nav a:hover { color: var(--teal); }
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

.content-grid { display: grid; grid-template-columns: 1fr 300px; gap: 24px; align-items: start; }
.profile-form { display: flex; flex-direction: column; gap: 20px; }
.form-card, .user-card, .security-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 16px rgba(18, 58, 92, .06); }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 18px; }
.section-title svg { color: var(--teal); }

.fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 20px; }
.personal-grid .sex-field { grid-column: 1 / -1; }
.full-width { grid-column: 1 / -1; }
.field label { display: block; font-size: .8rem; font-weight: 600; color: var(--navy); margin-bottom: 6px; }
.input-wrapper { display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fff; padding: 0 14px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.input-wrapper svg { flex: none; }
.input-wrapper input, .input-wrapper select { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 13px 0; font-size: .9rem; color: var(--navy); }
.input-wrapper input::placeholder { color: #8aa0b0; }

.form-footer { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-top: 22px; }
.save-button { display: inline-flex; align-items: center; gap: 8px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .9rem; padding: 13px 28px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.save-button:hover { background: var(--teal-dark); }
.save-button:disabled, .danger-button:disabled { background: #9aafc0; border-color: #9aafc0; color: #fff; cursor: not-allowed; }
.error-message { color: #c0392b; font-size: .85rem; font-weight: 600; }
.success-message { display: inline-flex; align-items: center; gap: 8px; color: var(--teal-dark); font-size: .85rem; font-weight: 600; }

.right-column { display: flex; flex-direction: column; gap: 20px; }
.user-card { text-align: center; }
.avatar-container { position: relative; width: 96px; height: 96px; margin: 0 auto 14px; }
.avatar { width: 96px; height: 96px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; overflow: hidden; border: 3px solid #fff; box-shadow: 0 0 0 2px var(--mint); }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.camera-button { position: absolute; right: -2px; bottom: 2px; width: 30px; height: 30px; border-radius: 50%; border: 2px solid #fff; background: var(--teal); color: #fff; display: grid; place-items: center; cursor: pointer; }
.hidden-input { display: none; }
.user-card h2 { font-size: 1.1rem; color: var(--navy); font-weight: 700; }
.user-card p { font-size: .82rem; color: var(--muted); margin-bottom: 16px; word-break: break-word; }
.edit-photo-button { display: inline-flex; align-items: center; gap: 8px; background: none; border: 1.5px solid var(--teal); color: var(--teal); font-weight: 600; font-size: .85rem; padding: 10px 22px; border-radius: 999px; cursor: pointer; transition: all .2s; }
.edit-photo-button:hover { background: var(--teal); color: #fff; }

.security-option { width: 100%; display: flex; align-items: center; gap: 12px; background: var(--bg-soft); border: 0; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: var(--navy); font-size: .88rem; font-weight: 600; text-align: left; cursor: pointer; transition: background .2s; }
.security-option:hover { background: var(--mint); }
.security-option svg:first-child { color: var(--teal); }
.security-option span { flex: 1; }
.option-arrow { color: var(--muted); transition: transform .2s; }
.security-option.open { background: var(--mint); }
.security-option.open .option-arrow { transform: rotate(90deg); }
.security-panel, .panel-form { display: flex; flex-direction: column; gap: 12px; }
.security-panel { margin: 4px 0 14px; }
.security-panel .save-button { justify-content: center; padding: 11px 20px; font-size: .85rem; }
.security-text { font-size: .8rem; color: var(--muted); }
.danger-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: none; border: 1.5px solid #c0392b; color: #c0392b; font-weight: 700; font-size: .85rem; padding: 11px 20px; border-radius: 999px; cursor: pointer; transition: all .2s; }
.danger-button:hover { background: #c0392b; color: #fff; }
.security-note { font-size: .78rem; color: var(--muted); margin-top: 4px; }

@media (max-width: 1000px) {
  .layout { grid-template-columns: 1fr; }
  .menu { flex-direction: row; overflow-x: auto; }
  .menu-item { white-space: nowrap; }
  .content-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .top-nav, .header-user { display: none; }
  .fields-grid { grid-template-columns: 1fr; }
  .page-heading { align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  .perfil-page * { transition: none !important; }
}
</style>