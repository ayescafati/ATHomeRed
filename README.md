# ATHomeRed – API (MVP)

**Autores:**
- Llanes, Federico Nicolás · [FedeLlanes](https://github.com/FedeLlanes)
- Rodríguez Puertas, Miguel Ignacio · [mirpuertas](https://github.com/mirpuertas)
- Scafati, Ayelén Luján · [ayescafati](https://github.com/ayescafati)

**Materia:** Programación II – UNSAM
**Cuatrimestre:** 2C 2025

**Deploy (Render):** [https://athomered-1.onrender.com](https://athomered-1.onrender.com)  
**Docs (Swagger UI):** [https://athomered-1.onrender.com/docs](https://athomered-1.onrender.com/docs)

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
- [Diagrama UML](#diagrama-uml)
- [Presentación (Canva)](#presentación-canva)
- [Tecnologías](#tecnologías)
- [Configuración](#configuración)
- [Puesta en marcha](#puesta-en-marcha)
  - [Local](#local)
  - [Producción (Render)](#producción-render)
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
ATHomeRed/
├── .dockerignore                     # Archivos que no se copian a la imagen de Docker
├── .gitattributes                    # Normaliza EOL/atributos en Git
├── .gitignore                        # Patrones a ignorar por Git (venv, .env, etc.)
├── .pre-commit-config.yaml           # Hooks de formato/lint antes de cada commit
├── Dockerfile                        # Imagen principal de la API (modo app)
├── LICENSE                           # Licencia del proyecto
├── README.md                         # Documentación principal del proyecto
├── alembic.ini                       # Config de Alembic para migraciones
├── alembic_test.ini                  # Config alternativa de Alembic (entorno de test)
├── pytest.ini                        # Configuración de pytest
├── requirements.txt                  # Dependencias básicas de la app
├── requirements-dev.txt              # Dependencias extra para desarrollo/testing
├── docs/
│   └── uml/
│       └── UML_ATHomeRed_Domain      # Diagrama UML (dominio)
├── alembic/
│   ├── env.py                        # Bootstrap de Alembic (engine, metadata, etc.)
│   ├── script.py.mako                # Template para generar nuevas migraciones
│   └── versions/                     # Historias de migraciones (una por versión de esquema)
│       └── bb44aaa63eb1_initial_migration.py   # Migración inicial (creación de tablas)
├── app/
│   ├── __init__.py
│   ├── main.py                       # Punto de entrada de FastAPI (creación de la app)
│   ├── api/                          # Capa de API (routers, schemas, policies)
│   │   ├── __init__.py
│   │   ├── dependencies.py           # Dependencias comunes (DB, servicios, etc.)
│   │   ├── event_bus.py              # Wiring del EventBus y observers
│   │   ├── exceptions.py             # Excepciones y handlers HTTP
│   │   ├── policies.py               # Policies de validación/autorización de la API
│   │   ├── schemas.py                # DTOs / modelos Pydantic expuestos por la API
│   │   └── routers/                  # Routers de cada “módulo” funcional
│   │       ├── __init__.py
│   │       ├── auth.py               # Endpoints de autenticación
│   │       ├── busqueda.py           # Endpoints de búsqueda de profesionales
│   │       ├── consultas.py          # Endpoints de gestión de consultas/citas
│   │       ├── pacientes.py          # Endpoints de pacientes
│   │       ├── profesionales.py      # Endpoints de profesionales
│   │       └── valoraciones.py       # Endpoints de valoraciones/opiniones
│   ├── domain/                       # Modelo de dominio (entidades, eventos, estrategias)
│   │   ├── entities/                 # Entidades de dominio
│   │   │   ├── agenda.py             # Define la entidad Agenda del dominio: gestiona turnos, horarios y disponibilidad de profesionales
│   │   │   ├── catalogo.py           # Entidad de dominio que representa el catálogo de servicios, especialidades o profesionales disponibles
│   │   │   ├── usuarios.py           # Entidad principal que representa usuarios: pacientes, profesionales y sus datos relevantes
│   │   │   └── valoraciones.py       # Entidad que gestiona valoraciones, opiniones y puntajes sobre profesionales o servicios
│   │   ├── enumeraciones.py          # Enums (roles, estados, etc.)
│   │   ├── eventos.py                # Eventos de dominio
│   │   ├── observers/                # Implementación del patrón Observer
│   │   │   ├── __init__.py
│   │   │   └── observadores.py       # Observers y contrato de Observer/Subject
│   │   ├── strategies/               # Estrategias de dominio (patrón Strategy)
│   │   │   ├── __init__.py
│   │   │   ├── buscador.py           # Contexto `Buscador` y estrategias de búsqueda
│   │   │   ├── estrategia.py         # Interfaz base de estrategia
│   │   │   └── estrategia_asignacion.py  # Estrategias de asignación de profesionales
│   │   └── value_objects/            # Objetos valor (VO) como Ubicación, etc.
│   │       ├── __init__.py
│   │       └── objetos_valor.py
│   ├── infra/                        # Infraestructura: ORM, repositorios, DB
│   │   ├── __init__.py
│   │   ├── persistence/              # Modelos ORM y configuración de base de datos
│   │   │   ├── base.py               # Base declarativa de SQLAlchemy
│   │   │   ├── database.py           # Engine, sesión y helpers de conexión
│   │   │   ├── agenda.py             # Modelo ORM de la agenda: mapea turnos y disponibilidad a la base de datos relacional
│   │   │   ├── auth.py               # Modelo ORM para autenticación: gestiona usuarios, contraseñas y tokens en la base de datos
│   │   │   ├── matriculas.py         # Modelo ORM para matrículas profesionales: almacena y valida credenciales de profesionales registrados
│   │   │   ├── paciente.py           # Modelo ORM para pacientes: almacena datos personales y de salud en la base de datos
│   │   │   ├── perfiles.py           # Modelo ORM de perfiles: representa profesionales y solicitantes, relaciones y atributos clave
│   │   │   ├── publicaciones.py      # Modelo ORM de publicaciones: artículos, anuncios o contenidos de profesionales
│   │   │   ├── relaciones.py         # Modelo ORM de relaciones: vínculos entre usuarios, profesionales y pacientes
│   │   │   ├── servicios.py # Modelo ORM de servicios: especialidades, tipos de atención y sus relaciones
│   │   │   ├── ubicacion.py # Modelo ORM de ubicaciones: direcciones y localización de usuarios o servicios
│   │   │   ├── usuarios.py # Modelo ORM de usuarios: datos de cuenta y perfil general
│   │   │   └── valoraciones.py # Modelo ORM de valoraciones: opiniones y puntajes sobre profesionales o servicios
│   │   └── repositories/             # Repositorios (puente dominio ↔ ORM)
│   │       ├── auth_repository.py # Acceso y operaciones de autenticación (usuarios, contraseñas, tokens)
│   │       ├── catalogo_repository.py # Acceso y gestión del catálogo de servicios y especialidades
│   │       ├── consulta_repository.py # Operaciones sobre consultas/citas entre pacientes y profesionales
│   │       ├── direccion_repository.py # Gestión de direcciones y ubicaciones de usuarios
│   │       ├── paciente_repository.py # Acceso y manipulación de datos de pacientes
│   │       ├── profesional_repository.py # Acceso y gestión de datos de profesionales
│   │       ├── usuario_repository.py # Operaciones generales sobre usuarios del sistema
│   │       └── valoracion_repository.py # Acceso y gestión de valoraciones y opiniones
│   ├── services/
│   │   └── auth_service.py           # Lógica de autenticación / manejo de tokens
│   └── static/                       # UI mínima embebida
│       ├── index.html                # Front de demo para probar la API
│       └── app.js                    # JavaScript del front de demo
├── docker/
│   ├── Dockerfile                    # Imagen para entorno de desarrollo/test
│   └── docker-compose.yml            # Orquestación local (API + Postgres)
├── scripts/
│   ├── database/                     # Utilidades para la base de datos
│   │   ├── __init__.py
│   │   ├── apply_sql.py              # Ejecuta SQL crudo sobre la DB
│   │   ├── create_schema.py          # Crea el esquema `athome` desde ORM
│   │   ├── ejecutar_seed.py          # Aplica el seed de datos inicial
│   │   ├── limpiar_bd.py             # Limpia / resetea la base
│   │   └── seed_completo_uuid.sql    # Script SQL de seed completo
│   └── utils/                        # Checks y herramientas auxiliares
│       ├──   __init__.py
│       ├── check_db.py               # Verificación de conexión y migraciones
│       ├── test_connection.py        # Test rápido de conexión a la DB
│       └── verify_seed.py            # Verifica consistencia del seed
├── tests/
│   ├── README.md                     # Sobre los test y cómo correrlos 
│   ├── conftest.py                   # Fixtures compartidos de pytest
│   ├── api/                          # Tests de la capa de API (endpoints)
│   ├── domain/                       # Tests de dominio (entidades, estrategias, eventos)
│   ├── integration/                  # Tests de integración (DB, Supabase, seed)
│   └── test_integracion_api_domain.py # Test de integración API ↔ dominio
└── .github/
    └── workflows/
        └── lint.yml                  # Workflow de CI para linting/formato


```


### Implementaciones


#### **API y routers por recurso**
La aplicación se instancia en `app/main.py` y publica endpoints agrupados por dominio bajo `app/api/routers/` (auth, búsqueda, consultas, pacientes, profesionales y valoraciones). Esta organización mantiene el contrato HTTP estable y facilita la navegación desde `/docs`.


#### **Autenticación y seguridad**
El flujo está operativo con **hash Argon2** y **JWT HS256**. El router `app/api/routers/auth.py` (prefijo `/api/v1/auth`) expone: `POST /register-json` (201) para alta de usuario con **roles excluyentes** (profesional/solicitante; si no se especifica, default a solicitante); `POST /login` que devuelve `{access_token, token_type}` y aplica **bloqueo temporal por intentos fallidos** (`423 Locked` si bloqueado; `401` para credenciales inválidas); y `GET /me`, que lee `Authorization: Bearer <token>` y retorna el perfil básico. La lógica vive en `app/services/auth_service.py` (`hash_password/verify_password`, `crear_access_token/validar_access_token` con `AT_HOME_RED_SECRET` y `ACCESS_TOKEN_EXPIRE_MINUTES`) y el repositorio `app/infra/repositories/usuario_repository.py` gestiona `obtener_por_email`, `incrementar_intentos_fallidos`, `esta_bloqueado`, `resetear_intentos_fallidos` y `actualizar_ultimo_login`.


#### **Persistencia y migraciones**
El modelo de datos está implementado en **SQLAlchemy** y versionado con **Alembic** (migración inicial en `alembic/versions/...`). La capa de **repositorios** realiza el mapeo ORM↔dominio y encapsula las operaciones CRUD. La base de datos corre en **Supabase**, que nos brinda un entorno de **PostgreSQL** en la nube, accedido mediante la capa de persistencia.

Las migraciones ahora las gestiona **Alembic**: definimos los modelos/persistencias en SQLAlchemy, Alembic genera una nueva versión y la aplicamos (upgrade); antes este proceso se hacía de forma manual. Las comprobaciones y utilidades relacionadas están en `scripts/utils/check_db.py` y `scripts/utils/test_connections.py`. En Supabase solo tenemos el hosting de la base; la creación y evolución de las tablas queda a cargo de Alembic a partir de los modelos ORM.


#### **Reservas / consultas**
El módulo de **consultas** permite crear, leer, actualizar y cancelar consultas, además de manejar transiciones de estado explícitas (confirmar, completar, reprogramar). También ofrece listados filtrables por profesional y por paciente.

Antes de persistir una consulta se aplican políticas de integridad (profesional verificado y activo, vínculo válido paciente–solicitante, solicitante activo) y reglas de negocio (horarios consistentes, sin fechas pasadas ni solapamientos). La ubicación se modela como `Ubicacion` (value object) y, en esta versión, se apoya en la dirección del profesional. Cada cambio de estado dispara un evento de dominio que se publica en el `EventBus`, retomado luego en **Notificaciones (Observer)** y en **Patrones y arquitectura**.


#### **Búsqueda (Strategy)**
El router de búsqueda construye un `FiltroBusqueda` a partir del DTO, resuelve la especialidad (por nombre o ID) usando el catálogo y valida los criterios de entrada. Según esos criterios, selecciona dinámicamente la estrategia de dominio y ejecuta el contexto `Buscador`. Los errores de validación se responden con códigos HTTP apropiados (400/404) y los errores inesperados con 500. Este diseño, basado en un patrón de comportamiento GoF, permite cambiar el algoritmo de búsqueda sin modificar la lógica principal de los endpoints.



#### **Notificaciones (Observer)**
El sistema emite **eventos de dominio** y los procesa mediante un **EventBus**. El bus permite suscribirse tanto con handlers funcionales como con observers tradicionales. En esta demo usamos, a modo de ejemplo, un `NotificadorEmail` (simulado por consola) y un `AuditLogger` (que registra en los logs). La infraestructura está preparada para integrar envío real de correos vía SMTP configurado por variables de entorno, como se detalla en **Patrones y arquitectura**.



### Usuarios


- **Usuario (abstracta).** Persona con cuenta de acceso que sirve como base para los dos roles operativos del sistema. Atributos: `id`, `nombre`, `apellido`, `email`, `celular`, `Ubicacion`, `activo` (True por defecto). Métodos útiles: `nombre_completo`, `activar`/`desactivar` y `datos_contacto`.


- **Profesional.** Hereda de `Usuario` y ofrece servicios profesionales de salud. Debe tener al menos una matrícula activa (`matriculas`: lista 1:N). Puede tener varias especialidades (`especialidades`), disponibilidades (`disponibilidades`) y matrículas (`matriculas`). Expone `agregar_disponibilidad` y `agregar_matricula` para gestionar su agenda y credenciales.


- **Solicitante.** Hereda de `Usuario` y gestiona turnos propios o de la persona a su cargo. Mantiene un único `paciente` y el método `agregar_paciente`.


- **Paciente.** Persona atendida; **no** hereda de `Usuario` (puede no tener cuenta). Atributos: `id`, `nombre`, `apellido`, `fecha_nacimiento`, `Ubicacion`, `solicitante_id`, `relacion` (p. ej. `"Yo mismo"`, `"hijo"`, `"Tutor"`, etc.), `notas`. Y los métodos: `edad`, `nombre_completo` y `es_menor`. 


**Nota de diseño.** Se separa explícitamente “quién tiene cuenta” (Usuario) de “quién recibe la atención” (Paciente). Esto permite que un **Solicitante** tenga un único **Pacientes** pudiendo ser adaptado en el futuro a "uno a muchos". 




### Clases principales


La siguiente tabla resume las clases, value objects y componentes relevantes tal como están nombrados e implementados en el repositorio. Útil para referencia rápida durante la defensa.


###### Entidades y value objects


| Clase / Estructura                | Rol en el sistema (ubicación) |
|-----------------------------------|--------------------------------|
| `Usuario` *(abstracta)*           | Base de usuarios. `app/domain/entities/usuarios.py` |
| `Profesional`                     | Ofrece servicios; tiene `especialidades`, `disponibilidades` y `matriculas`. `entities/usuarios.py` |
| `Solicitante` *(Responsable)*     | Gestiona turnos de un único `Paciente`. `entities/usuarios.py` |
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

| Componente / DTO | Rol (ubicación) |
|------------------|-----------------|
| `AuthService` | Lógica de hash Argon2, JWT HS256, registro/login, intents/bloqueo. `app/services/auth_service.py` |
| `UsuarioRepository` | Acceso a usuarios: alta, búsquedas, intents, último login. `app/infra/repositories/usuario_repository.py` |
| `RegisterRequest` | DTO de registro. `app/api/schemas.py` |
| `LoginRequest` | DTO de login. `app/api/schemas.py` |
| `TokenSchema` | Respuesta `{access_token, token_type}`. `app/api/schemas.py` |
| `auth.py` (router) | Endpoints `/register-json` (201), `/login`, `/me` (Bearer). `app/api/routers/auth.py` |


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


El patrón **Strategy** es el eje del módulo de búsqueda/asignación. Las interfaces y estrategias viven en `app/domain/strategies/` (por ejemplo, `estrategia.py` y `buscador.py`) y se invocan desde el router `app/api/routers/busqueda.py`. Esta organización permite intercambiar la lógica de búsqueda o de asignación sin tocar los endpoints: el router selecciona la estrategia activa y la ejecuta. Actualmente hay al menos dos variantes implementadas para cubrir escenarios de búsqueda distintos.


El **Observer** se implementa con un *EventBus* simple para reaccionar a eventos de dominio sin acoplar emisores y efectos colaterales. El bus está en `app/api/event_bus.py`, los eventos en `app/domain/eventos.py` y los observadores (por ejemplo, un `NotificadorEmail`) en `app/domain/observers/`. En el estado actual funciona en **modo demo** (notifica por consola con `print`). Para producción se prevé vincularlo a un servidor de correo (SMTP) configurado vía `.env` y, si hace falta, sumar otros observadores como auditoría o webhooks sin modificar el código que emite los eventos.


El patrón **Repository** separa el dominio de los detalles de persistencia. Los repositorios concretos residen en `app/infra/repositories/` y los modelos/ORM y utilidades de base de datos en `app/infra/persistence/`. Aunque no es un patrón GoF, es un patrón de arquitectura estándar en la industria y permite mantener el dominio independiente de SQLAlchemy y del esquema físico, facilitando pruebas, mocks y cambios de tecnología.


La **arquitectura en capas** se refleja en tres espacios principales: `app/domain/` (entidades, eventos, value objects y estrategias, sin dependencias de infraestructura), `app/infra/` (ORM, repositorios y servicios de aplicación como autenticación) y `app/api/` (routers, dependencias, esquemas, *event bus* y *policies*). Esta separación hace que el dominio no dependa de la infraestructura y que la API publique casos de uso manteniendo el acoplamiento bajo control.


En nuestro proyecto usamos decoradores de forma transversal y concreta: declaramos endpoints con `@app.get("/health")` y `@app.get("/")` en `app/main.py`, y en `app/api/routers/busqueda.py` definimos la ruta de búsqueda con `@router.post("/profesionales", response_model=BusquedaProfesionalResponse)`. En ese mismo router combinamos esos decoradores de ruta con la inyección de dependencias vía `Depends(...)` para obtener repositorios como `get_profesional_repository` y `get_catalogo_repository` sin acoplarlos a la vista. En el módulo de políticas (`app/api/policies.py`) usamos decoradores del lenguaje, por ejemplo `@staticmethod` en `validar_solicitante_es_dueno`, para expresar reglas de autorización como utilidades claras y reutilizables. Incluso en las pruebas aplicamos decoradores de Pytest, como `@pytest.mark.authflow` y `@pytest.mark.auth_neg` en `tests/api/test_auth.py`, para marcar escenarios y filtrar ejecuciones. En espíritu, estos decoradores “añaden comportamiento” sin modificar los objetos, de un modo análogo al patrón GoF *Decorator*; sin embargo, en nuestro código su rol es estrictamente idiomático e infraestructural de Python, FastAPI y Pytest, y no modelamos un *Decorator* como objeto de dominio.


En cuanto al **estado actual**, el proyecto ya cuenta con Strategy operativo en el router de búsqueda, Observer funcional en modo demostrativo, y Repository para aislar dominio y persistencia; además, hay esquema de base de datos y endpoints integrados a la API.


---


## Diagrama UML

El proyecto incluye un diagramas UML de dominio. El mismo puede observarse en el siguiente enlace:


- **[Diagrama de clases (de dominio)](docs/uml/UML_ATHomeRed_Domain.svg)**

### Qué muestra


- **Entidades principales**
  - `Usuario` *(abstracta)*, `Solicitante`, `Profesional`, `Paciente`
  - *Value Objects*: `Ubicacion`, `Disponibilidad`, `Matricula`
  - Catálogo/servicios: `Especialidad`, `Tarifa`, `Publicacion`
  - Agenda: `Cita`/`Consulta` (con `EstadoCita`)


- **Patrones representados**
  - **Strategy (búsqueda):** `Buscador` (contexto), `Estrategia` (interfaz),
    `BusquedaPorZona`, `BusquedaPorEspecialidad`, `BusquedaCombinada`
  - **Observer (notificaciones/auditoría):** `Observer`, `Subject`, `NotificadorEmail`,
    `AuditLogger`, `Event` (eventos de `Cita`)


---

## Presentación (Canva)

La presentación utilizada para exponer el proyecto puede verse en el siguiente enlace:

- [Ver presentación en Canva](https://www.canva.com/design/DAG4oDxIeHw/tnIWLaE6OiSu6puOHtIJhg/edit?ui=eyJBIjp7fX0)


---


## Tecnologías


- **Lenguaje**: Python 3.11+
- **API**: FastAPI
- **Servidor de aplicación:** Uvicorn
- **Validación de datos:** Pydantic
- **ORM**: SQLAlchemy
- **DB**: Supabase (PostgreSQL)
- **Migraciones**: Alembic
- **Autenticación / seguridad:** JWT (HS256, `python-jose`) + Argon2 (`passlib`)
- **Configuración:** variables de entorno `.env` (python-dotenv)
- **Contenedores**: Docker Hub
- **Docs:** OpenAPI / Swagger UI generadas por FastAPI
- **Postman** Para pruebas de endpoints
- **Testing** Pytest
- **CI:**: LINT(PEP8)


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

### Producción (Render)

La API está desplegada en Render en:

- Base URL: https://athomered-1.onrender.com  
- Docs (Swagger UI): https://athomered-1.onrender.com/docs

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
# ATHomeRed – API (MVP)
