<script setup>
    import Header from '../components/header.vue'
    import logo from '../assets/images/Logo.png'
    import icone from '../assets/images/icone.png'
    import {UserRound,CalendarDays,VenusAndMars,Mail,Phone,MapPin,Building2,Map,LockKeyhole,Eye,EyeOff
    } from 'lucide-vue-next';

    import { ref } from 'vue'

    const mostrarSenha = ref(false)
</script>

<template>
    <Header></Header>

    <main>
        <div class="register-card">

            <section class="register-info">
                <img :src="logo" alt="Busca Bula" id="logo_Register">

                <h2>Tenha acesso rápido<br>e seguro às bulas de<br>medicamentos.</h2>

                <p>
                    Cadastre-se para consultar informações<br>oficiais da ANVISA de forma simples,<br>
                    rápida e confiável.
                </p>

                <img :src="icone" alt="iconeRegister" id="iconeRegister">
            </section>

            <!-- Lado direito: cadastro -->
            <section class="register-form">
                <h2>Criar conta</h2>
                <p class="subtitle">
                    Preencha os dados abaixo para começar a usar o Busca Bula.
                </p>

                <form @submit.prevent>

                    <!-- Nome completo e idade -->
                    <div class="form-row">
                        <div class="form-group">
                            <label for="nome">Nome completo</label>
                            <div class="input-container">
                                <UserRound :size="16" />
                                <input
                                    type="text"
                                    id="nome"
                                    placeholder="Digite seu nome completo"
                                    required
                                >
                            </div>
                        </div>

                        <div class="form-group idade">
                            <label for="idade">Idade</label>
                            <div class="input-container">
                                <CalendarDays :size="16" />
                                <input
                                    type="number"
                                    id="idade"
                                    placeholder="Ex.: 25"
                                    min="1"
                                    max="120"
                                    required
                                >
                            </div>
                        </div>
                    </div>

                    <!-- Sexo -->
                    <div class="form-group">
                        <label for="sexo">Sexo</label>
                        <div class="input-container">
                            <VenusAndMars :size="16" />
                            <select id="sexo" required>
                                <option value="" disabled selected>
                                    Selecione seu sexo
                                </option>
                                <option value="feminino">Feminino</option>
                                <option value="masculino">Masculino</option>
                                <option value="outro">Outro</option>
                                <option value="nao-informar">Prefiro não informar</option>
                            </select>
                        </div>
                    </div>

                    <!-- E-mail e celular -->
                    <div class="form-row">
                        <div class="form-group">
                            <label for="email">E-mail</label>
                            <div class="input-container">
                                <Mail :size="16" />
                                <input
                                    type="email"
                                    id="email"
                                    placeholder="Digite seu e-mail"
                                    required
                                >
                            </div>
                        </div>

                        <div class="form-group celular">
                            <label for="celular">Celular</label>
                            <div class="input-container">
                                <Phone :size="16" />
                                <input
                                    type="tel"
                                    id="celular"
                                    placeholder="(11) 91234-5678"
                                    required
                                >
                            </div>
                        </div>
                    </div>

                    <!-- Endereço -->
                    <div class="form-group">
                        <label for="endereco">Endereço</label>
                        <div class="input-container">
                            <MapPin :size="16" />
                            <input
                                type="text"
                                id="endereco"
                                placeholder="Digite seu endereço completo"
                                required
                            >
                        </div>
                    </div>

                    <!-- Cidade e estado -->
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cidade">Cidade</label>
                            <div class="input-container">
                                <Building2 :size="16" />
                                <input
                                    type="text"
                                    id="cidade"
                                    placeholder="Digite sua cidade"
                                    required
                                >
                            </div>
                        </div>

                        <div class="form-group estado">
                            <label for="estado">Estado</label>
                            <div class="input-container">
                                <Map :size="16" />
                                <select id="estado" required>
                                    <option value="" disabled selected>
                                        Selecione seu estado
                                    </option>
                                    <option value="AC">Acre</option>
                                    <option value="AL">Alagoas</option>
                                    <option value="AP">Amapá</option>
                                    <option value="AM">Amazonas</option>
                                    <option value="BA">Bahia</option>
                                    <option value="CE">Ceará</option>
                                    <option value="DF">Distrito Federal</option>
                                    <option value="ES">Espírito Santo</option>
                                    <option value="GO">Goiás</option>
                                    <option value="MA">Maranhão</option>
                                    <option value="MT">Mato Grosso</option>
                                    <option value="MS">Mato Grosso do Sul</option>
                                    <option value="MG">Minas Gerais</option>
                                    <option value="PA">Pará</option>
                                    <option value="PB">Paraíba</option>
                                    <option value="PR">Paraná</option>
                                    <option value="PE">Pernambuco</option>
                                    <option value="PI">Piauí</option>
                                    <option value="RJ">Rio de Janeiro</option>
                                    <option value="RN">Rio Grande do Norte</option>
                                    <option value="RS">Rio Grande do Sul</option>
                                    <option value="RO">Rondônia</option>
                                    <option value="RR">Roraima</option>
                                    <option value="SC">Santa Catarina</option>
                                    <option value="SP">São Paulo</option>
                                    <option value="SE">Sergipe</option>
                                    <option value="TO">Tocantins</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Senha -->
                    <div class="form-group">
                        <label for="senha">Senha</label>
                        <div class="input-container">
                            <LockKeyhole :size="16" />
                            <input
                                :type="mostrarSenha ? 'text' : 'password'"
                                id="senha"
                                placeholder="Crie uma senha"
                                minlength="8"
                                required
                            >
                            <button
                                type="button"
                                class="toggle-senha"
                                @click="mostrarSenha = !mostrarSenha"
                                :aria-label="mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'"
                            >
                                <Eye v-if="!mostrarSenha" :size="16" />
                                <EyeOff v-else :size="16" />
                            </button>
                        </div>
                    </div>

                    <!-- Botão cadastrar -->
                    <button type="submit" id="btn-entrar">
                        Cadastrar <span>→</span>
                    </button>

                    <p class="login-link">
                        Já tem uma conta? <a href="/login">Entrar</a>
                    </p>

                </form>
            </section>

        </div>
    </main>
