<script setup>
import { Accessibility } from 'lucide-vue-next'
import BrandLogo from './brand-logo.vue'
import ilustracao from '../assets/images/icone.png'

defineProps({
  destaque: { type: String, required: true },
  resumo: { type: String, required: true },
  largo: { type: Boolean, default: false }
})
</script>

<template>
  <div class="auth-page">
    <header class="auth-header">
      <RouterLink :to="{ name: 'search' }" class="auth-logo" aria-label="Ir para a busca">
        <BrandLogo />
      </RouterLink>
      <button class="auth-icon-button" type="button" aria-label="Opções de acessibilidade">
        <Accessibility :size="21" />
      </button>
    </header>

    <main class="auth-main">
      <div class="auth-card" :class="{ wide: largo }">
        <section class="auth-info" aria-hidden="true">
          <h2>{{ destaque }}</h2>
          <p>{{ resumo }}</p>
          <img :src="ilustracao" alt="" class="auth-illustration" />
        </section>

        <section class="auth-form">
          <slot />
        </section>
      </div>
    </main>
  </div>
</template>

<style>
.auth-page { min-height: 100dvh; display: flex; flex-direction: column; background: #fff; }
.auth-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: calc(var(--safe-top) + 10px) 16px 10px; background: #fff; box-shadow: 0 1px 0 var(--line); }
.auth-logo { display: flex; min-width: 0; }
.auth-icon-button { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--navy); background: none; color: var(--navy); display: grid; place-items: center; cursor: pointer; flex: none; }

.auth-main { flex: 1; display: flex; justify-content: center; align-items: flex-start; padding: 0 0 calc(var(--safe-bottom) + 24px); }
.auth-card { width: 100%; background: #fff; display: grid; }
.auth-info { display: none; }
.auth-form { padding: 28px 20px; min-width: 0; }

.auth-form h1 { color: var(--navy); font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; margin-bottom: 6px; }
.auth-form .subtitle { color: var(--muted); font-size: .9rem; margin-bottom: 24px; }
.auth-form form { display: flex; flex-direction: column; gap: 16px; }
.auth-form .form-row { display: grid; gap: 16px; }
.auth-form .form-group { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.auth-form .form-group label { color: var(--navy); font-size: .85rem; font-weight: 600; }
.auth-form .input-container { display: flex; align-items: center; gap: 10px; min-height: 48px; border: 1px solid #d7e1e8; border-radius: 10px; padding: 0 14px; color: #52738d; background: #fff; transition: border-color .2s, box-shadow .2s; }
.auth-form .input-container:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .18); }
.auth-form .input-container svg { flex: none; }
.auth-form .input-container input,
.auth-form .input-container select { flex: 1; width: 100%; min-width: 0; border: 0; outline: 0; background: transparent; padding: 12px 0; font-size: 1rem; color: var(--navy); }
.auth-form .input-container input::placeholder { color: #9aafc0; }
.auth-form .input-container select { cursor: pointer; }
.auth-form .toggle-password { display: grid; place-items: center; width: 40px; height: 40px; margin-right: -10px; border: 0; background: none; color: var(--muted); cursor: pointer; flex: none; }

.auth-form .submit-button { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; min-height: 50px; margin-top: 8px; border: 0; border-radius: 999px; background: var(--teal); color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; transition: background .2s; }
.auth-form .submit-button:hover { background: var(--teal-dark); }
.auth-form .submit-button:disabled { background: #9aafc0; cursor: not-allowed; }
.auth-form .error-message { text-align: center; color: var(--danger); font-size: .9rem; font-weight: 600; }
.auth-form .alternate-link { text-align: center; color: var(--navy); font-size: .9rem; }
.auth-form .alternate-link a { color: var(--teal); font-weight: 700; }
.auth-form .alternate-link a:hover { text-decoration: underline; }

@media (min-width: 560px) {
  .auth-page { background: #f1f6f9; }
  .auth-main { align-items: center; padding: 32px 20px calc(var(--safe-bottom) + 32px); }
  .auth-card { max-width: 460px; border: 1px solid #e1eaf0; border-radius: 16px; overflow: hidden; box-shadow: 0 24px 60px rgba(17, 12, 46, .12); }
  .auth-form { padding: 32px; }
  .auth-form .form-row { grid-template-columns: 1.4fr 1fr; }
}

@media (min-width: 900px) {
  .auth-header { padding: 12px 48px; }
  .auth-card { max-width: 820px; grid-template-columns: 1fr 1fr; }
  .auth-card.wide { max-width: 980px; grid-template-columns: .85fr 1.15fr; }
  .auth-info { display: flex; flex-direction: column; gap: 12px; padding: 40px 32px; background: #f1f6f9; }
  .auth-info h2 { color: var(--navy); font-size: 1.35rem; line-height: 1.35; font-weight: 800; }
  .auth-info p { color: #71879a; font-size: .92rem; }
  .auth-illustration { margin-top: auto; width: 100%; max-width: 320px; align-self: center; }
  .auth-form { padding: 40px; }
}
</style>
