"""
Script para limpiar la base de datos antes de ejecutar el seed completo.
Elimina todos los datos manteniendo la estructura de tablas.
"""
from app.infra.persistence.database import SessionLocal
from sqlalchemy import text

def limpiar_bd():
    s = SessionLocal()
    
    print("=" * 80)
    print("LIMPIEZA DE BASE DE DATOS")
    print("=" * 80)
    
    try:
        # Orden de eliminación respetando FKs (de hijos a padres)
        tablas_orden = [
            'consulta',
            'valoracion',
            'matricula',
            'paciente',
            'solicitante',
            'profesional',
            'usuario',
            'direccion',
            'barrio',
            'departamento',
            'provincia',
            'relacion_solicitante',
            'especialidad',
            'auditoria_login',
        ]
        
        print("\n🗑️  Eliminando datos de las tablas...")
        
        for tabla in tablas_orden:
            print(f"   Limpiando athome.{tabla}...", end='')
            s.execute(text(f"DELETE FROM athome.{tabla}"))
            count = s.execute(text(f"SELECT COUNT(*) FROM athome.{tabla}")).scalar()
            print(f" ✅ ({count} registros restantes)")
        
        s.commit()
        
        print("\n📊 Verificación final:")
        for tabla in tablas_orden:
            count = s.execute(text(f"SELECT COUNT(*) FROM athome.{tabla}")).scalar()
            if count > 0:
                print(f"   ⚠️  athome.{tabla}: {count} registros")
            else:
                print(f"   ✅ athome.{tabla}: vacía")
        
        print("\n" + "=" * 80)
        print("✅ BASE DE DATOS LIMPIA")
        print("=" * 80)
        
    except Exception as e:
        s.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        s.close()

if __name__ == "__main__":
    limpiar_bd()