</template>

<style scoped>

:global(body) {
    margin: 0;
    min-height: 110vh;
    background-color: #F1F6F9;

    background-image:
        radial-gradient(
            circle 180px at 100% 0%,
            #DDF3F2 99%,
            transparent 100%
        ),
        radial-gradient(
            circle 250px at 0% 100%,
            #DDF3F2 99%,
            transparent 100%
        );

    background-attachment: fixed;
    background-repeat: no-repeat;
}

main {
    height: calc(110vh - 50px);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    box-sizing: border-box;
    overflow: hidden;
}

/* Quadrado do register */
.register-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
    width: 880px;
    height: 580px;
    background-color: white;
    border: 1px solid #E1EAF0;
    border-radius: 9px;
    overflow: hidden;
    box-shadow: rgba(17, 12, 46, 0.15) 0px 48px 100px 0px;
    font-family: Arial, Helvetica, sans-serif;
    margin-top: auto;
    margin-bottom: auto;
}

/* Lado esquerdo */
.register-info {
    padding: 30px 25px;
    background-color: #F1F6F9;
    display: flex;
    flex-direction: column;
}

#logo_Register {
    width: 300px;
    height: auto;
    display: block;
    margin-bottom: 18px;
    margin-left: 40px;
}

#iconeRegister {
    width: 350px;
}

.register-info h2 {
    color: #174563;
    font-size: 20px;
    line-height: 1.4;
    margin: 0 0 10px 50px;
}

.register-info p {
    color: #71879A;
    font-size: 13px;
    line-height: 1.5;
    margin: 0 0 10px 50px;
}

/* Lado direito - cadastro */
.register-form {
    padding: 22px 30px;
    background-color: #FFFFFF;
    min-width: 0;
}

.register-form h2 {
    color: #174563;
    font-size: 19px;
    margin: 2px 0 4px;
}

.subtitle {
    color: #71879A;
    font-size: 12px;
    margin: 0 0 15px;
}

.register-form form {
    display: flex;
    flex-direction: column;
}

.form-row {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 14px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-bottom: 11px;
    min-width: 0;
}

.form-group label {
    color: #174563;
    font-size: 11px;
    font-weight: 600;
}

.input-container {
    display: flex;
    align-items: center;
    gap: 8px;
    height: 38px;
    box-sizing: border-box;
    border: 1px solid #D7E1E8;
    border-radius: 7px;
    padding: 0 9px;
    color: #52738D;
    min-width: 0;
}

.input-container:focus-within {
    border-color: #0DA99F;
}

.input-container input,
.input-container select {
    flex: 1;
    width: 100%;
    min-width: 0;
    border: none;
    outline: none;
    padding: 0;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9px;
    color: #174563;
    background: transparent;
}

.input-container input::placeholder {
    color: #9AAFC0;
    font-size: 11px;
}

.input-container select {
    cursor: pointer;
}

.toggle-senha {
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    padding: 0;
    background: transparent;
    color: #71879A;
    cursor: pointer;
}

/* Botão Cadastrar */
#btn-entrar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    height: 32px;
    margin-top: 1px;
    padding: 0 15px;
    border: none;
    border-radius: 25px;
    background-color: #0DA99F;
    color: white;
    font-size: 10px;
    font-weight: 600;
    cursor: pointer;
}

#btn-entrar:hover {
    background-color: #0B968E;
}

.login-link {
    margin: 14px 0 0;
    text-align: center;
    color: #174563;
    font-size: 9px;
}

.login-link a {
    color: #0DA99F;
    text-decoration: none;
    font-weight: 600;
}

.login-link a:hover {
    text-decoration: underline;
}

/* Adaptação para telas menores */
@media (max-width: 650px) {
    main {
        height: auto;
        min-height: calc(100vh - 50px);
        padding: 20px 15px;
        overflow: visible;
    }

    .register-card {
        grid-template-columns: 1fr;
        width: 100%;
        max-width: 400px;
        height: auto;
    }

    .register-info,
    .register-form {
        padding: 25px;
    }

    .form-row {
        grid-template-columns: 1fr;
        gap: 0;
    }
}
</style>
