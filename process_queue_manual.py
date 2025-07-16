#!/usr/bin/env python3
"""
Script manual para procesar la cola FIFO de mensajes
"""

import sys
import os
import json
import time
import redis
import logging
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar servicios
from services.websocket_service import WebSocketService

def process_queue_manually():
    """Procesador manual de cola FIFO"""
    
    # Configurar Redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url)
    websocket_service = WebSocketService()
    
    # Nombres de las colas
    message_queue_key = 'webhook_messages_queue'
    failed_queue_key = 'webhook_messages_failed'
    processing_queue_key = 'webhook_messages_processing'
    
    max_attempts = 3
    retry_delay = 5  # segundos (más corto para pruebas)
    
    logger.info("Iniciando procesador manual de cola FIFO")
    logger.info(f"Redis URL: {redis_url}")
    logger.info(f"WebSocket disponible: {websocket_service.health_check()}")
    
    try:
        while True:
            try:
                # Obtener mensaje de la cola FIFO (RPOP para mantener orden FIFO)
                message_json = redis_client.brpop(message_queue_key, timeout=10)
                
                if not message_json:
                    # Sin mensajes, mostrar estado y continuar
                    queue_lengths = {
                        "pending": redis_client.llen(message_queue_key),
                        "processing": redis_client.llen(processing_queue_key),
                        "failed": redis_client.llen(failed_queue_key)
                    }
                    if queue_lengths["pending"] > 0 or queue_lengths["processing"] > 0 or queue_lengths["failed"] > 0:
                        logger.info(f"Estado de colas: {queue_lengths}")
                    continue
                
                # Deserializar mensaje
                message_data = json.loads(message_json[1])
                
                # Mover a cola de procesamiento
                redis_client.lpush(processing_queue_key, json.dumps(message_data))
                
                # Incrementar contador de intentos
                message_data['attempts'] = message_data.get('attempts', 0) + 1
                
                logger.info(f"Procesando mensaje FIFO intento {message_data['attempts']} desde {message_data.get('from', 'unknown')}")
                
                # Intentar procesar el mensaje
                success = False
                try:
                    websocket_service.send_message(message_data)
                    success = True
                    logger.info(f"✅ Mensaje FIFO procesado exitosamente desde {message_data.get('from', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje FIFO: {str(e)}")
                    
                    # Verificar si hemos superado el máximo de intentos
                    if message_data['attempts'] >= max_attempts:
                        # Mover a cola de fallos
                        redis_client.lpush(failed_queue_key, json.dumps(message_data))
                        logger.error(f"💀 Mensaje FIFO movido a cola de fallos después de {max_attempts} intentos: {message_data.get('from', 'unknown')}")
                        success = True  # Para no reintentarlo
                    else:
                        # Volver a poner en la cola principal con delay
                        logger.info(f"🔄 Reintentando mensaje en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        redis_client.lpush(message_queue_key, json.dumps(message_data))
                        logger.info(f"📤 Mensaje FIFO reintentado y devuelto a la cola: {message_data.get('from', 'unknown')}")
                        success = True
                
                # Remover de cola de procesamiento
                redis_client.lrem(processing_queue_key, 1, json.dumps(message_data))
                
            except KeyboardInterrupt:
                logger.info("⏹️  Deteniendo procesador manual...")
                break
                
            except Exception as e:
                logger.error(f"Error en procesador FIFO: {str(e)}")
                time.sleep(5)  # Esperar antes de continuar
                
    except KeyboardInterrupt:
        logger.info("Procesador manual detenido por el usuario")
        
    except Exception as e:
        logger.error(f"Error crítico en procesador FIFO: {str(e)}")
        
    finally:
        # Mostrar estado final
        queue_lengths = {
            "pending": redis_client.llen(message_queue_key),
            "processing": redis_client.llen(processing_queue_key),
            "failed": redis_client.llen(failed_queue_key)
        }
        logger.info(f"Estado final de colas: {queue_lengths}")

if __name__ == '__main__':
    process_queue_manually()
