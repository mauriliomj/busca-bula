<script setup>
import { computed, ref, watch } from 'vue'
import { CheckCircle, ImageUp, Palette, RotateCcw, Save, Trash2 } from 'lucide-vue-next'
import { buildBrandPalette } from '../services/brand-colors'
import { extractErrorMessage } from '../services/http-client'

const COR_PRIMARIA_PADRAO = '#0f9e94'
const COR_SECUNDARIA_PADRAO = '#123a5c'
const TAMANHO_MAXIMO_LOGO = 512 * 1024
const TIPOS_DE_LOGO = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const FORMATO_HEXADECIMAL = /^#[0-9a-f]{6}$/i

const props = defineProps({
  marca: { type: Object, required: true },
  nomeDaOrganizacao: { type: String, default: '' },
  salvarCores: { type: Function, required: true },
  enviarLogo: { type: Function, required: true },
  removerLogo: { type: Function, required: true }
})

const emit = defineEmits(['atualizada'])

const corPrimaria = ref('')
const corSecundaria = ref('')
const inputLogo = ref(null)
const processando = ref(false)
const mensagem = ref('')
const erro = ref('')

watch(
  () => props.marca,
  (marca) => {
    corPrimaria.value = marca.corPrimaria || COR_PRIMARIA_PADRAO
    corSecundaria.value = marca.corSecundaria || COR_SECUNDARIA_PADRAO
  },
  { immediate: true }
)

const coresValidas = computed(
  () => FORMATO_HEXADECIMAL.test(corPrimaria.value) && FORMATO_HEXADECIMAL.test(corSecundaria.value)
)

const estiloDaPrevia = computed(() =>
  coresValidas.value ? buildBrandPalette(corPrimaria.value, corSecundaria.value) : {}
)

async function executar(acao, mensagemDeSucesso, mensagemDeFalha) {
  erro.value = ''
  mensagem.value = ''
  processando.value = true
  try {
    emit('atualizada', await acao())
    mensagem.value = mensagemDeSucesso
  } catch (falha) {
    erro.value = extractErrorMessage(falha, mensagemDeFalha)
  } finally {
    processando.value = false
  }
}

function salvar() {
  if (!coresValidas.value) {
    erro.value = 'Use cores no formato #RRGGBB.'
    return
  }
  executar(
    () => props.salvarCores({ corPrimaria: corPrimaria.value, corSecundaria: corSecundaria.value }),
    'Cores salvas!',
    'Não foi possível salvar as cores.'
  )
}

function restaurarCoresPadrao() {
  executar(
    () => props.salvarCores({ corPrimaria: null, corSecundaria: null }),
    'Cores padrão restauradas.',
    'Não foi possível restaurar as cores.'
  )
}

function escolherLogo() {
  inputLogo.value?.click()
}

function enviarArquivo(evento) {
  const arquivo = evento.target.files[0]
  evento.target.value = ''
  if (!arquivo) return
  if (!TIPOS_DE_LOGO.includes(arquivo.type)) {
    erro.value = 'Envie uma imagem PNG, JPG, WEBP ou SVG.'
    return
  }
  if (arquivo.size > TAMANHO_MAXIMO_LOGO) {
    erro.value = 'A logo deve ter no máximo 512 KB.'
    return
  }
  executar(() => props.enviarLogo(arquivo), 'Logo atualizada!', 'Não foi possível enviar a logo.')
}

function excluirLogo() {
  executar(() => props.removerLogo(), 'Logo removida.', 'Não foi possível remover a logo.')
}
</script>

