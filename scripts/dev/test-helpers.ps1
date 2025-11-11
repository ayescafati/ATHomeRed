function Test-ATHomeRed-Unit {
    <#
    .SYNOPSIS
    Ejecuta solo tests unitarios (rápido)
    #>
    Write-Host "Ejecutando tests unitarios..." -ForegroundColor Cyan
    & venv\Scripts\Activate.ps1
    python -m pytest tests/ -m "not e2e" --tb=short -q
}

function Test-ATHomeRed-E2E {
    <#
    .SYNOPSIS
    Ejecuta tests E2E contra Supabase (requiere confirmación)
    #>
    Write-Host "Los tests E2E modificarán datos en Supabase" -ForegroundColor Yellow
    $confirm = Read-Host "¿Continuar? (S/N)"
    if ($confirm -eq "S" -or $confirm -eq "s") {
        & venv\Scripts\Activate.ps1
        python -m pytest tests/ -m e2e --runxfail -v
    }
}

function Test-ATHomeRed-All {
    <#
    .SYNOPSIS
    Ejecuta TODOS los tests (unitarios + E2E)
    #>
    Write-Host "Ejecutando TODOS los tests..." -ForegroundColor Cyan
    & venv\Scripts\Activate.ps1
    python -m pytest tests/ --runxfail -v
}

function Test-ATHomeRed-PreDeploy {
    <#
    .SYNOPSIS
    Suite completa pre-deploy
    #>
    & .\pre-deploy.ps1
}

Set-Alias -Name test-unit -Value Test-ATHomeRed-Unit
Set-Alias -Name test-e2e -Value Test-ATHomeRed-E2E
Set-Alias -Name test-all -Value Test-ATHomeRed-All
Set-Alias -Name predeploy -Value Test-ATHomeRed-PreDeploy

Write-Host "   Funciones de test cargadas:" -ForegroundColor Green
Write-Host "   test-unit      - Tests unitarios (rápido)" -ForegroundColor Gray
Write-Host "   test-e2e       - Tests E2E con Supabase" -ForegroundColor Gray
Write-Host "   test-all       - Todos los tests" -ForegroundColor Gray
Write-Host "   predeploy      - Suite completa pre-deploy" -ForegroundColor Gray
