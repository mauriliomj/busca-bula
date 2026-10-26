#!/usr/bin/env bash
# Sobe o projeto (banco, backend e frontend) com Docker.
# Se o Docker nao estiver instalado, o script instala automaticamente.

set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a; . ./.env; set +a
fi

FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

info() { printf '\033[1;36m[busca-bula]\033[0m %s\n' "$*"; }
erro() { printf '\033[1;31m[busca-bula]\033[0m %s\n' "$*" >&2; exit 1; }

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    command -v sudo >/dev/null 2>&1 || erro "O comando sudo nao foi encontrado. Rode o script como root."
    SUDO="sudo"
fi

instalar_pacotes() {
    if command -v apt-get >/dev/null 2>&1; then
        $SUDO apt-get update -qq && $SUDO apt-get install -y "$@"
    elif command -v dnf >/dev/null 2>&1; then
        $SUDO dnf install -y "$@"
    elif command -v yum >/dev/null 2>&1; then
        $SUDO yum install -y "$@"
    elif command -v pacman >/dev/null 2>&1; then
        $SUDO pacman -Sy --noconfirm "$@"
    elif command -v zypper >/dev/null 2>&1; then
        $SUDO zypper --non-interactive install "$@"
    else
        return 1
    fi
}

instalar_docker() {
    info "Docker nao encontrado. Instalando..."

    if command -v pacman >/dev/null 2>&1; then
        instalar_pacotes docker docker-compose
    elif command -v zypper >/dev/null 2>&1; then
        instalar_pacotes docker docker-compose
    else
        if ! command -v curl >/dev/null 2>&1; then
            instalar_pacotes curl || erro "Nao foi possivel instalar o curl."
        fi
        curl -fsSL https://get.docker.com | $SUDO sh
    fi

    if command -v systemctl >/dev/null 2>&1; then
        $SUDO systemctl enable --now docker
    fi

    if [ -n "$SUDO" ]; then
        $SUDO usermod -aG docker "$USER" || true
        info "Usuario $USER adicionado ao grupo docker (vale a partir do proximo login)."
    fi
}

iniciar_servico_docker() {
    if command -v systemctl >/dev/null 2>&1; then
        $SUDO systemctl start docker || true
    elif command -v service >/dev/null 2>&1; then
        $SUDO service docker start || true
    fi
}

command -v docker >/dev/null 2>&1 || instalar_docker

# Descobre se da para usar o docker direto ou se precisa de sudo
DOCKER=()
for tentativa in 1 2; do
    if docker info >/dev/null 2>&1; then
        DOCKER=(docker)
    elif [ -n "$SUDO" ] && $SUDO docker info >/dev/null 2>&1; then
        DOCKER=($SUDO docker)
    fi
    [ ${#DOCKER[@]} -gt 0 ] && break
    info "Iniciando o servico do Docker..."
    iniciar_servico_docker
    sleep 3
done
[ ${#DOCKER[@]} -gt 0 ] || erro "Nao foi possivel conectar ao Docker. Verifique se o servico esta rodando."

# Docker Compose (plugin novo ou docker-compose antigo)
if ! "${DOCKER[@]}" compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    info "Docker Compose nao encontrado. Instalando..."
    instalar_pacotes docker-compose-plugin || instalar_pacotes docker-compose \
        || erro "Nao foi possivel instalar o Docker Compose."
fi

if "${DOCKER[@]}" compose version >/dev/null 2>&1; then
    COMPOSE=("${DOCKER[@]}" compose)
elif [ "${DOCKER[0]}" = "sudo" ]; then
    COMPOSE=(sudo docker-compose)
else
    COMPOSE=(docker-compose)
fi

# Hash dos arquivos que definem as dependencias de cada imagem.
# A imagem so e reconstruida quando nao existe ou quando esse hash muda,
# assim nada e baixado de novo a cada execucao.
hash_arquivos() {
    cat "$@" | { sha256sum 2>/dev/null || shasum -a 256; } | cut -d' ' -f1
}

export BACKEND_DEPS_HASH FRONTEND_DEPS_HASH
BACKEND_DEPS_HASH="$(hash_arquivos backend/Dockerfile backend/requirements.txt)"
FRONTEND_DEPS_HASH="$(hash_arquivos frontend/busca-bula/Dockerfile frontend/busca-bula/package.json frontend/busca-bula/package-lock.json)"

precisa_build() {
    local imagem="$1" hash="$2" atual
    atual="$("${DOCKER[@]}" image inspect -f '{{ index .Config.Labels "busca-bula.deps" }}' "$imagem" 2>/dev/null || true)"
    [ "$atual" != "$hash" ]
}

BUILD=()
precisa_build busca-bula-backend "$BACKEND_DEPS_HASH" && BUILD+=(backend)
precisa_build busca-bula-frontend "$FRONTEND_DEPS_HASH" && BUILD+=(frontend)

UP_ARGS=(up -d)
if [ ${#BUILD[@]} -gt 0 ]; then
    info "Construindo as imagens: ${BUILD[*]} (a primeira vez demora alguns minutos)..."
    "${COMPOSE[@]}" build "${BUILD[@]}"
    # node_modules fica em volume anonimo; renova para pegar o da imagem nova
    UP_ARGS+=(--renew-anon-volumes)
else
    info "Imagens ja estao atualizadas, nada para instalar."
fi

info "Subindo os containers..."
"${COMPOSE[@]}" "${UP_ARGS[@]}"

URL="http://localhost:${FRONTEND_PORT}"
if command -v curl >/dev/null 2>&1; then
    info "Aguardando o frontend responder..."
    for _ in $(seq 1 60); do
        curl -s -o /dev/null "$URL" && break
        sleep 2
    done
fi

echo
info "Projeto rodando!"
info "  Frontend: $URL"
info "  Backend:  http://localhost:${BACKEND_PORT}"
info "  Admin:    http://localhost:${BACKEND_PORT}/admin/"
info "Para ver os logs: ${COMPOSE[*]} logs -f"
info "Para parar:       ./stop.sh"

if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
    xdg-open "$URL" >/dev/null 2>&1 &
fi
