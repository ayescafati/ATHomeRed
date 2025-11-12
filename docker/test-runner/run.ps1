param(
    [string]$ComposeFile = "${PSScriptRoot}\docker-compose.test.yml",
    [switch]$NoBuild,
    [switch]$Full   # Usa perfil 'full' (incluye Postgres + migraciones)
)

$ErrorActionPreference = "Stop"

Write-Host "==> Using compose file: $ComposeFile"

# Clean up previous run
Write-Host "==> docker compose down -v --remove-orphans"
docker compose -f $ComposeFile down -v --remove-orphans | Out-Host

if ($Full) { Write-Host "==> Profile: full (Postgres ON)" } else { Write-Host "==> Profile: default (no Postgres)" }

$profileArgs = @()
if ($Full) { $profileArgs += @('--profile','full') }

# Up with or without build
if ($NoBuild) {
    Write-Host "==> docker compose $($profileArgs -join ' ') up --abort-on-container-exit --exit-code-from api-test"
    docker compose -f $ComposeFile @profileArgs up --abort-on-container-exit --exit-code-from api-test
} else {
    Write-Host "==> docker compose $($profileArgs -join ' ') up --build --abort-on-container-exit --exit-code-from api-test"
    docker compose -f $ComposeFile @profileArgs up --build --abort-on-container-exit --exit-code-from api-test
}

$exitCode = $LASTEXITCODE

Write-Host "==> Exit code: $exitCode"

# Always bring down after run
Write-Host "==> docker compose down -v --remove-orphans"
docker compose -f $ComposeFile down -v --remove-orphans | Out-Host

exit $exitCode
