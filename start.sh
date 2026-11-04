#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a; . ./.env; set +a
fi

FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
NGROK_INSPECTOR_PORT="${NGROK_INSPECTOR_PORT:-4040}"

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

if [ -n "${NGROK_AUTHTOKEN:-}" ]; then
    COMPOSE+=(--profile tunnel)
fi

UP_ARGS=(up -d)
if [ ${#BUILD[@]} -gt 0 ]; then
    info "Construindo as imagens: ${BUILD[*]} (a primeira vez demora alguns minutos)..."
    "${COMPOSE[@]}" build "${BUILD[@]}"
    UP_ARGS+=(--renew-anon-volumes)
else
    info "Imagens ja estao atualizadas, nada para instalar."
fi

info "Subindo os containers..."
"${COMPOSE[@]}" "${UP_ARGS[@]}"

URL="http://localhost:${FRONTEND_PORT}"
API_URL="http://localhost:${BACKEND_PORT}"

aguardar_resposta() {
    local endereco="$1" tentativas="$2"
    for _ in $(seq 1 "$tentativas"); do
        curl -sf -o /dev/null "$endereco" && return 0
        sleep 2
    done
    return 1
}

if command -v curl >/dev/null 2>&1; then
    info "Aguardando o backend atualizar os bancos e responder..."
    aguardar_resposta "${API_URL}/api/health" 90 \
        || info "O backend ainda nao respondeu. Veja os logs com: ${COMPOSE[*]} logs -f backend"
    info "Aguardando o frontend responder..."
    aguardar_resposta "$URL" 60 || true
fi

ler_url_do_ngrok() {
    curl -sf "http://127.0.0.1:${NGROK_INSPECTOR_PORT}/api/tunnels" 2>/dev/null \
        | grep -o '"public_url":"https://[^"]*"' | head -n 1 | cut -d'"' -f4
}

URL_PUBLICA=""
if [ -n "${NGROK_AUTHTOKEN:-}" ] && command -v curl >/dev/null 2>&1; then
    info "Aguardando o tunel do ngrok..."
    for _ in $(seq 1 30); do
        URL_PUBLICA="$(ler_url_do_ngrok)"
        [ -n "$URL_PUBLICA" ] && break
        sleep 2
    done
fi

IP_LOCAL="$(hostname -I 2>/dev/null | awk '{print $1}')"

URL_DO_CELULAR=""
if [ -n "${DEFAULT_ORGANIZATION:-}" ]; then
    if [ -n "$URL_PUBLICA" ]; then
        URL_DO_CELULAR="$URL_PUBLICA"
    elif [ -n "$IP_LOCAL" ]; then
        URL_DO_CELULAR="http://${IP_LOCAL}:${FRONTEND_PORT}"
    fi
fi

QRCODE_IMAGE="alpine:3"

gerar_qrcode() {
    if command -v qrencode >/dev/null 2>&1; then
        qrencode -t ANSIUTF8 -m 2 "$1"
    else
        "${DOCKER[@]}" run --rm "$QRCODE_IMAGE" sh -c \
            'apk add -q libqrencode-tools >/dev/null 2>&1 && qrencode -t ANSIUTF8 -m 2 "$1"' qrencode "$1" 2>/dev/null
    fi
}

mostrar_qrcode() {
    local qrcode
    qrcode="$(gerar_qrcode "$1" || true)"
    if [ -n "$qrcode" ]; then
        echo
        info "Aponte a camera do celular para o QR code:"
        printf '%s\n' "$qrcode"
    else
        info "Nao foi possivel gerar o QR code. Abra no celular: $1"
    fi
}

echo
info "Projeto rodando!"
info "  Frontend:     $URL"
info "  Backend:      ${API_URL}"
info "  Docs da API:  ${API_URL}/docs"
info "  Organizacoes: http://<subdominio>.localhost:${FRONTEND_PORT}"
if [ -n "${DEFAULT_ORGANIZATION:-}" ]; then
    [ -n "$IP_LOCAL" ] && info "  Rede local:   http://${IP_LOCAL}:${FRONTEND_PORT} (organizacao ${DEFAULT_ORGANIZATION}, sem instalar o app)"
    if [ -n "$URL_PUBLICA" ]; then
        info "  Celular:      ${URL_PUBLICA} (HTTPS, permite instalar o app)"
    elif [ -n "${NGROK_AUTHTOKEN:-}" ]; then
        info "  O tunel do ngrok nao respondeu. Veja os logs com: ${COMPOSE[*]} logs -f ngrok"
    fi
else
    info "  Para abrir pelo celular, defina DEFAULT_ORGANIZATION (e NGROK_AUTHTOKEN) no .env."
fi
[ -n "$URL_DO_CELULAR" ] && mostrar_qrcode "$URL_DO_CELULAR"
echo
info "Para ver os logs: ${COMPOSE[*]} logs -f"
info "Para parar:       ./stop.sh"

if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
    xdg-open "$URL" >/dev/null 2>&1 &
fi
