#!/usr/bin/env python3
"""
Script para probar el sistema FIFO completo
Ejecutar: python test_fifo_system.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5050"

def test_health():
    """Probar health check básico"""
    print("🏥 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: OK")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_queue_status():
    """Probar estado de la cola FIFO"""
    print("\n📊 Probando estado de cola FIFO...")
    try:
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado de cola obtenido:")
            print(f"   - WebSocket disponible: {data['status'].get('websocket_available')}")
            print(f"   - Procesador corriendo: {data['status'].get('processor_running')}")
            print(f"   - Thread procesador vivo: {data['status'].get('processor_thread_alive')}")
            print(f"   - Nombre del thread: {data['status'].get('processor_thread_name')}")
            print(f"   - Tamaño de cola: {data['status'].get('queue_size', 0)}")
            return data['status']
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_queue_lengths():
    """Probar longitudes de cola"""
    print("\n📏 Probando longitudes de cola...")
    try:
        response = requests.get(f"{BASE_URL}/api/queue/lengths", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensajes pendientes: {data['queue_lengths'].get('pending', 0)}")
            return data['queue_lengths']
        else:
            print(f"❌ Error obteniendo longitudes: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_fifo_queue():
    """Probar la cola FIFO con mensaje de prueba"""
    print("\n🧪 Probando cola FIFO con mensaje de prueba...")
    try:
        response = requests.post(f"{BASE_URL}/api/queue/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Mensaje de prueba enviado a cola FIFO:")
            print(f"   - Método: {data['result'].get('method')}")
            print(f"   - Éxito: {data['result'].get('success')}")
            return True
        else:
            print(f"❌ Error probando cola: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def simulate_webhook():
    """Simular un webhook de WhatsApp"""
    print("\n📱 Simulando webhook de WhatsApp...")
    
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1035271725346226",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "573219306305",
                                "phone_number_id": "723278304205850"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Usuario de Prueba"
                                    },
                                    "wa_id": "573103391854"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "573103391854",
                                    "id": "test_message_id_12345",
                                    "timestamp": str(int(time.time())),
                                    "text": {
                                        "body": "Mensaje de prueba del sistema FIFO"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=webhook_data, timeout=5)
        if response.status_code == 200:
            print("✅ Webhook simulado enviado correctamente")
            print("   - El mensaje debería aparecer en los logs del procesador FIFO")
            return True
        else:
            print(f"❌ Error enviando webhook: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA FIFO")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ El servicio no está disponible. Verifica que esté corriendo.")
        sys.exit(1)
    
    # Test 2: Estado de cola
    queue_status = test_queue_status()
    if not queue_status:
        print("\n❌ No se pudo obtener estado de cola")
        sys.exit(1)
    
    # Verificar que el procesador esté corriendo
    if not queue_status.get('processor_running'):
        print("\n⚠️ El procesador FIFO NO está corriendo")
        print("   Esto puede indicar un problema en la inicialización")
    
    if not queue_status.get('processor_thread_alive'):
        print("\n⚠️ El thread del procesador NO está vivo")
        print("   Esto puede indicar un problema en el threading")
    
    # Test 3: Longitudes de cola
    test_queue_lengths()
    
    # Test 4: Probar cola FIFO
    test_fifo_queue()
    
    # Esperar un momento para que se procese
    print("\n⏳ Esperando 3 segundos para que se procese...")
    time.sleep(3)
    
    # Test 5: Verificar longitudes después
    print("\n📏 Verificando longitudes después de la prueba...")
    test_queue_lengths()
    
    # Test 6: Simular webhook real
    simulate_webhook()
    
    # Esperar un momento para que se procese
    print("\n⏳ Esperando 5 segundos para que se procese el webhook...")
    time.sleep(5)
    
    # Test final: Verificar estado final
    print("\n📊 Estado final del sistema:")
    test_queue_status()
    test_queue_lengths()
    
    print("\n" + "=" * 50)
    print("✅ PRUEBAS COMPLETADAS")
    print("\n📋 Para verificar que funcionó:")
    print("   1. Revisa los logs: docker logs webhook_personal-app-1 -f")
    print("   2. Busca mensajes como: '➡️ PROCESANDO MENSAJE FIFO'")
    print("   3. Busca mensajes como: '✅ MENSAJE COMPLETADO'")
    print("\n🔧 Si no ves esos logs, el procesador FIFO puede no estar iniciado correctamente")

if __name__ == "__main__":
    main()