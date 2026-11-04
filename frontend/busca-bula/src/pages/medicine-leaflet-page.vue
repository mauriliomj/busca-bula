<script setup>
import { ref } from 'vue'

const query = ref('')

const navItems = [
  { label: 'Início', href: '#', active: true },
  { label: 'Sobre', href: '#sobre' },
  { label: 'Ajuda', href: '#ajuda' },
  { label: 'Contato', href: '#contato' }
]

const examples = ['Paracetamol', 'Dipirona', 'Amoxicilina', 'Losartana']

const features = [
  { icon: 'i-bolt', title: 'Busca rápida', text: 'Encontre a bula que precisa em poucos cliques.' },
  { icon: 'i-shield', title: 'Fontes oficiais', text: 'Informações da ANVISA e órgãos reguladores.' },
  { icon: 'i-access', title: 'Acessível para todos', text: 'Texto claro, linguagem simples e fácil de entender.' },
  { icon: 'i-device', title: 'Em qualquer lugar', text: 'Acesse pelo computador, tablet ou celular.' }
]

const topMedicines = ['Paracetamol', 'Dipirona', 'Amoxicilina', 'Losartana']

const socials = [
  { label: 'Instagram', href: '#', icon: 'i-instagram' },
  { label: 'YouTube', href: '#', icon: 'i-video' },
  { label: 'Vídeos', href: '#', icon: 'i-video' }
]

function search() {
  const term = query.value.trim()
  if (!term) return
  // TODO: integrar com a API / router (ex.: router.push({ path: '/medicamentos', query: { q: term } }))
  console.log('Buscar:', term)
}

function useExample(name) {
  query.value = name
  search()
}
</script>

