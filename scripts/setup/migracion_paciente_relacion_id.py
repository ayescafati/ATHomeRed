"""
Migración: Hacer paciente.relacion_id NOT NULL

PASO 1: Poblar relacion_id NULL con 'Yo mismo' (id=35)
PASO 2: Agregar constraint NOT NULL
"""

from app.infra.persistence.database import SessionLocal
from sqlalchemy import text


def main():
    s = SessionLocal()

    print("=" * 80)
    print("MIGRACIÓN: paciente.relacion_id → NOT NULL")
    print("=" * 80)

    # Verificar estado actual
    print("\n1️⃣ Verificando estado actual...")
    result = s.execute(
        text(
            """
        SELECT 
            COUNT(*) as total,
            COUNT(relacion_id) as con_relacion,
            COUNT(*) - COUNT(relacion_id) as sin_relacion
        FROM athome.paciente
    """
        )
    ).fetchone()

    print(f"   Total pacientes: {result[0]}")
    print(f"   Con relacion_id: {result[1]}")
    print(f"   Sin relacion_id (NULL): {result[2]}")

    if result[2] > 0:
        print(
            f"\n2️⃣ Poblando {result[2]} pacientes con relacion_id = 35 ('Yo mismo')..."
        )
        s.execute(
            text(
                """
            UPDATE athome.paciente 
            SET relacion_id = 35
            WHERE relacion_id IS NULL
        """
            )
        )
        s.commit()
        print("   ✅ Completado")
    else:
        print("\n2️⃣ No hay pacientes con relacion_id NULL, saltando...")

    # Verificar constraint actual
    print("\n3️⃣ Verificando constraint actual...")
    constraint_check = s.execute(
        text(
            """
        SELECT is_nullable 
        FROM information_schema.columns
        WHERE table_schema = 'athome' 
        AND table_name = 'paciente'
        AND column_name = 'relacion_id'
    """
        )
    ).fetchone()

    if constraint_check[0] == "YES":
        print("   Columna es nullable: YES")
        print("\n4️⃣ Agregando constraint NOT NULL...")
        s.execute(
            text(
                """
            ALTER TABLE athome.paciente 
            ALTER COLUMN relacion_id SET NOT NULL
        """
            )
        )
        s.commit()
        print("   ✅ Constraint NOT NULL agregado")
    else:
        print("   Columna ya es NOT NULL, saltando...")

    # Verificar FK
    print("\n5️⃣ Verificando foreign key constraint...")
    fk_check = s.execute(
        text(
            """
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = 'athome'
        AND table_name = 'paciente'
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%relacion%'
    """
        )
    ).fetchone()

    if not fk_check:
        print("   FK no existe, creando...")
        s.execute(
            text(
                """
            ALTER TABLE athome.paciente 
            ADD CONSTRAINT fk_paciente_relacion 
            FOREIGN KEY (relacion_id) 
            REFERENCES athome.relacion_solicitante(id)
        """
            )
        )
        s.commit()
        print("   ✅ FK creado: fk_paciente_relacion")
    else:
        print(f"   FK ya existe: {fk_check[0]}")

    # Verificación final
    print("\n6️⃣ Verificación final...")
    final = s.execute(
        text(
            """
        SELECT 
            p.id,
            p.nombre,
            p.apellido,
            p.relacion_id,
            r.nombre as relacion_nombre
        FROM athome.paciente p
        JOIN athome.relacion_solicitante r ON p.relacion_id = r.id
        ORDER BY p.nombre
    """
        )
    ).fetchall()

    print(f"\n✅ Total pacientes con relacion: {len(final)}")
    for row in final:
        print(f"   {row[1]} {row[2]:15s} → relacion_id={row[3]:2d} ({row[4]})")

    s.close()

    print("\n" + "=" * 80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    main()