<template>
  <div class="branding-editor">
    <div class="editor-block">
      <h3 class="block-title"><ImageUp :size="16" />Logo</h3>

      <div class="logo-row">
        <div class="logo-preview">
          <img v-if="marca.logoUrl" :src="marca.logoUrl" :alt="`Logo ${nomeDaOrganizacao}`" />
          <span v-else>Sem logo</span>
        </div>

        <div class="logo-actions">
          <button class="outline-button" type="button" :disabled="processando" @click="escolherLogo">
            <ImageUp :size="14" />{{ marca.logoUrl ? 'Trocar logo' : 'Enviar logo' }}
          </button>
          <button
            v-if="marca.logoUrl"
            class="outline-button danger"
            type="button"
            :disabled="processando"
            @click="excluirLogo"
          >
            <Trash2 :size="14" />Remover
          </button>
          <small>PNG, JPG, WEBP ou SVG, até 512 KB.</small>
        </div>

        <input
          ref="inputLogo"
          class="hidden-input"
          type="file"
          accept="image/png,image/jpeg,image/webp,image/svg+xml"
          @change="enviarArquivo"
        />
      </div>
    </div>

    <form class="editor-block" @submit.prevent="salvar">
      <h3 class="block-title"><Palette :size="16" />Cores</h3>

      <div class="color-grid">
        <div class="color-field">
          <label for="cor-primaria">Cor principal</label>
          <div class="color-input">
            <input v-model="corPrimaria" type="color" aria-label="Escolher cor principal" />
            <input id="cor-primaria" v-model="corPrimaria" type="text" maxlength="7" spellcheck="false" />
          </div>
          <small>Botões, links e destaques.</small>
        </div>

        <div class="color-field">
          <label for="cor-secundaria">Cor secundária</label>
          <div class="color-input">
            <input v-model="corSecundaria" type="color" aria-label="Escolher cor secundária" />
            <input id="cor-secundaria" v-model="corSecundaria" type="text" maxlength="7" spellcheck="false" />
          </div>
          <small>Títulos e textos de destaque.</small>
        </div>
      </div>

      <div class="brand-preview" :style="estiloDaPrevia" aria-hidden="true">
        <p class="preview-label">Prévia</p>
        <p class="preview-title">Acesse suas bulas</p>
        <p class="preview-text">Informações oficiais sobre medicamentos.</p>
        <span class="preview-button">Entrar →</span>
        <span class="preview-link">Cadastre-se</span>
      </div>

      <div class="editor-actions">
        <button class="save-button" type="submit" :disabled="processando">
          <Save :size="15" />Salvar cores
        </button>
        <button class="text-button" type="button" :disabled="processando" @click="restaurarCoresPadrao">
          <RotateCcw :size="14" />Restaurar padrão
        </button>
      </div>
    </form>

    <p v-if="erro" class="error-message" role="alert">{{ erro }}</p>
    <p v-if="mensagem" class="success-message" role="status"><CheckCircle :size="15" />{{ mensagem }}</p>
  </div>
</template>

<style scoped>
.branding-editor { display: flex; flex-direction: column; gap: 22px; }
.branding-editor button, .branding-editor input { font-family: inherit; }
.editor-block { display: flex; flex-direction: column; gap: 14px; }
.block-title { display: flex; align-items: center; gap: 8px; font-size: .9rem; font-weight: 700; color: var(--navy); }
.block-title svg { color: var(--teal); }

.logo-row { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
.logo-preview { width: 150px; height: 90px; border: 1px dashed var(--line); border-radius: 12px; background: var(--bg-soft); display: grid; place-items: center; overflow: hidden; padding: 10px; }
.logo-preview img { max-width: 100%; max-height: 100%; object-fit: contain; }
.logo-preview span { font-size: .8rem; color: var(--muted); }
.logo-actions { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
.logo-actions small, .color-field small { font-size: .75rem; color: var(--muted); }
.hidden-input { display: none; }

.outline-button { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1.5px solid var(--teal); color: var(--teal); font-weight: 600; font-size: .8rem; padding: 7px 16px; border-radius: 999px; cursor: pointer; transition: all .2s; }
.outline-button:hover { background: var(--teal); color: #fff; }
.outline-button.danger { border-color: #c0392b; color: #c0392b; }
.outline-button.danger:hover { background: #c0392b; color: #fff; }

.color-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; }
.color-field { min-width: 0; }
.color-field label { display: block; font-size: .8rem; font-weight: 600; color: var(--navy); margin-bottom: 6px; }
.color-input { min-width: 0; display: flex; align-items: center; gap: 10px; border: 1px solid var(--line); border-radius: 10px; padding: 6px 10px; background: #fff; }
.color-input:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.color-input input[type='color'] { width: 30px; height: 30px; border: 0; padding: 0; background: none; cursor: pointer; flex: none; }
.color-input input[type='text'] { flex: 1; width: 100%; min-width: 0; border: 0; outline: 0; font-size: .88rem; color: var(--navy); text-transform: lowercase; font-family: inherit; }

.brand-preview { border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; background: #f1f6f9; display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
.preview-label { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
.preview-title { font-size: 1rem; font-weight: 700; color: var(--brand-secondary, #123a5c); }
.preview-text { font-size: .8rem; color: #71879a; }
.preview-button { margin-top: 4px; background: var(--brand-primary, #0f9e94); color: #fff; font-size: .8rem; font-weight: 600; padding: 7px 22px; border-radius: 999px; }
.preview-link { font-size: .78rem; font-weight: 600; color: var(--brand-primary, #0f9e94); }

.editor-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.save-button { display: inline-flex; align-items: center; gap: 8px; background: var(--teal); color: #fff; border: 0; font-weight: 700; font-size: .88rem; padding: 12px 24px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.save-button:hover { background: var(--teal-dark); }
.text-button { display: inline-flex; align-items: center; gap: 6px; background: none; border: 0; color: var(--muted); font-weight: 600; font-size: .82rem; cursor: pointer; }
.text-button:hover { color: var(--navy); }
.save-button:disabled, .outline-button:disabled, .text-button:disabled { opacity: .6; cursor: not-allowed; }

.error-message { color: #c0392b; font-size: .85rem; font-weight: 600; }
.success-message { display: inline-flex; align-items: center; gap: 8px; color: var(--teal-dark); font-size: .85rem; font-weight: 600; }
</style>