<template>
  <div class="page">
    <!-- SVG sprite -->
    <svg width="0" height="0" style="position:absolute" aria-hidden="true">
      <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
      <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
      <symbol id="i-chev" viewBox="0 0 24 24"><path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
      <symbol id="i-pill" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2.5" y="8.5" width="19" height="7" rx="3.5" transform="rotate(-45 12 12)"/><path d="m9 9 6 6"/></g></symbol>
      <symbol id="i-user" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></g></symbol>
      <symbol id="i-access" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.5" r="1.8"/><path d="M5 8.5c4.7 1.5 9.3 1.5 14 0M12 9v5m0 0-3.5 7M12 14l3.5 7"/></g></symbol>
      <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2 5 13.5h6L10 22l9-12h-6.2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></symbol>
      <symbol id="i-shield" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.6 3.1 8.2 7.5 9.5 4.4-1.3 7.5-4.9 7.5-9.5V6z"/><path d="m8.8 12 2.4 2.4 4-4.6"/></g></symbol>
      <symbol id="i-device" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="4" width="14" height="10" rx="1.5"/><path d="M6.5 19h6M9.5 14v5"/><rect x="15.5" y="9" width="6" height="11" rx="1.5"/></g></symbol>
      <symbol id="i-instagram" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/></g><circle cx="17.3" cy="6.7" r=".8" fill="currentColor"/></symbol>
      <symbol id="i-video" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="m10 9.5 5 2.5-5 2.5z" fill="currentColor"/></symbol>
      <symbol id="i-logo" viewBox="0 0 48 48"><rect x="14" y="4" width="28" height="36" rx="4" fill="#0f9e94"/><rect x="18" y="8" width="20" height="28" rx="2" fill="#d9f1ee"/><circle cx="20" cy="26" r="11" fill="#fff" stroke="#123a5c" stroke-width="3.5"/><path d="M13 34 5 43" stroke="#123a5c" stroke-width="4.5" stroke-linecap="round"/><path d="M15.5 22h9M15.5 26h9M15.5 30h6" stroke="#0f9e94" stroke-width="2.2" stroke-linecap="round"/></symbol>
    </svg>

    <!-- Header -->
    <header class="header">
      <div class="container header-inner">
        <a href="#" class="logo" aria-label="Busca Bula – início">
          <svg width="52" height="52"><use href="#i-logo" /></svg>
          <div>Busca <span>Bula</span></div>
        </a>

        <nav aria-label="Navegação principal">
          <ul>
            <li v-for="item in navItems" :key="item.label">
              <a :href="item.href" :aria-current="item.active ? 'page' : undefined">{{ item.label }}</a>
            </li>
          </ul>
        </nav>

        <div class="header-actions">
          <button class="icon-btn" type="button" aria-label="Opções de acessibilidade">
            <svg width="24" height="24"><use href="#i-access" /></svg>
          </button>
          <a href="/login" class="btn-login">
            <svg width="18" height="18"><use href="#i-user" /></svg>Acessar
          </a>
        </div>
      </div>
    </header>

    <main>
      <!-- Hero -->
      <section class="hero">
        <div class="container hero-inner">
          <div>
            <h1>Encontre a bula do seu medicamento <em>em segundos</em></h1>
            <p class="lead">
              O <strong>Busca Bula</strong> é uma plataforma digital que facilita o acesso às bulas de medicamentos,
              com informações oficiais da ANVISA, de forma rápida, simples e segura.
            </p>

            <form class="search" role="search" @submit.prevent="search">
              <svg class="lens" width="22" height="22"><use href="#i-search" /></svg>
              <input
                v-model="query"
                type="search"
                placeholder="Digite o nome do medicamento ou princípio ativo..."
                aria-label="Buscar medicamento ou princípio ativo"
              />
              <button type="submit">
                <svg width="22" height="22"><use href="#i-search" /></svg>Buscar
              </button>
            </form>

            <div class="examples">
              <span>Exemplos:</span>
              <a v-for="name in examples" :key="name" href="#" @click.prevent="useExample(name)">{{ name }}</a>
            </div>
          </div>

          <div class="hero-art">
            <svg class="art" viewBox="0 0 300 300" role="img" aria-label="Ilustração de uma bula com lupa">
              <path d="M60 70c10-40 70-60 110-40 40 18 90 20 115 60 25 42 0 90-40 120-40 32-100 40-140 15-40-26-60-60-60-90 0-25 5-45 15-65z" fill="#c9ece8" opacity=".75" />
              <path d="M70 55h110l35 35v135a12 12 0 0 1-12 12H70a12 12 0 0 1-12-12V67a12 12 0 0 1 12-12z" fill="#123a5c" />
              <rect x="76" y="73" width="110" height="130" rx="3" fill="#f3fafa" />
              <g fill="#4d7aa0"><rect x="88" y="88" width="70" height="7" rx="3" /><rect x="88" y="108" width="90" height="7" rx="3" /><rect x="88" y="126" width="60" height="7" rx="3" /><rect x="88" y="144" width="80" height="7" rx="3" /><rect x="88" y="162" width="56" height="7" rx="3" /></g>
              <circle cx="190" cy="150" r="48" fill="#fff" stroke="#123a5c" stroke-width="12" />
              <circle cx="190" cy="150" r="36" fill="#c9ece8" />
              <path d="M176 135a22 22 0 0 1 20-8" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" />
              <path d="m228 188 40 44" stroke="#123a5c" stroke-width="14" stroke-linecap="round" />
            </svg>
            <p>Informação confiável para cuidar melhor da sua saúde.</p>
          </div>
        </div>
      </section>

      <!-- Diferenciais -->
      <section class="features" aria-label="Diferenciais">
        <div class="container">
          <ul>
            <li v-for="f in features" :key="f.title">
              <div class="feat-icon"><svg width="28" height="28"><use :href="'#' + f.icon" /></svg></div>
              <h3>{{ f.title }}</h3>
              <p>{{ f.text }}</p>
            </li>
          </ul>
        </div>
      </section>

      <!-- Mais buscados -->
      <section class="top" aria-labelledby="top-title">
        <div class="container">
          <div class="section-head">
            <h2 id="top-title">Medicamentos mais buscados</h2>
            <a href="#" class="see-all">Ver todos <svg width="16" height="16"><use href="#i-arrow" /></svg></a>
          </div>
          <ul class="med-grid">
            <li v-for="med in topMedicines" :key="med">
              <a class="med" href="#">
                <span class="med-icon"><svg width="24" height="24"><use href="#i-pill" /></svg></span>
                <span class="med-info"><strong>{{ med }}</strong><small>(princípio ativo)</small></span>
                <svg class="chev" width="16" height="16"><use href="#i-chev" /></svg>
              </a>
            </li>
          </ul>
        </div>
      </section>

      <!-- Informação é um cuidado -->
      <section class="info" id="sobre">
        <div class="container">
          <div class="info-box">
            <svg class="art" width="170" height="150" viewBox="0 0 170 150" aria-hidden="true">
              <circle cx="70" cy="80" r="62" fill="#d4efec" />
              <rect x="30" y="10" width="86" height="116" rx="8" fill="#123a5c" />
              <rect x="37" y="18" width="72" height="100" rx="3" fill="#f3fafa" />
              <g fill="#4d7aa0"><rect x="46" y="32" width="46" height="7" rx="3" /><rect x="46" y="50" width="56" height="7" rx="3" /><rect x="46" y="68" width="40" height="7" rx="3" /><rect x="46" y="86" width="50" height="7" rx="3" /></g>
              <path d="M122 62h38v38c0 20-14 32-19 36-5-4-19-16-19-36z" fill="#0f9e94" transform="translate(-2 -4)" />
              <path d="m131 96 8 8 14-16" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <div>
              <h2>Informação é um cuidado</h2>
              <p>
                O <strong>Busca Bula</strong> oferece acesso às bulas de medicamentos com base em fontes <strong>oficiais</strong>,
                como a ANVISA. Nosso objetivo é facilitar o acesso à informação, contribuindo para o uso mais seguro e consciente dos medicamentos.
              </p>
              <p class="note">
                O Busca Bula tem caráter informativo e não substitui a orientação de médicos, farmacêuticos ou outros profissionais de saúde.
              </p>
            </div>
            <a href="#" class="btn-outline">Saiba mais <svg width="18" height="18"><use href="#i-arrow" /></svg></a>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer id="contato">
      <div class="container">
        <div class="footer-grid">
          <div>
            <a href="#" class="logo"><svg width="42" height="42"><use href="#i-logo" /></svg><div>Busca <span>Bula</span></div></a>
            <p class="tagline">Informação que faz a diferença.</p>
          </div>

          <ul class="footer-links" id="ajuda">
            <li v-for="item in navItems" :key="item.label"><a :href="item.href">{{ item.label }}</a></li>
          </ul>

          <div>
            <h4>Fontes oficiais</h4>
            <div class="anvisa">
              <svg width="38" height="34" viewBox="0 0 38 34" aria-hidden="true"><g stroke="#fff" stroke-width="2.5" stroke-linecap="round" fill="none"><path d="M2 12h34M2 22h34M19 2v30" /><path d="M8 6l22 22M30 6 8 28" opacity=".5" /></g></svg>
              <div><strong>ANVISA</strong><small>Agência Nacional de Vigilância Sanitária</small></div>
            </div>
            <a class="anvisa-link" href="https://www.gov.br/anvisa" target="_blank" rel="noopener">
              Acesse o site da ANVISA <svg width="13" height="13"><use href="#i-arrow" /></svg>
            </a>
          </div>

          <div>
            <h4>Siga-nos</h4>
            <div class="socials">
              <a v-for="s in socials" :key="s.label + s.icon" :href="s.href" :aria-label="s.label">
                <svg width="16" height="16"><use :href="'#' + s.icon" /></svg>
              </a>
            </div>
          </div>
        </div>

        <div class="copy">
          <span>© 2025 Busca Bula. Todos os direitos reservados.</span>
          <span>Projeto acadêmico | Fatec de Cotia</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
