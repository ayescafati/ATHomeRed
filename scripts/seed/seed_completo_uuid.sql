-- =============================================================================
-- SEED COMPLETO - AtHomeRed (ACTUALIZADO A ESQUEMA MIGRACIONES 2025-11-12)
-- Ajustado para:
--  * Tablas con claves UUID por defecto (gen_random_uuid())
--  * Separación profesional <-> especialidades (tabla puente profesional_especialidad)
--  * Tabla matricula con provincia_id y fechas vigencia
--  * Tabla usuario requiere activo/verificado/es_* y constraints de rol exclusivo
--  * Tabla paciente sin direccion_id y relacion_id NOT NULL
--  * Quita columnas obsoletas (biografia, anios_experiencia, especialidad_nombre en profesional)
--  * Usa secuencia de relacion_solicitante correctamente tras insert explícito de IDs
-- =============================================================================
-- PRECONDICIÓN: EXTENSIÓN pgcrypto habilitada (para gen_random_uuid()).
-- Si no existe: CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- Ejecutar dentro de una única transacción para atomicidad.
BEGIN;

-- =============================================================================
-- 1. PROVINCIAS
-- =============================================================================
INSERT INTO athome.provincia (nombre) VALUES ('Ciudad Autónoma de Buenos Aires') ON CONFLICT (nombre) DO NOTHING;
INSERT INTO athome.provincia (nombre) VALUES ('Buenos Aires') ON CONFLICT (nombre) DO NOTHING;

-- =============================================================================
-- 2. DEPARTAMENTOS (Comunas CABA)
-- =============================================================================
DO $$
DECLARE
  v_caba UUID;
BEGIN
  SELECT id INTO v_caba FROM athome.provincia WHERE nombre='Ciudad Autónoma de Buenos Aires';
  INSERT INTO athome.departamento (provincia_id, nombre) VALUES
    (v_caba,'Comuna 1'),(v_caba,'Comuna 4'),(v_caba,'Comuna 8'),(v_caba,'Comuna 9'),
    (v_caba,'Comuna 10'),(v_caba,'Comuna 11'),(v_caba,'Comuna 12'),(v_caba,'Comuna 13')
  ON CONFLICT ON CONSTRAINT uq_departamento_provincia_nombre DO NOTHING;
END $$;

-- =============================================================================
-- 3. BARRIOS
-- =============================================================================
DO $$
DECLARE
  rec RECORD;
BEGIN
  -- Asociar barrios a cada comuna existente
  FOR rec IN SELECT id, nombre FROM athome.departamento LOOP
    IF rec.nombre = 'Comuna 1' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Retiro'),(rec.id,'San Nicolás'),(rec.id,'Montserrat') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 4' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'La Boca'),(rec.id,'Barracas'),(rec.id,'Parque Patricios') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 8' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Villa Lugano'),(rec.id,'Villa Soldati'),(rec.id,'Villa Riachuelo') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 9' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Liniers'),(rec.id,'Mataderos'),(rec.id,'Parque Avellaneda') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 10' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Floresta'),(rec.id,'Villa Luro'),(rec.id,'Monte Castro') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 11' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Villa Devoto'),(rec.id,'Villa del Parque'),(rec.id,'Villa Santa Rita') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 12' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Saavedra'),(rec.id,'Villa Urquiza'),(rec.id,'Villa Pueyrredón') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    ELSIF rec.nombre = 'Comuna 13' THEN
      INSERT INTO athome.barrio (departamento_id,nombre) VALUES (rec.id,'Belgrano'),(rec.id,'Colegiales'),(rec.id,'Núñez') ON CONFLICT ON CONSTRAINT uq_barrio_departamento_nombre DO NOTHING;
    END IF;
  END LOOP;
END $$;

