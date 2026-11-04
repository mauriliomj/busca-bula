<script setup>
import logoBuscaBula from '../assets/images/Logo.png'
import { useCurrentOrganization } from '../services/organization-branding'

const organizacao = useCurrentOrganization()
</script>

<template>
  <img v-if="organizacao?.logoUrl" :src="organizacao.logoUrl" :alt="organizacao.nome" class="brand-logo" />
  <img v-else :src="logoBuscaBula" alt="Busca Bula" class="brand-logo" width="330" height="110" />
</template>

<style scoped>
.brand-logo { height: 40px; width: auto; max-width: 170px; object-fit: contain; object-position: left center; }

@media (min-width: 1000px) {
  .brand-logo { height: 52px; max-width: 230px; }
}
</style>
