import logging
from typing import Dict, List, Optional
from .whatsapp_service import WhatsAppService
from .websocket_service import WebSocketService
from .message_queue_service import MessageQueueService
from .simple_cache import get_number_cache

logger = logging.getLogger(__name__)


class MessageProcessor:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.whatsapp_service = whatsapp_service
        self.websocket_service = WebSocketService()
        self.message_queue_service = MessageQueueService()
        
    def process_webhook_data(self, data: Dict) -> List[Dict]:
        """Procesa los datos del webhook y extrae los mensajes"""
        messages = []
        
        if not data.get('entry'):
            return messages
        
        for entry in data['entry']:
            if not entry.get('changes'):
                continue
                
            for change in entry['changes']:
                if change.get('field') != 'messages':
                    continue
                    
                value = change.get('value', {})
                
                # Procesar mensajes entrantes
                if 'messages' in value:
                    for message in value['messages']:
                        processed_message = self._process_message(message, value)
                        if processed_message:
                            messages.append(processed_message)
                
                # Procesar estados de mensajes
                if 'statuses' in value:
                    for status in value['statuses']:
                        self._process_status(status)
        
        return messages
    
    def _process_message(self, message: Dict, value: Dict) -> Optional[Dict]:
        """Procesa un mensaje individual"""
        try:
            msg_data = {
                'id': message.get('id'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'from': message.get('from')
            }
            
            # Obtener información del contacto
            contacts = value.get('contacts', [])
            for contact in contacts:
                if contact.get('wa_id') == message.get('from'):
                    msg_data['contact'] = {
                        'name': contact.get('profile', {}).get('name'),
                        'wa_id': contact.get('wa_id')
                    }
                    break
            
            # Procesar según el tipo de mensaje
            if message['type'] == 'text':
                msg_data['text'] = message.get('text', {}).get('body')
            elif message['type'] in ['image', 'document', 'audio', 'video']:
                media_info = message.get(message['type'], {})
                msg_data['media'] = {
                    'id': media_info.get('id'),
                    'mime_type': media_info.get('mime_type'),
                    'caption': media_info.get('caption', '')
                }
            elif message['type'] == 'location':
                location_info = message.get('location', {})
                msg_data['location'] = {
                    'latitude': location_info.get('latitude'),
                    'longitude': location_info.get('longitude'),
                    'name': location_info.get('name', ''),
                    'address': location_info.get('address', '')
                }
            elif message['type'] == 'button':
                button_info = message.get('button', {})
                msg_data['button'] = {
                    'payload': button_info.get('payload'),
                    'text': button_info.get('text')
                }
            
            logger.info(f"Mensaje procesado: {msg_data['type']} de {msg_data['from']}")
            return msg_data
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            return None
    
    def _process_status(self, status: Dict):
        """Procesa el estado de un mensaje"""
        try:
            logger.info(f"Estado de mensaje: {status.get('status')} para {status.get('recipient_id')}")
        except Exception as e:
            logger.error(f"Error procesando estado: {str(e)}")
    
    def handle_message(self, message_data: Dict) -> Optional[Dict]:
        """Procesa un mensaje y lo envía al WebSocket"""
        try:
            from_number = message_data.get('from')
            
            # Enviar mensaje al WebSocket
            self.send_to_websocket(message_data)
            
            logger.info(f"Mensaje procesado y enviado al WebSocket desde {from_number}")
            return {
                "processed": True,
                "sent_to_websocket": True
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            return {"processed": False, "error": str(e)}
    
    def get_media_content(self, media_id: str) -> Optional[str]:
        """Obtiene el contenido multimedia"""
        return self.whatsapp_service.get_media_url(media_id)
    
    
    def send_to_websocket(self, webhook_data: Dict):
        """Envía el JSON completo de WhatsApp al WebSocket usando el servicio dedicado con cola como respaldo"""
        try:
            # Extraer el número de teléfono del webhook
            from_number = None
            if 'entry' in webhook_data:
                for entry in webhook_data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('field') == 'messages':
                                value = change.get('value', {})
                                if 'messages' in value and value['messages']:
                                    from_number = value['messages'][0].get('from')
                                    break
                        if from_number:
                            break
                    if from_number:
                        break

            # Validar cache solo si hay número de teléfono
            if from_number:
                cache = get_number_cache()
                cached_data = cache.get_number(from_number)

                # Agregar información del cache si está guardado
                if cached_data:
                    webhook_data['cached_info'] = {
                        'name': cached_data.get('name'),
                        'phone': cached_data.get('phone'),
                        'data': cached_data.get('data', {}),
                        'created_at': cached_data.get('created_at'),
                        'updated_at': cached_data.get('updated_at')
                    }
                    webhook_data['save_number'] = True
                    logger.info(f"Número {from_number} encontrado en cache - Nombre: {cached_data.get('name', 'N/A')}")
                else:
                    webhook_data['save_number'] = False
                    logger.info(f"Número {from_number} NO encontrado en cache")
            else:
                webhook_data['save_number'] = False
                logger.info("No se pudo extraer número de teléfono del webhook")

            # Usar el servicio de cola que maneja WebSocket directo y cola como respaldo
            result = self.message_queue_service.add_message_to_queue(webhook_data)

            if result['success']:
                logger.info(f"Webhook JSON enviado vía {result['method']}")
            else:
                logger.error(f"Error enviando webhook: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Error crítico enviando webhook al WebSocket: {str(e)}")
