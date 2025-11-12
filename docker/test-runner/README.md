Docker test runner (aislado)
=============================

Este directorio contiene un Dockerfile y un docker-compose para ejecutar los tests
de manera aislada dentro de un contenedor que NO monta volúmenes del host. El
contenedor copia el proyecto durante el build y ejecuta pytest; por tanto no
modifica archivos fuera del contenedor.

Uso (PowerShell):

1) Construir y ejecutar con docker-compose (recomendado):

```powershell
# Construir e iniciar (ejecuta pytest)
docker compose -f docker/test-runner/docker-compose.yml up --build --remove-orphans --exit-code-from test-runner
```

2) Ejecutar build + run manual (alternativa):

```powershell
docker build -f docker/test-runner/Dockerfile -t athomered-tests .
docker run --rm athomered-tests
```

3) Ejecutar solo los tests de auth (ejemplo):

```powershell
$env:PYTEST_ARGS = 'tests/domain/test_auth_service.py -q'
docker compose -f docker/test-runner/docker-compose.yml up --build
```

Notas de seguridad y aislamiento:
- No se montan volúmenes del host. El contenedor contiene una copia del repo.
- El proceso se ejecuta como usuario no-root `runner` dentro del contenedor.
- Si necesitás acceso a la salida completa de pytest, quita `-q` o adapta PYTEST_ARGS.
