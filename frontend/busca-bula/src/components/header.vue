<script setup>
import logo from '../assets/images/Logo.png'
import { PersonStanding } from 'lucide-vue-next'
</script>

<template>
    <header>
        <img
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
    border: 2px solid #174563;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
}

#ajuda {
    border-radius: 30px;
    font-size: 14px;
    border: 1.5px solid #174563;
    background: white;
    padding: 10px;
}

button {
    color: #174563;
    cursor: pointer;
}
</style>
