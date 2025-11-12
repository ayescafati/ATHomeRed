"""
Ejemplo práctico de uso de la API con Observer.
Simula cómo un paciente y un profesional interactúan con el sistema.

REQUISITOS:
1. Servidor corriendo: python run_server.py
2. Base de datos inicializada
3. Usuarios creados (paciente y profesional)

Uso:
    python scripts/dev/ejemplo_uso_api_observer.py
"""

import requests
import json
from datetime import date, time, datetime, timedelta
from uuid import uuid4


BASE_URL = "http://localhost:8000/api/v1"


def print_separator(titulo):
    print("\n" + "=" * 80)
    print(f"  {titulo}")
    print("=" * 80)


def print_step(numero, titulo):
    print(f"\n{'─' * 80}")
    print(f"PASO {numero}: {titulo}")
    print("─" * 80)


def hacer_request(method, endpoint, token=None, json_data=None, params=None):
    """Helper para hacer requests con manejo de errores"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data)
        
        print(f"\n📡 {method} {endpoint}")
        if json_data:
            print(f"   Payload: {json.dumps(json_data, indent=2, default=str)}")
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except:
                return None
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo: python run_server.py")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None


def main():
    print_separator("EJEMPLO PRÁCTICO: API con Observer Pattern")
    
    print("\n📋 Este ejemplo simula:")
    print("   1. Paciente se autentica")
    print("   2. Paciente busca profesional de Enfermería")
    print("   3. Paciente solicita una cita")
    print("   4. Paciente confirma la cita → Observer se dispara")
    print("   5. Profesional se autentica")
    print("   6. Profesional ve sus citas")
    print("   7. Profesional completa la cita → Observer se dispara")
    
    input("\n⏸️  Presiona Enter para continuar...")
    
    # ========== FLUJO DEL PACIENTE ==========
    print_separator("PARTE 1: FLUJO DEL PACIENTE")
    
    print_step(1, "PACIENTE se autentica")
    print("\n👤 Login del paciente...")
    
    # Credenciales del paciente (debes tener este usuario creado)
    paciente_login = {
        "username": "paciente.test@athomered.com",
        "password": "password123"
    }
    
    print(f"   Email: {paciente_login['username']}")
    auth_response = hacer_request("POST", "/auth/login", json_data=paciente_login)
    
    if not auth_response:
        print("\n❌ No se pudo autenticar al paciente.")
        print("   Crea un usuario paciente primero:")
        print("   POST /api/v1/auth/register")
        print('   {"email": "paciente.test@athomered.com", "password": "password123", "nombre": "Juan Test"}')
        return
    
    paciente_token = auth_response.get("access_token")
    print(f"   ✅ Token obtenido: {paciente_token[:30]}...")
    
    # Obtener ID del paciente del token (simplificado)
    # En producción decodificarías el JWT
    paciente_id = "aquí-iría-el-id-del-paciente"  # Mock
    
    print_step(2, "PACIENTE busca profesional de Enfermería")
    
    filtros = {
        "especialidad_id": 1,  # ID de Enfermería
        "provincia": "Buenos Aires"
    }
    
    profesionales = hacer_request("GET", "/busqueda/profesionales", 
                                  token=paciente_token, params=filtros)
    
    if not profesionales or len(profesionales) == 0:
        print("\n❌ No se encontraron profesionales.")
        print("   Asegúrate de tener profesionales creados y verificados en la BD")
        return
    
    profesional = profesionales[0]
    profesional_id = profesional["id"]
    print(f"\n   ✅ Profesional encontrado:")
    print(f"      Nombre: {profesional.get('nombre', 'N/A')}")
    print(f"      ID: {profesional_id}")
    print(f"      Especialidad: {profesional.get('especialidad', {}).get('nombre', 'N/A')}")
    
    print_step(3, "PACIENTE solicita una cita")
    
    # Crear cita para mañana
    manana = date.today() + timedelta(days=1)
    
    nueva_cita = {
        "profesional_id": profesional_id,
        "paciente_id": paciente_id,  # En producción vendría del token
        "solicitante_id": paciente_id,
        "fecha": manana.isoformat(),
        "hora_inicio": "14:00:00",
        "hora_fin": "15:30:00",
        "ubicacion": {
            "provincia": "Buenos Aires",
            "departamento": "CABA",
            "barrio": "Palermo",
            "calle": "Av. Santa Fe",
            "numero": "2500",
            "latitud": -34.588333,
            "longitud": -58.414167
        },
        "motivo": "Cuidado post-operatorio a domicilio"
    }
    
    cita_creada = hacer_request("POST", "/consultas/", 
                                token=paciente_token, json_data=nueva_cita)
    
    if not cita_creada:
        print("\n⚠️  No se pudo crear la cita. Ajusta los datos según tu BD.")
        return
    
    cita_id = cita_creada["id"]
    print(f"\n   ✅ Cita creada:")
    print(f"      ID: {cita_id}")
    print(f"      Estado: {cita_creada['estado']}")
    print(f"      Fecha: {cita_creada['fecha']} {cita_creada['hora_inicio']}-{cita_creada['hora_fin']}")
    
    print_step(4, "PACIENTE confirma la cita (Observer se dispara)")
    
    print("\n   🔔 Al confirmar, el Observer enviará notificaciones automáticamente:")
    print("      - Email al paciente confirmando")
    print("      - Email al profesional informando")
    
    input("\n⏸️  Presiona Enter para confirmar la cita...")
    
    confirmacion = hacer_request("POST", f"/consultas/{cita_id}/confirmar",
                                token=paciente_token)
    
    if confirmacion:
        print(f"\n   ✅ Cita confirmada!")
        print(f"      Estado: {confirmacion['estado']}")
        print("\n   📧 En el servidor deberías ver:")
        print("      ========== NOTIFICADOR EMAIL ==========")
        print(f"         Evento: CITA CONFIRMADA")
        print(f"         Cita ID: {cita_id}")
        print(f"         Confirmado por: paciente:{paciente_id}")
        print("      ========================================")
    
    # ========== FLUJO DEL PROFESIONAL ==========
    print_separator("PARTE 2: FLUJO DEL PROFESIONAL")
    
    print_step(5, "PROFESIONAL se autentica")
    print("\n👨‍⚕️ Login del profesional...")
    
    profesional_login = {
        "username": "profesional.enfermeria@athomered.com",
        "password": "password123"
    }
    
    print(f"   Email: {profesional_login['username']}")
    prof_auth = hacer_request("POST", "/auth/login", json_data=profesional_login)
    
    if not prof_auth:
        print("\n❌ No se pudo autenticar al profesional.")
        return
    
    prof_token = prof_auth.get("access_token")
    print(f"   ✅ Token obtenido: {prof_token[:30]}...")
    
    print_step(6, "PROFESIONAL consulta sus citas")
    
    mis_citas = hacer_request("GET", f"/consultas/profesional/{profesional_id}",
                             token=prof_token, params={"solo_activas": True})
    
    if mis_citas:
        print(f"\n   ✅ Citas activas: {len(mis_citas)}")
        for i, c in enumerate(mis_citas[:3], 1):
            print(f"      {i}. ID: {c['id'][:8]}... | Estado: {c['estado']} | Fecha: {c['fecha']}")
    
    print_step(7, "PROFESIONAL completa la cita (Observer se dispara)")
    
    print("\n   El profesional brinda el servicio y marca la cita como completada.")
    print("   🔔 El Observer notificará al paciente automáticamente.")
    
    input("\n⏸️  Presiona Enter para completar la cita...")
    
    completar_data = {
        "notas_finales": "Servicio de enfermería completado. Curación realizada correctamente. Paciente estable. Control en 7 días."
    }
    
    cita_completada = hacer_request("POST", f"/consultas/{cita_id}/completar",
                                   token=prof_token, json_data=completar_data)
    
    if cita_completada:
        print(f"\n   ✅ Cita completada!")
        print(f"      Estado: {cita_completada['estado']}")
        print(f"      Notas: {cita_completada.get('notas', 'N/A')[:80]}...")
        print("\n   📧 En el servidor deberías ver:")
        print("      ========== NOTIFICADOR EMAIL ==========")
        print(f"         Evento: CITA COMPLETADA")
        print(f"         Cita ID: {cita_id}")
        print(f"         Notas: {completar_data['notas_finales'][:50]}...")
        print("      ========================================")
    
    # ========== RESUMEN FINAL ==========
    print_separator("RESUMEN")
    
    print("\n✅ Flujo completado exitosamente!")
    print("\n📊 Eventos del Observer disparados:")
    print("   1. CitaCreada → Al crear la cita")
    print("   2. CitaConfirmada → Cuando el paciente confirmó")
    print("   3. CitaCompletada → Cuando el profesional finalizó")
    print("\n💡 Puntos clave:")
    print("   • Ni el paciente ni el profesional llamaron directamente al Observer")
    print("   • Las notificaciones se dispararon automáticamente")
    print("   • El patrón Observer desacopla la lógica de negocio de las notificaciones")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución cancelada por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
