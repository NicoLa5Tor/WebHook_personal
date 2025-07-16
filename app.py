from flask import Flask, request, jsonify
import os
import logging
from dotenv import load_dotenv
from api import register_blueprints

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'hola')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Agregar configuración a la app
app.config['VERIFY_TOKEN'] = VERIFY_TOKEN
app.config['DEBUG'] = DEBUG

# Registrar blueprints
register_blueprints(app)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=DEBUG)
