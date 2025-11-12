# 🧪 Tests - AtHomeRed

Estructura de testing profesional con múltiples niveles.

## 📁 Estructura

```
tests/
├── domain/              # Tests unitarios del dominio (sin BD)
│   ├── test_entities.py
│   ├── test_estrategias_busqueda.py
│   └── test_buscador.py
├── api/                 # Tests de endpoints con mocks
│   ├── test_busqueda.py
│   └── test_pacientes.py
├── integration/         # Tests con BD real
│   ├── test_busqueda_con_bd.py      (SQLite en memoria)
│   └── test_busqueda_postgres.py    (PostgreSQL de test)
├── conftest.py          # Fixtures compartidas
└── README.md            # Este archivo
```

## 🎯 Tipos de Tests

### 1. Tests Unitarios (Domain)
**Qué testean**: Lógica de negocio pura  
**Dependencias**: Ninguna (mocks de repositorios)  
**Velocidad**: Milisegundos  
**Comando**:
```bash
pytest tests/domain -v
```

### 2. Tests de API (con Mocks)
**Qué testean**: Endpoints HTTP, validaciones, serialización  
**Dependencias**: FastAPI (sin BD)  
**Velocidad**: Segundos  
**Comando**:
```bash
pytest tests/api -v
```

### 3. Tests de Integración (con BD)
**Qué testean**: Stack completo FastAPI → Repos → BD  
**Dependencias**: SQLite en memoria O PostgreSQL test  
**Velocidad**: Segundos  
**Comando**:
```bash
# Con SQLite (más rápido)
pytest tests/integration/test_busqueda_con_bd.py -v -m integration

# Con PostgreSQL (más realista)
pytest tests/integration/test_busqueda_postgres.py -v -m postgres
```

## 🚀 Comandos Rápidos

### Desarrollo Diario
```bash
# Tests rápidos (unitarios + API con mocks)
pytest tests/domain tests/api -v

# Todo menos PostgreSQL
pytest tests/ -v -m "not postgres"
```

### Pre-Commit
```bash
# Todos los tests de integración
pytest tests/ -v -m integration
```

### CI/CD
```bash
# Cobertura completa
pytest tests/ -v --cov=app --cov-report=html
```

## 📊 Cobertura Actual

- ✅ 52 tests unitarios (dominio)
- ✅ 15 tests de API (con mocks)
- ✅ 7 tests de integración API-Domain
- ⚠️ 3 tests de integración con BD (ejemplos)

**Total: ~77 tests automatizados**

## 🔧 Setup para Tests con PostgreSQL

### Opción 1: PostgreSQL Local
```bash
# Crear BD de test
createdb athomered_test
psql athomered_test -c "CREATE EXTENSION postgis;"

# Correr tests
pytest tests/integration -v -m postgres
```

### Opción 2: Docker
```bash
# Levantar PostgreSQL de test
docker run -d --name postgres-test \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=athomered_test \
  -p 5433:5432 \
  postgis/postgis:15-3.3

# Correr tests
pytest tests/integration -v -m postgres
```

## 🏗️ Arquitectura de Testing

### Pirámide de Tests (siguiendo mejores prácticas)
```
       /\        E2E Tests (pocas, lentas)
      /  \       
     /____\      Integration Tests (algunas, moderadas)
    /      \     
   /        \    API Tests con Mocks (bastantes, rápidas)
  /__________\   
 /            \  Unit Tests (muchas, muy rápidas)
/______________\ 
```

### Ventajas de esta arquitectura:
1. ✅ Tests rápidos en desarrollo (unitarios)
2. ✅ Confianza en integraciones (con BD)
3. ✅ CI/CD eficiente (tests escalonados)
4. ✅ Rollback automático (BD limpia entre tests)

## 🎓 Convenciones

### Naming
- `test_*.py` para archivos de tests
- `Test*` para clases de tests
- `test_*` para funciones de tests

### Markers
```python
@pytest.mark.unit          # Test unitario (default para domain/)
@pytest.mark.integration   # Test con BD de test
@pytest.mark.postgres      # Requiere PostgreSQL
@pytest.mark.slow          # Test lento (>1s)
```

### Fixtures
```python
# Datos de dominio
profesional_cardiologia
ubicacion_buenos_aires
especialidad_cardiologia

# Mocks
mock_profesional_repository
mock_catalogo_repository

# BD real
db_session
db_con_datos_base
seed_postgres_data
```

## 📝 Agregar Nuevos Tests

### Test Unitario (Domain)
```python
# tests/domain/test_mi_feature.py
def test_mi_logica_de_negocio():
    resultado = mi_funcion()
    assert resultado == esperado
```

### Test de API (con Mock)
```python
# tests/api/test_mi_endpoint.py
def test_mi_endpoint(client, mock_repos):
    response = client.post("/endpoint", json=payload)
    assert response.status_code == 200
```

### Test de Integración (con BD)
```python
# tests/integration/test_mi_feature_bd.py
@pytest.mark.integration
def test_con_bd_real(client, db_session):
    # Crear datos en BD
    # Hacer request
    # Verificar resultado
    pass
```

## 🐛 Debugging Tests

```bash
# Ver output completo
pytest tests/api/test_busqueda.py::test_nombre -vvs

# Solo tests que fallan
pytest tests/ --lf

# Con debugger
pytest tests/domain/test_buscador.py --pdb

# Con coverage
pytest tests/ --cov=app --cov-report=term-missing
```

## 📚 Referencias

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
