# Endpoint de Broadcast de Mensajes Interactivos

## Descripción

El nuevo endpoint `/api/messages/send-broadcast-interactive` permite enviar el **mismo mensaje interactivo** a múltiples números telefónicos de forma eficiente. A diferencia del endpoint masivo existente, este broadcast utiliza un único JSON con los datos del mensaje y un array de números telefónicos.

## Características Principales

- ✅ **Envío único**: Un solo mensaje interactivo para múltiples números
- ✅ **Optimización de archivos**: Si usa archivos base64, se suben una sola vez y se reutilizan
- ✅ **Soporte asíncrono**: Puede usar colas para envíos masivos
- ✅ **Estadísticas detalladas**: Contador de éxitos, fallos y errores específicos
- ✅ **Flexible**: Soporta headers de texto, imagen, video y documentos

## Endpoint

```
POST /api/messages/send-broadcast-interactive
```

## Parámetros

### Requeridos
- `phones` (array): Array de números telefónicos (formato: 57300XXXXXXX)
- `body_text` (string): Texto principal del mensaje

### Opcionales
- `header_type` (string): Tipo de header ("text", "image", "video", "document")
- `header_content` (string): Contenido del header (texto, URL o base64)
- `button_text` (string): Texto del botón (por defecto: "Ver más")
- `button_url` (string): URL del botón (por defecto: "https://example.com")
- `footer_text` (string): Texto del pie de página
- `use_queue` (boolean): Si usar cola asíncrona (por defecto: false)

## Ejemplos de Uso

### 1. Mensaje Básico

```json
{
  "phones": [
    "573001234567",
    "573007654321",
    "573009876543"
  ],
  "body_text": "¡Oferta especial! 50% de descuento en todos nuestros productos."
}
```

### 2. Mensaje con Header de Texto

```json
{
  "phones": [
    "573001234567",
    "573007654321"
  ],
  "header_type": "text",
  "header_content": "🎉 Oferta Especial",
  "body_text": "¡Aprovecha nuestra promoción limitada! 50% de descuento en todos nuestros productos.",
  "button_text": "Ver Ofertas",
  "button_url": "https://mitienda.com/ofertas",
  "footer_text": "Válido hasta el 31 de diciembre"
}
```

### 3. Mensaje con Imagen (URL)

```json
{
  "phones": [
    "573001234567",
    "573007654321"
  ],
  "header_type": "image",
  "header_content": "https://mitienda.com/promo-image.jpg",
  "body_text": "¡Nueva colección disponible! Descubre los últimos diseños.",
  "button_text": "Ver Colección",
  "button_url": "https://mitienda.com/nueva-coleccion",
  "footer_text": "Envío gratis en compras superiores a $100"
}
```

### 4. Mensaje con Imagen Base64

```json
{
  "phones": [
    "573001234567",
    "573007654321"
  ],
  "header_type": "image",
  "header_content": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
  "body_text": "Imagen personalizada para ti. ¡Mira lo que tenemos preparado!",
  "button_text": "Ver Más",
  "button_url": "https://mitienda.com/personalizado",
  "footer_text": "Contenido exclusivo"
}
```

### 5. Envío Asíncrono con Cola

```json
{
  "phones": [
    "573001234567",
    "573007654321",
    "573009876543",
    "573005555555"
  ],
  "body_text": "Mensaje importante que se enviará a través de cola",
  "button_text": "Más Información",
  "button_url": "https://mitienda.com/info",
  "use_queue": true
}
```

## Respuestas

### Envío Directo (use_queue: false)

```json
{
  "success": true,
  "message": "Mensaje broadcast procesado",
  "result": {
    "total": 3,
    "successful": 2,
    "failed": 1,
    "errors": [
      "Error para 573001234567: Invalid phone number format"
    ]
  }
}
```

### Envío Asíncrono (use_queue: true)

```json
{
  "success": true,
  "message": "Mensaje broadcast enviado a cola",
  "task_id": "abc123-def456-ghi789"
}
```

## Consulta de Estado de Tarea

Para envíos asíncronos, puedes consultar el estado:

```
GET /api/messages/task-status/{task_id}
```

**Respuesta:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": {
    "total": 3,
    "successful": 3,
    "failed": 0,
    "errors": []
  }
}
```

## Manejo de Errores

### Errores de Validación (400)

```json
{
  "error": "Se requiere el campo 'phones' con un array de números telefónicos"
}
```

```json
{
  "error": "Se requiere el campo 'body_text'"
}
```

### Error de Servicio (500)

```json
{
  "error": "Error interno del servidor"
}
```

## Optimizaciones

### 1. Archivos Base64
- Si el header es un archivo base64, se sube **una sola vez** a WhatsApp
- El `media_id` se reutiliza para todos los envíos del broadcast
- Esto reduce significativamente el tiempo de procesamiento

### 2. Procesamiento Asíncrono
- Para listas grandes de números, usa `"use_queue": true`
- El procesamiento se realiza en background usando Celery
- Puedes consultar el progreso con el `task_id`

## Diferencias con Otros Endpoints

| Característica | `/send-broadcast-interactive` | `/send-bulk-interactive` |
|---------------|------------------------------|--------------------------|
| **Mensaje** | Único para todos | Personalizado por contacto |
| **Parámetros** | Un solo JSON con array phones | Array de objetos recipient |
| **Optimización** | Archivo base64 se sube 1 vez | Archivo se sube por cada envío |
| **Uso típico** | Promociones, anuncios | Mensajes personalizados |

## Casos de Uso Ideales

- 📢 **Anuncios promocionales** masivos
- 📰 **Newsletters** con botones de acción
- 🎯 **Campañas de marketing** dirigidas
- 📅 **Recordatorios** de eventos
- 🎁 **Ofertas especiales** con imágenes

## Pruebas

Para probar el endpoint, ejecuta:

```bash
python test_broadcast_interactive.py
```

El script incluye pruebas para:
- Mensajes con headers de texto
- Mensajes con imágenes (URL y base64)
- Mensajes mínimos
- Manejo de errores
- Envío asíncrono con cola

## Límites y Consideraciones

- ⚠️ **Límite de WhatsApp**: Respeta los límites de API de WhatsApp Business
- ⚠️ **Archivos grandes**: Los archivos base64 grandes pueden tomar tiempo en subirse
- ⚠️ **Números inválidos**: Los números incorrectos se reportan en el array de errores
- ⚠️ **Rate limiting**: Para listas muy grandes, considera usar `use_queue: true`

## Logging

El sistema genera logs detallados para:
- Subida de archivos base64
- Envíos exitosos y fallidos
- Errores específicos por número
- Estadísticas de broadcast

¡El endpoint está listo para usarse en producción! 🚀
