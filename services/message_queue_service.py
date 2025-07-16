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
    _processor_started = False
    
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
        
        # Iniciar procesador de cola en background SOLO UNA VEZ
        if not MessageQueueService._processor_started:
            MessageQueueService._processor_started = True
            self._start_queue_processor()
    
    def add_message_to_queue(self, message_data: Dict):
        """Añade un mensaje a la cola FIFO para procesamiento"""
        try:
            # SIEMPRE añadir a la cola, nunca intentar envío directo
            message_with_timestamp = {
                **message_data,
                'queued_at': time.time(),
                'attempts': 0
            }
            
            self.message_queue.put(message_with_timestamp)
            logger.info(f"Mensaje añadido a cola FIFO desde {message_data.get('from', 'unknown')}")
            
            return {"success": True, "method": "fifo_queue"}
                
        except Exception as e:
            logger.error(f"Error crítico añadiendo mensaje a cola: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _start_queue_processor(self):
        """Inicia el procesador de cola en background usando threading"""
        if self.running:
            return
        
        try:
            self.running = True
            self.processor_thread = threading.Thread(target=self._process_queue_loop, daemon=True)
            self.processor_thread.start()
            logger.info("Procesador de cola FIFO iniciado con threading")
        except Exception as e:
            logger.error(f"Error iniciando procesador de cola: {str(e)}")
            self.running = False
    
    def _process_queue_loop(self):
        """Loop principal del procesador de cola FIFO - UN mensaje a la vez"""
        logger.info("Iniciando loop de procesador FIFO - UN SOLO MENSAJE A LA VEZ")
        
        while self.running:
            try:
                # Obtener mensaje de la cola FIFO (bloquea hasta que haya mensaje)
                message_data = self.message_queue.get(timeout=1)
                
                logger.info(f"\n➡️ PROCESANDO MENSAJE FIFO desde {message_data.get('from', 'unknown')} - texto: '{message_data.get('text', 'N/A')}'")
                
                # Intentar enviar el mensaje
                try:
                    self.websocket_service.send_message(message_data)
                    logger.info(f"✅ MENSAJE COMPLETADO - desde {message_data.get('from', 'unknown')} - texto: '{message_data.get('text', 'N/A')}'")
                    
                    # Marcar como completado
                    self.message_queue.task_done()
                    logger.info(f"🚀 LISTO PARA SIGUIENTE MENSAJE\n")
                    
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
                    
                    logger.info(f"🔄 Mensaje devuelto al frente de la cola para reintento")
                    logger.info(f"⏸️ ESPERANDO 5 SEGUNDOS ANTES DE REINTENTAR...")
                    time.sleep(5)
                    # Continuar con el siguiente ciclo (que será el mismo mensaje)
                    
            except queue.Empty:
                # No hay mensajes en la cola, continuar
                continue
                
            except Exception as e:
                logger.error(f"Error crítico en procesador FIFO: {str(e)}")
                time.sleep(5)  # Esperar antes de continuar
                
        logger.info("Loop de procesador FIFO terminado")
    
    def stop_processor(self):
        """Detiene el procesador de cola"""
        self.running = False
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5)
            logger.info("Procesador de cola detenido")
    
    def get_queue_status(self) -> Dict:
        """Obtiene el estado de la cola"""
        try:
            return {
                "websocket_available": self.websocket_service.health_check(),
                "processor_running": self.running,
                "processor_thread_alive": self.processor_thread.is_alive() if self.processor_thread else False,
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
            logger.info("Reiniciando procesador de cola...")
            self.running = True
            
            # Reiniciar el thread del procesador
            if self.processor_thread and not self.processor_thread.is_alive():
                self.processor_thread = threading.Thread(target=self._process_queue_loop, daemon=True)
                self.processor_thread.start()
                logger.info("Procesador de cola reiniciado")
                return {"success": True, "message": "Procesador reiniciado"}
            else:
                logger.info("El procesador ya está corriendo")
                return {"success": True, "message": "Procesador ya está corriendo"}
                
        except Exception as e:
            logger.error(f"Error reiniciando procesador: {str(e)}")
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
            
            logger.warning(f"Cola limpiada - {cleared_count} mensajes removidos")
            return {"cleared": cleared_count}
            
        except Exception as e:
            logger.error(f"Error limpiando cola: {str(e)}")
            return {"error": str(e)}