-- =============================================================================
-- 4. DIRECCIONES (2 por barrio)
-- =============================================================================
DO $$
DECLARE
  b RECORD;
  calles TEXT[][] := ARRAY[
    ARRAY['Av. del Libertador','Reconquista'], ARRAY['Av. Corrientes','Maipú'], ARRAY['Av. de Mayo','Perú'],
    ARRAY['Caminito','Brandsen'], ARRAY['Av. Montes de Oca','Iriarte'], ARRAY['Av. Caseros','Uspallata'],
    ARRAY['Av. Cruz','Soldado de la Frontera'], ARRAY['Mariano Acosta','Av. Int. Roca'], ARRAY['Av. Gral. Paz','Pergamino'],
    ARRAY['Ramón Falcón','Montiel'], ARRAY['Av. Emilio Castro','Murguiondo'], ARRAY['Av. Directorio','Lacarra'],
    ARRAY['Av. Avellaneda','Bahía Blanca'], ARRAY['Av. Rivadavia','Corvalán'], ARRAY['Álvarez Jonte','J. V. González'],
    ARRAY['Nueva York','Asunción'], ARRAY['Cuenca','Av. Nazca'], ARRAY['Álvarez Jonte','Helguera'],
    ARRAY['Av. Ricardo Balbín','Vedia'], ARRAY['Av. Triunvirato','Bauness'], ARRAY['Artigas','Bolivia'],
    ARRAY['Av. Cabildo','Juramento'], ARRAY['Av. Federico Lacroze','Conesa'], ARRAY['Av. Cabildo','Crisólogo Larralde']
  ];
  idx INT := 1;
BEGIN
  FOR b IN SELECT id FROM athome.barrio ORDER BY id LOOP
    EXIT WHEN idx > array_length(calles,1);
    INSERT INTO athome.direccion (barrio_id, calle, numero) VALUES
      (b.id, calles[idx][1], (500 + idx) * 2),
      (b.id, calles[idx][2], (600 + idx) * 2);
    idx := idx + 1;
  END LOOP;
END $$;

-- =============================================================================
-- 5. ESPECIALIDADES
-- =============================================================================
INSERT INTO athome.especialidad (nombre, descripcion, tarifa) VALUES
 ('Acompañamiento Terapéutico General','Apoyo integral en salud mental.',15000),
 ('Acompañamiento Terapéutico Geriatría','Atención especializada adultos mayores.',15000),
 ('Acompañamiento Terapéutico (Especialización TEA/TDAH)','Intervención específica TEA y TDAH.',15000),
 ('Enfermería','Atención domiciliaria general.',18000),
 ('Enfermería Geriátrica','Cuidados especializados geriatría.',18000),
 ('Cuidados Paliativos','Atención integral en patologías terminales.',25000)
ON CONFLICT (nombre) DO NOTHING;

-- =============================================================================
-- 6. RELACIONES SOLICITANTE-PACIENTE (IDs fijos)
-- =============================================================================
INSERT INTO athome.relacion_solicitante (id,nombre) VALUES
  (35,'Yo mismo'),(36,'Madre'),(37,'Padre'),(38,'Hijo'),(39,'Hija'),(40,'Hermano'),(41,'Hermana'),
  (42,'Esposo'),(43,'Esposa'),(44,'Abuelo'),(45,'Abuela'),(46,'Tío'),(47,'Tía'),(48,'Tutor/a'),(49,'Otro familiar')
ON CONFLICT (id) DO NOTHING;
-- Ajustar secuencia para futuras inserciones automáticas
SELECT setval(pg_get_serial_sequence('athome.relacion_solicitante','id'), (SELECT MAX(id) FROM athome.relacion_solicitante));

