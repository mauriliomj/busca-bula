<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  House,
  UserRound,
  LogOut,
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
  Trash2
} from 'lucide-vue-next'
import MemberLayout from '../components/member-layout.vue'
import { ORGANIZATION_ADMIN_ROLE, currentUserRole, logoutUser } from '../services/auth-service'
import { extractErrorMessage } from '../services/http-client'
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

const router = useRouter()
const administradorDaOrganizacao = currentUserRole() === ORGANIZATION_ADMIN_ROLE

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
    await logoutUser()
    router.replace({ name: 'login' })
  } catch (falha) {
    erroSeguranca.value = extractErrorMessage(falha, 'Não foi possível excluir a conta.')
  } finally {
    processandoSeguranca.value = false
  }
}

async function sair() {
  await logoutUser()
  router.replace({ name: 'login' })
}

async function carregarPerfil() {
  try {
    perfil.value = await fetchCurrentUser()
  } catch (falha) {
    erroPerfil.value = extractErrorMessage(falha, 'Não foi possível carregar seu perfil.')
  }
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
  <MemberLayout
    ativo="perfil"
    titulo="Meu Perfil"
    descricao="Mantenha seus dados sempre atualizados para uma melhor experiência no Busca Bula."
    :icone="UserRound"
  >
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

        <button class="logout-card" type="button" @click="sair">
          <LogOut :size="17" />Sair da conta
        </button>
      </aside>
    </div>
  </MemberLayout>
</template>

<style scoped>
.content-grid { display: grid; grid-template-columns: 1fr; gap: 16px; align-items: start; }
.right-column { order: -1; display: flex; flex-direction: column; gap: 16px; }
.profile-form { display: flex; flex-direction: column; gap: 16px; }
.form-card, .user-card, .security-card { background: #fff; border-radius: 16px; padding: 18px 16px; box-shadow: var(--card-shadow); }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 16px; }
.section-title svg { color: var(--teal); flex: none; }

.fields-grid { display: grid; grid-template-columns: 1fr; gap: 14px 20px; }
.personal-grid .sex-field, .full-width { grid-column: 1 / -1; }
.field label { display: block; font-size: .82rem; font-weight: 600; color: var(--navy); margin-bottom: 6px; }
.input-wrapper { display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fff; padding: 0 14px; color: var(--muted); transition: border-color .2s, box-shadow .2s; }
.input-wrapper:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.input-wrapper svg { flex: none; }
.input-wrapper input, .input-wrapper select { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; padding: 12px 0; font-size: 1rem; color: var(--navy); }
.input-wrapper input::placeholder { color: #8aa0b0; }

.form-footer { display: flex; flex-direction: column; align-items: stretch; gap: 12px; margin-top: 20px; }
.save-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 48px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .95rem; padding: 0 28px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.save-button:hover { background: var(--teal-dark); }
.save-button:disabled, .danger-button:disabled { background: #9aafc0; border-color: #9aafc0; color: #fff; cursor: not-allowed; }
.error-message { color: var(--danger); font-size: .85rem; font-weight: 600; }
.success-message { display: inline-flex; align-items: center; gap: 8px; color: var(--teal-dark); font-size: .85rem; font-weight: 600; }

.user-card { display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 4px 16px; text-align: left; }
.avatar-container { position: relative; width: 72px; height: 72px; grid-row: span 3; }
.avatar { width: 72px; height: 72px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; overflow: hidden; border: 3px solid #fff; box-shadow: 0 0 0 2px var(--mint); }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.camera-button { position: absolute; right: -4px; bottom: -2px; width: 32px; height: 32px; border-radius: 50%; border: 2px solid #fff; background: var(--teal); color: #fff; display: grid; place-items: center; cursor: pointer; }
.hidden-input { display: none; }
.user-card h2 { font-size: 1.05rem; color: var(--navy); font-weight: 700; overflow-wrap: anywhere; }
.user-card p { font-size: .82rem; color: var(--muted); overflow-wrap: anywhere; }
.edit-photo-button { justify-self: start; display: inline-flex; align-items: center; gap: 8px; min-height: 40px; background: none; border: 1.5px solid var(--teal); color: var(--teal); font-weight: 600; font-size: .85rem; padding: 0 18px; border-radius: 999px; cursor: pointer; transition: all .2s; margin-top: 6px; }
.edit-photo-button:hover { background: var(--teal); color: #fff; }

.security-option { width: 100%; min-height: 52px; display: flex; align-items: center; gap: 12px; background: var(--bg-soft); border: 0; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: var(--navy); font-size: .9rem; font-weight: 600; text-align: left; cursor: pointer; transition: background .2s; }
.security-option:hover { background: var(--mint); }
.security-option svg:first-child { color: var(--teal); }
.security-option span { flex: 1; }
.option-arrow { color: var(--muted); transition: transform .2s; }
.security-option.open { background: var(--mint); }
.security-option.open .option-arrow { transform: rotate(90deg); }
.security-panel, .panel-form { display: flex; flex-direction: column; gap: 12px; }
.security-panel { margin: 4px 0 14px; }
.security-text { font-size: .82rem; color: var(--muted); }
.danger-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 46px; background: none; border: 1.5px solid var(--danger); color: var(--danger); font-weight: 700; font-size: .88rem; padding: 0 20px; border-radius: 999px; cursor: pointer; transition: all .2s; }
.danger-button:hover { background: var(--danger); color: #fff; }
.security-note { font-size: .8rem; color: var(--muted); margin-top: 4px; }

.logout-card { display: flex; align-items: center; justify-content: center; gap: 10px; min-height: 52px; background: #fff; border: 1.5px solid var(--line); border-radius: 16px; color: var(--navy); font-weight: 700; font-size: .95rem; cursor: pointer; box-shadow: var(--card-shadow); }
.logout-card:hover { border-color: var(--danger); color: var(--danger); }

@media (min-width: 640px) {
  .form-card, .user-card, .security-card { padding: 24px; }
  .fields-grid { grid-template-columns: 1fr 1fr; }
  .form-footer { flex-direction: row; align-items: center; flex-wrap: wrap; gap: 16px; }
  .input-wrapper input, .input-wrapper select { font-size: .92rem; }
}

@media (min-width: 1000px) {
  .content-grid { grid-template-columns: 1fr 300px; gap: 24px; }
  .right-column { order: 0; gap: 20px; }
  .profile-form { gap: 20px; }
  .user-card { display: block; text-align: center; }
  .avatar-container, .avatar { width: 96px; height: 96px; }
  .avatar-container { margin: 0 auto 14px; }
  .camera-button { right: -2px; bottom: 2px; }
  .user-card p { margin-bottom: 16px; }
  .edit-photo-button { margin-top: 0; }
  .logout-card { display: none; }
}
</style>
