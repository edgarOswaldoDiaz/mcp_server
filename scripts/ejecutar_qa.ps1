param(
    [string]$AgentUrl = "http://localhost:8002"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================"
Write-Host " QA STACK - SUITE OFICIAL"
Write-Host "======================================"

# Verificar agente
Write-Host "`n[1/3] Verificando agente..."

try {
    $card = Invoke-RestMethod `
        -Uri "$AgentUrl/.well-known/agent-card.json" `
        -TimeoutSec 10

    Write-Host "[PASS] Agent Card disponible" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Agente no disponible: $AgentUrl" -ForegroundColor Red
    exit 2
}

# Configurar URL de pruebas
$env:AGENT_URL = $AgentUrl

# Preparar carpeta de evidencias
$evidencias = Join-Path $PSScriptRoot "..\docs\qa\evidencias"
New-Item -ItemType Directory -Force $evidencias | Out-Null

$fecha = Get-Date -Format "yyyyMMdd-HHmmss"
$log = Join-Path $evidencias "pytest-$fecha.txt"

# Ejecutar suite
Write-Host "`n[2/3] Ejecutando pytest..."
python -m pytest .\tests -v --tb=short 2>&1 |
    Tee-Object -FilePath $log

$pytestExit = $LASTEXITCODE

# Resultado
Write-Host "`n[3/3] Resultado..."

if ($pytestExit -eq 0) {
    Write-Host "[PASS] Suite pytest completada" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] pytest terminó con errores" -ForegroundColor Red
}

Write-Host "Evidencia: $log"

Write-Host "`n======================================"

if ($pytestExit -eq 0) {
    Write-Host "RESULTADO QA: PASS" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "RESULTADO QA: FAIL" -ForegroundColor Red
    exit 1
}
