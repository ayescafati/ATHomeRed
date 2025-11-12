"""
Demo completo del patrón Observer con todos los estados de citas.

Muestra cómo Paciente y Profesional interactúan con las citas
y cómo el Observer (NotificadorEmail) se dispara automáticamente.

Uso:
    python scripts/dev/demo_observer_completo.py
"""

from uuid import uuid4
from datetime import date, time
from app.domain.entities.agenda import Cita
from app.domain.observers.observadores import NotificadorEmail
from app.domain.value_objects.objetos_valor import Ubicacion
from app.domain.enumeraciones import EstadoCita


def main():
    print("=" * 80)
    print("DEMO: Patrón Observer - Gestión de Citas en ATHomeRed")
    print("=" * 80)
    print()

    # IDs de los actores
    paciente_id = uuid4()
    profesional_id = uuid4()
    
    print(f"👤 Paciente ID: {paciente_id}")
    print(f"👨‍⚕️ Profesional ID (Enfermería): {profesional_id}")
    print()

    # ========== PASO 1: CREAR CITA (Sistema/Paciente) ==========
    print("-" * 80)
    print("PASO 1: PACIENTE solicita una cita (estado PENDIENTE)")
    print("-" * 80)
    
    cita = Cita(
        id=uuid4(),
        paciente_id=paciente_id,
        profesional_id=profesional_id,
        fecha=date(2025, 11, 15),
        hora_inicio=time(14, 0),
        hora_fin=time(15, 30),
        ubicacion=Ubicacion(
            provincia="Buenos Aires",
            departamento="CABA",
            barrio="Almagro",
            calle="Av. Corrientes",
            numero="1234",
            latitud=-34.603722,
            longitud=-58.381592
        ),
        motivo_consulta="Cuidado post-operatorio a domicilio",
        estado=EstadoCita.PENDIENTE
    )
    
    print(f"✅ Cita creada: {cita.id}")
    print(f"   Estado: {cita.estado.value}")
    print(f"   Fecha: {cita.fecha} {cita.hora_inicio} - {cita.hora_fin}")
    print(f"   Duración: {cita.duracion}")
    print()

    # ========== PASO 2: PROFESIONAL CONFIRMA ==========
    print("-" * 80)
    print("PASO 2: PROFESIONAL acepta/confirma la cita")
    print("-" * 80)
    
    # Adjuntar Observer
    notificador = NotificadorEmail()
    cita.attach(notificador)
    print("🔔 Observer (NotificadorEmail) adjuntado")
    print()
    
    # Profesional confirma
    cita.confirmar(confirmado_por=f"profesional:{profesional_id}")
    print(f"✅ Estado actual: {cita.estado.value}")
    print()

    # ========== PASO 3: PACIENTE REPROGRAMA ==========
    print("-" * 80)
    print("PASO 3: PACIENTE necesita cambiar el horario")
    print("-" * 80)
    
    nueva_fecha = date(2025, 11, 16)
    nueva_hora_inicio = time(10, 0)
    nueva_hora_fin = time(11, 30)
    
    cita.reprogramar(
        nueva_fecha=nueva_fecha,
        nueva_hora_inicio=nueva_hora_inicio,
        nueva_hora_fin=nueva_hora_fin
    )
    print(f"✅ Cita reprogramada")
    print(f"   Nueva fecha: {cita.fecha} {cita.hora_inicio} - {cita.hora_fin}")
    print()

    # ========== PASO 4: PROFESIONAL COMPLETA ==========
    print("-" * 80)
    print("PASO 4: PROFESIONAL completa la cita (servicio finalizado)")
    print("-" * 80)
    
    cita.completar(notas_finales="Curación realizada correctamente. Paciente estable. Control en 7 días.")
    print(f"✅ Estado actual: {cita.estado.value}")
    print(f"   Notas finales: {cita.notas}")
    print()

    # ========== CASO ALTERNATIVO: CANCELACIÓN ==========
    print("-" * 80)
    print("CASO ALTERNATIVO: ¿Qué pasa si se cancela?")
    print("-" * 80)
    
    # Crear otra cita para demostrar cancelación
    cita2 = Cita(
        id=uuid4(),
        paciente_id=paciente_id,
        profesional_id=profesional_id,
        fecha=date(2025, 11, 20),
        hora_inicio=time(16, 0),
        hora_fin=time(17, 0),
        ubicacion=Ubicacion(
            provincia="Buenos Aires",
            departamento="CABA",
            barrio="Palermo",
            calle="Av. Santa Fe",
            numero="3000",
            latitud=-34.588333,
            longitud=-58.414167
        ),
        motivo_consulta="Control de presión arterial",
        estado=EstadoCita.PENDIENTE
    )
    
    cita2.attach(notificador)
    print(f"📅 Nueva cita creada: {cita2.id}")
    print()
    
    # Paciente cancela
    cita2.cancelar(
        motivo="Surgió un imprevisto familiar",
        cancelado_por=f"paciente:{paciente_id}"
    )
    print(f"✅ Cita cancelada por paciente")
    print(f"   Estado: {cita2.estado.value}")
    print()

    # ========== RESUMEN FINAL ==========
    print("=" * 80)
    print("RESUMEN: Flujos implementados en la API")
    print("=" * 80)
    print()
    print("🔹 POST /consultas/{id}/confirmar")
    print("   ├─ Paciente puede confirmar")
    print("   └─ Profesional puede confirmar")
    print()
    print("🔹 DELETE /consultas/{id} (cancelar)")
    print("   ├─ Paciente puede cancelar")
    print("   └─ Profesional puede cancelar")
    print()
    print("🔹 POST /consultas/{id}/completar")
    print("   └─ Solo Profesional puede completar")
    print()
    print("🔹 POST /consultas/{id}/reprogramar")
    print("   ├─ Paciente puede reprogramar")
    print("   └─ Profesional puede reprogramar")
    print()
    print("✨ En TODOS los casos, el Observer (NotificadorEmail) se dispara automáticamente")
    print("=" * 80)


if __name__ == "__main__":
    main()
