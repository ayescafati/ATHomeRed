# ATHomeRed – API (MVP)

**Autores:**  
- Llanes, Federico Nicolás · [FedeLlanes](https://github.com/FedeLlanes)
- Rodríguez Puertas, Miguel Ignacio · [mirpuertas](https://github.com/mirpuertas)  
- Scafati, Ayelén Luján · [ayescafati](https://github.com/ayescafati)  

**Materia:** Programación II – UNSAM  
**Cuatrimestre:** 2C 2025 

---

## Índice
- [¿Qué es ATHomeRed?](#qué-es-athomered)
- [Problema que resuelve](#problema-que-resuelve)
- [Valor que aporta](#valor-que-aporta)
- [Estado actual del proyecto](#estado-actual-del-proyecto)
  - [Estructura actual del repositorio](#estructura-actual-del-repositorio)
  - [Implementaciones](#implementaciones)
  - [Usuarios](usuarios)
  - [Clases principales](#clases-principales)
  - [Patrones y arquitectura](#patrones-y-arquitectura)
- [Diagramas UML](#diagramas-uml)
  - [Diagrama de clases](#diagrama-de-clases)
  - [Diagrama de base de datos](#diagrama-de-bases-de-datos)
- [Tecnologías](#tecnologías)
- [Configuración](#configuración)
- [Puesta en marcha](#puesta-en-marcha)
  - [Local](#local)
  - [Con Docker (DB)](#con-docker-db)
  - [Migraciones](#migraciones)
- [API rapida](#api-rápida)
- [Licencia](#licencia)
  
---

## ¿Qué es ATHomeRed?

**AT Home Red** es una Web API que busca formalizar y digitalizar la conexión entre familias (representadas por un **Responsable/Solicitante**) y profesionales del área de la salud domiciliaria, como **acompañantes terapéuticos** y **enfermeros/as**.

El sistema se apoya en una arquitectura **orientada a objetos en Python**, aplicando los patrones **Observer** y **Strategy** para permitir un diseño flexible, escalable y mantenible.

## Problema que resuelve

En Argentina, tanto la enfermería domiciliaria como el acompañamiento terapéutico presentan déficits estructurales:

- **Alta informalidad laboral:** vínculos laborales precarios, sin intermediación formal.  
- **Falta de plataformas seguras:** la búsqueda de profesionales se realiza “de boca en boca”.  
- **Desigualdad geográfica:** zonas rurales con poca oferta y sin trazabilidad.  
- **Ausencia de validación profesional:** dificultad para verificar matrículas o credenciales.

**AT Home Red** propone una red digital segura que conecta a **pacientes** con **acompañantes terapéuticos o enfermeros**, incorporando geolocalización, disponibilidad horaria y validación profesional.


## Valor que aporta

- **Para los pacientes y responsables:** acceso rápido a profesionales confiables y cercanos.  
- **Para los profesionales:** visibilidad, formalización laboral y nuevas oportunidades de trabajo.  
- **Para el sistema de salud:** disminución de la informalidad y bases para integración futura con obras sociales o prepagas.
  
## Estado actual del proyecto

AT Home Red (FastAPI) implementa los flujos centrales de un sistema de reservas domiciliarias (usuarios, profesionales, búsqueda y reservas) sobre una arquitectura por capas con patrones **Strategy**, **Observer** y **Repository**.

### Estructura actual del repositorio

```
ATHomeRed-main/
├── .env                               # Variables locales (no commitear)
├── .gitattributes                     # Normaliza EOL/atributos en Git
├── .gitignore                         # Archivos/carpetas a ignorar por Git
├── alembic.ini                        # Configuración de Alembic
├── LICENSE                            # Licencia del proyecto
├── requirements.txt                   # Dependencias de Python (pip)
├── alembic/
│   ├── env.py                         # Bootstrapping de Alembic (DB/session)
│   ├── script.py.mako                 # Template para nuevas migraciones
│   └── versions/
│       ├── .gitkeep                   # Placeholder de carpeta
│       └── 20251030_1951_bb44aaa63eb1_initial_migration.py  # Migración inicial
├── app/
│   ├── __init__.py
│   ├── main.py                        # Instancia FastAPI y registra routers
│   ├── api/
│   │   ├── dependencies.py            # Dependencias (DI) para routers/servicios
│   │   ├── event_bus.py               # Instancia y wiring del EventBus
│   │   ├── policies.py                # IntegrityPolicies (reglas/validaciones)
│   │   ├── schemas.py                 # DTOs Pydantic (request/response)
│   │   └── routers/                   # Routers por recurso (contrato HTTP)
│   │       ├── auth.py                # Router de autenticación real (MVP): registro, login y me con JWT
│   │       ├── busqueda.py            # Router para búsqueda de profesionales (Strategy)
│   │       ├── consultas.py           # Router para gestión de consultas/citas médicas
│   │       ├── pacientes.py           # Router para gestión de pacientes
│   │       ├── profesionales.py       # Router para gestión de profesionales
│   │       └── valoraciones.py        # Router para gestión de valoraciones
│   ├── docs/
│   │   └── uml/                       # Diagramas UML
│   ├── domain/                        # Capa de dominio (sin dependencias infra)
│   │   ├── enumeraciones.py           # Enums de dominio (EstadoCita, DíaSemana)
│   │   ├── eventos.py                 # Eventos de dominio (CitaCreada, CitaConfirmada, etc.)
│   │   ├── entities/
│   │   │   ├── agenda.py              # Entidad Cita (lógica de estados/negocio)
│   │   │   ├── catalogo.py            # Especialidad, Tarifa, Publicacion, FiltroBusqueda
│   │   │   ├── usuarios.py            # Usuario/Profesional/Solicitante (Responsable)
│   │   │   └── valoraciones.py        # Entidades de valoraciones/opiniones
│   │   ├── observers/
│   │   │   └── observadores.py        # Observer/Subject + EventBus (publish/subscribe, suscribir_observer); NotificadorEmail (demo print/log), AuditLogger (auditoría).
│   │   ├── strategies/
│   │   │   ├── buscador.py            # Contexto Strategy (ejecuta estrategias)
│   │   │   ├── estrategia_asignacion.py # Estrategias de asignación/validación
│   │   │   └── estrategia.py          # Contratos e implementaciones de búsqueda
│   │   └── value_objects/
│   │       └── objetos_valor.py       # Ubicacion, Disponibilidad, Matricula (VOs)
│   ├── infra/                         # Capa de infraestructura (ORM/repos/servicios)
│   │   ├── persistence/               # Modelos ORM y utilidades DB
│   │   │   ├── agenda.py              # Define modelos ORM para agenda, disponibilidades y consultas de profesionales
│   │   │   ├── auth.py                # Define modelos ORM para autenticación: refresh tokens y su relación con usuarios
│   │   │   ├── base.py                # Define la clase base declarativa y el esquema para los modelos ORM
│   │   │   ├── database.py            # Configura la conexión SQLAlchemy y la sesión de base de datos para la aplicación
│   │   │   ├── matriculas.py          # Define el modelo ORM de SQLAlchemy para matrículas profesionales y su relación con profesionales
│   │   │   ├── paciente.py            # Define el modelo ORM de SQLAlchemy para la entidad Paciente y sus relaciones
│   │   │   ├── perfiles.py            # Define modelos ORM de SQLAlchemy para perfiles de profesional y solicitante, con sus relaciones
│   │   │   ├── publicaciones.py       # ORM de publicaciones de profesionales
│   │   │   ├── relaciones.py          # Tablas relacionales auxiliares
│   │   │   ├── servicios.py           # ORM de catálogo/servicios
│   │   │   ├── ubicacion.py           # ORM de direcciones/geo
│   │   │   ├── usuarios.py            # ORM de usuarios
│   │   │   └── valoraciones.py        # ORM de valoraciones
│   │   └──  repositories/                # Repositorios (aislan dominio de ORM/DB)
│   │       ├── auth_repository.py        # Repositorio para operaciones de autenticación: gestión de refresh tokens y login en la base de datos
│   │       ├── catalogo_repository.py    # Repositorio para consultar y gestionar el catálogo de especialidades y servicios
│   │       ├── consulta_repository.py    # Repositorio para gestionar consultas médicas: creación, búsqueda y actualización en la base de datos
│   │       ├── direccion_repository.py   # Repositorio para gestionar direcciones: alta, búsqueda y actualización en la base de datos
│   │       ├── paciente_repository.py    # Repositorio para gestionar pacientes: alta, búsqueda y actualización en la base de datos.
│   │       ├── profesional_repository.py # Repositorio para gestionar profesionales: alta, búsqueda y actualización en la base de datos
│   │       ├── usuario_repository.py     # Repositorio para gestionar usuarios: alta, búsqueda y actualización en la base de datos
│   │       └── valoracion_repository.py  # Repositorio para gestionar valoraciones: alta, búsqueda y actualización de valoraciones de profesionales
│   ├── services/
│   │   └── auth_service.py            # Servicio de autenticación: registro, login, generación y validación de tokens JWT
│   ├── static/
│   │   ├── app.js                     # JavaScript para la interfaz web: maneja interacciones y peticiones de la aplicación
│   │   └── index.html                 # Página HTML principal de la aplicación web; estructura y muestra la interfaz al usuario
├── docker/
│   └── docker-compose.yml             # Orquesta servicios y contenedores Docker necesarios para el entorno de desarrollo y pruebas
└── scripts/                           # Scripts utilitarios de desarrollo/ops
    ├─ dev/
    │  ├─ __init__.py
    │  ├─ check_db.py                  # Verifica la conexión y disponibilidad de la base de datos del entorno de desarrollo
    │  ├─ ejemplo_catalogo.py          # Ej. de uso del catálogo: consulta y muestra especialidades y servicios disponibles
    │  ├─ smoke_auth.py                # Script de prueba rápida para verificar el funcionamiento básico del sistema de autenticación
    │  ├─ test_auth_completo.py        # Script de prueba completa para validar todos los endpoints del flujo de autenticación
    │  ├─ test_connection.py           # Script para probar la conexión básica a la base de datos del sistema
    │  └─ test-helpers.ps1             # Verifica que la aplicación pueda conectarse correctamente a la base de datos configurada
    ├─ seed/
    │  ├─ __init__.py
    │  ├─ demo_data.py
    │  └─ seed_especialidades.py
    └─ setup/
       ├─ __init__.py
       ├─ apply_sql.py
       ├─ create_schema.py
       └─ init_db.py

```

### Implementaciones

#### **API y routers por recurso**
La aplicación se instancia en `app/main.py` y publica endpoints agrupados por dominio bajo `app/api/routers/` (auth, búsqueda, consultas, pacientes, profesionales y valoraciones). Esta organización mantiene el contrato HTTP estable y facilita la navegación desde `/docs`.

#### **Autenticación y seguridad** 
El flujo está operativo con **hash Argon2** y **JWT HS256**. El router `app/api/routers/auth.py` (prefijo `/api/v1/auth`) expone: `POST /register-json` (201) para alta de usuario con **roles excluyentes** (profesional/solicitante; si no se especifica, default a solicitante); `POST /login` que devuelve `{access_token, token_type}` y aplica **bloqueo temporal por intentos fallidos** (`423 Locked` si bloqueado; `401` para credenciales inválidas); y `GET /me`, que lee `Authorization: Bearer <token>` y retorna el perfil básico. La lógica vive en `app/services/auth_service.py` (`hash_password/verify_password`, `crear_access_token/validar_access_token` con `AT_HOME_RED_SECRET` y `ACCESS_TOKEN_EXPIRE_MINUTES`) y el repositorio `app/infra/repositories/usuario_repository.py` gestiona `obtener_por_email`, `incrementar_intentos_fallidos`, `esta_bloqueado`, `resetear_intentos_fallidos` y `actualizar_ultimo_login`.

#### **Persistencia y migraciones** 
El modelo de datos está implementado en **SQLAlchemy** y versionado con **Alembic** (migración inicial en `alembic/versions/…`). La capa de **repositorios** realiza el mapeo ORM↔dominio y encapsula el CRUD. La base corre en **PostgreSQL** local o vía **Docker Compose**; la configuración se centraliza en `database.py`/`base.py` con `DATABASE_URL`.

#### **Reservas / consultas** 
El módulo de **consultas** ofrece creación (`POST /`, 201), lectura (`GET /{consulta_id}`), actualización (`PUT /{consulta_id}`) y cancelación (`DELETE /{consulta_id}`, 204), e incorpora **transiciones de estado** explícitas: confirmar (`POST /{consulta_id}/confirmar`), completar (`POST /{consulta_id}/completar`) y reprogramar (`POST /{consulta_id}/reprogramar`, requiere `fecha`, `hora_inicio`, `hora_fin`). Además, incluye listados filtrables por profesional (`GET /profesional/{profesional_id}` con `desde`, `hasta`, `solo_activas`) y por paciente (`GET /paciente/{paciente_id}` con `desde`, `solo_activas`). Antes de persistir se aplican **políticas de integridad** mediante `IntegrityPolicies` (profesional verificado/activo, pertenencia del paciente al solicitante, solicitante activo) y **reglas de negocio** (fin > inicio, no fechas pasadas y **anti-solapamiento**). La **ubicación** se modela como `Ubicacion` (VO) a partir del DTO y, provisoriamente, se persiste usando la **dirección del profesional** como `direccion_id`. Cada transición publica su **evento de dominio** en el `EventBus` (`CitaCreada`, `CitaConfirmada`, `CitaCancelada`, `CitaCompletada`, `CitaReprogramada`), como se verá en **Notificaciones (Observer)** y en la sección **Patrones y arquitectura**.

#### **Búsqueda y asignación (Strategy)** 
El router de búsqueda construye un `FiltroBusqueda` a partir del DTO, **resuelve la especialidad por nombre→ID** usando el catálogo (404 si no existe) y **valida ID** cuando corresponde. En función de los criterios, selecciona dinámicamente la estrategia del dominio (`BusquedaCombinada`, `BusquedaPorEspecialidad` o `BusquedaPorZona`) y ejecuta el **contexto `Buscador`**. Endpoints: `POST /profesionales` (retorna `profesionales`, `total` y `criterios_aplicados`), `GET /especialidades` (lista desde DB), `GET /ubicaciones/provincias`, `GET /ubicaciones/provincias/{provincia_id}/departamentos` y `GET /ubicaciones/departamentos/{departamento_id}/barrios`. Si no se especifica **ningún criterio válido** se responde 400; nombres/IDs de especialidad inexistentes devuelven 404; errores inesperados, 500. Como se verá en **Patrones y arquitectura**, este diseño permite **cambiar estrategias sin tocar los endpoints**.

#### **Notificaciones (Observer)** 
El sistema emite **eventos de dominio** y los procesa mediante un **EventBus**. El bus admite dos modalidades de suscripción: **handlers funcionales** (`suscribir(tipo, handler)`) y **observers tradicionales** (`suscribir_observer(tipo, observer)`), ambos definidos en `app/domain/observers/observadores.py`. En modo demo están activos: `NotificadorEmail` (imprime por consola) y `AuditLogger` (registra en logs). La instancia y el wiring viven en `app/api/event_bus.py`. Está **preparado para SMTP** vía variables de entorno, como se verá en **Patrones y arquitectura**.

#### **Operativa y utilidades** 
El repositorio incluye **Docker Compose** para la DB y **scripts de verificación** (smoke de auth, conexión y set-up) para acelerar el arranque local. Se provee `.env.example` con las variables críticas y la documentación **OpenAPI/Swagger UI** generada automáticamente por FastAPI.

### Usuarios

- **Usuario (abstracta).** Persona con cuenta de acceso que sirve como base para los dos roles operativos del sistema. Atributos: `id`, `nombre`, `apellido`, `email`, `celular`, `Ubicacion`, `activo` (True por defecto). Métodos útiles: `nombre_completo`, `activar`/`desactivar` y `datos_contacto`.

- **Profesional.** Hereda de `Usuario` y ofrece servicios de salud. Campos específicos: `verificado` (bool), `especialidades` (`Especialidad`), `disponibilidades` (`Disponibilidad`) y `matriculas` (`Matricula`). Expone `agregar_disponibilidad` para gestionar su agenda.

- **Solicitante.** Hereda de `Usuario` y gestiona turnos propios o de personas a su cargo. Mantiene una lista de `pacientes` y el método `agregar_paciente`. En casos de dependientes, el **email/celular de contacto** se toma del Solicitante.

- **Paciente.** Persona atendida; **no** hereda de `Usuario` (puede no tener cuenta). Atributos: `id`, `nombre`, `apellido`, `fecha_nacimiento`, `Ubicacion`, `solicitante_id`, `relacion` (p. ej. `"self"`, `"hijo/a"`, `"tutor/a"`), `notas`. Métodos de conveniencia: `edad(hoy)`, `es_menor_de_edad()`, `es_auto_gestionado()`.

**Nota de diseño.** Se separa explícitamente “quién tiene cuenta” (Usuario) de “quién recibe la atención” (Paciente). Esto permite que un **Solicitante** administre varios **Pacientes** y centraliza los datos de contacto. `Ubicacion` es un value object compartido; la verificación de profesionales y otras reglas viven fuera de estas clases (policies/servicios).


### Clases principales

La siguiente tabla resume las clases, value objects y componentes relevantes tal como están nombrados e implementados en el repositorio. Útil para referencia rápida durante la defensa.

###### Entidades y value objects

| Clase / Estructura                | Rol en el sistema (ubicación) |
|-----------------------------------|--------------------------------|
| `Usuario` *(abstracta)*           | Base de usuarios. `app/domain/entities/usuarios.py` |
| `Profesional`                     | Ofrece servicios; tiene `especialidades`, `disponibilidades` y `matriculas`. `entities/usuarios.py` |
| `Solicitante` *(Responsable)*     | Gestiona turnos de uno o varios `Paciente`. `entities/usuarios.py` |
| `Paciente`                        | Persona atendida (puede no ser usuario). `entities/usuarios.py` |
| `Cita` *(Consulta en API)*        | Turno con estados y métodos de negocio (`confirmar`, `cancelar`, `completar`, `reprogramar`; `puede_modificarse`). `app/domain/entities/agenda.py` |
| `Ubicacion` *(value object)*      | Dirección/lat-long y validaciones. `app/domain/value_objects/objetos_valor.py` |
| `Disponibilidad` *(value object)* | Días/horarios de trabajo. `value_objects/objetos_valor.py` |
| `Matricula` *(value object)*      | Datos de matrícula profesional. `entities/usuarios.py` |
| `Especialidad`                    | Tipo de servicio. `app/domain/entities/catalogo.py` |
| `Tarifa`                          | Precio/vigencia por especialidad. `entities/catalogo.py` |
| `Publicacion`                     | Info pública del profesional. `entities/catalogo.py` |
| `FiltroBusqueda`                  | Criterios (zona, especialidad, texto). `entities/catalogo.py` |

##### Autenticación

| Componente / DTO         | Rol (ubicación) |
|--------------------------|-----------------|
| `AuthService`            | Lógica de hash Argon2, JWT HS256, registro/login, intents/bloqueo. `app/services/auth_service.py` |
| `UsuarioRepository`      | Acceso a usuarios: alta, búsquedas, intents, último login. `app/infra/repositories/usuario_repository.py` |
| `RegisterRequest`        | DTO de registro. `app/api/schemas.py` |
| `LoginRequest`           | DTO de login. `app/api/schemas.py` |
| `TokenSchema`            | Respuesta `{access_token, token_type}`. `app/api/schemas.py` |
| `auth.py` (router)       | Endpoints `/register-json` (201), `/login`, `/me` (Bearer). `app/api/routers/auth.py` |

##### Búsqueda y asignación (Strategy)

| Clase / Interfaz            | Rol (módulo / archivo) |
|-----------------------------|------------------------|
| `Buscador`                  | Contexto que aplica la estrategia. `app/domain/strategies/buscador.py` |
| `Estrategia`                | Contrato de estrategias. `app/domain/strategies/estrategia.py` |
| `BusquedaPorZona`           | Estrategia por ubicación. `app/domain/strategies/estrategia.py` |
| `BusquedaPorEspecialidad`   | Estrategia por especialidad. `app/domain/strategies/estrategia.py` |
| `BusquedaCombinada`         | Combina criterios (zona + especialidad). `app/domain/strategies/estrategia.py` |
| `EstrategiaAsignacion`      | Políticas de asignación/validación (p. ej., disponibilidad, matrícula). `app/domain/strategies/estrategia_asignacion.py` |

##### Notificaciones (Observer)

| Clase / Servicio   | Rol (ubicación) |
|--------------------|------------------|
| `Observer` / `Subject` | Base del patrón. `app/domain/observers/observadores.py` |
| `EventBus`         | Publicación/suscripción: `suscribir(tipo, handler)` y `suscribir_observer(tipo, observer)`. Clase en `domain/observers/observadores.py`; instancia/wiring en `app/api/event_bus.py`. |
| `NotificadorEmail` | Observador demo: simula envío por consola para eventos de cita. `app/domain/observers/observadores.py` |
| `AuditLogger`      | Observador de auditoría (loggea `[AUDIT] Evento: ...`). `app/domain/observers/observadores.py` |
| Eventos de `Cita`  | `CitaCreada`, `CitaConfirmada`, `CitaCancelada`, `CitaCompletada`, `CitaReprogramada`. `app/domain/eventos.py` |

###### Enumeraciones

| Enum            | Observación (ubicación) |
|-----------------|-------------------------|
| `EstadoCita`    | Estados reales del flujo (p. ej., `PENDIENTE`, `CONFIRMADA`, `COMPLETADA`, `CANCELADA`, `REPROGRAMADA`). **Usar exactamente los definidos en** `app/domain/enumeraciones.py`. |
| `DiaSemana`     | LUNES..DOMINGO para disponibilidades. `app/domain/enumeraciones.py` |


  
### Patrones y arquitectura

El proyecto aplica tres patrones de diseño principales dentro de una arquitectura por capas: **Strategy**, **Observer** y **Repository**. Además, se utilizan decoradores de Python de forma transversal (por ejemplo, en los routers de FastAPI), aunque eso no implica que el patrón GoF *Decorator* esté modelado como objeto de dominio; es simplemente el uso idiomático del lenguaje y del framework.

El patrón **Strategy** es el eje del módulo de búsqueda/asignación. Las interfaces y estrategias viven en `app/domain/strategies/` (por ejemplo, `estrategia.py`, `buscador.py` y `estrategia_asignacion.py`) y se invocan desde el router `app/api/routers/busqueda.py`. Esta organización permite intercambiar la lógica de búsqueda o de asignación sin tocar los endpoints: el router selecciona la estrategia activa y la ejecuta. Actualmente hay al menos dos variantes implementadas para cubrir escenarios de búsqueda distintos.

El **Observer** se implementa con un *EventBus* simple para reaccionar a eventos de dominio sin acoplar emisores y efectos colaterales. El bus está en `app/api/event_bus.py`, los eventos en `app/domain/eventos.py` y los observadores (por ejemplo, un `NotificadorEmail`) en `app/domain/observers/`. En el estado actual funciona en **modo demo** (notifica por consola con `print`). Para producción se prevé vincularlo a un servidor de correo (SMTP) configurado vía `.env` y, si hace falta, sumar otros observadores como auditoría o webhooks sin modificar el código que emite los eventos.

El patrón **Repository** separa el dominio de los detalles de persistencia. Los repositorios concretos residen en `app/infra/repositories/` y los modelos/ORM y utilidades de base de datos en `app/infra/persistence/`. Aunque no es un patrón GoF, es un patrón de arquitectura estándar en la industria y permite mantener el dominio independiente de SQLAlchemy y del esquema físico, facilitando pruebas, mocks y cambios de tecnología.

La **arquitectura en capas** se refleja en tres espacios principales: `app/domain/` (entidades, eventos, value objects y estrategias, sin dependencias de infraestructura), `app/infra/` (ORM, repositorios y servicios de aplicación como autenticación) y `app/api/` (routers, dependencias, esquemas, *event bus* y *policies*). Esta separación hace que el dominio no dependa de la infraestructura y que la API publique casos de uso manteniendo el acoplamiento bajo control.

En nuestro proyecto usamos decoradores de forma transversal y concreta: declaramos endpoints con `@app.get("/health")` y `@app.get("/")` en `app/main.py`, y en `app/api/routers/busqueda.py` definimos la ruta de búsqueda con `@router.post("/profesionales", response_model=BusquedaProfesionalResponse)`. En ese mismo router combinamos esos decoradores de ruta con la inyección de dependencias vía `Depends(...)` para obtener repositorios como `get_profesional_repository` y `get_catalogo_repository` sin acoplarlos a la vista. En el módulo de políticas (`app/api/policies.py`) usamos decoradores del lenguaje, por ejemplo `@staticmethod` en `validar_solicitante_es_dueno`, para expresar reglas de autorización como utilidades claras y reutilizables. Incluso en las pruebas aplicamos decoradores de Pytest, como `@pytest.mark.authflow` y `@pytest.mark.auth_neg` en `tests/api/test_auth.py`, para marcar escenarios y filtrar ejecuciones. En espíritu, estos decoradores “añaden comportamiento” sin modificar los objetos, de un modo análogo al patrón GoF *Decorator*; sin embargo, en nuestro código su rol es estrictamente idiomático e infraestructural de Python, FastAPI y Pytest, y no modelamos un *Decorator* como objeto de dominio.

En cuanto al **estado actual**, el proyecto ya cuenta con Strategy operativo en el router de búsqueda, Observer funcional en modo demostrativo, y Repository para aislar dominio y persistencia; además, hay esquema de base de datos y endpoints integrados a la API. 

---

## Diagramas UML

El proyecto incluye **dos** diagramas UML: uno de **clases** (dominio y patrones) y otro de **base de datos** (esquema físico).

### Diagrama de clases 

- **[Diagrama de clases (MVP + búsqueda)](app/docs/uml/clases-uml-v1.svg)**

El diagrama de clases refleja el estado actual del **dominio** y los **patrones** aplicados. La terminología está unificada: se usa **Solicitante** (no “Responsable”) y se muestra **Cita/Consulta** como la misma entidad de negocio.

### Qué muestra

- **Entidades principales**
  - `Usuario` *(abstracta)*, `Solicitante`, `Profesional`, `Paciente`
  - *Value Objects*: `Ubicacion`, `Disponibilidad`, `Matricula`
  - Catálogo/servicios: `Especialidad`, `Tarifa`, `Publicacion`
  - Agenda: `Cita`/`Consulta` (con `EstadoCita`)

- **Relaciones clave**
  - `Solicitante` **1..*** `Paciente` (un solicitante puede gestionar varios pacientes)
  - `Profesional` **1..*** `Disponibilidad`
  - `Profesional` ***..*** `Especialidad`
  - `Cita` **1..1** `Profesional` y **1..1** `Paciente`; referencia una `Ubicacion`

- **Patrones representados**
  - **Strategy (búsqueda/asignación):** `Buscador` (contexto), `Estrategia` (interfaz),
    `BusquedaPorZona`, `BusquedaPorEspecialidad`, `BusquedaCombinada`
  - **Observer (notificaciones/auditoría):** `Observer`, `Subject`, `NotificadorEmail`,
    `AuditLogger`, `Event` (eventos de `Cita`)

### Diagrama de bases de datos

- **[Diagrama de base de datos](app/docs/uml/db-uml-v1.svg)**


---

## Tecnologías

- **Lenguaje**: Python 3.11+
- **API**: FastAPI
- **Servidor de aplicación:** Uvicorn
- **Validación de datos:** Pydantic
- **ORM**: SQLAlchemy
- **DB**: PostgreSQL
- **Migraciones**: Alembic
- **Autenticación / seguridad:** JWT (HS256, `python-jose`) + Argon2 (`passlib`)
- **Configuración:** variables de entorno `.env` (python-dotenv)
- **Contenedores**: Docker Compose (servicio de Postgres)
- **Docs:** OpenAPI / Swagger UI generadas por FastAPI

---

## Configuración

Copiá el ejemplo y completá valores:
```bash
cp .env.example .env
```

Variables relevantes:
- `DATABASE_URL` *(o variables individuales para host/puerto/usuario)*
- `AT_HOME_RED_SECRET` *(clave JWT)*
- `ACCESS_TOKEN_EXPIRE_MINUTES` *(minutos de validez del token)*
- **Observer (opcional para producción):**
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`

---

## Puesta en marcha

### Local
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
# Abrí http://localhost:8000 y /docs
```

### Con Docker (DB)
```bash
docker compose -f docker/docker-compose.yml up -d   # levanta PostgreSQL
alembic upgrade head                                 # aplica migraciones
uvicorn app.main:app --reload                        # levanta la API
```

### Migraciones
```bash
# Crear una nueva migración
alembic revision -m "descripcion" --autogenerate

# Aplicar
alembic upgrade head

# Revertir
alembic downgrade -1
```

---

## API rápida

**Auth (MVP)** – prefijo `/api/v1/auth`
- `POST /api/v1/auth/register-json` – registrar usuario
- `POST /api/v1/auth/login` – login (devuelve `access_token`)
- `GET /api/v1/auth/me` – perfil del usuario (requiere Bearer token)

**Ejemplo de login (cURL)**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"probando@gmail.com","password":"Prueba123."}'
```
---

## Licencia

Este proyecto se publica bajo la licencia incluida en [`LICENSE`](./LICENSE).