-- =============================================================================
-- 7. 100 PROFESIONALES + MATRÍCULAS + ESPECIALIDAD (1 cada uno)
-- =============================================================================
DO $$
DECLARE
  v_usuario UUID;
  v_prof UUID;
  v_dir UUID;
  v_caba UUID; v_pba UUID;
  v_especialidad_id INT;
  nombres TEXT[] := ARRAY['Juan','María','Carlos','Ana','Roberto','Laura','Diego','Patricia','Miguel','Gabriela','Fernando','Claudia','Ricardo','Silvia','Jorge','Mónica','Pablo','Sandra','Martín','Liliana','Andrés','Valeria','Sebastián','Natalia','Daniel','Carolina','Gustavo','Adriana','Alejandro','Mariana','Marcelo','Paula','Javier','Lucía','Raúl','Daniela','Eduardo','Cecilia','Oscar','Verónica','Héctor','Andrea','Alberto','Cristina','Sergio','Beatriz','Rubén','Marta','Luis','Rosa','Federico','Susana','Nicolás','Elena','Hernán','Viviana','Maximiliano','Alicia','Facundo','Isabel','Matías','Norma','Ezequiel','Gloria','Germán','Teresa','Leonardo','Irene','Emiliano','Graciela','Rodrigo','Mercedes','Ignacio','Noemí','Agustín','Olga','Santiago','Mirta','Lucas','Elsa','Tomás','Lidia','Mateo','Dora','Bruno','Carmen','Joaquín','Raquel','Thiago','Estela','Bautista','Nora','Valentín','Silvia','Santino','Stella','Francisco','Blanca','Benicio','Clara'];
  apellidos TEXT[] := ARRAY['González','Rodríguez','Fernández','López','Martínez','Sánchez','Pérez','García','Romero','Díaz','Torres','Álvarez','Ruiz','Moreno','Jiménez','Muñoz','Castillo','Castro','Ortiz','Silva','Vega','Ramos','Flores','Méndez','Vargas','Medina','Herrera','Aguilar','Gutiérrez','Ramírez','Cruz','Reyes','Santos','Morales','Delgado','Rojas','Benítez','Cabrera','Acosta','Molina','Figueroa','Peralta','Núñez','Luna','Sosa','Domínguez','Giménez','Ríos','Campos','Bustos'];
  especialidades TEXT[] := ARRAY[
    -- 30 General
    'Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General','Acompañamiento Terapéutico General',
    -- 15 Geriatría
    'Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría','Acompañamiento Terapéutico Geriatría',
    -- 10 TEA/TDAH
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)','Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    -- 20 Enfermería
    'Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería','Enfermería',
    -- 15 Enfermería Geriátrica
    'Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica','Enfermería Geriátrica',
    -- 10 Cuidados Paliativos
    'Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos','Cuidados Paliativos'
  ];
  i INT;
BEGIN
  SELECT id INTO v_caba FROM athome.provincia WHERE nombre='Ciudad Autónoma de Buenos Aires';
  SELECT id INTO v_pba  FROM athome.provincia WHERE nombre='Buenos Aires';
  FOR i IN 1..100 LOOP
    INSERT INTO athome.usuario (nombre, apellido, email, celular, es_profesional, es_solicitante, password_hash, intentos_fallidos, activo, verificado)
    VALUES (
      nombres[((i-1) % 100) + 1],
      apellidos[((i-1) % 50) + 1],
      'profesional' || i || '@athomered.com',
      '11' || LPAD((5000 + i)::TEXT, 8, '0'),
      TRUE, FALSE,
      '$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7',
      0, TRUE, TRUE
    ) RETURNING id INTO v_usuario;

    SELECT id INTO v_dir FROM athome.direccion ORDER BY RANDOM() LIMIT 1;
    INSERT INTO athome.profesional (usuario_id, direccion_id) VALUES (v_usuario, v_dir) RETURNING id INTO v_prof;

    SELECT id_especialidad INTO v_especialidad_id FROM athome.especialidad WHERE nombre = especialidades[i];
    INSERT INTO athome.profesional_especialidad (profesional_id, especialidad_id) VALUES (v_prof, v_especialidad_id);

    -- Matrícula (fechas: desde hace 2 años hasta dentro de 2 años)
    INSERT INTO athome.matricula (profesional_id, provincia_id, nro_matricula, vigente_desde, vigente_hasta)
    VALUES (
      v_prof,
      CASE WHEN i % 2 = 0 THEN v_caba ELSE v_pba END,
      (CASE WHEN i % 2 = 0 THEN 'CABA' ELSE 'PBA' END) || '-' ||
      (CASE WHEN especialidades[i] LIKE 'Acompañamiento%' THEN 'AT' ELSE 'EF' END) || '-' || LPAD((100000 + i)::TEXT, 6, '0'),
      CURRENT_DATE - INTERVAL '2 years',
      CURRENT_DATE + INTERVAL '2 years'
    );
  END LOOP;
