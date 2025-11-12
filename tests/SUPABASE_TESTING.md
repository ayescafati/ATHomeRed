# 🚀 Tests de Integración con Supabase

Guía para ejecutar tests de integración usando tu base de datos Supabase.

## 📋 Pre-requisitos

1. ✅ Proyecto Supabase activo
2. ✅ Database URL (connection string)
3. ✅ PostGIS habilitado (ya viene por defecto en Supabase)
4. ✅ Datos seeded (especialidades, ubicaciones, etc.)

## 🔧 Configuración

### 1. Obtener Connection String de Supabase

```bash
# En Supabase Dashboard:
# Project → Settings → Database → Connection string
# Seleccionar "URI" mode

# Ejemplo:
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
SUPABASE_DB_URL=postgresql://postgres:tu_password@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

**⚠️ IMPORTANTE**: Agregar `.env` a `.gitignore` (ya debería estar)

### 3. Verificar Conexión

```python
# Script rápido para verificar
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("SUPABASE_DB_URL"))
conn = engine.connect()
print("✅ Conexión exitosa a Supabase!")
conn.close()
```

## 🧪 Ejecutar Tests

### Tests Rápidos (sin BD)
```bash
# Solo unitarios y API con mocks (desarrollo diario)
pytest tests/domain tests/api -v
```

### Tests de Integración con Supabase
```bash
# Todos los tests de integración con Supabase
pytest tests/integration/test_supabase.py -v -m supabase

# Solo tests de lectura (no modifican BD)
pytest tests/integration/test_supabase.py -v -m readonly

# Test específico
pytest tests/integration/test_supabase.py::TestIntegracionSupabase::test_listar_especialidades_supabase -v
```

### Todos los Tests
```bash
# TODO excepto Supabase
pytest tests/ -v -m "not supabase"

# TODO incluyendo Supabase
pytest tests/ -v
```

## 🏗️ Arquitectura de Testing con Supabase

```
┌─────────────────────────────────────┐
│  Test                               │
│  ├─ Crea transacción               │
│  ├─ Inserta datos de prueba        │
│  ├─ Ejecuta lógica de negocio      │
│  ├─ Verifica resultados            │
│  └─ ROLLBACK automático            │  ← ¡BD queda limpia!
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  Supabase PostgreSQL                │
│  (sin basura de tests)              │
└─────────────────────────────────────┘
```

## 📊 Ventajas de Tests con Supabase

### ✅ Pros
- **BD real**: Valida con PostGIS, extensiones, constraints reales
- **Rollback automático**: BD queda limpia después de cada test
- **Tests aislados**: No interfieren entre sí
- **CI/CD ready**: Usa secrets para connection string
- **Sin setup local**: No necesitas PostgreSQL local

### ⚠️ Contras
- **Latencia de red**: Más lento que SQLite local
- **Requiere internet**: No funciona offline
- **Límites de conexiones**: Free tier tiene límites
- **Costo**: Plan pro para muchos tests

## 🎯 Estrategia Recomendada

### Desarrollo Diario
```bash
# Tests rápidos (sin BD) - 1-2 segundos
pytest tests/domain tests/api -v
```

### Pre-Commit
```bash
# Tests de integración básicos
pytest tests/integration/test_supabase.py -v -m readonly
```

### CI/CD (GitHub Actions)
```bash
# Suite completa con Supabase
pytest tests/ -v --cov=app
```

## 🔒 Seguridad

### ❌ NUNCA hacer:
```bash
# NO commitear .env con credenciales
git add .env  # ❌

# NO hardcodear passwords en código
SUPABASE_DB_URL = "postgresql://postgres:mipassword@..."  # ❌
```

### ✅ Sí hacer:
```bash
# Usar variables de entorno
load_dotenv()
db_url = os.getenv("SUPABASE_DB_URL")  # ✅

# Usar .env.example como template
cp .env.test.example .env
# Luego editar .env con tus credenciales reales

# En GitHub Actions, usar secrets
env:
  SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
```

## 🐛 Troubleshooting

### Error: "SUPABASE_DB_URL no configurado"
```bash
# Verificar que existe .env
ls -la .env

# Verificar contenido (sin mostrar password)
cat .env | grep SUPABASE_DB_URL | cut -d'@' -f2
```

### Error: "Could not connect to server"
```bash
# Verificar IP whitelisting en Supabase
# Dashboard → Settings → Database → Connection pooling
# Agregar tu IP o usar 0.0.0.0/0 para desarrollo
```

### Error: "Too many connections"
```bash
# Supabase Free tier: 60 conexiones simultáneas
# Asegurarse de cerrar conexiones:
# - Usar fixtures con yield
# - Llamar engine.dispose()
# - Usar poolclass=NullPool en tests
```

### Tests lentos
```bash
# Opción 1: Usar solo tests rápidos en desarrollo
pytest tests/domain tests/api -v

# Opción 2: Usar PostgreSQL local para tests
# (más rápido pero requiere setup)

# Opción 3: Cachear fixtures pesados
@pytest.fixture(scope="session")  # Se crea una vez por sesión
```

## 📚 Ejemplos de Tests

### Test con Rollback Automático
```python
@pytest.mark.integration
@pytest.mark.supabase
def test_crear_y_buscar_profesional(client_supabase, seed_supabase_data):
    # Crear profesional (se guarda en BD)
    # ...
    
    # Buscar profesional
    response = client_supabase.post("/busqueda/profesionales", json=payload)
    
    assert response.status_code == 200
    # Al terminar el test, ROLLBACK automático
    # El profesional NO queda en la BD
```

### Test de Solo Lectura
```python
@pytest.mark.integration
@pytest.mark.supabase
@pytest.mark.readonly
def test_listar_datos_reales(client_supabase):
    # Lee datos que ya existen en Supabase
    response = client_supabase.get("/busqueda/especialidades")
    
    assert response.status_code == 200
    # No modifica BD, no necesita rollback
```

## 🎓 Recursos

- [Supabase Database Docs](https://supabase.com/docs/guides/database)
- [SQLAlchemy Testing Patterns](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
