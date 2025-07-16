from flask import Blueprint, jsonify
import logging
from services.whatsapp_service import WhatsAppService
from services.queue_service import QueueService
from services.websocket_service import WebSocketService

logger = logging.getLogger(__name__)

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar el estado del servicio"""
    try:
        service_status = {
            "webhook": True,
            "whatsapp_service": False,
            "queue_service": False,
            "websocket_service": False
        }
        
        # Verificar WhatsApp service
        try:
            whatsapp_service = WhatsAppService()
            service_status["whatsapp_service"] = True
        except Exception as e:
            logger.error(f"Error verificando WhatsApp service: {str(e)}")
        
        # Verificar Queue service
        try:
            queue_service = QueueService()
            service_status["queue_service"] = True
        except Exception as e:
            logger.error(f"Error verificando Queue service: {str(e)}")
        
        # Verificar WebSocket service
        try:
            websocket_service = WebSocketService()
            service_status["websocket_service"] = websocket_service.health_check()
        except Exception as e:
            logger.error(f"Error verificando WebSocket service: {str(e)}")
        
        all_ok = all(service_status.values())
        
        return jsonify({
            "status": "healthy" if all_ok else "degraded",
            "services": service_status
        }), 200 if all_ok else 503
        
    except Exception as e:
        logger.error(f"Error verificando estado: {str(e)}")
        return jsonify({"error": str(e)}), 500

@status_bp.route('/health', methods=['GET'])
def health():
    """Endpoint simple de health check"""
    return jsonify({"status": "ok"}), 200
