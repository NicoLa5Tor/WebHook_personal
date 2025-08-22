import logging
import json
import websocket
from typing import Dict
from threading import Thread
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class WebSocketService:
    def __init__(self, websocket_url: str = None):
        self.websocket_url = websocket_url or os.getenv('WEBSOCKET_URL', 'ws://localhost:8080/ws')
        logger.info(f"🔌 WebSocketService inicializado - URL: {self.websocket_url}")
    
    def send_message(self, message_data: Dict):
        """Envía un mensaje al WebSocket"""
        try:
            # Crear conexión con timeout más largo para debugging
            logger.info(f"🔗 Conectando a WebSocket: {self.websocket_url}")
            ws = websocket.create_connection(self.websocket_url, timeout=15)
            
            # Preparar mensaje JSON
            message_json = json.dumps(message_data, ensure_ascii=False)
            message_size = len(message_json)
            
            # Enviar mensaje
            logger.info(f"📤 Enviando mensaje ({message_size} chars) al WebSocket...")
            ws.send(message_json)
            
            # Cerrar conexión
            ws.close()
            
            # Mejorar log con información del webhook
            log_info = self._extract_log_info(message_data)
            logger.info(f"✅ MENSAJE ENVIADO AL WEBSOCKET: {log_info}")
            
        except websocket.WebSocketConnectionClosedException as e:
            logger.error(f"❌ Conexión WebSocket cerrada inesperadamente: {str(e)}")
            raise
        except websocket.WebSocketTimeoutException as e:
            logger.error(f"❌ Timeout conectando a WebSocket: {str(e)}")
            raise
        except websocket.WebSocketException as e:
            logger.error(f"❌ Error WebSocket específico: {str(e)}")
            raise
        except ConnectionRefusedError as e:
            logger.error(f"❌ Conexión rechazada por WebSocket: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error general enviando al WebSocket: {str(e)}")
            logger.error(f"❌ Tipo de error: {type(e).__name__}")
            raise  # Propagar la excepción para que la cola la maneje
    
    def _extract_log_info(self, webhook_data: Dict) -> str:
        """Extrae información útil del webhook para el log"""
        try:
            # Buscar mensajes en el webhook
            if 'entry' in webhook_data:
                for entry in webhook_data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('field') == 'messages':
                                value = change.get('value', {})
                                if 'messages' in value:
                                    messages = value['messages']
                                    if messages:
                                        msg = messages[0]  # Primer mensaje
                                        msg_type = msg.get('type', 'unknown')
                                        msg_from = msg.get('from', 'unknown')
                                        
                                        # Información adicional según el tipo
                                        if msg_type == 'text':
                                            text = msg.get('text', {}).get('body', '')[:50]
                                            return f"text de {msg_from}: '{text}'"
                                        else:
                                            return f"{msg_type} de {msg_from}"
            
            # Verificar si tiene información del cache
            cache_info = ""
            if webhook_data.get('save_number'):
                if 'cached_info' in webhook_data:
                    cache_name = webhook_data['cached_info'].get('name', 'N/A')
                    cache_info = f" [cached: {cache_name}]"
                else:
                    cache_info = " [save_number: true]"
            else:
                cache_info = " [not in cache]"
            
            return f"webhook data{cache_info}"
            
        except Exception:
            return "webhook data (error parsing)"
    
    def send_message_async(self, message_data: Dict):
        """Envía un mensaje de forma asíncrona"""
        def send_in_background():
            try:
                self.send_message(message_data)
            except Exception as e:
                logger.error(f"❌ Error en envío asíncrono: {str(e)}")
        
        thread = Thread(target=send_in_background, daemon=True, name="AsyncWebSocketSender")
        thread.start()
        logger.info(f"🚀 Mensaje enviado de forma asíncrona - Thread: {thread.name}")
    
    def health_check(self) -> bool:
        """Verifica si el WebSocket está disponible"""
        try:
            logger.info(f"🏥 Realizando health check de WebSocket: {self.websocket_url}")
            ws = websocket.create_connection(self.websocket_url, timeout=5)
            ws.close()
            logger.info("✅ WebSocket health check: OK")
            return True
        except Exception as e:
            logger.warning(f"❌ WebSocket health check falló: {str(e)}")
            return False
    
    def test_connection(self) -> Dict:
        """Prueba la conexión con información detallada"""
        try:
            logger.info(f"🧪 Probando conexión detallada a: {self.websocket_url}")
            
            # Intentar conectar
            ws = websocket.create_connection(self.websocket_url, timeout=10)
            
            # Enviar mensaje de prueba
            test_message = {"test": "connection_test", "timestamp": str(int(__import__('time').time()))}
            ws.send(json.dumps(test_message))
            
            # Cerrar
            ws.close()
            
            logger.info("✅ Test de conexión WebSocket: EXITOSO")
            return {
                "success": True,
                "url": self.websocket_url,
                "message": "Conexión exitosa"
            }
            
        except Exception as e:
            logger.error(f"❌ Test de conexión WebSocket falló: {str(e)}")
            return {
                "success": False,
                "url": self.websocket_url,
                "error": str(e),
                "error_type": type(e).__name__
            }