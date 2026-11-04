import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { onSessionExpired } from './services/http-client'
import './styles/base.css'

onSessionExpired(() => {
  const rotaAtual = router.currentRoute.value
  if (rotaAtual.name === 'login') return
  router.push({ name: 'login', query: { next: rotaAtual.fullPath } })
})

createApp(App).use(router).mount('#app')
