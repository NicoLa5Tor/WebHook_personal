# API WhatsApp - Documentación de Endpoints

## Información General

**Base URL**: `http://localhost:5000`

**Autenticación**: No requerida (desarrollo)

---

## 📱 Endpoints de Mensajes

### 1. Enviar Mensaje Individual

**Endpoint**: `POST /api/send-message`

**Descripción**: Envía un mensaje de texto a un número específico.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-message \
-H "Content-Type: application/json" \
-d '{
  "phone": "573123456789",
  "message": "Hola, este es un mensaje de prueba",
  "use_queue": false
}'
```

**Input:**
```json
{
  "phone": "573123456789",
  "message": "Hola, este es un mensaje de prueba",
  "use_queue": false
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Mensaje enviado exitosamente",
  "data": {
    "messaging_product": "whatsapp",
    "contacts": [
      {
        "input": "573123456789",
        "wa_id": "573123456789"
      }
    ],
    "messages": [
      {
        "id": "wamid.HBgLNTczMTIzNDU2Nzg5FQIAEhggNjA2N0E2OEI3RjVBNEE2QjlBNjY2RjA5NkY0N0VBRkYA"
      }
    ]
  }
}
```

**Output (Error):**
```json
{
  "success": false,
  "error": "Error enviando mensaje: Invalid phone number"
}
```

---

### 2. Enviar Mensaje Template

**Endpoint**: `POST /api/send-template`

**Descripción**: Envía un mensaje usando plantillas aprobadas por WhatsApp.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-template \
-H "Content-Type: application/json" \
-d '{
  "phone": "573123456789",
  "template_name": "hello_world",
  "language": "es",
  "parameters": ["Juan", "Empresa XYZ"],
  "use_queue": false
}'
```

**Input:**
```json
{
  "phone": "573123456789",
  "template_name": "hello_world",
  "language": "es",
  "parameters": ["Juan", "Empresa XYZ"],
  "use_queue": false
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Plantilla enviada exitosamente",
  "data": {
    "messaging_product": "whatsapp",
    "contacts": [
      {
        "input": "573123456789",
        "wa_id": "573123456789"
      }
    ],
    "messages": [
      {
        "id": "wamid.HBgLNTczMTIzNDU2Nzg5FQIAEhggNjA2N0E2OEI3RjVBNEE2QjlBNjY2RjA5NkY0N0VBRkYA"
      }
    ]
  }
}
```

---

### 3. Envío Masivo de Mensajes

**Endpoint**: `POST /api/send-bulk`

**Descripción**: Envía mensajes personalizados a múltiples números.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-bulk \
-H "Content-Type: application/json" \
-d '{
  "recipients": [
    {
      "phone": "573123456789",
      "message": "Hola Juan, este es tu mensaje personalizado"
    },
    {
      "phone": "573987654321",
      "message": "Hola María, este es tu mensaje personalizado"
    }
  ],
  "use_queue": true
}'
```

**Input:**
```json
{
  "recipients": [
    {
      "phone": "573123456789",
      "message": "Hola Juan, este es tu mensaje personalizado"
    },
    {
      "phone": "573987654321",
      "message": "Hola María, este es tu mensaje personalizado"
    }
  ],
  "use_queue": true
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Envío masivo enviado a cola",
  "task_id": "12345678-1234-1234-1234-123456789abc"
}
```

---

### 4. Enviar Mensaje Interactivo

**Endpoint**: `POST /api/send-interactive`

**Descripción**: Envía un mensaje interactivo con botones.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-interactive \
-H "Content-Type: application/json" \
-d '{
  "phone": "573123456789",
  "header_type": "text",
  "header_content": "¡Oferta Especial!",
  "body_text": "Aprovecha nuestra oferta del 50% en todos los productos",
  "button_text": "Ver Oferta",
  "button_url": "https://mi-tienda.com/ofertas",
  "footer_text": "Válido hasta el 31 de diciembre",
  "use_queue": false
}'
```

**Input:**
```json
{
  "phone": "573123456789",
  "header_type": "text",
  "header_content": "¡Oferta Especial!",
  "body_text": "Aprovecha nuestra oferta del 50% en todos los productos",
  "button_text": "Ver Oferta",
  "button_url": "https://mi-tienda.com/ofertas",
  "footer_text": "Válido hasta el 31 de diciembre",
  "use_queue": false
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Mensaje interactivo enviado exitosamente",
  "data": {
    "messaging_product": "whatsapp",
    "contacts": [
      {
        "input": "573123456789",
        "wa_id": "573123456789"
      }
    ],
    "messages": [
      {
        "id": "wamid.HBgLNTczMTIzNDU2Nzg5FQIAEhggNjA2N0E2OEI3RjVBNEE2QjlBNjY2RjA5NkY0N0VBRkYA"
      }
    ]
  }
}
```

---

### 5. Envío Masivo Interactivo

**Endpoint**: `POST /api/send-bulk-interactive`

