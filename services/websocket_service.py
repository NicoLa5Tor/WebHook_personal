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
    
    def send_message(self, message_data: Dict):
        """Envía un mensaje al WebSocket"""
        try:
            ws = websocket.create_connection(self.websocket_url, timeout=10)
            message_json = json.dumps(message_data, ensure_ascii=False)
            ws.send(message_json)
            ws.close()
            
            # Mejorar log con información del webhook
            log_info = self._extract_log_info(message_data)
            logger.info(f"Mensaje enviado al WebSocket: {log_info}")
            
        except Exception as e:
            logger.error(f"Error enviando al WebSocket: {str(e)}")
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
            
            return "webhook data"
            
        except Exception:
            return "webhook data (error parsing)"
    
    def send_message_async(self, message_data: Dict):
        """Envía un mensaje de forma asíncrona"""
        def send_in_background():
            self.send_message(message_data)
        
        thread = Thread(target=send_in_background)
        thread.daemon = True
        thread.start()
    
    def health_check(self) -> bool:
        """Verifica si el WebSocket está disponible"""
        try:
            ws = websocket.create_connection(self.websocket_url, timeout=5)
            ws.close()
            return True
        except:
            return False
