# Web API en construcción — AT Home Red

**Autores:**  
- Karen Gonzales Ch. · [@KarenGonzalesCh](https://github.com/KarenGonzalesCh)
- Federico Nicolás Llanes · @usuario  
- Miguel Ignacio Rodríguez Puertas · [@mirpuertas](https://github.com/mirpuertas)  
- Ayelén Luján Scafati · [ayescafati](https://github.com/ayescafati)  

**Materia:** Programación II – UNSAM  
**Cuatrimestre:** 2C 2025  

---

## Estado del proyecto

> **AT Home Red** se encuentra actualmente **en construcción**.  
> Este repositorio contiene el **diagrama de clases UML preliminar** y el **el esqueleto completo del modelo UML** en Python, siguiendo las convenciones de **PEP 8**  
> Aún no se implementan comportamientos ni persistencia. El objetivo en esta etapa es consolidar la arquitectura, las clases principales y los patrones de diseño que darán forma al MVP.
>
> Las próximas versiones incorporarán la implementación real de métodos, la persistencia de datos, los endpoints de la API y
> un front de demostración que permitirá visualizar el flujo completo entre responsables, profesionales y pacientes.

## Descripción general

**AT Home Red** es una Web API que busca formalizar y digitalizar la conexión entre familias (representadas por un **Responsable**) y profesionales del área de la salud domiciliaria, como **acompañantes terapéuticos** y **enfermeros/as**.

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


## Estructura del proyecto
```
at_home_red/
│
├── asignacion/
│   ├── observadores.py          # Patrón Observer (Subject, Observer, Notificadores)
│   └── estrategia_asignacion.py # Estrategias para validar asignaciones de consulta
│
├── busqueda/
│   ├── buscador.py              # Contexto de búsqueda (usa distintas estrategias)
│   └── estrategia.py            # Clases Strategy (zona, especialidad, combinada)
│
├── modelos/
│   ├── usuarios.py              # Usuario, Profesional, Responsable, Paciente
│   ├── objetos_valor.py         # Ubicación (value object)
│   ├── catalogo.py              # Publicación, Especialidad, Disponibilidad
│   ├── eventos.py               # Clase Consulta (Subject del Observer)
│   └── interaccion.py           # Clases auxiliares de relación y gestión
│
├── enumeraciones.py             # Estados y días de la semana
├── __init__.py
└── docs/uml/                    # Diagramas UML
```

## Patrones de diseño aplicados

### Observer  
Permite que los observadores (por ejemplo, `NotificadorEmail` o `AuditLogger`) sean informados automáticamente ante cambios en las consultas.  
Esto desacopla la lógica de notificación del flujo principal.

### Strategy  
Define distintas estrategias de búsqueda (`BusquedaPorZona`, `BusquedaPorEspecialidad`, `BusquedaCombinada`) utilizadas por el **Buscador**, que actúa como contexto.  
Esto facilita ampliar el sistema sin modificar código existente.


## Diagramas UML

- **[Diagrama de clases](at_home_red/docs/uml/clases-uml-v1.svg)**
- **[Diagrama de DB](at_home_red/docs/uml/db-uml-v1.svg)**
- **[Diagrama UI](at_home_red/docs/uml/ui-uml-v1.svg)**

> **Versión preliminar:**
> El modelado UML se encuentra en construcción. Esta es **la primera versión**, elaborada para representar las bases del sistema y comenzar a integrar los patrones de diseño. En próximas iteraciones se unificarán ambos diagramas y se ajustarán los nombres, relaciones y estereotipos según la evolución del código.

Para reflejar la estructura y los patrones aplicados, el proyecto incluye **dos diagramas de clases complementarios**, que representan distintos niveles de detalle del sistema.

#### 1. Diagrama inferior (modelo funcional y búsqueda)

El **diagrama inferior** (con fondo lila) muestra el **modelo funcional del MVP**, incluyendo las clases principales del sistema:
`Usuario`, `Responsable`, `Profesional`, `Paciente`, `Ubicacion`, `Disponibilidad`, `Publicacion` y `Consulta`.

Además, este diagrama incorpora el **patrón Strategy** aplicado al módulo de **búsqueda de profesionales**, con las clases:
`Buscador`, `EstrategiaBusqueda`, `BusquedaPorZona`, `BusquedaPorEspecialidad` y `BusquedaCombinada`.
Esto permite ver cómo el patrón se integra de manera directa con las entidades del sistema.

#### 2. Diagrama superior (Observer + Strategy en asignación)

El **diagrama superior** (con fondo blanco) se centra en los **patrones de diseño** aplicados al proceso de **asignación y notificación de consultas**.
En este se representan:

* **Observer:** `Subject`, `Observer`, `NotificadorEmail`, `AuditLogger`, aplicados sobre la clase `Cita` (equivalente a `Consulta` en el MVP).
* **Strategy (asignación):** `AsignacionStrategy`, `DisponibilidadHorariaStrategy` y `MatriculaProvinciaStrategy`, que nos definen las políticas de validación al asignar un profesional.

#### 3. Estado actual y próximos pasos

Ambos diagramas fueron desarrollados en paralelo y actualmente presentan **nombres y estructuras parcialmente distintas** (por ejemplo, `Cita` y `Consulta`, o la duplicación de estrategias).
Esto es **intencional en esta primera versión**, ya que el objetivo es explorar los dos niveles de modelado:

* El **modelo funcional** (entidades principales del MVP).
* La **arquitectura de patrones** que se aplicará sobre él.


## Clases principales

| Clase         | Rol en el sistema |
|----------------|------------------|
| `Usuario` (abstracta) | Clase base con atributos y métodos comunes. |
| `Profesional` | Representa acompañantes terapéuticos o enfermeros verificados. |
| `Responsable` | Usuario que gestiona las consultas del paciente. |
| `Paciente` | Persona atendida, con datos y ubicación. |
| `Consulta` | Cita entre un Responsable y un Profesional. |
| `Buscador` | Contexto que centraliza la búsqueda de profesionales. |
| `EstrategiaBusqueda` | Interfaz para las estrategias concretas. |
| `Disponibilidad` | Días y horarios de trabajo del profesional. |
| `Publicacion` | Información visible de los servicios del profesional. |
| `Ubicacion` | Objeto de valor que modela la localización geográfica. |



## Clases principales

### Modelo funcional (MVP)

| Clase                        | Rol en el sistema                                                |
| ---------------------------- | ---------------------------------------------------------------- |
| `Usuario` *(abstracta)*      | Clase base para todos los usuarios.                              |
| `Profesional`                | Representa acompañantes terapéuticos o enfermeros verificados.   |
| `Responsable`                | Usuario que gestiona las consultas del paciente.                 |
| `Paciente`                   | Persona atendida, con datos y ubicación.                         |
| `Ubicacion` *(value object)* | Modela dirección, latitud, longitud y validaciones geográficas.  |
| `Disponibilidad`             | Días y horarios de trabajo del profesional.                      |
| `Especialidad`               | Describe tipo de servicio y tarifa.                              |
| `Publicacion`                | Contiene información visible de los servicios ofrecidos.         |
| `Consulta`                   | Cita entre un Responsable y un Profesional, con estados y notas. |
| `FiltroBusqueda`             | Define los criterios de filtrado (zona, especialidad, horario).  |

### Búsqueda (Strategy)

| Clase                              | Rol                                             |
| ---------------------------------- | ----------------------------------------------- |
| `Buscador`                         | Contexto que aplica una estrategia de búsqueda. |
| `EstrategiaBusqueda` *(interface)* | Contrato para las estrategias concretas.        |
| `BusquedaPorZona`                  | Estrategia basada en ubicación geográfica.      |
| `BusquedaPorEspecialidad`          | Estrategia basada en tipo de servicio.          |
| `BusquedaCombinada`                | Combina varios criterios simultáneamente.       |


### Asignación y notificaciones

| Clase                           | Rol                                                           |
| ------------------------------- | ------------------------------------------------------------- |
| `Subject`                       | Parte del patrón Observer; administra observadores.           |
| `Observer`                      | Interfaz base para observadores.                              |
| `NotificadorEmail`              | Envía notificaciones cuando cambia el estado de una consulta. |
| `AuditLogger`                   | Registra eventos y auditorías del sistema.                    |
| `AsignacionStrategy`            | Contrato para políticas de validación de asignación.          |
| `DisponibilidadHorariaStrategy` | Verifica disponibilidad del profesional.                      |
| `MatriculaProvinciaStrategy`    | Valida matrícula y jurisdicción del profesional.              |


### Soporte / Enumeraciones

| Enum / Clase | Descripción                                            |
| ------------ | ------------------------------------------------------ |
| `EstadoCita` | Enum con estados: *SOLICITADA, CONFIRMADA, CANCELADA*. |
| `DiaSemana`  | Enum con los días: *LU, MA, MI, JU, VI, SA, DO*.       |
| `Event`      | Estructura de evento usada por el patrón Observer.     |


## Instalación (modo local)

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/<tu-usuario>/ATHomeRed.git
   ```
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   ```
3. Activar entorno:
   ```bash
   venv\Scripts\activate     # En Windows
   source venv/bin/activate  # En Linux
   ```
4. Instalar dependencias (en futuras versiones):
   ```bash
   pip install -r requirements.txt
   ```


## Futuro del proyecto

 Próximas etapas planificadas:
- Implementación real de los métodos en clases principales.  
- Conexión con base de datos.  
- Creación de endpoints con **FastAPI**.  
- Autenticación básica y gestión de usuarios.  
- Frontend de demostración.  
