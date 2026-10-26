# Busca Bula

Projeto com backend em Django (Django REST Framework), frontend em Vue 3 + Vite e banco PostgreSQL com a extensão pgvector. Tudo roda dentro de containers Docker.

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
4. Sobe os containers (`docker compose up -d`).
5. Espera o frontend responder e abre o navegador.

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

| Serviço        | Endereço                      |
| -------------- | ----------------------------- |
| Frontend       | http://localhost:5173         |
| Backend (API)  | http://localhost:8000         |
| Admin Django   | http://localhost:8000/admin/  |

O banco PostgreSQL fica acessível apenas entre os containers.

## Comandos úteis

Ver os logs de todos os serviços:

```bash
docker compose logs -f
```

Ver o log de um serviço só (`backend`, `frontend` ou `db`):

```bash
docker compose logs -f backend
```

Rodar comandos do Django dentro do container:

```bash
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
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
```

## Estrutura

```
busca-bula/
├── backend/               # API em Django
│   ├── config/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/busca-bula/   # Aplicação Vue 3 + Vite
│   └── Dockerfile
├── docker/postgres/       # Script de inicialização do banco
├── scripts/               # Scripts PowerShell usados pelos .bat
├── docker-compose.yml
├── start.sh / stop.sh     # Linux
└── start.bat / stop.bat   # Windows
```
