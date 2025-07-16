from flask import Blueprint, request, jsonify
import logging
from services.simple_cache import get_number_cache

logger = logging.getLogger(__name__)

simple_cache_bp = Blueprint('simple_cache', __name__)

@simple_cache_bp.route('/numbers', methods=['GET'])
def get_numbers():
    """Obtiene todos los números"""
    try:
        cache = get_number_cache()
        numbers = cache.get_all_numbers()
        return jsonify({
            "success": True,
            "numbers": numbers,
            "total": len(numbers)
        }), 200
    except Exception as e:
        logger.error(f"Error getting numbers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@simple_cache_bp.route('/numbers/<phone>', methods=['GET'])
def get_number(phone: str):
    """Obtiene información de un número específico"""
    try:
        cache = get_number_cache()
        number = cache.get_number(phone)
        
        if number:
            return jsonify({
                "success": True,
                "number": number
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Number not found"
            }), 404
    except Exception as e:
        logger.error(f"Error getting number: {str(e)}")
        return jsonify({"error": str(e)}), 500

@simple_cache_bp.route('/numbers', methods=['POST'])
def add_number():
    """Agrega un número"""
    try:
        data = request.json
        phone = data.get('phone')
        name = data.get('name')
        number_data = data.get('data', {})
        
        if not phone:
            return jsonify({"error": "Phone number is required"}), 400
        
        cache = get_number_cache()
        success = cache.add_number(phone, name, number_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Number {phone} added successfully"
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to add number"
            }), 500
    except Exception as e:
        logger.error(f"Error adding number: {str(e)}")
        return jsonify({"error": str(e)}), 500

@simple_cache_bp.route('/numbers/<phone>', methods=['DELETE'])
def delete_number(phone: str):
    """Elimina un número"""
    try:
        cache = get_number_cache()
        success = cache.delete_number(phone)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Number {phone} deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Number not found"
            }), 404
    except Exception as e:
        logger.error(f"Error deleting number: {str(e)}")
        return jsonify({"error": str(e)}), 500

@simple_cache_bp.route('/numbers/clear', methods=['POST'])
def clear_numbers():
    """Limpia todos los números"""
    try:
        cache = get_number_cache()
        deleted = cache.clear_all()
        
        return jsonify({
            "success": True,
            "deleted": deleted,
            "message": f"Deleted {deleted} numbers"
        }), 200
    except Exception as e:
        logger.error(f"Error clearing numbers: {str(e)}")
        return jsonify({"error": str(e)}), 500
