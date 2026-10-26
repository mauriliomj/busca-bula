# Para os containers do projeto no Windows.
# Use "stop.bat --limpar" para apagar tambem os dados do banco.

param([string]$Opcao)

$Raiz = Split-Path -Parent $PSScriptRoot
Set-Location $Raiz

function Info($msg) { Write-Host "[busca-bula] $msg" -ForegroundColor Cyan }
function Erro($msg) { Write-Host "[busca-bula] $msg" -ForegroundColor Red; exit 1 }

$dockerBin = Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin'
if (Test-Path $dockerBin) { $env:Path += ";$dockerBin" }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Erro 'Docker nao encontrado. Nada para parar.' }

cmd /c "docker info >nul 2>&1"
if ($LASTEXITCODE -ne 0) { Erro 'O Docker nao esta rodando. Abra o Docker Desktop e tente de novo.' }

if ($Opcao -eq '--limpar') {
    Info 'Removendo containers e dados do banco...'
    docker compose down -v
} else {
    Info 'Parando os containers...'
    docker compose down
}
if ($LASTEXITCODE -ne 0) { Erro 'Falha ao parar os containers.' }

Info 'Projeto parado.'
