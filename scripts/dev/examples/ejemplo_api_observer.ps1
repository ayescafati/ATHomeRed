# ============================================================================
# EJEMPLO PRÁCTICO: API con Observer Pattern usando CURL
# ============================================================================
# 
# Este script muestra cómo interactuar con la API de ATHomeRed
# y cómo el patrón Observer se dispara automáticamente.
#
# REQUISITOS:
# 1. Servidor corriendo: python run_server.py
# 2. Base de datos inicializada con usuarios y especialidades
#
# USO: Ejecuta cada comando en PowerShell uno por uno
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PARTE 1: FLUJO DEL PACIENTE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ----------------------------------------------------------------------------
# PASO 1: Paciente se autentica
# ----------------------------------------------------------------------------
Write-Host "PASO 1: Login del paciente..." -ForegroundColor Yellow

$pacienteLogin = @{
    username = "paciente.test@athomered.com"
    password = "password123"
} | ConvertTo-Json

Write-Host "POST /api/v1/auth/login" -ForegroundColor Gray
$pacienteAuth = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body $pacienteLogin `
    -ContentType "application/json"

$pacienteToken = $pacienteAuth.access_token
Write-Host "✅ Token obtenido: $($pacienteToken.Substring(0,30))..." -ForegroundColor Green

# ----------------------------------------------------------------------------
# PASO 2: Paciente busca profesional de Enfermería
# ----------------------------------------------------------------------------
Write-Host "`nPASO 2: Buscar profesional de Enfermería..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer $pacienteToken"
}

Write-Host "GET /api/v1/busqueda/profesionales?especialidad_id=1" -ForegroundColor Gray
$profesionales = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/busqueda/profesionales?especialidad_id=1&provincia=Buenos%20Aires" `
    -Method Get `
    -Headers $headers

if ($profesionales.Count -gt 0) {
    $profesional = $profesionales[0]
    $profesionalId = $profesional.id
    Write-Host "✅ Profesional encontrado: $($profesional.nombre)" -ForegroundColor Green
    Write-Host "   ID: $profesionalId" -ForegroundColor Gray
    Write-Host "   Especialidad: $($profesional.especialidad.nombre)" -ForegroundColor Gray
} else {
    Write-Host "❌ No se encontraron profesionales" -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------------
# PASO 3: Paciente solicita una cita
# ----------------------------------------------------------------------------
Write-Host "`nPASO 3: Solicitar una cita..." -ForegroundColor Yellow

$manana = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")

$nuevaCita = @{
    profesional_id = $profesionalId
    paciente_id = "mock-paciente-id-123"  # En producción vendría del token
    solicitante_id = "mock-paciente-id-123"
    fecha = $manana
    hora_inicio = "14:00:00"
    hora_fin = "15:30:00"
    ubicacion = @{
        provincia = "Buenos Aires"
        departamento = "CABA"
        barrio = "Palermo"
        calle = "Av. Santa Fe"
        numero = "2500"
        latitud = -34.588333
        longitud = -58.414167
    }
    motivo = "Cuidado post-operatorio a domicilio"
} | ConvertTo-Json -Depth 10

Write-Host "POST /api/v1/consultas/" -ForegroundColor Gray
$citaCreada = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/consultas/" `
    -Method Post `
    -Body $nuevaCita `
    -Headers $headers `
    -ContentType "application/json"

$citaId = $citaCreada.id
Write-Host "✅ Cita creada: $citaId" -ForegroundColor Green
Write-Host "   Estado: $($citaCreada.estado)" -ForegroundColor Gray
Write-Host "   Fecha: $($citaCreada.fecha) $($citaCreada.hora_inicio)-$($citaCreada.hora_fin)" -ForegroundColor Gray

# ----------------------------------------------------------------------------
# PASO 4: Paciente confirma la cita (OBSERVER SE DISPARA AQUÍ)
# ----------------------------------------------------------------------------
Write-Host "`nPASO 4: Confirmar la cita (Observer se dispara automáticamente)..." -ForegroundColor Yellow
Write-Host "`n🔔 Al confirmar, el NotificadorEmail enviará emails a:" -ForegroundColor Cyan
Write-Host "   • Paciente (confirmación de cita)" -ForegroundColor Cyan
Write-Host "   • Profesional (nueva cita confirmada)" -ForegroundColor Cyan

Read-Host "`n⏸️  Presiona Enter para confirmar la cita"

