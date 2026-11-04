# Busca Bula

Projeto com backend em FastAPI (SQLAlchemy + Alembic), frontend em Vue 3 + Vite e banco PostgreSQL com a extensão pgvector. Tudo roda dentro de containers Docker.

O Busca Bula é multitenant: cada organização (farmácia, plano de saúde) acessa o app pelo seu próprio subdomínio e tem um banco de dados exclusivo.

## Requisitos

Nenhum. Os scripts de inicialização verificam se o Docker está instalado e, se não estiver, instalam automaticamente:

- **Linux:** instala o Docker Engine e o Docker Compose (Ubuntu, Debian, Fedora, CentOS, Arch, openSUSE e derivados). Vai pedir a senha do `sudo`.
- **Windows 10/11:** instala o WSL 2 e o Docker Desktop pelo `winget`. O Windows vai pedir permissão de administrador.

É preciso ter conexão com a internet na primeira execução.

## Como usar

### Linux

Na pasta do projeto, abra um terminal e rode:

```bash
./start.sh
```

Para parar:

```bash
./stop.sh
```

Se aparecer "permissão negada", rode com `bash start.sh` / `bash stop.sh`.

### Windows

Dê dois cliques em **`start.bat`** (ou rode `start.bat` no Prompt de Comando / PowerShell).

Para parar, dê dois cliques em **`stop.bat`**.

> Na primeira vez em que o Docker for instalado, o Windows pode pedir para reiniciar o computador. Depois de reiniciar, rode o `start.bat` de novo. Também pode ser necessário aceitar os termos de uso do Docker Desktop na primeira vez em que ele abrir.

## O que os scripts fazem

### start (`start.sh` / `start.bat`)

1. Verifica se o Docker está instalado e instala caso não esteja.
2. Inicia o serviço do Docker (ou abre o Docker Desktop no Windows) e espera ele ficar pronto.
3. Constrói as imagens do backend e do frontend **somente se ainda não existirem ou se as dependências mudaram** (`Dockerfile`, `requirements.txt`, `package.json` ou `package-lock.json`).
4. Sobe os containers (`docker compose up -d`). Ao iniciar, o backend aplica as migrations do banco da plataforma e de todas as organizações.
5. Espera o backend e o frontend responderem e abre o navegador.

A primeira execução demora alguns minutos e precisa de internet, porque as imagens são baixadas e as dependências instaladas. Nas próximas nada é baixado de novo: o script detecta o que já está instalado e só sobe os containers.

### stop (`stop.sh` / `stop.bat`)

Para e remove os containers. Os dados do banco **são mantidos** para a próxima vez.

Para apagar também os dados do banco e começar do zero:

```bash
./stop.sh --limpar        # Linux
stop.bat --limpar         # Windows
```

## Endereços

Com o projeto rodando:

| Serviço                    | Endereço                                  |
| -------------------------- | ----------------------------------------- |
| Painel da plataforma       | http://localhost:5173/login               |
| App de uma organização     | http://&lt;subdominio&gt;.localhost:5173/login |
| Backend (API)              | http://localhost:8000                     |
| Documentação da API        | http://localhost:8000/docs                |

O banco PostgreSQL fica acessível apenas entre os containers.

## Primeiro acesso

1. Crie o administrador da plataforma:

   ```bash
   docker compose exec backend python -m app.commands.create_platform_admin --name "Seu Nome" --email voce@email.com
   ```

   A senha é pedida no terminal (mínimo de 8 caracteres).

2. Entre em http://localhost:5173/login com esse e-mail e crie uma organização no painel, por exemplo com o subdomínio `farmaciax`.
3. Acesse http://farmaciax.localhost:5173/register para cadastrar um usuário dessa organização. O administrador informado na criação da organização entra por http://farmaciax.localhost:5173/login e cai no painel de membros (`/members`).

## Páginas por perfil

| Perfil                          | Onde entra                          | Páginas                                                   |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| Administrador da plataforma     | `localhost:5173/login`              | `/org`: organizações e identidade visual delas; `/org#catalogo`: catálogo ANVISA |
| Administrador da organização    | `<subdominio>.localhost:5173/login` | `/members`: membros e identidade visual da organização; `/user`: perfil |
| Membro                          | `<subdominio>.localhost:5173/login` | `/search` e `/medicine`: busca e detalhes; `/consultations`: histórico; `/user`: perfil |

