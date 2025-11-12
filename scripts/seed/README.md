# 🌱 Scripts de Semillas (Seed Data)

Este directorio contiene scripts para cargar datos iniciales en la base de datos de ATHomeRed.

## 📁 Archivos Disponibles

### `seed_especialidades.py`
Script específico para cargar únicamente las especialidades del dominio de Enfermería y Acompañamiento Terapéutico.

**Especialidades incluidas:**
- Acompañamiento Terapéutico
- Enfermería General
- Enfermería Especializada
- Acompañamiento Geriátrico
- Acompañamiento en Salud Mental
- Apoyo a Personas con Discapacidad
- Cuidados Paliativos
- Rehabilitación Domiciliaria

**Uso:**
```powershell
python scripts/seed/seed_especialidades.py
```

---

### `seed_minimo.py` ⚡
Script para cargar **datos mínimos** necesarios para pruebas rápidas.

**Incluye:**
- 4 estados de consulta
- 5 tipos de relaciones solicitante-paciente
- 3 especialidades principales
- 2 profesionales (uno con enfermería, otro con acompañamiento)
- 2 solicitantes con sus pacientes

**Ideal para:**
- Testing rápido
- Desarrollo inicial
- Verificar que el sistema funciona

**Uso:**
```powershell
python scripts/seed/seed_minimo.py
```

**Credenciales generadas:**
- Email: Cualquiera de los generados (ej: `maria.gonzalez@athomered.com`)
- Password: `Password123!`

---

### `seed_completo.py` 🎯
Script **completo y profesional** para cargar un dataset realista y representativo del dominio.

**Incluye:**
- 6 estados de consulta
- 14 tipos de relaciones
- 8 especialidades detalladas
- 8 profesionales con múltiples especialidades
- 6 solicitantes con pacientes variados
- Ubicaciones completas (provincias, departamentos, barrios de Córdoba)
- Disponibilidades horarias para profesionales
- 20 consultas en diferentes estados
- Valoraciones para consultas completadas

**Perfiles de ejemplo:**
- Profesionales con diferentes especialidades
- Pacientes de distintas edades y condiciones:
  - Adultos mayores con diabetes
  - Post-operatorios
  - Discapacidad intelectual
  - Cuidados paliativos
  - Salud mental
  - Rehabilitación post-ACV

**Características:**
- ✅ Datos realistas del dominio de enfermería
- ✅ Respeta todas las restricciones de integridad
- ✅ Incluye casos variados para testing completo
- ✅ Opción para limpiar tablas antes de cargar
- ✅ Resumen detallado de la carga

**Uso:**
```powershell
python scripts/seed/seed_completo.py
```

El script preguntará si desea limpiar las tablas existentes antes de cargar.

**Credenciales generadas:**
- Email: Cualquier email de la lista (profesional o solicitante)
- Password: `Password123!`

**Ejemplos de emails:**
- `ml.gonzalez@athomered.com` (Enfermera)
- `ce.fernandez@athomered.com` (Acompañante Terapéutico)
- `patricia.romero@email.com` (Solicitante)

---

### `demo_data.py`
Script legacy de demostración. Considerar usar `seed_completo.py` en su lugar.

---

## 🚀 Ejecución

### Prerequisitos
1. Base de datos configurada (PostgreSQL/SQLite)
2. Migraciones Alembic aplicadas
3. Variables de entorno configuradas en `.env`

### Orden Recomendado

**Para desarrollo inicial:**
```powershell
# 1. Aplicar migraciones
alembic upgrade head

# 2. Cargar semilla mínima
python scripts/seed/seed_minimo.py
```

**Para testing completo:**
```powershell
# 1. Aplicar migraciones
alembic upgrade head

# 2. Cargar semilla completa
python scripts/seed/seed_completo.py
```

**Para agregar solo especialidades:**
```powershell
python scripts/seed/seed_especialidades.py
```

---

## 📊 Estructura de Datos

### Orden de Dependencias
Los scripts respetan el siguiente orden de carga:

1. **Catálogos Base**
   - Estados de consulta
   - Relaciones solicitante-paciente

2. **Especialidades**
   - Información de servicios ofrecidos

3. **Ubicaciones**
   - Provincias → Departamentos → Barrios

4. **Usuarios y Perfiles**
   - Usuario → Profesional/Solicitante

5. **Relaciones**
   - Especialidades ↔ Profesionales
   - **Matrículas de profesionales** ⚠️ **OBLIGATORIO** (RN-001: Todo profesional debe tener al menos una matrícula)

6. **Pacientes**
   - Asociados a solicitantes

7. **Disponibilidades**
   - Horarios de profesionales

8. **Consultas**
   - Citas entre pacientes y profesionales

9. **Valoraciones**
   - Reviews de consultas completadas

---

## 🔐 Seguridad

- Todos los usuarios generados tienen password hasheado con bcrypt
- Password por defecto: `Password123!`
- **IMPORTANTE:** Cambiar en producción

---

## 🛠️ Troubleshooting

### Error: "No se puede conectar a la base de datos"
Verificar:
- Variables de entorno en `.env`
- Que la base de datos esté corriendo
- Credenciales correctas

### Error: "Tabla no existe"
Ejecutar migraciones:
```powershell
alembic upgrade head
```

### Error: "Violación de constraint"
Si las tablas ya tienen datos, usar la opción de limpieza en `seed_completo.py` o limpiar manualmente.

### Limpiar todas las tablas manualmente:
```sql
-- En PostgreSQL
TRUNCATE athome.valoracion, athome.consulta, athome.disponibilidad, 
         athome.paciente, athome.profesional_especialidad, athome.matricula,
         athome.profesional, athome.solicitante, athome.usuario 
RESTART IDENTITY CASCADE;
```

---

## 📝 Notas

- Los scripts son **idempotentes** en la medida de lo posible (usan `ON CONFLICT DO NOTHING` donde aplica)
- `seed_completo.py` ofrece opción interactiva para limpiar antes de cargar
- Los datos están diseñados específicamente para el dominio de **Enfermería y Acompañamiento Terapéutico**
- Todos los datos son ficticios y creados para propósitos de desarrollo/testing

---

## 🤝 Contribuir

Para agregar más datos o modificar existentes:

1. Respetar el orden de dependencias
2. Usar UUIDs para IDs (excepto especialidades que usan int)
3. Validar que los datos sean realistas del dominio
4. Documentar cambios en este README

---

## 📞 Soporte

Para problemas o preguntas sobre los scripts de semillas, consultar:
- `tests/TESTING_GUIDE.md` - Guía de testing
- `otros/IMPLEMENTATION_GUIDE.md` - Guía de implementación
