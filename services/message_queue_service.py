import logging
import threading
import time
import queue
from typing import Dict
from .websocket_service import WebSocketService

logger = logging.getLogger(__name__)

class MessageQueueService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MessageQueueService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.websocket_service = WebSocketService()
        self.message_queue = queue.Queue()
        
        # Control de threading
        self.processor_thread = None
        self.running = False
        self._initialized = True

        logger.info("🚀 MessageQueueService inicializado")

        # Asegurar que el procesador esté activo al inicializar
        self._ensure_processor_running()

    def _ensure_processor_running(self):
        """Verifica y reinicia el procesador de cola si no está activo"""
        if self.processor_thread:
            thread_alive = self.processor_thread.is_alive()
            thread_registered = self.processor_thread in threading.enumerate()
        else:
            thread_alive = False
            thread_registered = False

        if not self.processor_thread or not thread_alive or not thread_registered:
            # Reiniciar flags para permitir nuevo thread
            self.running = False
            self.processor_thread = None
            self._start_queue_processor()
    
    def add_message_to_queue(self, message_data: Dict):
        """Añade un mensaje a la cola FIFO para procesamiento"""
        try:
            # Asegurar que el procesador esté activo
            self._ensure_processor_running()

            # Extraer info básica para logging
            from_number = "unknown"
            message_text = "N/A"
            
            # Intentar extraer número y texto del webhook
            if 'entry' in message_data:
                for entry in message_data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('field') == 'messages':
                                value = change.get('value', {})
                                if 'messages' in value and value['messages']:
                                    msg = value['messages'][0]
                                    from_number = msg.get('from', 'unknown')
                                    if msg.get('type') == 'text':
                                        message_text = msg.get('text', {}).get('body', 'N/A')[:30]
                                    else:
                                        message_text = f"[{msg.get('type', 'unknown')}]"
                                    break
                        if from_number != "unknown":
                            break
                    if from_number != "unknown":
                        break
            
            # SIEMPRE añadir a la cola, nunca intentar envío directo
            message_with_timestamp = {
                **message_data,
                'queued_at': time.time(),
                'attempts': 0
            }
            
            self.message_queue.put(message_with_timestamp)
            logger.info(f"📩 MENSAJE AÑADIDO A COLA FIFO - de: {from_number} - texto: '{message_text}' - cola actual: {self.message_queue.qsize()}")
            
            return {"success": True, "method": "webhook_fifo_queue"}
                
        except Exception as e:
            logger.error(f"❌ Error crítico añadiendo mensaje a cola: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _start_queue_processor(self):
        """Inicia el procesador de cola en background usando threading"""
        if self.running:
            logger.warning("⚠️ Procesador ya está corriendo")
            return
        
        try:
            self.running = True
            self.processor_thread = threading.Thread(target=self._process_queue_loop, daemon=True, name="FIFOProcessor")
            self.processor_thread.start()
            logger.info("🎯 PROCESADOR DE COLA FIFO INICIADO CON THREADING")
            logger.info(f"🔧 Thread ID: {self.processor_thread.ident}, Thread Name: {self.processor_thread.name}")
        except Exception as e:
            logger.error(f"❌ Error iniciando procesador de cola: {str(e)}")
            self.running = False
    
    def _process_queue_loop(self):
        """Loop principal del procesador de cola FIFO - UN mensaje a la vez"""
        logger.info("🚀 INICIANDO LOOP DE PROCESADOR FIFO - UN SOLO MENSAJE A LA VEZ")
        logger.info("🔄 Esperando mensajes en la cola...")
        
        while self.running:
            try:
                # Obtener mensaje de la cola FIFO (bloquea hasta que haya mensaje)
                message_data = self.message_queue.get(timeout=1)
                
                # Extraer info para logging
                from_number = "unknown"
                message_text = "N/A"
                
                try:
                    if 'entry' in message_data:
                        for entry in message_data['entry']:
                            if 'changes' in entry:
                                for change in entry['changes']:
                                    if change.get('field') == 'messages':
                                        value = change.get('value', {})
                                        if 'messages' in value and value['messages']:
                                            msg = value['messages'][0]
                                            from_number = msg.get('from', 'unknown')
                                            if msg.get('type') == 'text':
                                                message_text = msg.get('text', {}).get('body', 'N/A')[:30]
                                            else:
                                                message_text = f"[{msg.get('type', 'unknown')}]"
                                            break
                                    if from_number != "unknown":
                                        break
                            if from_number != "unknown":
                                break
                except:
                    pass  # Si hay error extrayendo info, usar defaults
                
                logger.info(f"\n➡️ PROCESANDO MENSAJE FIFO - de: {from_number} - texto: '{message_text}' - cola restante: {self.message_queue.qsize()}")
                
                # Intentar enviar el mensaje
                try:
                    self.websocket_service.send_message(message_data)
                    logger.info(f"✅ MENSAJE COMPLETADO - de: {from_number} - texto: '{message_text}'")
                    
                    # Marcar como completado
                    self.message_queue.task_done()
                    logger.info(f"🚀 LISTO PARA SIGUIENTE MENSAJE (cola: {self.message_queue.qsize()})\n")
                    
                except Exception as e:
                    logger.error(f"❌ Error enviando mensaje por WebSocket: {str(e)}")
                    
                    # Devolver el mensaje al frente de la cola para reintentarlo inmediatamente
                    # Usar una cola temporal para mantener el orden FIFO
                    temp_queue = queue.Queue()
                    temp_queue.put(message_data)
                    
                    # Mover todos los mensajes restantes a la cola temporal
                    while not self.message_queue.empty():
                        try:
                            temp_queue.put(self.message_queue.get_nowait())
                        except queue.Empty:
                            break
                    
                    # Restaurar todos los mensajes con el mensaje fallido al frente
                    while not temp_queue.empty():
                        try:
                            self.message_queue.put(temp_queue.get_nowait())
                        except queue.Empty:
                            break
                    
                    logger.info(f"🔄 Mensaje devuelto al frente de la cola para reintento - de: {from_number}")
                    logger.info(f"⏸️ ESPERANDO 5 SEGUNDOS ANTES DE REINTENTAR...")
                    time.sleep(5)
                    # Continuar con el siguiente ciclo (que será el mismo mensaje)
                    
            except queue.Empty:
                # No hay mensajes en la cola, continuar esperando
                continue
                
            except Exception as e:
                logger.error(f"❌ Error crítico en procesador FIFO: {str(e)}")
                time.sleep(5)  # Esperar antes de continuar
                
        logger.info("🛑 Loop de procesador FIFO terminado")
    
    def stop_processor(self):
        """Detiene el procesador de cola"""
        self.running = False
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5)
            logger.info("🛑 Procesador de cola detenido")
    
    def get_queue_status(self) -> Dict:
        """Obtiene el estado de la cola"""
        try:
            # Verificar y reiniciar si el procesador no está activo
            self._ensure_processor_running()

            thread_alive = self.processor_thread.is_alive() if self.processor_thread else False
            return {
                "websocket_available": self.websocket_service.health_check(),
                "processor_running": self.running,
                "processor_thread_alive": thread_alive,
                "processor_thread_name": self.processor_thread.name if self.processor_thread else None,
                "queue_size": self.message_queue.qsize(),
                "queue_healthy": True
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado de cola: {str(e)}")
            return {"error": str(e)}
    
    def get_queue_lengths(self) -> Dict:
        """Obtiene las longitudes de las diferentes colas"""
        try:
            return {
                "pending": self.message_queue.qsize()
            }
        except Exception as e:
            logger.error(f"Error obteniendo longitudes de cola: {str(e)}")
            return {"error": str(e)}
    
    def restart_processor(self) -> Dict:
        """Reinicia el procesador de cola"""
        try:
            logger.info("🔄 Reiniciando procesador de cola (forzado)...")

            # Detener cualquier thread previo
            self.running = False
            if self.processor_thread and self.processor_thread.is_alive():
                self.processor_thread.join(timeout=1)

            # Forzar creación de nuevo thread
            self.processor_thread = None
            self._start_queue_processor()

            if self.processor_thread and self.processor_thread.is_alive():
                logger.info("✅ Procesador de cola operativo")
                return {"success": True, "message": "Procesador reiniciado"}
            else:
                logger.info("❌ No se pudo reiniciar el procesador")
                return {"success": False, "message": "No se pudo reiniciar"}

        except Exception as e:
            logger.error(f"❌ Error reiniciando procesador: {str(e)}")
            return {"error": str(e)}
    
    def clear_queue(self) -> Dict:
        """Limpia la cola (usar con precaución)"""
        try:
            # Vaciar la cola
            cleared_count = 0
            try:
                while True:
                    self.message_queue.get_nowait()
                    cleared_count += 1
            except queue.Empty:
                pass
            
            logger.warning(f"🧹 Cola limpiada - {cleared_count} mensajes removidos")
            return {"cleared": cleared_count}
            
        except Exception as e:
            logger.error(f"❌ Error limpiando cola: {str(e)}")
            return {"error": str(e)}
    
    def clear_all_queues(self) -> Dict:
        """Alias para clear_queue para compatibilidad con la API"""
        return self.clear_queue()
    
    def retry_failed_messages(self, limit: int = 10) -> Dict:
        """No aplicable para FIFO queue, pero mantenemos para compatibilidad API"""
        return {"success": True, "message": "FIFO queue reintenta automáticamente"}
