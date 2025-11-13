-- ============================================================================
-- SEED COMPLETO - AtHomeRed
-- Fecha: 2025-11-12
-- ============================================================================
-- Contiene:
--   1. Jerarquía geográfica (Provincia → Departamento → Barrio → Dirección)
--   2. Especialidades y tarifas
--   3. Relaciones Solicitante-Paciente
--   4. 100 Profesionales con matrículas y direcciones
--   5. 50 Pacientes con relaciones coherentes
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. JERARQUÍA GEOGRÁFICA
-- ============================================================================

-- PROVINCIA
INSERT INTO athome.provincia (nombre)
VALUES ('Ciudad Autónoma de Buenos Aires')
ON CONFLICT (nombre) DO NOTHING;

-- DEPARTAMENTO (Comunas de CABA)
INSERT INTO athome.departamento (provincia_nombre, nombre)
VALUES
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 1'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 4'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 8'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 9'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 10'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 11'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 12'),
  ('Ciudad Autónoma de Buenos Aires', 'Comuna 13')
ON CONFLICT (provincia_nombre, nombre) DO NOTHING;

-- BARRIOS
INSERT INTO athome.barrio (departamento_nombre, provincia_nombre, nombre)
VALUES
  -- Comuna 1
  ('Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Retiro'),
  ('Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'San Nicolás'),
  ('Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Montserrat'),
  -- Comuna 4
  ('Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'La Boca'),
  ('Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Barracas'),
  ('Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Parque Patricios'),
  -- Comuna 8
  ('Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Villa Lugano'),
  ('Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Villa Soldati'),
  ('Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Villa Riachuelo'),
  -- Comuna 9
  ('Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Liniers'),
  ('Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Mataderos'),
  ('Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Parque Avellaneda'),
  -- Comuna 10
  ('Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Floresta'),
  ('Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Villa Luro'),
  ('Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Monte Castro'),
  -- Comuna 11
  ('Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Villa Devoto'),
  ('Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Villa del Parque'),
  ('Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Villa Santa Rita'),
  -- Comuna 12
  ('Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Saavedra'),
  ('Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Villa Urquiza'),
  ('Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Villa Pueyrredón'),
  -- Comuna 13
  ('Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Belgrano'),
  ('Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Colegiales'),
  ('Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Núñez')
ON CONFLICT (barrio_nombre, departamento_nombre, provincia_nombre) DO NOTHING;

-- DIRECCIONES (48 direcciones, 2 por barrio)
INSERT INTO athome.direccion (barrio_nombre, departamento_nombre, provincia_nombre, calle, numero)
VALUES
  -- Comuna 1
  ('Retiro', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Av. del Libertador', '650'),
  ('Retiro', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Reconquista', '600'),
  ('San Nicolás', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Av. Corrientes', '1300'),
  ('San Nicolás', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Maipú', '500'),
  ('Montserrat', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Av. de Mayo', '800'),
  ('Montserrat', 'Comuna 1', 'Ciudad Autónoma de Buenos Aires', 'Perú', '400'),

  -- Comuna 4
  ('La Boca', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Caminito', '100'),
  ('La Boca', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Brandsen', '805'),
  ('Barracas', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Av. Montes de Oca', '800'),
  ('Barracas', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Iriarte', '2500'),
  ('Parque Patricios', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Av. Caseros', '2900'),
  ('Parque Patricios', 'Comuna 4', 'Ciudad Autónoma de Buenos Aires', 'Uspallata', '3100'),

  -- Comuna 8
  ('Villa Lugano', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Av. Cruz', '4200'),
  ('Villa Lugano', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Soldado de la Frontera', '5200'),
  ('Villa Soldati', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Mariano Acosta', '3000'),
  ('Villa Soldati', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Av. Int. Roca', '6200'),
  ('Villa Riachuelo', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Av. Gral. Paz', '14000'),
  ('Villa Riachuelo', 'Comuna 8', 'Ciudad Autónoma de Buenos Aires', 'Pergamino', '2000'),

  -- Comuna 9
  ('Liniers', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Ramón Falcón', '6800'),
  ('Liniers', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Montiel', '500'),
  ('Mataderos', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Av. Emilio Castro', '6900'),
  ('Mataderos', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Murguiondo', '2100'),
  ('Parque Avellaneda', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Av. Directorio', '4200'),
  ('Parque Avellaneda', 'Comuna 9', 'Ciudad Autónoma de Buenos Aires', 'Lacarra', '1100'),

  -- Comuna 10
  ('Floresta', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Av. Avellaneda', '4200'),
  ('Floresta', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Bahía Blanca', '300'),
  ('Villa Luro', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Av. Rivadavia', '10200'),
  ('Villa Luro', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Corvalán', '100'),
  ('Monte Castro', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'Álvarez Jonte', '5300'),
  ('Monte Castro', 'Comuna 10', 'Ciudad Autónoma de Buenos Aires', 'J. V. González', '4400'),

  -- Comuna 11
  ('Villa Devoto', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Nueva York', '4500'),
  ('Villa Devoto', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Asunción', '3800'),
  ('Villa del Parque', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Cuenca', '2500'),
  ('Villa del Parque', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Av. Nazca', '2000'),
  ('Villa Santa Rita', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Álvarez Jonte', '3400'),
  ('Villa Santa Rita', 'Comuna 11', 'Ciudad Autónoma de Buenos Aires', 'Helguera', '2100'),

  -- Comuna 12
  ('Saavedra', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Av. Ricardo Balbín', '4300'),
  ('Saavedra', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Vedia', '1900'),
  ('Villa Urquiza', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Av. Triunvirato', '4700'),
  ('Villa Urquiza', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Bauness', '2200'),
  ('Villa Pueyrredón', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Artigas', '5400'),
  ('Villa Pueyrredón', 'Comuna 12', 'Ciudad Autónoma de Buenos Aires', 'Bolivia', '3500'),

  -- Comuna 13
  ('Belgrano', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Av. Cabildo', '2200'),
  ('Belgrano', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Juramento', '1700'),
  ('Colegiales', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Av. Federico Lacroze', '3200'),
  ('Colegiales', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Conesa', '700'),
  ('Núñez', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Av. Cabildo', '3400'),
  ('Núñez', 'Comuna 13', 'Ciudad Autónoma de Buenos Aires', 'Crisólogo Larralde', '2400')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 2. ESPECIALIDADES Y TARIFAS
-- ============================================================================

INSERT INTO athome.especialidad (nombre, tarifa)
VALUES
  ('Acompañamiento Terapéutico General', 15000),
  ('Acompañamiento Terapéutico Geriatría', 15000),
  ('Acompañamiento Terapéutico (Especialización TEA/TDAH)', 15000),
  ('Enfermería', 18000),
  ('Enfermería Geriátrica', 18000),
  ('Cuidados Paliativos', 25000)
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================================
-- 3. RELACIONES SOLICITANTE-PACIENTE
-- ============================================================================

INSERT INTO athome.relacion_solicitante (id, nombre)
VALUES
  (35, 'Yo mismo'),
  (36, 'Madre'),
  (37, 'Padre'),
  (38, 'Hijo'),
  (39, 'Hija'),
  (40, 'Hermano'),
  (41, 'Hermana'),
  (42, 'Esposo'),
  (43, 'Esposa'),
  (44, 'Abuelo'),
  (45, 'Abuela'),
  (46, 'Tío'),
  (47, 'Tía'),
  (48, 'Tutor/a'),
  (49, 'Otro familiar')
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 4. 100 PROFESIONALES
-- ============================================================================
-- Distribución:
--   30 AT General
--   15 AT Geriatría
--   10 AT TEA/TDAH
--   20 Enfermería
--   15 Enfermería Geriátrica
--   10 Cuidados Paliativos
-- ============================================================================

-- Primero creamos usuarios para los profesionales
-- Email: profesional{N}@athomered.com
-- Password: todos usan 'password123' hasheado

DO $$
DECLARE
  v_usuario_id UUID;
  v_direccion_id UUID;
  v_profesional_id UUID;
  v_provincia_nombre TEXT;
  v_especialidad_nombre TEXT;
  v_matricula_prefix TEXT;
  v_matricula_numero TEXT;
  nombres TEXT[] := ARRAY[
    'Juan', 'María', 'Carlos', 'Ana', 'Roberto', 'Laura', 'Diego', 'Patricia', 'Miguel', 'Gabriela',
    'Fernando', 'Claudia', 'Ricardo', 'Silvia', 'Jorge', 'Mónica', 'Pablo', 'Sandra', 'Martín', 'Liliana',
    'Andrés', 'Valeria', 'Sebastián', 'Natalia', 'Daniel', 'Carolina', 'Gustavo', 'Adriana', 'Alejandro', 'Mariana',
    'Marcelo', 'Paula', 'Javier', 'Lucía', 'Raúl', 'Daniela', 'Eduardo', 'Cecilia', 'Oscar', 'Verónica',
    'Héctor', 'Andrea', 'Alberto', 'Cristina', 'Sergio', 'Beatriz', 'Rubén', 'Marta', 'Luis', 'Rosa',
    'Federico', 'Susana', 'Nicolás', 'Elena', 'Hernán', 'Viviana', 'Maximiliano', 'Alicia', 'Facundo', 'Isabel',
    'Matías', 'Norma', 'Ezequiel', 'Gloria', 'Germán', 'Teresa', 'Leonardo', 'Irene', 'Emiliano', 'Graciela',
    'Rodrigo', 'Mercedes', 'Ignacio', 'Noemí', 'Agustín', 'Olga', 'Santiago', 'Mirta', 'Lucas', 'Elsa',
    'Tomás', 'Lidia', 'Mateo', 'Dora', 'Bruno', 'Carmen', 'Joaquín', 'Raquel', 'Thiago', 'Estela',
    'Bautista', 'Nora', 'Valentín', 'Silvia', 'Santino', 'Stella', 'Francisco', 'Blanca', 'Benicio', 'Clara'
  ];
  apellidos TEXT[] := ARRAY[
    'González', 'Rodríguez', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'García', 'Romero', 'Díaz',
    'Torres', 'Álvarez', 'Ruiz', 'Moreno', 'Jiménez', 'Muñoz', 'Castillo', 'Castro', 'Ortiz', 'Silva',
    'Vega', 'Ramos', 'Flores', 'Méndez', 'Vargas', 'Medina', 'Herrera', 'Aguilar', 'Gutiérrez', 'Ramírez',
    'Cruz', 'Reyes', 'Santos', 'Morales', 'Delgado', 'Rojas', 'Benítez', 'Cabrera', 'Acosta', 'Molina',
    'Figueroa', 'Peralta', 'Núñez', 'Luna', 'Sosa', 'Domínguez', 'Giménez', 'Ríos', 'Campos', 'Bustos'
  ];
  especialidades TEXT[] := ARRAY[
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General', 'Acompañamiento Terapéutico General',
    -- 15 AT Geriatría
    'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría',
    'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría',
    'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría',
    'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría',
    'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría', 'Acompañamiento Terapéutico Geriatría',
    -- 10 AT TEA/TDAH
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)', 'Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)', 'Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)', 'Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)', 'Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    'Acompañamiento Terapéutico (Especialización TEA/TDAH)', 'Acompañamiento Terapéutico (Especialización TEA/TDAH)',
    -- 20 Enfermería
    'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería',
    'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería',
    'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería',
    'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería', 'Enfermería',
    -- 15 Enfermería Geriátrica
    'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica',
    'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica',
    'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica', 'Enfermería Geriátrica',
    -- 10 Cuidados Paliativos
    'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos',
    'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos', 'Cuidados Paliativos'
  ];
  i INT;
BEGIN
  FOR i IN 1..100 LOOP
    -- Crear usuario
    INSERT INTO athome.usuario (nombre, apellido, email, telefono, password_hash)
    VALUES (
      nombres[((i - 1) % 100) + 1],
      apellidos[((i - 1) % 50) + 1],
      'profesional' || i || '@athomered.com',
      '11' || LPAD((5000 + i)::TEXT, 8, '0'),
      '$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7'  -- password: password123
    )
    RETURNING id INTO v_usuario_id;

    -- Obtener dirección random
    SELECT id INTO v_direccion_id
    FROM athome.direccion
    ORDER BY RANDOM()
    LIMIT 1;

    -- Crear profesional
    v_especialidad_nombre := especialidades[i];
    
    -- Determinar provincia (50% CABA, 50% PBA)
    IF (i % 2) = 0 THEN
      v_provincia_nombre := 'Ciudad Autónoma de Buenos Aires';
      v_matricula_prefix := 'CABA';
    ELSE
      v_provincia_nombre := 'Buenos Aires';
      v_matricula_prefix := 'PBA';
    END IF;

    INSERT INTO athome.profesional (usuario_id, especialidad_nombre, direccion_id, biografia, anios_experiencia)
    VALUES (
      v_usuario_id,
      v_especialidad_nombre,
      v_direccion_id,
      'Profesional con amplia experiencia en ' || v_especialidad_nombre || '. Atención personalizada y de calidad.',
      (i % 25) + 1  -- Entre 1 y 25 años de experiencia
    )
    RETURNING id INTO v_profesional_id;

    -- Crear matrícula
    -- AT para acompañantes, EF para enfermería/paliativos
    IF v_especialidad_nombre LIKE 'Acompañamiento%' THEN
      INSERT INTO athome.matricula (profesional_id, provincia_nombre, nro_matricula)
      VALUES (
        v_profesional_id,
        v_provincia_nombre,
        v_matricula_prefix || '-AT-' || LPAD((100000 + i)::TEXT, 6, '0')
      );
    ELSE
      INSERT INTO athome.matricula (profesional_id, provincia_nombre, nro_matricula)
      VALUES (
        v_profesional_id,
        v_provincia_nombre,
        v_matricula_prefix || '-EF-' || LPAD((200000 + i)::TEXT, 6, '0')
      );
    END IF;
  END LOOP;
END $$;

-- ============================================================================
-- 5. 50 PACIENTES CON COHERENCIA EDAD-ESPECIALIDAD
-- ============================================================================

DO $$
DECLARE
  v_usuario_id UUID;
  v_solicitante_id UUID;
  v_paciente_id UUID;
  v_direccion_id UUID;
  v_relacion_id INT;
  v_fecha_nac DATE;
  v_edad INT;
  v_profesional_especialidad TEXT;
  nombres_ninos TEXT[] := ARRAY['Mateo', 'Sofía', 'Benjamín', 'Martina', 'Lucas', 'Emma', 'Thiago', 'Valentina', 'Santino', 'Isabella'];
  nombres_adultos TEXT[] := ARRAY['Carlos', 'María', 'Roberto', 'Ana', 'Jorge', 'Laura', 'Fernando', 'Patricia', 'Diego', 'Claudia'];
  nombres_mayores TEXT[] := ARRAY['Alberto', 'Rosa', 'Héctor', 'Elsa', 'Raúl', 'Mirta', 'Oscar', 'Nora', 'Rubén', 'Lidia'];
  apellidos TEXT[] := ARRAY[
    'Fernández', 'López', 'Martínez', 'García', 'Rodríguez', 'Pérez', 'González', 'Sánchez', 'Romero', 'Díaz',
    'Torres', 'Álvarez', 'Ruiz', 'Moreno', 'Jiménez', 'Muñoz', 'Silva', 'Castro', 'Ortiz', 'Vega',
    'Ramos', 'Flores', 'Méndez', 'Vargas', 'Medina', 'Herrera', 'Gutiérrez', 'Ramírez', 'Cruz', 'Reyes',
    'Santos', 'Morales', 'Delgado', 'Rojas', 'Benítez', 'Cabrera', 'Acosta', 'Molina', 'Núñez', 'Luna',
    'Sosa', 'Domínguez', 'Giménez', 'Ríos', 'Campos', 'Bustos', 'Peralta', 'Figueroa', 'Aguilar', 'Vázquez'
  ];
  v_nombre TEXT;
  i INT;
BEGIN
  FOR i IN 1..50 LOOP
    -- Determinar especialidad del profesional (random entre los 100)
    SELECT e.nombre INTO v_profesional_especialidad
    FROM athome.profesional p
    JOIN athome.especialidad e ON p.especialidad_nombre = e.nombre
    ORDER BY RANDOM()
    LIMIT 1;

    -- Asignar edad coherente con la especialidad
    IF v_profesional_especialidad = 'Acompañamiento Terapéutico (Especialización TEA/TDAH)' THEN
      -- Niños/adolescentes (5-17 años)
      v_edad := 5 + (i % 13);
      v_fecha_nac := CURRENT_DATE - INTERVAL '1 year' * v_edad;
      v_nombre := nombres_ninos[((i - 1) % 10) + 1];
      -- Relación: Madre, Padre, Tutor/a
      v_relacion_id := CASE (i % 3)
        WHEN 0 THEN 36  -- Madre
        WHEN 1 THEN 37  -- Padre
        ELSE 48         -- Tutor/a
      END;
    ELSIF v_profesional_especialidad IN ('Acompañamiento Terapéutico Geriatría', 'Enfermería Geriátrica', 'Cuidados Paliativos') THEN
      -- Adultos mayores (65-90 años)
      v_edad := 65 + (i % 26);
      v_fecha_nac := CURRENT_DATE - INTERVAL '1 year' * v_edad;
      v_nombre := nombres_mayores[((i - 1) % 10) + 1];
      -- Relación: Hijo, Hija, Esposo/a, Yo mismo
      v_relacion_id := CASE (i % 5)
        WHEN 0 THEN 38  -- Hijo
        WHEN 1 THEN 39  -- Hija
        WHEN 2 THEN 42  -- Esposo
        WHEN 3 THEN 43  -- Esposa
        ELSE 35         -- Yo mismo
      END;
    ELSE
      -- Adultos generales (25-70 años)
      v_edad := 25 + (i % 46);
      v_fecha_nac := CURRENT_DATE - INTERVAL '1 year' * v_edad;
      v_nombre := nombres_adultos[((i - 1) % 10) + 1];
      -- Relación: cualquiera
      v_relacion_id := CASE (i % 8)
        WHEN 0 THEN 35  -- Yo mismo
        WHEN 1 THEN 36  -- Madre
        WHEN 2 THEN 37  -- Padre
        WHEN 3 THEN 40  -- Hermano
        WHEN 4 THEN 41  -- Hermana
        WHEN 5 THEN 42  -- Esposo
        WHEN 6 THEN 43  -- Esposa
        ELSE 49         -- Otro familiar
      END;
    END IF;

    -- Crear usuario solicitante
    INSERT INTO athome.usuario (nombre, apellido, email, telefono, password_hash)
    VALUES (
      'Solicitante' || i,
      apellidos[((i - 1) % 50) + 1],
      'solicitante' || i || '@athomered.com',
      '11' || LPAD((6000 + i)::TEXT, 8, '0'),
      '$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7'
    )
    RETURNING id INTO v_usuario_id;

    -- Obtener dirección random
    SELECT id INTO v_direccion_id
    FROM athome.direccion
    ORDER BY RANDOM()
    LIMIT 1;

    -- Crear solicitante
    INSERT INTO athome.solicitante (usuario_id, direccion_id)
    VALUES (v_usuario_id, v_direccion_id)
    RETURNING id INTO v_solicitante_id;

    -- Crear paciente
    INSERT INTO athome.paciente (
      nombre, 
      apellido, 
      fecha_nacimiento, 
      notas, 
      solicitante_id, 
      relacion_id
    )
    VALUES (
      v_nombre,
      apellidos[((i - 1) % 50) + 1],
      v_fecha_nac,
      'Paciente con ' || v_profesional_especialidad || '. Edad: ' || v_edad || ' años.',
      v_solicitante_id,
      v_relacion_id
    );
  END LOOP;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

SELECT 'Provincias: ' || COUNT(*) FROM athome.provincia;
SELECT 'Departamentos: ' || COUNT(*) FROM athome.departamento;
SELECT 'Barrios: ' || COUNT(*) FROM athome.barrio;
SELECT 'Direcciones: ' || COUNT(*) FROM athome.direccion;
SELECT 'Especialidades: ' || COUNT(*) FROM athome.especialidad;
SELECT 'Relaciones: ' || COUNT(*) FROM athome.relacion_solicitante;
SELECT 'Profesionales: ' || COUNT(*) FROM athome.profesional;
SELECT 'Matrículas: ' || COUNT(*) FROM athome.matricula;
SELECT 'Solicitantes: ' || COUNT(*) FROM athome.solicitante;
SELECT 'Pacientes: ' || COUNT(*) FROM athome.paciente;

-- Distribución por especialidad
SELECT 
  e.nombre,
  COUNT(p.id) as cantidad
FROM athome.especialidad e
LEFT JOIN athome.profesional p ON e.nombre = p.especialidad_nombre
GROUP BY e.nombre
ORDER BY cantidad DESC;

-- Distribución de pacientes por relación
SELECT 
  r.nombre,
  COUNT(p.id) as cantidad
FROM athome.relacion_solicitante r
LEFT JOIN athome.paciente p ON r.id = p.relacion_id
GROUP BY r.nombre
ORDER BY cantidad DESC;
