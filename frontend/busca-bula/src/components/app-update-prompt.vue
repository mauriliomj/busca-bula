<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRegisterSW } from 'virtual:pwa-register/vue'
import { RefreshCw, WifiOff } from 'lucide-vue-next'

const { needRefresh, updateServiceWorker } = useRegisterSW()
const offline = ref(!navigator.onLine)

function atualizarConexao() {
  offline.value = !navigator.onLine
}

onMounted(() => {
  window.addEventListener('online', atualizarConexao)
  window.addEventListener('offline', atualizarConexao)
})

onBeforeUnmount(() => {
  window.removeEventListener('online', atualizarConexao)
  window.removeEventListener('offline', atualizarConexao)
})
</script>

<template>
  <div class="app-notices" aria-live="polite">
    <p v-if="offline" class="notice offline"><WifiOff :size="16" />Sem conexão. Algumas informações podem não carregar.</p>
    <div v-if="needRefresh" class="notice update" role="status">
      <span>Nova versão do Busca Bula disponível.</span>
      <button type="button" @click="updateServiceWorker(true)"><RefreshCw :size="15" />Atualizar</button>
      <button type="button" class="dismiss" @click="needRefresh = false">Agora não</button>
    </div>
  </div>
</template>

<style scoped>
.app-notices { position: fixed; left: 12px; right: 12px; bottom: calc(var(--bottom-nav-height) + var(--safe-bottom) + 12px); z-index: 40; display: flex; flex-direction: column; gap: 8px; pointer-events: none; }
.notice { pointer-events: auto; display: flex; align-items: center; flex-wrap: wrap; gap: 8px 12px; padding: 12px 16px; border-radius: 14px; font-size: .88rem; font-weight: 600; box-shadow: 0 10px 30px rgba(18, 58, 92, .18); }
.offline { background: #fff4e0; color: #7a4d00; }
.update { background: var(--navy); color: #fff; }
.update span { flex: 1 1 180px; }
.update button { display: inline-flex; align-items: center; gap: 6px; min-height: 40px; padding: 0 16px; border: 0; border-radius: 999px; background: var(--teal); color: #fff; font-weight: 700; cursor: pointer; }
.update .dismiss { background: none; color: #fff; opacity: .85; }

@media (min-width: 1000px) {
  .app-notices { left: auto; right: 24px; bottom: 24px; max-width: 420px; }
}
</style>