END $$;

-- =============================================================================
-- 8. 50 PACIENTES + SOLICITANTES
-- =============================================================================
DO $$
DECLARE
  v_us UUID; v_sol UUID; v_dir UUID; v_rel INT; v_prof_especialidad TEXT; v_paciente_nombre TEXT; v_fecha_nac DATE; v_edad INT;
  nombres_ninos TEXT[] := ARRAY['Mateo','Sofía','Benjamín','Martina','Lucas','Emma','Thiago','Valentina','Santino','Isabella'];
  nombres_adultos TEXT[] := ARRAY['Carlos','María','Roberto','Ana','Jorge','Laura','Fernando','Patricia','Diego','Claudia'];
  nombres_mayores TEXT[] := ARRAY['Alberto','Rosa','Héctor','Elsa','Raúl','Mirta','Oscar','Nora','Rubén','Lidia'];
  apellidos TEXT[] := ARRAY['Fernández','López','Martínez','García','Rodríguez','Pérez','González','Sánchez','Romero','Díaz','Torres','Álvarez','Ruiz','Moreno','Jiménez','Muñoz','Silva','Castro','Ortiz','Vega','Ramos','Flores','Méndez','Vargas','Medina','Herrera','Gutiérrez','Ramírez','Cruz','Reyes','Santos','Morales','Delgado','Rojas','Benítez','Cabrera','Acosta','Molina','Núñez','Luna','Sosa','Domínguez','Giménez','Ríos','Campos','Bustos','Peralta','Figueroa','Aguilar','Vázquez'];
  i INT;
BEGIN
  FOR i IN 1..50 LOOP
    -- Especialidad aleatoria de profesional
    SELECT e.nombre INTO v_prof_especialidad
    FROM athome.profesional_especialidad pe
    JOIN athome.especialidad e ON e.id_especialidad = pe.especialidad_id
    ORDER BY RANDOM() LIMIT 1;

    IF v_prof_especialidad = 'Acompañamiento Terapéutico (Especialización TEA/TDAH)' THEN
      v_edad := 5 + (i % 13); v_paciente_nombre := nombres_ninos[((i-1)%10)+1]; v_rel := CASE (i % 3) WHEN 0 THEN 36 WHEN 1 THEN 37 ELSE 48 END;
    ELSIF v_prof_especialidad IN ('Acompañamiento Terapéutico Geriatría','Enfermería Geriátrica','Cuidados Paliativos') THEN
      v_edad := 65 + (i % 26); v_paciente_nombre := nombres_mayores[((i-1)%10)+1]; v_rel := CASE (i % 5) WHEN 0 THEN 38 WHEN 1 THEN 39 WHEN 2 THEN 42 WHEN 3 THEN 43 ELSE 35 END;
    ELSE
      v_edad := 25 + (i % 46); v_paciente_nombre := nombres_adultos[((i-1)%10)+1]; v_rel := CASE (i % 8) WHEN 0 THEN 35 WHEN 1 THEN 36 WHEN 2 THEN 37 WHEN 3 THEN 40 WHEN 4 THEN 41 WHEN 5 THEN 42 WHEN 6 THEN 43 ELSE 49 END;
    END IF;
    v_fecha_nac := CURRENT_DATE - (v_edad || ' years')::INTERVAL;

    -- Usuario solicitante
    INSERT INTO athome.usuario (nombre, apellido, email, celular, es_profesional, es_solicitante, password_hash, intentos_fallidos, activo, verificado)
    VALUES (
      'Solicitante' || i,
      apellidos[((i-1)%50)+1],
      'solicitante' || i || '@athomered.com',
      '11' || LPAD((6000 + i)::TEXT, 8, '0'),
      FALSE, TRUE,
      '$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7',
      0, TRUE, TRUE
    ) RETURNING id INTO v_us;

    SELECT id INTO v_dir FROM athome.direccion ORDER BY RANDOM() LIMIT 1;
    INSERT INTO athome.solicitante (usuario_id, direccion_id) VALUES (v_us, v_dir) RETURNING id INTO v_sol;

    INSERT INTO athome.paciente (nombre, apellido, fecha_nacimiento, notas, solicitante_id, relacion_id)
    VALUES (
      v_paciente_nombre,
      apellidos[((i-1)%50)+1],
      v_fecha_nac,
      'Paciente con ' || v_prof_especialidad || '. Edad: ' || v_edad || ' años.',
      v_sol,
      v_rel
    );
  END LOOP;
