<script setup>
    import Header from '../components/header.vue'
    import logo2 from '../assets/images/Logo2.png' 
    import icone from '../assets/images/icone.png'
    import {Mail, LockKeyhole } from 'lucide-vue-next'; 
</script>

<template>
    <Header></Header>

    <main>
        <div class="login-card">

            <section class="login-info">
                <img :src="logo2" alt="Busca Bula" id="logo_login">

                <h2>Acesse suas bulas<br>de forma rápida e segura.</h2>

                <p>
                    Encontre informações oficiais sobre
                    medicamentos em poucos cliques.
                </p>

                <img :src="icone" alt="iconelogin" id="iconeLogin">
            </section>

            <section class="login-form">
                <h2>Entrar</h2>
                <p class="subtitle">Informe seu e-mail para acessar sua conta.</p>

                <form>
                    <div class="form-group">
                        <label for="email">E-mail</label>
                        <div class="input-container">
                            <icon-placeholder><Mail :size="17" :stroke-width="1.8" /></icon-placeholder>
                            <input
                                type="email"
                                id="email"
                                placeholder="Digite seu e-mail"
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
                                placeholder="Digite sua senha"
                            >
                        </div>
                    </div>

                    <button type="submit" id="btn-entrar">
                        Entrar <span>→</span>
                    </button>
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

/*MAIN*/

main {
    height: calc(100vh - 50px);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    box-sizing: border-box;
    overflow: hidden;
}

/* Quadrado do login */
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

/* Lado esquerdo */
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

#iconeLogin{
    width: 230px;
}

.login-info h2 {
    color: #174563;
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

/* Lado direito */

icon-placeholder{
    color: rgb(70, 66, 66);
}

.login-form {
    padding: 30px;
    background-color: #FFFFFF;
}

.login-form h2 {
    color: #174563;
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
    color: #174563;
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
    color: #174563;
    background: transparent;
}

.input-container input::placeholder {
    color: #9AAFC0;
}

/* Botão Entrar */
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
    background-color: #0DA99F;
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
}

#btn-entrar:hover {
    background-color: #0B968E;
}

/* Adaptação para telas menores */
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
