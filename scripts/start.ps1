# Sobe o projeto (banco, backend e frontend) com Docker no Windows.
# Se o Docker Desktop nao estiver instalado, o script instala via winget.

$Raiz = Split-Path -Parent $PSScriptRoot
Set-Location $Raiz

if (Test-Path '.env') {
    Get-Content '.env' | Where-Object { $_ -match '^\s*([A-Z_]+)\s*=\s*(.*)$' } | ForEach-Object {
        Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2].Trim()
    }
}

$FrontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { '5173' }
$BackendPort = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { '8000' }

function Info($msg) { Write-Host "[busca-bula] $msg" -ForegroundColor Cyan }
function Erro($msg) { Write-Host "[busca-bula] $msg" -ForegroundColor Red; exit 1 }

function Atualizar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
    $dockerBin = Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin'
    if (Test-Path $dockerBin) { $env:Path += ";$dockerBin" }
}

function Docker-Instalado { [bool](Get-Command docker -ErrorAction SilentlyContinue) }

function Docker-Rodando {
    cmd /c "docker info >nul 2>&1"
    return ($LASTEXITCODE -eq 0)
}

function Instalar-Docker {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Erro 'winget nao encontrado. Atualize o "Instalador de Aplicativo" pela Microsoft Store e rode o start.bat de novo.'
    }

    cmd /c "wsl --status >nul 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Info 'Habilitando o WSL 2 (o Windows vai pedir permissao de administrador)...'
        Start-Process wsl.exe -ArgumentList '--install', '--no-distribution' -Verb RunAs -Wait
    }

    Info 'Instalando o Docker Desktop (o Windows vai pedir permissao de administrador)...'
    winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0 -and -not (Test-Path (Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'))) {
        Erro 'Falha ao instalar o Docker Desktop.'
    }

    Atualizar-Path
    Info 'Docker Desktop instalado.'
    Info 'Se o Windows pedir para reiniciar, reinicie o computador e rode o start.bat de novo.'
}

function Iniciar-Docker {
    if (Docker-Rodando) { return }

    $exe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
    if (Test-Path $exe) {
        Info 'Abrindo o Docker Desktop...'
        Start-Process $exe
    }

    Info 'Aguardando o Docker iniciar (na primeira vez aceite os termos do Docker Desktop)...'
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 3
        if (Docker-Rodando) { return }
    }
    Erro 'O Docker nao iniciou. Abra o Docker Desktop manualmente, espere ele carregar e rode o start.bat de novo.'
}

Atualizar-Path
if (-not (Docker-Instalado)) { Instalar-Docker }
if (-not (Docker-Instalado)) { Erro 'Docker nao encontrado mesmo apos a instalacao. Reinicie o computador e rode o start.bat de novo.' }
Iniciar-Docker

# Hash dos arquivos que definem as dependencias de cada imagem.
# A imagem so e reconstruida quando nao existe ou quando esse hash muda,
# assim nada e baixado de novo a cada execucao.
function Hash-Arquivos([string[]]$Arquivos) {
    $bytes = New-Object System.Collections.Generic.List[byte]
    foreach ($a in $Arquivos) { $bytes.AddRange([System.IO.File]::ReadAllBytes((Join-Path $Raiz $a))) }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    ($sha.ComputeHash($bytes.ToArray()) | ForEach-Object { $_.ToString('x2') }) -join ''
}

function Precisa-Build($Imagem, $Hash) {
    $json = docker image inspect --format '{{json .Config.Labels}}' $Imagem 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json) { return $true }
    $labels = $json | ConvertFrom-Json
    if (-not $labels) { return $true }
    return ($labels.'busca-bula.deps' -ne $Hash)
}

$env:BACKEND_DEPS_HASH = Hash-Arquivos @('backend\Dockerfile', 'backend\requirements.txt')
$env:FRONTEND_DEPS_HASH = Hash-Arquivos @('frontend\busca-bula\Dockerfile', 'frontend\busca-bula\package.json', 'frontend\busca-bula\package-lock.json')

$Build = @()
if (Precisa-Build 'busca-bula-backend' $env:BACKEND_DEPS_HASH) { $Build += 'backend' }
if (Precisa-Build 'busca-bula-frontend' $env:FRONTEND_DEPS_HASH) { $Build += 'frontend' }

$UpArgs = @('compose', 'up', '-d')
if ($Build.Count -gt 0) {
    Info "Construindo as imagens: $($Build -join ', ') (a primeira vez demora alguns minutos)..."
    docker compose build @Build
    if ($LASTEXITCODE -ne 0) { Erro 'Falha ao construir as imagens.' }
    # node_modules fica em volume anonimo; renova para pegar o da imagem nova
    $UpArgs += '--renew-anon-volumes'
} else {
    Info 'Imagens ja estao atualizadas, nada para instalar.'
}

Info 'Subindo os containers...'
& docker @UpArgs
if ($LASTEXITCODE -ne 0) { Erro 'Falha ao subir os containers.' }

$Url = "http://localhost:$FrontendPort"
Info 'Aguardando o frontend responder...'
for ($i = 0; $i -lt 60; $i++) {
    try {
        Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 | Out-Null
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}

Write-Host ''
Info 'Projeto rodando!'
Info "  Frontend: $Url"
Info "  Backend:  http://localhost:$BackendPort"
Info "  Admin:    http://localhost:$BackendPort/admin/"
Info 'Para ver os logs: docker compose logs -f'
Info 'Para parar:       stop.bat'

Start-Process $Url