END $$;

-- =============================================================================
-- 9. PUBLICACIONES (1 por profesional)
-- =============================================================================
DO $$
DECLARE
  rec RECORD;
  titulos_at TEXT[] := ARRAY[
    'Acompañamiento Terapéutico Profesional','AT con enfoque integral','Acompañamiento especializado',
    'Apoyo terapéutico domiciliario','AT personalizado','Acompañamiento con experiencia'
  ];
  titulos_enf TEXT[] := ARRAY[
    'Enfermería Profesional a Domicilio','Cuidados de Enfermería Especializados','Enfermería con vocación',
    'Atención de Enfermería Integral','Cuidados profesionales','Enfermería de calidad'
  ];
  descripciones_at TEXT[] := ARRAY[
    'Brindo acompañamiento terapéutico con enfoque integral, respetando los tiempos y necesidades de cada paciente.',
    'Profesional con amplia experiencia en acompañamiento terapéutico, trabajando en equipo con los profesionales tratantes.',
    'Acompañamiento personalizado orientado al fortalecimiento de la autonomía y bienestar del paciente.',
    'AT especializado con enfoque en la contención emocional y seguimiento del plan terapéutico.',
    'Acompañamiento profesional con formación continua y compromiso con cada tratamiento.',
    'Servicio de AT orientado a la reinserción social y mejora de la calidad de vida.'
  ];
  descripciones_enf TEXT[] := ARRAY[
    'Enfermería profesional a domicilio con atención personalizada y seguimiento continuo.',
    'Brindo cuidados de enfermería especializados con calidez humana y profesionalismo.',
    'Atención de enfermería integral, respetando la dignidad y necesidades de cada paciente.',
    'Cuidados profesionales de enfermería con experiencia en atención domiciliaria.',
    'Enfermería de calidad con enfoque en el bienestar y confort del paciente.',
    'Servicio de enfermería especializado con disponibilidad y compromiso.'
  ];
BEGIN
  FOR rec IN 
    SELECT p.id as prof_id, pe.especialidad_id, e.nombre as esp_nombre
    FROM athome.profesional p
    JOIN athome.profesional_especialidad pe ON p.id = pe.profesional_id
    JOIN athome.especialidad e ON pe.especialidad_id = e.id_especialidad
  LOOP
    INSERT INTO athome.publicacion (profesional_id, especialidad_id, titulo, descripcion, fecha_publicacion)
    VALUES (
      rec.prof_id,
      rec.especialidad_id,
      CASE 
        WHEN rec.esp_nombre LIKE 'Acompañamiento%' THEN titulos_at[1 + (random() * 5)::int]
        ELSE titulos_enf[1 + (random() * 5)::int]
      END,
      CASE 
        WHEN rec.esp_nombre LIKE 'Acompañamiento%' THEN descripciones_at[1 + (random() * 5)::int]
        ELSE descripciones_enf[1 + (random() * 5)::int]
      END,
      CURRENT_DATE - (random() * 180)::int
    );
  END LOOP;