</style>

<style scoped>
.page {
  --navy: #123a5c;
  --navy-dark: #16384f;
  --teal: #0f9e94;
  --teal-dark: #0b857c;
  --mint: #d9f1ee;
  --bg-soft: #eef7f8;
  --bg-light: #f7fbfc;
  --text: #2b4a63;
  --muted: #6b8497;
  --line: #dfe9ee;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  color: var(--text);
  background: #fff;
  line-height: 1.5;
}
.page *, .page *::before, .page *::after { box-sizing: border-box; margin: 0; padding: 0; }
.page a { color: inherit; text-decoration: none; }
.page ul { list-style: none; }
.page svg { display: block; }
.page :focus-visible { outline: 3px solid var(--teal); outline-offset: 3px; border-radius: 6px; }
.container { width: min(1100px, 100% - 48px); margin-inline: auto; }

/* Header */
.header { background: #fff; position: sticky; top: 0; z-index: 10; box-shadow: 0 1px 0 var(--line); }
.header-inner { display: flex; align-items: center; justify-content: space-between; height: 74px; gap: 24px; }
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.65rem; color: var(--navy); letter-spacing: -.02em; }
.logo span { color: var(--teal); }
nav ul { display: flex; gap: 34px; }
nav a { font-size: .9rem; font-weight: 500; color: var(--navy); padding: 8px 0; border-bottom: 2px solid transparent; }
nav a[aria-current='page'] { font-weight: 700; border-color: var(--teal); }
nav a:hover { color: var(--teal); }
.header-actions { display: flex; align-items: center; gap: 18px; }
.icon-btn { width: 38px; height: 38px; border-radius: 50%; border: 2px solid var(--navy); background: none; color: var(--navy); display: grid; place-items: center; cursor: pointer; }
.btn-login { display: inline-flex; align-items: center; gap: 10px; background: var(--navy); color: #fff !important; font-weight: 600; font-size: .88rem; padding: 11px 26px; border-radius: 999px; transition: background .2s; }
.btn-login:hover { background: #0c2b46; }

/* Hero */
.hero { background: var(--bg-soft); padding: 56px 0 50px; }
.hero-inner { display: grid; grid-template-columns: 1.25fr 1fr; gap: 40px; align-items: center; }
.hero h1 { font-size: clamp(2rem, 4vw, 2.7rem); line-height: 1.12; font-weight: 800; color: var(--navy); letter-spacing: -.03em; margin-bottom: 18px; }
.hero h1 em { font-style: normal; color: var(--teal); }
.lead { font-size: .98rem; max-width: 460px; color: var(--navy-dark); margin-bottom: 34px; }
.search { display: flex; align-items: center; background: #fff; border-radius: 999px; box-shadow: 0 6px 22px rgba(18, 58, 92, .08); border: 1px solid var(--line); overflow: hidden; max-width: 650px; }
.search .lens { margin-left: 22px; flex: none; color: var(--muted); }
.search input { flex: 1; border: 0; outline: 0; font: inherit; font-size: .95rem; padding: 18px 14px; color: var(--navy); background: transparent; min-width: 0; }
.search input::placeholder { color: #8aa0b0; }
.search:focus-within { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(15, 158, 148, .2); }
.search button { display: inline-flex; align-items: center; gap: 10px; background: var(--teal); color: #fff; border: 0; font: inherit; font-weight: 700; font-size: .95rem; padding: 18px 36px; border-radius: 999px; cursor: pointer; transition: background .2s; }
.search button:hover { background: var(--teal-dark); }
.examples { margin-top: 20px; display: flex; flex-wrap: wrap; align-items: center; font-size: .85rem; gap: 4px 0; }
.examples span { margin-right: 12px; }
.examples a { padding: 0 14px; border-left: 1px solid #b8cad6; color: var(--navy); }
.examples a:first-of-type { border-left: 0; padding-left: 0; }
.examples a:hover { color: var(--teal); }
.hero-art { display: flex; align-items: center; gap: 18px; justify-content: flex-end; }
.hero-art .art { flex: none; width: min(300px, 100%); height: auto; }
.hero-art p { font-size: .95rem; max-width: 110px; line-height: 1.6; }
.hero-art p::after { content: ''; display: block; width: 36px; height: 3px; background: var(--teal); margin-top: 14px; border-radius: 2px; }

/* Features */
.features { padding: 48px 0 54px; border-bottom: 1px solid var(--line); }
.features ul { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; text-align: center; }
.feat-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--teal); color: #fff; display: grid; place-items: center; margin: 0 auto 18px; }
.features h3 { font-size: 1.05rem; color: var(--navy); margin-bottom: 10px; font-weight: 700; }
.features p { font-size: .85rem; color: var(--muted); max-width: 190px; margin-inline: auto; }

/* Mais buscados */
.top { background: var(--bg-light); padding: 40px 0 44px; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; }
.section-head h2 { font-size: 1.5rem; color: var(--navy); font-weight: 800; letter-spacing: -.02em; }
.see-all { color: var(--teal) !important; font-weight: 600; font-size: .85rem; display: inline-flex; align-items: center; gap: 6px; }
.see-all:hover { text-decoration: underline !important; }
.med-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.med { display: flex; align-items: center; gap: 16px; background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 16px 20px; transition: border-color .2s, box-shadow .2s; }
.med:hover { border-color: var(--teal); box-shadow: 0 6px 18px rgba(18, 58, 92, .08); }
.med-icon { width: 42px; height: 42px; border-radius: 50%; background: var(--mint); color: var(--teal); display: grid; place-items: center; flex: none; }
.med-info { flex: 1; min-width: 0; }
.med-info strong { display: block; font-size: .9rem; color: var(--navy); }
.med-info small { font-size: .72rem; color: var(--muted); }
.med .chev { color: var(--navy); }

/* Info */
.info { padding: 34px 0 44px; }
.info-box { background: var(--bg-soft); border-radius: 18px; padding: 34px 40px; display: grid; grid-template-columns: 200px 1fr auto; gap: 36px; align-items: center; }
.info-box h2 { font-size: 1.35rem; color: var(--navy); font-weight: 800; margin-bottom: 10px; }
.info-box p { font-size: .88rem; color: var(--navy-dark); max-width: 520px; }
.info-box p.note { color: var(--muted); margin-top: 14px; }
.btn-outline { display: inline-flex; align-items: center; gap: 12px; border: 1.5px solid var(--teal); color: var(--teal) !important; font-weight: 600; font-size: .95rem; padding: 14px 34px; border-radius: 999px; transition: all .2s; }
.btn-outline:hover { background: var(--teal); color: #fff !important; }

/* Footer */
footer { background: var(--navy-dark); color: #fff; padding: 36px 0 22px; }
footer .logo { color: #fff; font-size: 1.35rem; }
footer .logo span { color: #3cd3c6; }
.tagline { font-size: .75rem; margin-top: 4px; color: #d3e0e8; }
.footer-grid { display: grid; grid-template-columns: 1.2fr .8fr 1.2fr .8fr; gap: 30px; align-items: start; padding-bottom: 26px; border-bottom: 1px solid rgba(255, 255, 255, .18); }
.footer-grid h4 { font-size: .75rem; font-weight: 700; margin-bottom: 12px; }
.footer-links li { margin-bottom: 10px; font-size: .82rem; color: #d3e0e8; }
.footer-links a:hover, .anvisa-link:hover { color: #3cd3c6; }
.anvisa { display: flex; align-items: center; gap: 12px; }
.anvisa strong { display: block; font-size: .85rem; }
.anvisa small { font-size: .62rem; color: #d3e0e8; }
.anvisa-link { display: inline-flex; align-items: center; gap: 6px; font-size: .7rem; margin-top: 14px; color: #fff; }
.socials { display: flex; gap: 14px; }
.socials a { width: 30px; height: 30px; border-radius: 50%; background: rgba(255, 255, 255, .14); color: #fff; display: grid; place-items: center; transition: background .2s; }
.socials a:hover { background: var(--teal); }
.copy { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; font-size: .72rem; color: #c5d4de; padding-top: 18px; }

/* Responsivo */
@media (max-width: 960px) {
  nav ul { gap: 18px; }
  .hero-inner { grid-template-columns: 1fr; }
  .hero-art { justify-content: center; }
  .features ul, .med-grid { grid-template-columns: repeat(2, 1fr); }
  .info-box { grid-template-columns: 1fr; justify-items: start; }
  .info-box .art { width: 140px; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  nav { display: none; }
  .header-inner { height: 64px; }
  .btn-login { padding: 10px 18px; }
  .search { flex-direction: column; border-radius: 20px; align-items: stretch; }
  .search .lens { display: none; }
  .search input { padding: 16px 20px; }
  .search button { justify-content: center; border-radius: 0 0 20px 20px; }
  .features ul, .med-grid, .footer-grid { grid-template-columns: 1fr; }
  .hero-art p { max-width: none; }
  .info-box { padding: 26px 22px; }
  .section-head { flex-wrap: wrap; gap: 8px; }
}
@media (prefers-reduced-motion: reduce) {
  .page * { transition: none !important; }
}
</style>