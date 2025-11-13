# 📚 Scripts de ATHomeRed

Esta carpeta contiene scripts organizados para desarrollo, configuración y demostración del sistema.

## 📁 Estructura

```
scripts/
├── setup/          # Scripts de configuración inicial
├── seed/           # Scripts para poblar datos de prueba
└── dev/            # Scripts de desarrollo y ejemplos
```

## 🚀 Scripts de Setup (Configuración Inicial)

### `setup/init_db.py`
Inicializa la base de datos completa con esquema y datos base.

```bash
python scripts/setup/init_db.py
```

### `setup/create_schema.py`
Crea solo el esquema de base de datos sin datos.

```bash
python scripts/setup/create_schema.py
```

### `setup/apply_sql.py`
Aplica un archivo SQL específico a la base de datos.

```bash
python scripts/setup/apply_sql.py archivo.sql
```

## 🌱 Scripts de Seed (Datos de Prueba)

### `seed/seed_especialidades.py`
Carga las especialidades de ATHomeRed en la base de datos.

```bash
python scripts/seed/seed_especialidades.py
```

**Especialidades incluidas:**
- Enfermería ($2500)
- Acompañante Terapéutico ($2000)
- Geriatría ($2800)
- Cuidados Paliativos ($3000)
- Fisioterapia a Domicilio ($2200)

### `seed/demo_data.py`
Carga datos de prueba completos (usuarios, profesionales, pacientes, citas).

```bash
python scripts/seed/demo_data.py
```

## 🔧 Scripts de Desarrollo

### `dev/check_db.py`
Verifica el estado de la base de datos y muestra estadísticas.

```bash
python scripts/dev/check_db.py
```

**Muestra:**
- Cantidad de usuarios, profesionales, pacientes
- Cantidad de especialidades
- Cantidad de citas por estado
- Últimas tablas creadas

### `dev/test_connection.py`
Prueba la conexión a la base de datos.

```bash
python scripts/dev/test_connection.py
```

### `dev/smoke_auth.py`
Prueba rápida del sistema de autenticación.

```bash
python scripts/dev/smoke_auth.py
```

**Verifica:**
- Registro de usuario
- Login y generación de token
- Validación de token
- Refresh token

## 🎯 Ejemplos del Patrón Observer

### `dev/demo_observer_completo.py`
**Demostración completa del patrón Observer en memoria.**

Simula todos los estados de una cita y muestra cómo el Observer (NotificadorEmail) se dispara automáticamente.

```bash
python scripts/dev/demo_observer_completo.py
```

**Flujo demostrado:**
1. Paciente solicita cita (PENDIENTE)
2. Profesional confirma (CONFIRMADA) → Observer dispara notificación
3. Paciente reprograma (REPROGRAMADA) → Observer dispara notificación
4. Profesional completa (COMPLETADA) → Observer dispara notificación
5. Caso alternativo: Cancelación → Observer dispara notificación

**Salida esperada:**
```
========== NOTIFICADOR EMAIL ==========
   Evento: CITA CONFIRMADA
   Cita ID: bcf6fca7-99c2-47fd-9f85-7ccf18f206e4
   Confirmado por: profesional:8f83c0cd-...
   Email enviado a profesional y solicitante
========================================
```

### `dev/ejemplo_uso_api_observer.py`
**Ejemplo práctico de uso de la API con Observer.**

Interactúa con la API real para demostrar el flujo completo paciente-profesional.

```bash
# Primero inicia el servidor
python run_server.py

# En otra terminal
python scripts/dev/ejemplo_uso_api_observer.py
```

**Requisitos:**
- Servidor corriendo en `http://localhost:8000`
- Usuarios creados (paciente y profesional)
- Base de datos inicializada

**Flujo:**
1. **Paciente:**
   - Se autentica
   - Busca profesional de Enfermería
   - Solicita cita
   - Confirma cita → **Observer se dispara**

2. **Profesional:**
   - Se autentica
   - Consulta sus citas
   - Completa la cita → **Observer se dispara**

### `dev/ejemplo_api_observer.ps1`
**Script de PowerShell para probar la API con curl.**

```powershell
.\scripts\dev\ejemplo_api_observer.ps1
```

**Características:**
- ✅ Colores y formato visual
- ✅ Pausa entre pasos para ver resultados
- ✅ Muestra exactamente qué endpoints se llaman
- ✅ Explica cuándo el Observer se dispara

### `dev/ejemplo_api_observer_curl.sh`
**Script bash con comandos curl puros.**

```bash
bash scripts/dev/ejemplo_api_observer_curl.sh
```

Útil para entender la estructura de las peticiones HTTP.

## 📋 Comandos Rápidos

```bash
# Setup completo desde cero
python scripts/setup/init_db.py
python scripts/seed/seed_especialidades.py
python scripts/seed/demo_data.py

# Verificar estado
python scripts/dev/check_db.py

# Probar autenticación
python scripts/dev/smoke_auth.py

# Demo del Observer (sin servidor)
python scripts/dev/demo_observer_completo.py

# Ejemplo con API real (servidor debe estar corriendo)
python run_server.py  # Terminal 1
python scripts/dev/ejemplo_uso_api_observer.py  # Terminal 2
```

## 💡 Notas Importantes

### Observer Pattern
El patrón Observer está implementado en la entidad `Cita` y se dispara **automáticamente** cuando:
- Se confirma una cita (`confirmar()`)
- Se cancela una cita (`cancelar()`)
- Se reprograma una cita (`reprogramar()`)
- Se completa una cita (`completar()`)

**Ni el paciente ni el profesional necesitan llamar directamente al Observer.** Las notificaciones se envían automáticamente al invocar estos métodos desde la API.

### Endpoints con Observer
```
POST   /api/v1/consultas/{id}/confirmar     ← Paciente o Profesional
DELETE /api/v1/consultas/{id}               ← Paciente o Profesional (cancelar)
POST   /api/v1/consultas/{id}/completar     ← Solo Profesional
POST   /api/v1/consultas/{id}/reprogramar   ← Paciente o Profesional
```

## 🔐 Autenticación

Todos los endpoints de gestión de citas requieren autenticación mediante JWT token:

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario@email.com","password":"pass123"}'

# 2. Usar el token
curl -X POST http://localhost:8000/api/v1/consultas/{id}/confirmar \
  -H "Authorization: Bearer {token}"
```

## 🐛 Troubleshooting

**Error: "ModuleNotFoundError: No module named 'app'"**
```bash
# Solución: Configurar PYTHONPATH
export PYTHONPATH=/ruta/al/proyecto  # Linux/Mac
$env:PYTHONPATH="C:\ruta\al\proyecto"  # PowerShell
```

**Error: "Connection refused" en ejemplos de API**
```bash
# Solución: Asegúrate de que el servidor esté corriendo
python run_server.py
```

**Error: "Usuario no encontrado" en login**
```bash
# Solución: Crear usuarios de prueba primero
python scripts/seed/demo_data.py
```

## 📚 Más Información

- Ver `app/domain/observers/observadores.py` para implementación del Observer
- Ver `app/api/routers/consultas.py` para endpoints con Observer
- Ver `app/domain/entities/agenda.py` para lógica de estados de Cita
