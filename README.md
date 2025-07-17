# WhatsApp Business API - Estructura Escalable

Este proyecto implementa un sistema para trabajar con la API de WhatsApp Business usando una estructura escalable con blueprints de Flask.

## Estructura del Proyecto

```
Whatsapp/
├── app.py                          # Aplicación Flask principal
├── worker.py                       # Worker para tareas de Celery
├── test_api.py                     # Script de pruebas
├── requirements.txt                # Dependencias
├── .env                           # Variables de entorno
├── README.md                      # Este archivo
├── services/                      # Servicios de negocio
│   ├── whatsapp_service.py        # Servicio para API de WhatsApp
│   ├── message_processor.py       # Procesador de mensajes
│   ├── queue_service.py           # Servicio de colas con Celery
│   └── websocket_service.py       # Servicio para WebSocket
└── api/                          # Blueprints de la API
    ├── __init__.py               # Configuración de blueprints
    ├── webhook.py                # Endpoints del webhook
    ├── messages.py               # Endpoints de mensajes
    └── status.py                 # Endpoints de estado
```

## Características

✅ **Estructura escalable**: Blueprints organizados por funcionalidad
✅ **Servicios separados**: Lógica de negocio en servicios independientes
✅ **Colas asíncronas**: Manejo de tareas pesadas con Celery
✅ **Webhook completo**: Recepción y procesamiento de mensajes
✅ **API REST**: Endpoints para envío individual, masivo y plantillas
✅ **Respuestas automáticas**: Procesamiento inteligente de mensajes
✅ **WebSocket Integration**: Envío automático de mensajes recibidos a WebSocket
✅ **Monitoreo**: Endpoints de estado y health check

## Instalación

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno** en `.env`:
   ```env
   VERIFY_TOKEN=hola
   ACCESS_TOKEN=tu_token_de_acceso_aqui
   PHONE_NUMBER_ID=tu_phone_number_id_aqui
   VERSION=v17.0
   BASE_URL=https://graph.facebook.com
   DEBUG=True
   REDIS_URL=redis://localhost:6379/0
   WEBSOCKET_URL=ws://localhost:8080/ws
   ```

3. **Iniciar Redis** (necesario para las colas):
   ```bash
   redis-server
   ```

## Uso

### Ejecutar la aplicación principal:
```bash
python app.py
```

### Ejecutar el worker para tareas asíncronas:
```bash
python worker.py
```

### Ejecutar las pruebas:
```bash
python test_api.py
```

### Ejecutar las pruebas del WebSocket:
```bash
python test_websocket.py
```

## Endpoints de la API

### Webhook
- `GET /webhook` - Verificación del webhook
- `POST /webhook` - Recepción de eventos

### Mensajes
- `POST /api/send-message` - Enviar mensaje individual
- `POST /api/send-template` - Enviar plantilla
- `POST /api/send-bulk` - Envío masivo
- `POST /api/send-interactive` - Enviar mensaje interactivo
- `POST /api/send-bulk-interactive` - Envío masivo interactivo
- `POST /api/send-personalized-broadcast` - Broadcast personalizado con texto único por destinatario
- `POST /api/send-broadcast-interactive` - Broadcast interactivo (mismo mensaje para todos)
- `POST /api/send-list` - Enviar mensaje de lista
- `GET /api/task-status/<task_id>` - Estado de tareas asíncronas
- `GET /api/media/<media_id>` - Obtener URL de multimedia

### Estado
- `GET /api/status` - Estado completo del servicio
- `GET /api/health` - Health check simple

## Ejemplos de Uso

### Enviar mensaje individual:
```bash
curl -X POST http://localhost:5000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"phone": "5491234567890", "message": "Hola!"}'
```

### Enviar mensaje usando cola:
```bash
curl -X POST http://localhost:5000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"phone": "5491234567890", "message": "Hola!", "use_queue": true}'
```

### Envío masivo:
```bash
curl -X POST http://localhost:5000/api/send-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"phone": "5491234567890", "message": "Mensaje 1"},
      {"phone": "5491234567891", "message": "Mensaje 2"}
    ]
  }'
```

### Envío broadcast personalizado:
```bash
curl -X POST http://localhost:5000/api/send-personalized-broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {
        "phone": "573103391854",
        "body_text": "Hola Juan, tu pedido #12345 está listo para recoger."
      },
      {
        "phone": "573103391855",
        "body_text": "Hola María, tu pedido #67890 está listo para recoger."
      }
    ],
    "header_type": "image",
    "header_content": "https://example.com/image.jpg",
    "button_text": "Ver Pedido",
    "button_url": "https://mi-tienda.com/mis-pedidos",
    "footer_text": "Gracias por tu compra - Mi Tienda",
    "use_queue": true
  }'
```

### Verificar estado de tarea:
```bash
curl http://localhost:5000/api/task-status/TASK_ID
```

## Ventajas de la Estructura

1. **Escalabilidad**: Los blueprints permiten agregar nuevas funcionalidades fácilmente
2. **Mantenibilidad**: Código organizado en módulos específicos
3. **Testabilidad**: Servicios independientes fáciles de probar
4. **Flexibilidad**: Uso opcional de colas para tareas pesadas
5. **Monitoreo**: Endpoints dedicados para verificar el estado

## Funcionalidades Avanzadas

### Respuestas Automáticas
El sistema incluye respuestas automáticas para:
- Saludos: "hola", "hello"
- Ayuda: "ayuda", "help"
- Información: "info"
- Contacto: "contacto"

### Tipos de Mensajes Soportados
- Texto
- Imágenes
- Documentos
- Audio
- Video
- Ubicación
- Botones

### Colas Asíncronas
- Envío de mensajes individuales
- Envío masivo
- Envío de plantillas
- Reintentos automáticos

### Integración WebSocket
- Envío automático de mensajes recibidos a WebSocket
- Reintentos automáticos en caso de fallo
- Health check del WebSocket
- Envío asíncrono para mejor rendimiento

## Configuración de Producción

Para producción, considera:
1. Usar gunicorn: `gunicorn -w 4 app:app`
2. Configurar Redis con persistencia
3. Usar supervisor para el worker
4. Implementar logging a archivos
5. Configurar monitoreo con Prometheus

## Solución de Problemas

1. **Error 500**: Verificar que Redis esté ejecutándose
2. **Tasks no se procesan**: Verificar que el worker esté ejecutándose
3. **Webhook no funciona**: Verificar VERIFY_TOKEN en .env
4. **Mensajes no se envían**: Verificar credenciales de WhatsApp API

Este proyecto mantiene la simplicidad de uso mientras provee una estructura escalable para el crecimiento futuro.
