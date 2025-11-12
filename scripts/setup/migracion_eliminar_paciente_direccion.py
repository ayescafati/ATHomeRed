"""
Migración: Eliminar paciente.direccion_id (redundante)

RAZÓN: La dirección del servicio siempre es la del SOLICITANTE
- Si paciente = solicitante → usa solicitante.direccion_id
- Si paciente ≠ solicitante → usa solicitante.direccion_id (viven juntos)
- Si paciente vive separado → NO IMPORTA (servicio se presta en casa del solicitante)
"""
from app.infra.persistence.database import SessionLocal
from sqlalchemy import text

def main():
    s = SessionLocal()
    
    print("=" * 80)
    print("MIGRACIÓN: Eliminar paciente.direccion_id")
    print("=" * 80)
    
    # Verificar si la columna existe
    print("\n1️⃣ Verificando existencia de columna...")
    col_check = s.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'athome'
        AND table_name = 'paciente'
        AND column_name = 'direccion_id'
    """)).fetchone()
    
    if not col_check:
        print("   ❌ Columna direccion_id no existe, nada que hacer")
        s.close()
        return
    
    print("   ✅ Columna direccion_id existe")
    
    # Verificar datos actuales
    print("\n2️⃣ Verificando datos actuales...")
    data_check = s.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(direccion_id) as con_direccion,
            COUNT(*) - COUNT(direccion_id) as sin_direccion
        FROM athome.paciente
    """)).fetchone()
    
    print(f"   Total pacientes: {data_check[0]}")
    print(f"   Con direccion_id: {data_check[1]}")
    print(f"   Sin direccion_id: {data_check[2]}")
    
    if data_check[1] > 0:
        print(f"\n   ⚠️  {data_check[1]} pacientes tienen direccion_id poblado")
        print("   Estos datos se perderán al eliminar la columna")
        print("   (No es problema porque es información redundante)")
        
        # Mostrar algunos ejemplos
        print("\n   📋 Ejemplos de direcciones que se perderán:")
        ejemplos = s.execute(text("""
            SELECT 
                p.nombre,
                p.apellido,
                p.direccion_id,
                d.calle,
                d.numero
            FROM athome.paciente p
            LEFT JOIN athome.direccion d ON p.direccion_id = d.id
            WHERE p.direccion_id IS NOT NULL
            LIMIT 3
        """)).fetchall()
        
        for ej in ejemplos:
            print(f"      {ej[0]} {ej[1]} → {ej[3]} {ej[4] if ej[4] else ''}")
    
    # Verificar foreign key
    print("\n3️⃣ Verificando foreign key constraint...")
    fk_check = s.execute(text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = 'athome'
        AND table_name = 'paciente'
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%direccion%'
    """)).fetchone()
    
    if fk_check:
        print(f"   FK encontrado: {fk_check[0]}")
        print(f"   Eliminando FK primero...")
        s.execute(text(f"""
            ALTER TABLE athome.paciente 
            DROP CONSTRAINT {fk_check[0]}
        """))
        s.commit()
        print("   ✅ FK eliminado")
    else:
        print("   No hay FK para direccion_id")
    
    # Eliminar columna
    print("\n4️⃣ Eliminando columna direccion_id...")
    s.execute(text("""
        ALTER TABLE athome.paciente 
        DROP COLUMN direccion_id
    """))
    s.commit()
    print("   ✅ Columna eliminada")
    
    # Verificación final
    print("\n5️⃣ Verificación final...")
    final_check = s.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'athome'
        AND table_name = 'paciente'
        ORDER BY ordinal_position
    """)).fetchall()
    
    print("\n   📋 Esquema final de tabla paciente:")
    for col in final_check:
        null_str = "NULL" if col[2] == 'YES' else "NOT NULL"
        print(f"      {col[0]:25s} {col[1]:20s} {null_str}")
    
    s.close()
    
    print("\n" + "=" * 80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 80)
    print("\n💡 RECORDATORIO:")
    print("   - Actualizar PacienteORM en app/infra/persistence/paciente.py")
    print("   - Actualizar PacienteRepository para eliminar referencias a direccion_id")

if __name__ == "__main__":
    main()
