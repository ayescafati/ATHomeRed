#!/bin/bash
# ============================================================================
# EJEMPLO: API con Observer Pattern usando CURL
# ============================================================================
# Este script demuestra cómo el patrón Observer se dispara automáticamente
# cuando pacientes y profesionales interactúan con las citas.
#
# REQUISITOS: Servidor corriendo en http://localhost:8000
# USO: bash ejemplo_api_observer_curl.sh
# ============================================================================

BASE_URL="http://localhost:8000/api/v1"

echo ""
echo "========================================"
echo "PARTE 1: FLUJO DEL PACIENTE"
echo "========================================"
echo ""

# PASO 1: Login del paciente
echo "PASO 1: Login del paciente..."
PACIENTE_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "paciente.test@athomered.com",
    "password": "password123"
  }' | jq -r '.access_token')

if [ "$PACIENTE_TOKEN" = "null" ]; then
  echo "❌ Error al autenticar paciente"
  exit 1
fi

echo "✅ Token obtenido: ${PACIENTE_TOKEN:0:30}..."

# PASO 2: Buscar profesional de Enfermería
echo ""
echo "PASO 2: Buscar profesional de Enfermería..."
PROFESIONAL_ID=$(curl -s -X GET "$BASE_URL/busqueda/profesionales?especialidad_id=1&provincia=Buenos%20Aires" \
  -H "Authorization: Bearer $PACIENTE_TOKEN" | jq -r '.[0].id')

if [ "$PROFESIONAL_ID" = "null" ]; then
  echo "❌ No se encontró profesional"
  exit 1
fi

echo "✅ Profesional encontrado: $PROFESIONAL_ID"

# PASO 3: Crear cita
echo ""
echo "PASO 3: Solicitar una cita..."
MANANA=$(date -d "+1 day" +%Y-%m-%d)

CITA_RESPONSE=$(curl -s -X POST "$BASE_URL/consultas/" \
  -H "Authorization: Bearer $PACIENTE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"profesional_id\": \"$PROFESIONAL_ID\",
    \"paciente_id\": \"mock-paciente-id\",
    \"solicitante_id\": \"mock-paciente-id\",
    \"fecha\": \"$MANANA\",
    \"hora_inicio\": \"14:00:00\",
    \"hora_fin\": \"15:30:00\",
    \"ubicacion\": {
      \"provincia\": \"Buenos Aires\",
      \"departamento\": \"CABA\",
      \"barrio\": \"Palermo\",
      \"calle\": \"Av. Santa Fe\",
      \"numero\": \"2500\",
      \"latitud\": -34.588333,
      \"longitud\": -58.414167
    },
    \"motivo\": \"Cuidado post-operatorio\"
  }")

CITA_ID=$(echo $CITA_RESPONSE | jq -r '.id')
echo "✅ Cita creada: $CITA_ID"

# PASO 4: CONFIRMAR CITA (OBSERVER SE DISPARA)
echo ""
echo "PASO 4: Confirmar la cita (Observer se dispara automáticamente)..."
echo ""
echo "🔔 Al confirmar, el NotificadorEmail enviará emails automáticamente"
echo "   Presiona Enter para continuar..."
read

curl -s -X POST "$BASE_URL/consultas/$CITA_ID/confirmar" \
  -H "Authorization: Bearer $PACIENTE_TOKEN" | jq '.'

echo ""
echo "✅ Cita confirmada!"
echo "📧 Revisa la consola del servidor para ver:"
echo "   ========== NOTIFICADOR EMAIL =========="
echo "      Evento: CITA CONFIRMADA"
echo "      Cita ID: $CITA_ID"
echo "   ========================================"

# ============================================================================

echo ""
echo "========================================"
echo "PARTE 2: FLUJO DEL PROFESIONAL"
echo "========================================"
echo ""

# PASO 5: Login del profesional
echo "PASO 5: Login del profesional..."
PROF_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "profesional.enfermeria@athomered.com",
    "password": "password123"
  }' | jq -r '.access_token')

echo "✅ Token obtenido: ${PROF_TOKEN:0:30}..."

# PASO 6: Ver citas
echo ""
echo "PASO 6: Profesional consulta sus citas..."
curl -s -X GET "$BASE_URL/consultas/profesional/$PROFESIONAL_ID?solo_activas=true" \
  -H "Authorization: Bearer $PROF_TOKEN" | jq '. | length' | xargs echo "✅ Citas activas:"

# PASO 7: COMPLETAR CITA (OBSERVER SE DISPARA)
echo ""
echo "PASO 7: Profesional completa la cita (Observer se dispara automáticamente)..."
echo ""
echo "🔔 Al completar, el NotificadorEmail notificará al paciente"
echo "   Presiona Enter para continuar..."
read

curl -s -X POST "$BASE_URL/consultas/$CITA_ID/completar" \
  -H "Authorization: Bearer $PROF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notas_finales": "Servicio completado. Paciente estable. Control en 7 días."
  }' | jq '.'

echo ""
echo "✅ Cita completada!"
echo "📧 Revisa la consola del servidor para ver:"
echo "   ========== NOTIFICADOR EMAIL =========="
echo "      Evento: CITA COMPLETADA"
echo "      Cita ID: $CITA_ID"
echo "   ========================================"

# ============================================================================

echo ""
echo "========================================"
echo "RESUMEN"
echo "========================================"
echo ""
echo "✅ Flujo completado!"
echo ""
echo "📊 Eventos del Observer disparados:"
echo "   1. CitaCreada"
echo "   2. CitaConfirmada ← Paciente confirmó"
echo "   3. CitaCompletada ← Profesional completó"
echo ""
echo "💡 Clave: Las notificaciones se dispararon AUTOMÁTICAMENTE"
echo "=========================================="
echo ""
