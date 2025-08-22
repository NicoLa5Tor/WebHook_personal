from flask import Blueprint, jsonify, request
import logging
import time
from services.message_queue_service import MessageQueueService

logger = logging.getLogger(__name__)

message_queue_bp = Blueprint('message_queue', __name__)

# Inicializar servicio
message_queue_service = MessageQueueService()

@message_queue_bp.route('/queue/status', methods=['GET'])
def get_queue_status():
    """Obtiene el estado general de las colas"""
    try:
        status = message_queue_service.get_queue_status()
        lengths = message_queue_service.get_queue_lengths()
        
        return jsonify({
            "success": True,
            "status": status,
            "queue_lengths": lengths
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de cola: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@message_queue_bp.route('/queue/lengths', methods=['GET'])
def get_queue_lengths():
    """Obtiene las longitudes de las colas"""
    try:
        lengths = message_queue_service.get_queue_lengths()
        
        return jsonify({
            "success": True,
            "queue_lengths": lengths
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo longitudes de cola: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@message_queue_bp.route('/queue/retry_failed', methods=['POST'])
def retry_failed_messages():
    """Reintenta mensajes fallidos"""
    try:
        limit = request.json.get('limit', 10) if request.json else 10
        
        result = message_queue_service.retry_failed_messages(limit)
        
        return jsonify({
            "success": True,
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error reintentando mensajes: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@message_queue_bp.route('/queue/clear', methods=['DELETE'])
def clear_all_queues():
    """Limpia todas las colas (usar con precaución)"""
    try:
        result = message_queue_service.clear_all_queues()
        
        return jsonify({
            "success": True,
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error limpiando colas: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@message_queue_bp.route('/queue/test', methods=['POST'])
def test_queue():
    """Prueba el sistema de colas con un mensaje de prueba"""
    try:
        test_message = {
            "from": "test_user",
            "type": "text",
            "text": "Mensaje de prueba del sistema de colas",
            "timestamp": str(int(time.time()))
        }
        
        result = message_queue_service.add_message_to_queue(test_message)
        
        return jsonify({
            "success": True,
            "result": result,
            "test_message": test_message
        }), 200
        
    except Exception as e:
        logger.error(f"Error probando cola: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# AGREGAR ESTE ENDPOINT AL FINAL DE api/message_queue.py

@message_queue_bp.route('/queue/restart', methods=['POST'])
def restart_queue_processor():
    """Reinicia el procesador de cola FIFO"""
    try:
        result = message_queue_service.restart_processor()
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Error reiniciando procesador: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500