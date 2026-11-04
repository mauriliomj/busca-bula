<script setup>
import AppUpdatePrompt from './components/app-update-prompt.vue'
import { useCurrentOrganization } from './services/organization-branding'

useCurrentOrganization()
</script>

<template>
  <RouterView />
  <AppUpdatePrompt />
</template>
