#!/usr/bin/env bash
# Para os containers do projeto.
# Use "./stop.sh --limpar" para apagar tambem os dados do banco.

set -euo pipefail
cd "$(dirname "$0")"

info() { printf '\033[1;36m[busca-bula]\033[0m %s\n' "$*"; }
erro() { printf '\033[1;31m[busca-bula]\033[0m %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || erro "Docker nao encontrado. Nada para parar."

if docker info >/dev/null 2>&1; then
    DOCKER=(docker)
elif sudo docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
else
    erro "Nao foi possivel conectar ao Docker."
fi

if "${DOCKER[@]}" compose version >/dev/null 2>&1; then
    COMPOSE=("${DOCKER[@]}" compose)
elif [ "${DOCKER[0]}" = "sudo" ]; then
    COMPOSE=(sudo docker-compose)
else
    COMPOSE=(docker-compose)
fi

ARGS=(--profile tunnel down)
if [ "${1:-}" = "--limpar" ]; then
    info "Removendo containers e dados do banco..."
    ARGS+=(-v)
else
    info "Parando os containers..."
fi

"${COMPOSE[@]}" "${ARGS[@]}"
info "Projeto parado."