Uma organização só pode ser excluída depois de desativada. A exclusão apaga o banco e o usuário PostgreSQL dela.

## Catálogo ANVISA

O catálogo junta três fontes públicas em um banco próprio (`busca_bula_catalog`), compartilhado por todas as organizações em modo somente leitura:

| Fonte | Arquivo | O que vira |
| ----- | ------- | ---------- |
| Medicamentos registrados (ANVISA) | `DADOS_ABERTOS_MEDICAMENTOS.csv` | `medicines`: um registro por número de registro |
| Índice de bulas (Bulário Eletrônico) | `TA_CONSULTA_BULA_PRODUTO.CSV` | `leaflets`: bula do paciente de cada registro |
| Preços CMED | `TA_PRECO_MEDICAMENTO.csv` | `medicine_presentations`: apresentações com EAN e preços por alíquota de ICMS |
| Textos das bulas do paciente ([ChatBulário](https://huggingface.co/datasets/walmeidadf/ChatBulario), CC BY 4.0) | `data/*.parquet` | `leaflet_documents` e `leaflet_sections`: texto das 9 seções da bula do paciente |

As três tabelas se ligam pelo número de registro de 9 dígitos (na tabela CMED, os 9 primeiros dígitos do registro da apresentação).

Para sincronizar, use o botão **Sincronizar agora** em `/org#catalogo` ou rode:

```bash
docker compose exec backend python -m app.commands.import_catalog
docker compose exec backend python -m app.commands.import_catalog --source prices
```

Os arquivos baixados ficam em cache no volume `catalog_cache`, e o download só se repete quando a ANVISA publica uma versão nova (`If-Modified-Since`). A primeira sincronização baixa cerca de 80 MB.

### Bulas: origem do texto

O Bulário Eletrônico (`consultas.anvisa.gov.br`) é protegido por um desafio Cloudflare Turnstile que bloqueia navegadores automatizados. O Busca Bula não contorna essa proteção. O texto das bulas vem de duas fontes:

1. **ChatBulário** ([dataset](https://huggingface.co/datasets/walmeidadf/ChatBulario) de walmeidadf, licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)): cerca de 7.900 bulas do paciente já separadas nas 9 seções da RDC 47/2009, importadas com o restante do catálogo. A atribuição aparece junto do texto em cada bula.
2. **Envio de PDF** em `/org#catalogo`: o administrador da plataforma baixa a bula do paciente no Bulário pelo próprio navegador e envia o PDF. O texto é extraído com `pdfplumber`, separado nas 9 seções e substitui o texto do dataset para aquele registro. Uma nova importação do dataset não sobrescreve bulas enviadas em PDF.

Quando o expediente da bula guardada é diferente do expediente atual no índice oficial da ANVISA, a bula aparece com o aviso de que existe uma versão mais recente.

Tabelas da bula original (por exemplo, dose por faixa de peso) perdem a estrutura na extração de texto e aparecem como uma linha por célula.

## Busca de medicamentos

A busca exige login no endereço da organização e aceita nome comercial, princípio ativo, classe terapêutica, número de registro ou o código de barras (EAN) da caixa. Acentos e maiúsculas são ignorados e, quando o termo exato não é encontrado, a busca mostra nomes parecidos (`pg_trgm`). Por padrão só aparecem registros ativos; buscas por registro ou código de barras mostram também os inativos.

O detalhe do medicamento mostra o registro na ANVISA, a situação da bula no Bulário Eletrônico e as apresentações da tabela CMED com o preço máximo ao consumidor. Como a alíquota de ICMS de medicamentos varia por estado, a pessoa escolhe qual alíquota aplicar.

### Histórico de consultas e LGPD

Os medicamentos consultados podem revelar informações de saúde, que a LGPD trata como dado pessoal sensível. Por isso o histórico fica desligado até a pessoa autorizar em **Minhas Consultas**. A data da autorização é registrada, o histórico fica no banco da organização, e desativá-lo, limpar o histórico ou excluir a conta apaga as consultas.

## Identidade visual

Cada organização pode ter logo (PNG, JPG, WEBP ou SVG, até 512 KB) e duas cores: a principal (botões, links e destaques) e a secundária (títulos). Sem personalização, o app usa as cores padrão do Busca Bula. A logo e as cores ficam no banco da própria organização e são aplicadas automaticamente em todas as páginas abertas pelo subdomínio dela.

Os navegadores atuais resolvem qualquer `*.localhost` para a própria máquina, então não é preciso configurar DNS em desenvolvimento.

## Isolamento entre organizações

| Banco                  | Conteúdo                                         | Acesso                                   |
| ---------------------- | ------------------------------------------------ | ---------------------------------------- |
| `busca_bula`           | organizações e administradores da plataforma     | backend                                  |
| `tenant_<subdominio>`  | usuários, identidade visual e histórico de consultas | somente o usuário `tenant_<subdominio>`  |
| `busca_bula_catalog`   | medicamentos, bulas e preços (dados públicos)    | `..._writer` grava (ETL); `..._reader` só lê |

- Cada organização tem um banco e um usuário PostgreSQL próprios, criados automaticamente pelo painel. O acesso público ao banco é revogado, então o usuário de uma organização não consegue nem se conectar ao banco de outra.
- A senha do usuário de cada banco é derivada de `TENANT_DATABASE_SECRET` e não fica gravada em lugar nenhum.
- Os tokens de login são assinados com uma chave diferente por organização: o token de uma organização não é aceito em outra.

## Comandos úteis

Ver os logs de todos os serviços:

```bash
docker compose logs -f
```

Ver o log de um serviço só (`backend`, `frontend` ou `db`):

```bash
docker compose logs -f backend
```

Rodar os testes do backend (usam bancos `test_*` separados, sem tocar nos dados de desenvolvimento):

```bash
docker compose exec backend pytest
```

Migrations (Alembic, uma árvore para a plataforma e outra para as organizações):

```bash
docker compose exec backend python -m app.commands.migrate_all_databases
docker compose exec backend alembic -n platform revision -m "descricao"
docker compose exec backend alembic -n tenant revision -m "descricao"
```

Instalar um pacote novo no frontend:

```bash
docker compose exec frontend npm install nome-do-pacote
```

> No Linux, se o seu usuário ainda não estiver no grupo `docker`, coloque `sudo` antes dos comandos `docker` (ou faça logout/login depois da primeira instalação).

As pastas `backend/` e `frontend/busca-bula/` são compartilhadas com os containers, então qualquer alteração no código é aplicada na hora, sem precisar reiniciar. Se mudar o `requirements.txt` ou o `package.json`, rode o `start` de novo: ele percebe a mudança e reconstrói só a imagem que precisa.

## Configuração

Os valores padrão já funcionam sem precisar configurar nada. Se quiser mudar alguma coisa (por exemplo, quando a porta 5173 ou 8000 já estiver em uso), crie um arquivo `.env` na raiz do projeto:

```env
FRONTEND_PORT=5173
BACKEND_PORT=8000
POSTGRES_DB=busca_bula
POSTGRES_USER=busca_bula
POSTGRES_PASSWORD=busca_bula
BASE_DOMAIN=localhost
JWT_SECRET=troque-em-producao
TENANT_DATABASE_SECRET=troque-em-producao
```

`TENANT_DATABASE_SECRET` não pode mudar depois que existirem organizações, porque as senhas dos bancos delas são derivadas dele.

## Estrutura

```
busca-bula/
├── backend/               # API em FastAPI (MVC)
│   ├── app/
│   │   ├── controllers/   # rotas HTTP
│   │   ├── services/      # regras de negócio
│   │   ├── repositories/  # acesso ao banco
│   │   ├── models/        # tabelas (platform/ e tenant/)
│   │   ├── schemas/       # validação de entrada e saída
│   │   ├── dependencies/  # organização atual e autenticação
│   │   ├── core/          # configuração, bancos e segurança
│   │   └── commands/      # comandos de linha de comando
│   ├── migrations/        # platform/ e tenant/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/busca-bula/   # Aplicação Vue 3 + Vite (camada de visão)
│   ├── src/pages/
│   ├── src/services/      # comunicação com a API
│   └── Dockerfile
├── docker/postgres/       # Script de inicialização do banco
├── scripts/               # Scripts PowerShell usados pelos .bat
├── docker-compose.yml
├── start.sh / stop.sh     # Linux
└── start.bat / stop.bat   # Windows
```