END $$;

-- =============================================================================
-- 10. DISPONIBILIDADES (2-3 por profesional)
-- =============================================================================
DO $$
DECLARE
  prof RECORD;
  horarios TEXT[][] := ARRAY[
    ARRAY['Lunes,Martes,Miércoles,Jueves,Viernes', '08:00', '14:00'],
    ARRAY['Lunes,Martes,Miércoles,Jueves,Viernes', '14:00', '20:00'],
    ARRAY['Lunes,Miércoles,Viernes', '09:00', '17:00'],
    ARRAY['Martes,Jueves', '08:00', '16:00'],
    ARRAY['Sábado,Domingo', '10:00', '18:00'],
    ARRAY['Lunes,Martes,Miércoles', '07:00', '15:00'],
    ARRAY['Jueves,Viernes,Sábado', '10:00', '18:00']
  ];
  num_disponibilidades INT;
  idx INT;
  horario_usado INT[];
BEGIN
  FOR prof IN SELECT id FROM athome.profesional LOOP
    -- Cada profesional tiene 2 o 3 disponibilidades aleatorias
    num_disponibilidades := 2 + (random())::int; -- 2 o 3
    horario_usado := ARRAY[]::INT[];
    
    FOR i IN 1..num_disponibilidades LOOP
      -- Elegir un horario aleatorio que no se haya usado
      LOOP
        idx := 1 + (random() * 6)::int;
        EXIT WHEN NOT (idx = ANY(horario_usado));
      END LOOP;
      horario_usado := array_append(horario_usado, idx);
      
      INSERT INTO athome.disponibilidad (profesional_id, dias_semana, hora_inicio, hora_fin)
      VALUES (
        prof.id,
        horarios[idx][1],
        horarios[idx][2]::time,
        horarios[idx][3]::time
      );
    END LOOP;
  END LOOP;
END $$;

COMMIT;

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================
SELECT 'Provincias: ' || COUNT(*) FROM athome.provincia;
SELECT 'Departamentos: ' || COUNT(*) FROM athome.departamento;
SELECT 'Barrios: ' || COUNT(*) FROM athome.barrio;
SELECT 'Direcciones: ' || COUNT(*) FROM athome.direccion;
SELECT 'Especialidades: ' || COUNT(*) FROM athome.especialidad;
SELECT 'Relaciones: ' || COUNT(*) FROM athome.relacion_solicitante;
SELECT 'Profesionales: ' || COUNT(*) FROM athome.profesional;
SELECT 'Profesional_Especialidad: ' || COUNT(*) FROM athome.profesional_especialidad;
SELECT 'Matrículas: ' || COUNT(*) FROM athome.matricula;
SELECT 'Solicitantes: ' || COUNT(*) FROM athome.solicitante;
SELECT 'Pacientes: ' || COUNT(*) FROM athome.paciente;
SELECT 'Publicaciones: ' || COUNT(*) FROM athome.publicacion;
SELECT 'Disponibilidades: ' || COUNT(*) FROM athome.disponibilidad;

-- Distribución por especialidad
SELECT e.nombre, COUNT(pe.profesional_id) AS cantidad
FROM athome.especialidad e
LEFT JOIN athome.profesional_especialidad pe ON e.id_especialidad = pe.especialidad_id
GROUP BY e.nombre ORDER BY cantidad DESC;

-- Distribución de pacientes por relación
SELECT r.nombre, COUNT(p.id) AS cantidad
FROM athome.relacion_solicitante r
LEFT JOIN athome.paciente p ON r.id = p.relacion_id
GROUP BY r.nombre ORDER BY cantidad DESC;
