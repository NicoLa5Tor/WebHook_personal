from flask import Blueprint, request, jsonify
import logging
from services.whatsapp_service import WhatsAppService
from services.queue_service import QueueService

logger = logging.getLogger(__name__)

messages_bp = Blueprint('messages', __name__)

# Inicializar servicios
whatsapp_service = None
queue_service = None

def init_services():
    global whatsapp_service, queue_service
    try:
        # Forzar recarga de .env
        from dotenv import load_dotenv
        load_dotenv()
        whatsapp_service = WhatsAppService()
        queue_service = QueueService()
    except Exception as e:
        logger.error(f"Error inicializando servicios de mensajes: {str(e)}")

@messages_bp.route('/send-message', methods=['POST'])
def send_message():
    """Endpoint para enviar mensajes individuales"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        use_queue = data.get('use_queue', False)
        
        if not phone or not message:
            return jsonify({"error": "Faltan parámetros: phone y message son requeridos"}), 400
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_message_async(phone, message)
            return jsonify({
                "success": True,
                "message": "Mensaje enviado a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_text_message(phone, message)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": "Mensaje enviado exitosamente",
                    "data": result['data']
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result['error']
                }), 400
            
    except Exception as e:
        logger.error(f"Error enviando mensaje: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/send-template', methods=['POST'])
def send_template():
    """Endpoint para enviar mensajes de plantilla"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        phone = data.get('phone')
        template_name = data.get('template_name')
        language = data.get('language', 'es')
        parameters = data.get('parameters', [])
        use_queue = data.get('use_queue', False)
        
        if not phone or not template_name:
            return jsonify({"error": "Faltan parámetros: phone y template_name son requeridos"}), 400
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_template_async(phone, template_name, language, parameters)
            return jsonify({
                "success": True,
                "message": "Plantilla enviada a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_template_message(phone, template_name, language, parameters)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": "Plantilla enviada exitosamente",
                    "data": result['data']
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result['error']
                }), 400
            
    except Exception as e:
        logger.error(f"Error enviando plantilla: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/send-bulk', methods=['POST'])
def send_bulk():
    """Endpoint para envío masivo de mensajes"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        recipients = data.get('recipients', [])
        use_queue = data.get('use_queue', True)  # Por defecto usar cola para masivos
        
        if not recipients:
            return jsonify({"error": "Falta parámetro: recipients es requerido"}), 400
        
        # Validar estructura de recipients
        for recipient in recipients:
            if not recipient.get('phone') or not recipient.get('message'):
                return jsonify({"error": "Cada recipient debe tener 'phone' y 'message'"}), 400
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_bulk_messages_async(recipients)
            return jsonify({
                "success": True,
                "message": "Envío masivo enviado a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_bulk_messages(recipients)
            
            return jsonify({
                "success": True,
                "message": "Envío masivo completado",
                "result": result
            }), 200
        
    except Exception as e:
        logger.error(f"Error en envío masivo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Endpoint para obtener el estado de una tarea"""
    global queue_service
    
    if not queue_service:
        init_services()
    
    try:
        if not queue_service:
            return jsonify({"error": "Servicio de cola no disponible"}), 500
        
        status = queue_service.get_task_status(task_id)
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de tarea: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/media/<media_id>', methods=['GET'])
def get_media(media_id):
    """Endpoint para obtener URL de contenido multimedia"""
    global whatsapp_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        media_url = whatsapp_service.get_media_url(media_id)
        
        if media_url:
            return jsonify({
                "success": True,
                "media_url": media_url
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo obtener la URL del archivo"
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo media: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/send-interactive', methods=['POST'])
def send_interactive():
    """Endpoint para enviar mensajes interactivos individuales"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        phone = data.get('phone')
        header_type = data.get('header_type')
        header_content = data.get('header_content')
        body_text = data.get('body_text')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        footer_text = data.get('footer_text')
        use_queue = data.get('use_queue', False)
        
        if not phone or not body_text:
            return jsonify({"error": "Faltan parámetros: phone y body_text son requeridos"}), 400
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_interactive_message_async(
                phone, header_type, header_content, body_text, button_text, button_url, footer_text
            )
            return jsonify({
                "success": True,
                "message": "Mensaje interactivo enviado a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_interactive_message(
                phone, header_type, header_content, body_text, button_text, button_url, footer_text
            )
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": "Mensaje interactivo enviado exitosamente",
                    "data": result['data']
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result['error']
                }), 400
            
    except Exception as e:
        logger.error(f"Error enviando mensaje interactivo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/send-bulk-interactive', methods=['POST'])
def send_bulk_interactive():
    """Endpoint para envío masivo de mensajes interactivos"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        recipients = data.get('recipients', [])
        use_queue = data.get('use_queue', True)  # Por defecto usar cola para masivos
        
        if not recipients:
            return jsonify({"error": "Falta parámetro: recipients es requerido"}), 400
        
        # Validar estructura de recipients
        for recipient in recipients:
            if not recipient.get('phone') or not recipient.get('body_text'):
                return jsonify({"error": "Cada recipient debe tener 'phone' y 'body_text'"}), 400
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_bulk_interactive_messages_async(recipients)
            return jsonify({
                "success": True,
                "message": "Envío masivo interactivo enviado a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_bulk_interactive_messages(recipients)
            
            return jsonify({
                "success": True,
                "message": "Envío masivo interactivo completado",
                "result": result
            }), 200
        
    except Exception as e:
        logger.error(f"Error en envío masivo interactivo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/send-broadcast-interactive', methods=['POST'])
def send_broadcast_interactive():
    """Endpoint para enviar el mismo mensaje interactivo a múltiples números"""
    global whatsapp_service, queue_service
    
    if not whatsapp_service:
        init_services()
    
    try:
        if not whatsapp_service:
            return jsonify({"error": "Servicio no disponible"}), 500
        
        data = request.json
        
        if not data:
            return jsonify({"error": "Se requiere un JSON con los datos del mensaje"}), 400
        
        # Validar que se proporcionen los números telefónicos
        phones = data.get('phones', [])
        if not isinstance(phones, list) or len(phones) == 0:
            return jsonify({"error": "Se requiere el campo 'phones' con un array de números telefónicos"}), 400
        
        # Validar que haya al menos body_text
        body_text = data.get('body_text')
        if not body_text:
            return jsonify({"error": "Se requiere el campo 'body_text'"}), 400
        
        # Extraer parámetros del mensaje
        header_type = data.get('header_type')
        header_content = data.get('header_content')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        footer_text = data.get('footer_text')
        use_queue = data.get('use_queue', True)  # Por defecto usar cola para masivos
        
        if use_queue and queue_service:
            # Enviar usando cola
            task = queue_service.send_broadcast_interactive_message_async(
                phones, header_type, header_content, body_text, 
                button_text, button_url, footer_text
            )
            return jsonify({
                "success": True,
                "message": "Mensaje broadcast enviado a cola",
                "task_id": task.id
            }), 200
        else:
            # Enviar directamente
            result = whatsapp_service.send_broadcast_interactive_message(
                phones, header_type, header_content, body_text, 
                button_text, button_url, footer_text
            )
            
            return jsonify({
                "success": True,
                "message": "Mensaje broadcast procesado",
                "result": result
            }), 200
        
    except Exception as e:
        logger.error(f"Error en broadcast interactive message: {str(e)}")
        return jsonify({"error": str(e)}), 500
