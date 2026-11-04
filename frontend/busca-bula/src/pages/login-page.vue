<script setup>
    import Header from '../components/header.vue'
    import logo2 from '../assets/images/Logo2.png' 
    import icone from '../assets/images/icone.png'
    import {Mail, LockKeyhole } from 'lucide-vue-next';
    import { computed, onMounted, ref } from 'vue'
    import { currentUserRole, isAuthenticated, loginUser, resolvePostLoginPath } from '../services/auth-service'
    import { extractErrorMessage } from '../services/http-client'
    import { loadCurrentOrganization } from '../services/organization-branding'
    import { isPlatformContext } from '../services/organization-context'

    const areaDaPlataforma = isPlatformContext()
    const email = ref('')
    const senha = ref('')
    const enviando = ref(false)
    const erro = ref('')
    const organizacao = ref(null)
    const organizacaoIndisponivel = ref(false)

    const subtitulo = computed(() => {
        if (areaDaPlataforma) return 'Área administrativa da plataforma Busca Bula.'
        if (organizacao.value) return `Informe seu e-mail para acessar sua conta ${organizacao.value.nome}.`
        return 'Informe seu e-mail para acessar sua conta.'
    })

    async function carregarOrganizacao() {
        try {
            organizacao.value = await loadCurrentOrganization()
        } catch (falha) {
            organizacaoIndisponivel.value = true
            erro.value = extractErrorMessage(falha, 'Não foi possível carregar a organização.')
        }
    }

    async function entrar() {
        erro.value = ''
        enviando.value = true
        try {
            const papel = await loginUser(email.value, senha.value)
            window.location.href = resolvePostLoginPath(papel)
        } catch (falha) {
            erro.value = extractErrorMessage(falha, 'Não foi possível entrar. Tente novamente.')
        } finally {
            enviando.value = false
        }
    }

    onMounted(() => {
        if (isAuthenticated()) {
            window.location.href = resolvePostLoginPath(currentUserRole())
            return
        }
        if (!areaDaPlataforma) carregarOrganizacao()
    })
</script>

<template>
    <Header></Header>

    <main>
        <div class="login-card">

            <section class="login-info">
                <img
                    v-if="organizacao?.logoUrl"
                    :src="organizacao.logoUrl"
                    :alt="organizacao.nome"
                    id="logo_organizacao"
                >
                <img v-else :src="logo2" alt="Busca Bula" id="logo_login">

                <h2>Acesse suas bulas<br>de forma rápida e segura.</h2>

                <p>
                    Encontre informações oficiais sobre
                    medicamentos em poucos cliques.
                </p>

                <img :src="icone" alt="iconelogin" id="iconeLogin">
            </section>

            <section class="login-form">
                <h2>Entrar</h2>
                <p class="subtitle">{{ subtitulo }}</p>

                <form @submit.prevent="entrar">
                    <div class="form-group">
                        <label for="email">E-mail</label>
                        <div class="input-container">
                            <icon-placeholder><Mail :size="17" :stroke-width="1.8" /></icon-placeholder>
                            <input
                                type="email"
                                id="email"
                                v-model="email"
                                placeholder="Digite seu e-mail"
                                autocomplete="email"
                                required
                            >
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="senha">Senha</label>
                        <div class="input-container">
                            <icon-placeholder><LockKeyhole :size="17" :stroke-width="1.8"/></icon-placeholder>
                            <input
                                type="password"
                                id="senha"
                                v-model="senha"
                                placeholder="Digite sua senha"
                                autocomplete="current-password"
                                required
                            >
                        </div>
                    </div>

                    <button type="submit" id="btn-entrar" :disabled="enviando || organizacaoIndisponivel">
                        {{ enviando ? 'Entrando...' : 'Entrar' }} <span>→</span>
                    </button>

                    <p v-if="erro" class="mensagem-erro" role="alert">{{ erro }}</p>

                    <p v-if="!areaDaPlataforma && !organizacaoIndisponivel" class="register-link">
                        Não tem uma conta? <a href="/register">Cadastre-se</a>
                    </p>
                </form>
            </section>

        </div>
    </main>
</template>

<style scoped>

:global(html),
:global(body),
:global(#app) {
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
}

:global(body) {
    background-color: #F1F6F9;
    margin: 0;

}


main {
    height: calc(100vh - 50px);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    box-sizing: border-box;
    overflow: hidden;
}

.login-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
    width: 700px;
    min-height: 450px;
    background-color: white;
    border: 1px solid #E1EAF0;
    border-radius: 9px;
    overflow: hidden;
    box-shadow: rgba(17, 12, 46, 0.15) 0px 48px 100px 0px;
    font-family: Arial, Helvetica, sans-serif;
}

.login-info {
    padding: 30px 25px;
    background-color: #F1F6F9;
}

#logo_login {
    width: 200px;
    height: auto;
    display: block;
    margin-bottom: 18px;
}

#logo_organizacao {
    display: block;
    max-width: 200px;
    max-height: 90px;
    margin-bottom: 18px;
    object-fit: contain;
}

#iconeLogin{
    width: 230px;
}

.login-info h2 {
    color: var(--brand-secondary, #174563);
    font-size: 17px;
    line-height: 1.4;
    margin: 0 0 10px;
}

.login-info p {
    color: #71879A;
    font-size: 13px;
    line-height: 1.5;
    margin: 0;
}


icon-placeholder{
    color: rgb(70, 66, 66);
}

.login-form {
    padding: 30px;
    background-color: #FFFFFF;
}

.login-form h2 {
    color: var(--brand-secondary, #174563);
    font-size: 21px;
    margin: 3px 0 8px;
}

.subtitle {
    color: #71879A;
    font-size: 13px;
    margin: 0 0 25px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 18px;
}

.form-group label {
    color: var(--brand-secondary, #174563);
    font-size: 13px;
    font-weight: 600;
}

.input-container {
    display: flex;
    align-items: center;
    height: 37px;
    border: 1px solid #D7E1E8;
    border-radius: 7px;
    padding: 0 10px;
}

.input-container input {
    width: 100%;
    min-width: 0;
    border: none;
    outline: none;
    padding: 8px;
    font-size: 11px;
    color: var(--brand-secondary, #174563);
    background: transparent;
}

.input-container input::placeholder {
    color: #9AAFC0;
}

#btn-entrar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    height: 37px;
    margin-top: 25px;
    padding: 0 15px;
    border: none;
    border-radius: 25px;
    background-color: var(--brand-primary, #0DA99F);
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
}

#btn-entrar:hover {
    background-color: var(--brand-primary-dark, #0B968E);
}

#btn-entrar:disabled {
    background-color: #9AAFC0;
    cursor: not-allowed;
}

.mensagem-erro {
    margin: 14px 0 0;
    text-align: center;
    color: #D64545;
    font-size: 12px;
}

.register-link {
    margin: 16px 0 0;
    text-align: center;
    color: var(--brand-secondary, #174563);
    font-size: 12px;
}

.register-link a {
    color: var(--brand-primary, #0DA99F);
    text-decoration: none;
    font-weight: 600;
}

.register-link a:hover {
    text-decoration: underline;
}

@media (max-width: 650px) {
    main {
        padding: 35px 15px;
    }

    .login-card {
        grid-template-columns: 1fr;
        width: 100%;
        max-width: 400px;
    }

    .login-info,
    .login-form {
        padding: 25px;
    }
}

</style>