Write-Host "POST /api/v1/consultas/$citaId/confirmar" -ForegroundColor Gray
$citaConfirmada = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/consultas/$citaId/confirmar" `
    -Method Post `
    -Headers $headers

Write-Host "`n✅ Cita confirmada!" -ForegroundColor Green
Write-Host "   Estado: $($citaConfirmada.estado)" -ForegroundColor Gray
Write-Host "`n📧 En la consola del servidor deberías ver:" -ForegroundColor Magenta
Write-Host "   ========== NOTIFICADOR EMAIL ==========" -ForegroundColor DarkGray
Write-Host "      Evento: CITA CONFIRMADA" -ForegroundColor DarkGray
Write-Host "      Cita ID: $citaId" -ForegroundColor DarkGray
Write-Host "      Confirmado por: paciente:..." -ForegroundColor DarkGray
Write-Host "   ========================================" -ForegroundColor DarkGray

# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PARTE 2: FLUJO DEL PROFESIONAL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ----------------------------------------------------------------------------
# PASO 5: Profesional se autentica
# ----------------------------------------------------------------------------
Write-Host "PASO 5: Login del profesional..." -ForegroundColor Yellow

$profesionalLogin = @{
    username = "profesional.enfermeria@athomered.com"
    password = "password123"
} | ConvertTo-Json

Write-Host "POST /api/v1/auth/login" -ForegroundColor Gray
$profAuth = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body $profesionalLogin `
    -ContentType "application/json"

$profToken = $profAuth.access_token
Write-Host "✅ Token obtenido: $($profToken.Substring(0,30))..." -ForegroundColor Green

$profHeaders = @{
    "Authorization" = "Bearer $profToken"
}

# ----------------------------------------------------------------------------
# PASO 6: Profesional ve sus citas
# ----------------------------------------------------------------------------
Write-Host "`nPASO 6: Profesional consulta sus citas..." -ForegroundColor Yellow

Write-Host "GET /api/v1/consultas/profesional/$profesionalId" -ForegroundColor Gray
$misCitas = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/consultas/profesional/$profesionalId?solo_activas=true" `
    -Method Get `
    -Headers $profHeaders

Write-Host "✅ Citas activas: $($misCitas.Count)" -ForegroundColor Green
foreach ($c in $misCitas | Select-Object -First 3) {
    Write-Host "   • ID: $($c.id.Substring(0,8))... | Estado: $($c.estado) | Fecha: $($c.fecha)" -ForegroundColor Gray
}

# ----------------------------------------------------------------------------
# PASO 7: Profesional completa la cita (OBSERVER SE DISPARA AQUÍ)
# ----------------------------------------------------------------------------
Write-Host "`nPASO 7: Profesional completa la cita (Observer se dispara automáticamente)..." -ForegroundColor Yellow
Write-Host "`n🔔 Al completar, el NotificadorEmail enviará email al paciente" -ForegroundColor Cyan
Write-Host "   informando que el servicio finalizó." -ForegroundColor Cyan

Read-Host "`n⏸️  Presiona Enter para completar la cita"

$completarData = @{
    notas_finales = "Servicio de enfermería completado. Curación realizada correctamente. Paciente estable. Control en 7 días."
} | ConvertTo-Json

Write-Host "POST /api/v1/consultas/$citaId/completar" -ForegroundColor Gray
$citaCompletada = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/consultas/$citaId/completar" `
    -Method Post `
    -Body $completarData `
    -Headers $profHeaders `
    -ContentType "application/json"

Write-Host "`n✅ Cita completada!" -ForegroundColor Green
Write-Host "   Estado: $($citaCompletada.estado)" -ForegroundColor Gray
Write-Host "   Notas: $($citaCompletada.notas.Substring(0,60))..." -ForegroundColor Gray
Write-Host "`n📧 En la consola del servidor deberías ver:" -ForegroundColor Magenta
Write-Host "   ========== NOTIFICADOR EMAIL ==========" -ForegroundColor DarkGray
Write-Host "      Evento: CITA COMPLETADA" -ForegroundColor DarkGray
Write-Host "      Cita ID: $citaId" -ForegroundColor DarkGray
Write-Host "      Notas: Servicio de enfermería..." -ForegroundColor DarkGray
Write-Host "   ========================================" -ForegroundColor DarkGray

# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ Flujo completado exitosamente!`n" -ForegroundColor Green

Write-Host "📊 Eventos del Observer disparados:" -ForegroundColor Yellow
Write-Host "   1. CitaCreada → Al crear la cita" -ForegroundColor Gray
Write-Host "   2. CitaConfirmada → Cuando el paciente confirmó" -ForegroundColor Gray
Write-Host "   3. CitaCompletada → Cuando el profesional finalizó`n" -ForegroundColor Gray

Write-Host "💡 Puntos clave:" -ForegroundColor Yellow
Write-Host "   • Ni el paciente ni el profesional llamaron directamente al Observer" -ForegroundColor Gray
Write-Host "   • Las notificaciones se dispararon automáticamente" -ForegroundColor Gray
Write-Host "   • El patrón Observer desacopla la lógica de negocio de las notificaciones" -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan
