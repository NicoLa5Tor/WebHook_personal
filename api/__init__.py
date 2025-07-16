from flask import Blueprint
from .webhook import webhook_bp
from .messages import messages_bp
from .status import status_bp
from .simple_cache import simple_cache_bp
from .message_queue import message_queue_bp

# Crear el blueprint principal de la API
api_bp = Blueprint('api', __name__)

def register_blueprints(app):
    """Registra todos los blueprints de la API"""
    app.register_blueprint(webhook_bp)
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(status_bp, url_prefix='/api')
    app.register_blueprint(simple_cache_bp, url_prefix='/api')
    app.register_blueprint(message_queue_bp, url_prefix='/api')

__all__ = ['api_bp', 'register_blueprints']