**Descripción**: Envía mensajes interactivos personalizados a múltiples números.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-bulk-interactive \
-H "Content-Type: application/json" \
-d '{
  "recipients": [
    {
      "phone": "573123456789",
      "header_type": "text",
      "header_content": "Hola Juan",
      "body_text": "Tu pedido está listo para recoger",
      "button_text": "Ver Pedido",
      "button_url": "https://mi-tienda.com/pedido/123"
    },
    {
      "phone": "573987654321",
      "header_type": "text",
      "header_content": "Hola María",
      "body_text": "Tu pedido está listo para recoger",
      "button_text": "Ver Pedido",
      "button_url": "https://mi-tienda.com/pedido/456"
    }
  ],
  "use_queue": true
}'
```

**Input:**
```json
{
  "recipients": [
    {
      "phone": "573123456789",
      "header_type": "text",
      "header_content": "Hola Juan",
      "body_text": "Tu pedido está listo para recoger",
      "button_text": "Ver Pedido",
      "button_url": "https://mi-tienda.com/pedido/123"
    }
  ],
  "use_queue": true
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Envío masivo interactivo enviado a cola",
  "task_id": "12345678-1234-1234-1234-123456789abc"
}
```

---

### 6. Broadcast Interactivo

**Endpoint**: `POST /api/send-broadcast-interactive`

**Descripción**: Envía el mismo mensaje interactivo a múltiples números.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/send-broadcast-interactive \
-H "Content-Type: application/json" \
-d '{
  "phones": ["573123456789", "573987654321", "573555666777"],
  "header_type": "text",
  "header_content": "Notificación Important",
  "body_text": "Nueva actualización disponible en nuestra aplicación",
  "button_text": "Actualizar Ahora",
  "button_url": "https://mi-app.com/update",
  "footer_text": "Equipo de Desarrollo",
  "use_queue": true
}'
```

**Input:**
```json
{
  "phones": ["573123456789", "573987654321", "573555666777"],
  "header_type": "text",
  "header_content": "Notificación Important",
  "body_text": "Nueva actualización disponible en nuestra aplicación",
  "button_text": "Actualizar Ahora",
  "button_url": "https://mi-app.com/update",
  "footer_text": "Equipo de Desarrollo",
  "use_queue": true
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Mensaje broadcast enviado a cola",
  "task_id": "12345678-1234-1234-1234-123456789abc"
}
```

---

### 7. Estado de Tarea

**Endpoint**: `GET /api/task-status/{task_id}`

**Descripción**: Obtiene el estado de una tarea en cola.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/task-status/12345678-1234-1234-1234-123456789abc
```

**Output (Éxito):**
```json
{
  "task_id": "12345678-1234-1234-1234-123456789abc",
  "status": "SUCCESS",
  "result": {
    "sent": 3,
    "failed": 0,
    "total": 3
  },
  "created_at": "2025-01-16T10:30:00Z",
  "completed_at": "2025-01-16T10:32:15Z"
}
```

---

### 8. Obtener Media

**Endpoint**: `GET /api/media/{media_id}`

**Descripción**: Obtiene la URL de un archivo multimedia.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/media/123456789
```

**Output (Éxito):**
```json
{
  "success": true,
  "media_url": "https://mmg.whatsapp.net/v/t62.7118-24/123456789"
}
```

---

## 🗂️ Endpoints de Cache

### 9. Obtener Todos los Números

**Endpoint**: `GET /api/numbers`

