"""
Script para agregar consultas y valoraciones a datos existentes
Ejecutar después de seed_completo.py o seed_minimo.py
"""

import sys
from pathlib import Path
from datetime import date, time, datetime, timedelta
from uuid import uuid4
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.infra.persistence.database import SessionLocal
from app.infra.persistence.agenda import ConsultaORM
from app.infra.persistence.valoraciones import ValoracionORM


def agregar_consultas_valoraciones():
    """Agrega consultas y valoraciones a los datos existentes"""
    
    session = SessionLocal()
    
    print("\n" + "=" * 70)
    print("📋 AGREGANDO DIRECCIONES, CONSULTAS Y VALORACIONES")
    print("=" * 70 + "\n")
    
    try:
        # 0. Crear algunas direcciones primero
        print("[0/4] Creando direcciones de servicio...")
        direcciones_ids = []
        
        # Obtener un barrio existente
        barrio_result = session.execute(
            text("SELECT id FROM athome.barrio LIMIT 1")
        ).fetchone()
        
        if barrio_result:
            barrio_id = str(barrio_result[0])
            
            # Crear algunas direcciones de ejemplo
            direcciones_data = [
                {"calle": "Av. Colón", "numero": 1234},
                {"calle": "Bv. San Juan", "numero": 567},
                {"calle": "Av. Vélez Sarsfield", "numero": 890},
                {"calle": "Humberto Primo", "numero": 456},
                {"calle": "Duarte Quirós", "numero": 789},
                {"calle": "Av. Yrigoyen", "numero": 321},
                {"calle": "Calle Buenos Aires", "numero": 654},
            ]
            
            for dir_data in direcciones_data:
                dir_id = str(uuid4())
                session.execute(
                    text(
                        "INSERT INTO athome.direccion (id, calle, numero, barrio_id) "
                        "VALUES (:id, :calle, :numero, :barrio_id)"
                    ),
                    {
                        "id": dir_id,
                        "calle": dir_data["calle"],
                        "numero": dir_data["numero"],
                        "barrio_id": barrio_id
                    }
                )
                direcciones_ids.append(dir_id)
            
            session.commit()
            print(f"  ✓ {len(direcciones_ids)} direcciones creadas")
        else:
            print("  ⚠ No hay barrios en la DB, usando direcciones sin barrio")
        
        # 1. Obtener profesionales existentes
        print("\n[1/4] Obteniendo profesionales...")
        profesionales = session.execute(
            text("SELECT id FROM athome.profesional LIMIT 20")
        ).fetchall()
        
        if not profesionales:
            print("❌ No hay profesionales en la base de datos")
            return
        
        profesionales_ids = [str(p[0]) for p in profesionales]
        print(f"  ✓ {len(profesionales_ids)} profesionales encontrados")
        
        # 2. Obtener pacientes existentes
        print("\n[2/4] Obteniendo pacientes...")
        pacientes = session.execute(
            text("SELECT id FROM athome.paciente LIMIT 20")
        ).fetchall()
        
        if not pacientes:
            print("❌ No hay pacientes en la base de datos")
            return
        
        pacientes_ids = [str(p[0]) for p in pacientes]
        print(f"  ✓ {len(pacientes_ids)} pacientes encontrados")
        
        # 3. Obtener estados
        estados_map = {}
        estados = ["pendiente", "confirmada", "completada", "cancelada", "en_curso"]
        for estado in estados:
            result = session.execute(
                text("SELECT id FROM athome.estado_consulta WHERE codigo = :codigo"),
                {"codigo": estado}
            ).fetchone()
            if result:
                estados_map[estado] = result[0]
        
        print(f"  ✓ {len(estados_map)} estados encontrados")
        
        # 4. Verificar que tenemos direcciones
        if not direcciones_ids:
            print("\n❌ No se pueden crear consultas sin direcciones")
            return
        
        # 5. Crear consultas
        print("\n[3/4] Creando consultas...")
        hoy = date.today()
        consultas_creadas = 0
        consultas_completadas = []
        
        # Determinar cuántas consultas crear
        num_consultas = min(30, len(profesionales_ids) * len(pacientes_ids))
        
        for i in range(num_consultas):
            try:
                prof_id = random.choice(profesionales_ids)
                pac_id = random.choice(pacientes_ids)
                
                # Fecha aleatoria (últimos 30 días o próximos 30 días)
                dias_offset = random.randint(-30, 30)
                fecha_consulta = hoy + timedelta(days=dias_offset)
                
                # Horario aleatorio
                hora_inicio = time(random.randint(8, 16), random.choice([0, 30]))
                hora_fin_hour = (hora_inicio.hour + random.randint(1, 3)) % 24
                hora_fin = time(hora_fin_hour, hora_inicio.minute)
                
                # Estado según la fecha
                if dias_offset < -7:
                    estado = "completada"
                elif dias_offset < 0:
                    estado = random.choice(["completada", "cancelada"])
                elif dias_offset < 7:
                    estado = random.choice(["pendiente", "confirmada"])
                else:
                    estado = "pendiente"
                
                consulta_id = str(uuid4())
                consulta = ConsultaORM(
                    id=consulta_id,
                    paciente_id=pac_id,
                    profesional_id=prof_id,
                    direccion_servicio_id=random.choice(direcciones_ids),  # Usar dirección aleatoria
                    fecha=fecha_consulta,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    estado_id=estados_map.get(estado, estados_map.get("pendiente")),
                    notas=f"Consulta generada automáticamente - Estado: {estado}",
                )
                session.add(consulta)
                consultas_creadas += 1
                
                # Guardar consultas completadas para valoraciones
                if estado == "completada":
                    consultas_completadas.append({
                        "id": consulta_id,
                        "paciente_id": pac_id,
                        "profesional_id": prof_id,
                    })
                
            except Exception as e:
                print(f"  ⚠ Error creando consulta {i+1}: {str(e)[:60]}")
                session.rollback()
                continue
        
        session.commit()
        print(f"  ✓ {consultas_creadas} consultas creadas")
        
        # 6. Crear valoraciones para consultas completadas
        if consultas_completadas:
            print(f"\n[4/4] Creando valoraciones para {len(consultas_completadas)} consultas completadas...")
            
            comentarios = [
                "Excelente atención, muy profesional y cálido trato.",
                "Muy buen servicio, puntual y comprometido con el paciente.",
                "Profesional muy capacitado, explicó todo claramente.",
                "Muy satisfechos con la atención brindada.",
                "Excelente cuidado y seguimiento del tratamiento.",
                "Muy recomendable, trato humano y profesional.",
                "Superó nuestras expectativas, muy buen trabajo.",
                "Atención de primera calidad.",
                "Muy profesional, resolvió todas nuestras dudas.",
                "Excelente experiencia, volveremos a solicitar sus servicios.",
            ]
            
            valoraciones_creadas = 0
            
            for consulta in consultas_completadas:
                # Crear valoración con probabilidad del 60%
                if random.random() < 0.6:
                    try:
                        valoracion = ValoracionORM(
                            id=str(uuid4()),
                            paciente_id=consulta["paciente_id"],
                            profesional_id=consulta["profesional_id"],
                            puntuacion=random.randint(4, 5),  # Mayormente positivas
                            comentario=random.choice(comentarios),
                            # creado_en se setea automáticamente por default
                        )
                        session.add(valoracion)
                        valoraciones_creadas += 1
                    except Exception as e:
                        print(f"  ⚠ Error creando valoración: {str(e)[:60]}")
                        continue
            
            session.commit()
            print(f"  ✓ {valoraciones_creadas} valoraciones creadas")
        
        print("\n" + "=" * 70)
        print("✅ CONSULTAS Y VALORACIONES AGREGADAS EXITOSAMENTE")
        print("=" * 70)
        print(f"\n📊 Resumen:")
        print(f"   • Consultas creadas: {consultas_creadas}")
        print(f"   • Valoraciones creadas: {valoraciones_creadas if consultas_completadas else 0}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    agregar_consultas_valoraciones()
