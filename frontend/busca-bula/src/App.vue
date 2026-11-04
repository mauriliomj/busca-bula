<script setup>
  import { defineAsyncComponent } from 'vue';
  import Header from './components/header.vue';
  import { useCurrentOrganization } from './services/organization-branding';

  useCurrentOrganization();

  const arquivos = import.meta.glob('./pages/*.vue');

  const paginas = {};
  for (const arquivo in arquivos) {
    const nome = arquivo.replace('./pages/', '').replace('.vue', '').replace(/-page$/, '');
    paginas[nome] = arquivos[arquivo];
  }

  const caminho = window.location.pathname.replace(/^\/+|\/+$/g, '').replace(/-page$/, '');
  const paginaAtual = paginas[caminho] ? defineAsyncComponent(paginas[caminho]) : null;
</script>

<template>
  <component v-if="paginaAtual" :is="paginaAtual" />

  <template v-else>
    <Header></Header>

    <main class="lista-paginas">
      <h2>Páginas</h2>
      <a v-for="nome in Object.keys(paginas)" :key="nome" :href="'/' + nome">
        /{{ nome }}
      </a>
    </main>
  </template>
</template>

<style scoped>
.lista-paginas {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 300px;
  margin: 50px auto;
  font-family: Arial, Helvetica, sans-serif;
}

.lista-paginas h2 {
  color: #174563;
  margin: 0 0 10px;
}

.lista-paginas a {
  padding: 10px 15px;
  border: 1px solid #D7E1E8;
  border-radius: 7px;
  color: #0DA99F;
  font-weight: 600;
  text-decoration: none;
}

.lista-paginas a:hover {
  border-color: #0DA99F;
}
</style>