**Descripción**: Obtiene todos los números guardados en cache.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/numbers
```

**Output (Éxito):**
```json
{
  "success": true,
  "numbers": [
    {
      "phone": "573123456789",
      "name": "Juan Pérez",
      "data": {
        "email": "juan@example.com",
        "company": "Empresa XYZ"
      },
      "created_at": "2025-01-16T10:00:00Z",
      "updated_at": "2025-01-16T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 10. Obtener Número Específico

**Endpoint**: `GET /api/numbers/{phone}`

**Descripción**: Obtiene información de un número específico.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/numbers/573123456789
```

**Output (Éxito):**
```json
{
  "success": true,
  "number": {
    "phone": "573123456789",
    "name": "Juan Pérez",
    "data": {
      "email": "juan@example.com",
      "company": "Empresa XYZ"
    },
    "created_at": "2025-01-16T10:00:00Z",
    "updated_at": "2025-01-16T10:00:00Z"
  }
}
```

**Output (No encontrado):**
```json
{
  "success": false,
  "message": "Number not found"
}
```

---

### 11. Agregar Número

**Endpoint**: `POST /api/numbers`

**Descripción**: Agrega un nuevo número al cache.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/numbers \
-H "Content-Type: application/json" \
-d '{
  "phone": "573123456789",
  "name": "Juan Pérez",
  "data": {
    "email": "juan@example.com",
    "company": "Empresa XYZ",
    "department": "Ventas"
  }
}'
```

**Input:**
```json
{
  "phone": "573123456789",
  "name": "Juan Pérez",
  "data": {
    "email": "juan@example.com",
    "company": "Empresa XYZ",
    "department": "Ventas"
  }
}
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Number 573123456789 added successfully"
}
```

---

### 12. Eliminar Número

**Endpoint**: `DELETE /api/numbers/{phone}`

**Descripción**: Elimina un número del cache.

**Curl:**
```bash
curl -X DELETE http://localhost:5000/api/numbers/573123456789
```

**Output (Éxito):**
```json
{
  "success": true,
  "message": "Number 573123456789 deleted successfully"
}
```

**Output (No encontrado):**
```json
{
  "success": false,
  "message": "Number not found"
}
```

---

### 13. Limpiar Cache

**Endpoint**: `POST /api/numbers/clear`

**Descripción**: Elimina todos los números del cache.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/numbers/clear
```

**Output (Éxito):**
```json
{
  "success": true,
  "deleted": 5,
  "message": "Deleted 5 numbers"
}
```

---

## 🔄 Endpoints de Cola de Mensajes

### 14. Estado de Cola

**Endpoint**: `GET /api/queue/status`

**Descripción**: Obtiene el estado general de las colas.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/queue/status
```

**Output (Éxito):**
```json
{
  "success": true,
  "status": {
    "websocket_available": true,
    "processor_running": true,
    "processor_thread_alive": true,
    "queue_healthy": true
  },
  "queue_lengths": {
    "pending": 3
  }
}
```

---

### 15. Longitudes de Cola

**Endpoint**: `GET /api/queue/lengths`

**Descripción**: Obtiene las longitudes de las colas.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/queue/lengths
```

**Output (Éxito):**
```json
{
  "success": true,
  "queue_lengths": {
    "pending": 3
  }
}
```

---

### 16. Limpiar Cola

**Endpoint**: `DELETE /api/queue/clear`

**Descripción**: Limpia todas las colas (usar con precaución).

**Curl:**
```bash
curl -X DELETE http://localhost:5000/api/queue/clear
```

**Output (Éxito):**
```json
{
  "success": true,
  "result": {
    "cleared": 5
  }
}
```

---

### 17. Probar Cola

**Endpoint**: `POST /api/queue/test`

**Descripción**: Envía un mensaje de prueba a la cola.

**Curl:**
```bash
curl -X POST http://localhost:5000/api/queue/test
```

**Output (Éxito):**
```json
{
  "success": true,
  "result": {
    "success": true,
    "method": "fifo_queue"
  },
  "test_message": {
    "from": "test_user",
    "type": "text",
    "text": "Mensaje de prueba del sistema de colas",
    "timestamp": "1705491000"
  }
}
```

---

## 📊 Endpoints de Estado

### 18. Estado del Servicio

**Endpoint**: `GET /api/status`

**Descripción**: Verifica el estado de todos los servicios.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/status
```

**Output (Éxito):**
```json
{
  "status": "healthy",
  "services": {
    "webhook": true,
    "whatsapp_service": true,
    "queue_service": true,
    "websocket_service": true
  }
}
```

**Output (Degradado):**
```json
{
  "status": "degraded",
  "services": {
    "webhook": true,
    "whatsapp_service": true,
    "queue_service": false,
    "websocket_service": false
  }
}
```

---

### 19. Health Check

**Endpoint**: `GET /api/health`

**Descripción**: Health check simple.

**Curl:**
```bash
curl -X GET http://localhost:5000/api/health
```

**Output (Éxito):**
```json
{
  "status": "ok"
}
```

---

## 📨 Webhook

### 20. Webhook de WhatsApp

**Endpoint**: `POST /webhook`

**Descripción**: Recibe webhooks de WhatsApp (configurado automáticamente).

**Verificación GET:**
```bash
curl -X GET "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=hola&hub.challenge=123456"
```

**Output (Éxito):**
```
123456
```

**Webhook POST** (automático desde WhatsApp):
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "ENTRY_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15550559999",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Juan Pérez"
                },
                "wa_id": "573123456789"
              }
            ],
            "messages": [
              {
                "from": "573123456789",
                "id": "wamid.ID",
                "timestamp": "1705491000",
                "text": {
                  "body": "Hola mundo"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

---

## 🔧 Notas Importantes

### Códigos de Estado HTTP
- **200**: Éxito
- **201**: Creado
- **400**: Error en la solicitud
- **404**: No encontrado
- **500**: Error del servidor
- **503**: Servicio no disponible

### Formato de Números de Teléfono
- Usar formato internacional: `573123456789`
- Sin signos `+` o espacios

### Parámetros Opcionales
- `use_queue`: `true`/`false` (por defecto `false` para individuales, `true` para masivos)
- `language`: Código de idioma (por defecto `"es"`)

### Cache Automático
- Todos los mensajes entrantes se verifican automáticamente contra el cache
- Se añaden campos `save_number` y `cached_info` al JSON del webhook
- Los datos se envían al WebSocket con la información del cache incluida

### Sistema de Cola FIFO
- Mensajes se procesan en orden estricto
- Si hay error de WebSocket, se reintenta el mismo mensaje cada 5 segundos
- La cola se detiene hasta que el mensaje con error sea exitoso
