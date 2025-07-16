from flask import Blueprint, request, jsonify, current_app
import logging
from services.whatsapp_service import WhatsAppService
from services.message_processor import MessageProcessor

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

# Inicializar servicios
whatsapp_service = None
message_processor = None

def init_services():
    global whatsapp_service, message_processor
    try:
        # Forzar recarga de .env
        from dotenv import load_dotenv
        load_dotenv()
        whatsapp_service = WhatsAppService()
        message_processor = MessageProcessor(whatsapp_service)
    except Exception as e:
        logger.error(f"Error inicializando servicios webhook: {str(e)}")

@webhook_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Endpoint del webhook de WhatsApp"""
    global whatsapp_service, message_processor
    
    if not whatsapp_service:
        init_services()
    
    if request.method == 'GET':
        # Verificación del webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = current_app.config.get('VERIFY_TOKEN', 'hola')

        if mode == "subscribe" and token == verify_token:
            logger.info("Webhook verificado exitosamente")
            return challenge, 200
        else:
            logger.warning("Error en la verificación del webhook")
            return "Error de verificación", 403

    elif request.method == 'POST':
        # Procesar eventos del webhook
        try:
            data = request.json
            logger.info(f"Webhook recibido: {data}")
            
            if not message_processor:
                logger.error("Procesador de mensajes no disponible")
                return jsonify({"error": "Servicio no disponible"}), 500
            
            # Enviar el JSON completo de WhatsApp al WebSocket
            message_processor.send_to_websocket(data)
            
            return jsonify({"message": "Webhook enviado al WebSocket"}), 200
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500
