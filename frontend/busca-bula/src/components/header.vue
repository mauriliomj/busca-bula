<script setup>
import logo from '../assets/images/Logo.png'
import { PersonStanding } from 'lucide-vue-next'
import { useCurrentOrganization } from '../services/organization-branding'

const organizacao = useCurrentOrganization()
</script>

<template>
    <header>
        <img
            v-if="organizacao?.logoUrl"
            :src="organizacao.logoUrl"
            :alt="`Logo ${organizacao.nome}`"
            id="logo_organizacao"
        >
        <img
            v-else
            :src="logo"
            alt="Logo Busca Bula"
            id="logo_buscabula"
        >

        <div class="buttons_header">
            <button id="acessibility" aria-label="Acessibilidade">
                <PersonStanding :size="30" :stroke-width="1.8" />
            </button>

            |

            <button id="ajuda">Ajuda</button>
        </div>
    </header>
</template>

<style scoped>
header {
    display: flex;
    width: 100%;
    justify-content: space-between;
    background-color: white;
}

#logo_buscabula {
    width: 230px;
    margin-left: 70px;
}

#logo_organizacao {
    max-width: 230px;
    max-height: 56px;
    margin: 12px 0 12px 70px;
    object-fit: contain;
}

.buttons_header {
    margin-right: 70px;
    display: flex;
    align-items: center;
    gap: 15px;
}

#acessibility {
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: 50%;
    border: 2px solid var(--brand-secondary, #174563);
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
}

#ajuda {
    border-radius: 30px;
    font-size: 14px;
    border: 1.5px solid var(--brand-secondary, #174563);
    background: white;
    padding: 10px;
}

button {
    color: var(--brand-secondary, #174563);
    cursor: pointer;
}
</style>
