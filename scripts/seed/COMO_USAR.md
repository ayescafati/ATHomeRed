# 🎯 Guía de Uso - Scripts de Semillas

## Ejecución Rápida

### Opción 1: Semilla Mínima (Recomendada para desarrollo)
```powershell
python scripts/seed/seed_minimo.py
```

**Crea:**
- 3 Especialidades
- 2 Profesionales
- 2 Solicitantes con pacientes
- Estados y relaciones básicas

**Tiempo:** ~5 segundos

---

### Opción 2: Semilla Completa (Recomendada para testing)
```powershell
# Sin limpiar (agrega a datos existentes)
python scripts/seed/seed_completo.py

# Con limpieza previa (⚠️ ELIMINA TODOS LOS DATOS)
python scripts/seed/seed_completo.py --limpiar
```

**Crea:**
- 8 Especialidades del dominio
- 8 Profesionales con especialidades variadas
- 6 Solicitantes con pacientes
- Ubicaciones completas (Córdoba, Buenos Aires, Santa Fe)
- 20 Consultas en diferentes estados
- Valoraciones para consultas completadas
- Disponibilidades horarias

**Tiempo:** ~15 segundos

---

### Opción 3: Solo Especialidades
```powershell
python scripts/seed/seed_especialidades.py
```

---

## Credenciales de Acceso

**Password universal:** `Password123!`

### Profesionales (seed_minimo):
- `maria.gonzalez@athomered.com` - Enfermería General
- `carlos.fernandez@athomered.com` - Acompañamiento Terapéutico

### Solicitantes (seed_minimo):
- `ana.martinez@email.com`
- `roberto.lopez@email.com`

### Profesionales (seed_completo):
- `ml.gonzalez@athomered.com` - Enfermería
- `ce.fernandez@athomered.com` - Acompañamiento Terapéutico
- `as.martinez@athomered.com` - Salud Mental
- `rd.lopez@athomered.com` - Cuidados Paliativos
- `gb.sanchez@athomered.com` - Discapacidad
- `jl.rodriguez@athomered.com` - Geriatría
- `sm.diaz@athomered.com` - Acompañamiento Terapéutico
- `fa.perez@athomered.com` - Rehabilitación

### Solicitantes (seed_completo):
- `patricia.romero@email.com` - Post-operatorio
- `ricardo.molina@email.com` - Adulta mayor con diabetes
- `claudia.torres@email.com` - Joven con discapacidad
- `daniel.vargas@email.com` - Cuidados paliativos
- `andrea.benitez@email.com` - Salud mental
- `sergio.acosta@email.com` - Rehabilitación post-ACV

---

## Casos de Uso

### Para Desarrollo Local
```powershell
# Primera vez
alembic upgrade head
python scripts/seed/seed_minimo.py
```

### Para Testing Completo
```powershell
# Limpiar y cargar datos frescos
python scripts/seed/seed_completo.py --limpiar
```

### Para Agregar Más Datos
```powershell
# Sin limpiar, agrega a los existentes
python scripts/seed/seed_completo.py
```

---

## Verificación

### Verificar que los datos se cargaron
```powershell
python scripts/dev/check_db.py
```

### Probar autenticación
```powershell
python scripts/dev/smoke_auth.py
```

### Ver especialidades
```powershell
python
>>> from app.infra.persistence.database import SessionLocal
>>> from app.infra.persistence.servicios import EspecialidadORM
>>> session = SessionLocal()
>>> especialidades = session.query(EspecialidadORM).all()
>>> for e in especialidades:
...     print(f"{e.nombre}: ${e.tarifa}")
```

---

## Troubleshooting

### ❌ Error: "duplicate key value violates unique constraint"
**Solución:** Los datos ya existen. Usar `--limpiar` para borrarlos primero:
```powershell
python scripts/seed/seed_completo.py --limpiar
```

### ❌ Error: "Table does not exist"
**Solución:** Aplicar migraciones primero:
```powershell
alembic upgrade head
```

### ❌ Error: "Cannot connect to database"
**Solución:** Verificar `.env` y que la base de datos esté corriendo.

---

## Estructura de Datos Generados

### Especialidades (8 total)
| Nombre | Tarifa |
|--------|--------|
| Acompañamiento Terapéutico | $3,500 |
| Enfermería General | $4,000 |
| Enfermería Especializada | $5,500 |
| Acompañamiento Geriátrico | $3,800 |
| Acompañamiento en Salud Mental | $4,200 |
| Apoyo a Personas con Discapacidad | $3,600 |
| Cuidados Paliativos | $4,800 |
| Rehabilitación Domiciliaria | $4,000 |

### Estados de Consulta
- Pendiente
- Confirmada
- En Curso
- Completada
- Cancelada
- Reprogramada

### Perfiles de Pacientes Incluidos
- **Adultos mayores:** Con diabetes, post-ACV, cuidados generales
- **Salud mental:** Trastorno bipolar, crisis
- **Discapacidad:** Intelectual, apoyo social
- **Post-operatorios:** Cirugía de cadera, recuperación
- **Cuidados paliativos:** Oncológico, confort

---

## Notas Importantes

⚠️ **IMPORTANTE:** El flag `--limpiar` ELIMINA TODOS LOS DATOS de las tablas.  
✅ Los scripts son seguros y respetan las restricciones de integridad.  
🔐 Todos los passwords están hasheados con Argon2.  
📊 Los datos son realistas del dominio de Enfermería y Acompañamiento Terapéutico.

---

## Próximos Pasos

Después de cargar los datos:

1. **Iniciar servidor:**
   ```powershell
   python run_server.py
   ```

2. **Probar API:**
   - Abrir http://localhost:8000/docs
   - Usar endpoint `/auth/login`
   - Explorar endpoints de profesionales, consultas, etc.

3. **Ver frontend:**
   - Abrir http://localhost:8000/static/index.html
   - Login con credenciales generadas

---

## Documentación Adicional

- `scripts/seed/README.md` - Documentación detallada
- `tests/TESTING_GUIDE.md` - Guía de testing
- `otros/USAGE_GUIDE.md` - Guía de uso del sistema
