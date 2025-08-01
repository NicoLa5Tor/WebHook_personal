import requests
import os
import logging
import base64
import io
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        # Solo guardamos valores que no cambian frecuentemente
        self.version = os.getenv('VERSION', 'v17.0')
        self.base_url = os.getenv('BASE_URL', 'https://graph.facebook.com')
        
        # Verificar que PHONE_NUMBER_ID esté presente al inicializar
        if not self._get_phone_number_id():
            raise ValueError("PHONE_NUMBER_ID es requerido")
    
    def _get_max_workers(self) -> int:
        """Obtiene la cantidad máxima de workers desde .env"""
        try:
            return int(os.getenv('BULK_MAX_WORKERS', '10'))
        except ValueError:
            return 10
    
    def _get_phone_number_id(self) -> str:
        """Obtiene el PHONE_NUMBER_ID dinámicamente desde .env"""
        # Forzar recarga completa del .env
        load_dotenv(override=True)  # override=True fuerza recargar
        phone_number_id = os.getenv('PHONE_NUMBER_ID')
        if not phone_number_id:
            raise ValueError("PHONE_NUMBER_ID es requerido")
        return phone_number_id
    
    def _get_access_token(self) -> str:
        """Obtiene el token de acceso dinámicamente desde .env"""
        # Forzar recarga completa del .env
        load_dotenv(override=True)  # override=True fuerza recargar
        access_token = os.getenv('ACCESS_TOKEN')
        if not access_token:
            raise ValueError("ACCESS_TOKEN es requerido")
        return access_token
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def _get_url(self) -> str:
        return f"{self.base_url}/{self.version}/{self._get_phone_number_id()}/messages"
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """Envía un mensaje de texto"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Mensaje enviado exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando mensaje: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Excepción enviando mensaje: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_template_message(self, to: str, template_name: str, language: str = "es", parameters: Optional[List[str]] = None) -> Dict:
        """Envía un mensaje de plantilla"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language}
            }
        }
        
        if parameters:
            payload["template"]["components"] = [{
                "type": "body",
                "parameters": [{"type": "text", "text": param} for param in parameters]
            }]
        
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Plantilla enviada exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando plantilla: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Excepción enviando plantilla: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_bulk_messages(self, recipients: List[Dict]) -> Dict:
        """Envía mensajes masivos de forma simultánea"""
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Función para enviar mensaje a un solo destinatario
        def send_to_recipient(recipient):
            phone = recipient.get('phone')
            message = recipient.get('message')
            
            if not phone or not message:
                return {"success": False, "error": "Datos incompletos", "phone": phone}
            
            result = self.send_text_message(phone, message)
            
            return {"success": result["success"], "error": result.get("error", ""), "phone": phone}
        
        # Enviar mensajes simultáneamente usando ThreadPoolExecutor
        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=min(len(recipients), max_workers)) as executor:
            # Enviar todas las tareas al pool de threads
            future_to_recipient = {executor.submit(send_to_recipient, recipient): recipient for recipient in recipients}
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_recipient):
                recipient = future_to_recipient[future]
                phone = recipient.get('phone')
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Error para {phone}: {result['error']}")
                except Exception as exc:
                    results["failed"] += 1
                    results["errors"].append(f"Error para {phone}: {str(exc)}")
        
        return results
    
    def send_interactive_message(self, to: str, header_type: str = None, header_content: str = None, 
                                 body_text: str = None, button_text: str = None, button_url: str = None,
                                 footer_text: str = None) -> Dict:
        """Envía un mensaje interactivo con botón CTA"""
        
        # Estructura base del mensaje interactivo
        interactive_data = {
            "type": "cta_url",
            "body": {
                "text": body_text or "Mensaje interactivo"
            },
            "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": button_text or "Ver más",
                    "url": button_url or "https://example.com"
                }
            }
        }
        
        # Agregar header si se proporciona
        if header_type and header_content:
            if header_type == "text":
                interactive_data["header"] = {
                    "type": "text",
                    "text": header_content
                }
            elif header_type in ["image", "video", "document"]:
                # Determinar si es URL o base64
                if header_content.startswith(('http://', 'https://')):
                    # Es una URL
                    interactive_data["header"] = {
                        "type": header_type,
                        header_type: {
                            "link": header_content
                        }
                    }
                else:
                    # Es base64 - necesitamos subirlo primero
                    logger.info(f"Detectado base64, subiendo archivo...")
                    media_id = self.upload_media_from_base64(header_content, header_type)
                    
                    if media_id:
                        interactive_data["header"] = {
                            "type": header_type,
                            header_type: {
                                "id": media_id
                            }
                        }
                    else:
                        logger.error("No se pudo subir el archivo base64")
                        # Continuar sin header si falla el upload
                        pass
        
        # Agregar footer si se proporciona
        if footer_text:
            interactive_data["footer"] = {
                "text": footer_text
            }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive_data
        }
        
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Mensaje interactivo enviado exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando mensaje interactivo: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Excepción enviando mensaje interactivo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_personalized_broadcast_messages(self, recipients: List[Dict], header_type: str = None, header_content: str = None,
                                               button_text: str = None, button_url: str = None, footer_text: str = None) -> Dict:
        """Envía mensajes interactivos personalizados"""
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        # Si es base64, subir una sola vez y reutilizar el media_id
        media_id = None
        if header_type and header_content and header_type in ["image", "video", "document"]:
            if not header_content.startswith(('http://', 'https://')):
                logger.info(f"Detectado base64, subiendo archivo una sola vez...")
                media_id = self.upload_media_from_base64(header_content, header_type)
                if not media_id:
                    logger.error("No se pudo subir el archivo base64")
                    results["errors"].append("No se pudo subir el archivo base64")
                    results["failed"] = len(recipients)
                    return results

        # Función para enviar mensaje a un solo número
        def send_to_recipient(recipient):
            phone = recipient.get('phone')
            body_text = recipient.get('body_text')

            if not phone or not body_text:
                return {"success": False, "error": "Datos incompletos para {phone}", "phone": phone}

            # Usar media_id si ya se subió, o header_content original si es URL
            final_header_content = media_id if media_id else header_content

            result = self.send_interactive_message(
                phone, header_type, final_header_content, body_text, 
                button_text, button_url, footer_text
            )

            return {"success": result["success"], "error": result.get("error", ""), "phone": phone}

        # Enviar mensajes simultáneamente usando ThreadPoolExecutor
        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=min(len(recipients), max_workers)) as executor:
            # Enviar todas las tareas al pool de threads
            future_to_recipient = {executor.submit(send_to_recipient, recipient): recipient for recipient in recipients}

            # Procesar resultados conforme se completan
            for future in as_completed(future_to_recipient):
                recipient = future_to_recipient[future]
                phone = recipient.get('phone')
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Error para {phone}: {result['error']}")
                except Exception as exc:
                    results["failed"] += 1
                    results["errors"].append(f"Error para {phone}: {str(exc)}")

        return results
    
    def send_bulk_list_messages(self, recipients: List[Dict], header_text: str = None, footer_text: str = None,
                                button_text: str = None, sections: List[Dict] = None) -> Dict:
        """Envía mensajes de lista masivos personalizados de forma simultánea"""
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Función para enviar mensaje de lista a un solo destinatario
        def send_list_to_recipient(recipient):
            phone = recipient.get('phone')
            body_text = recipient.get('body_text')
            
            if not phone or not body_text:
                return {"success": False, "error": "Datos incompletos: phone y body_text son requeridos", "phone": phone}
            
            result = self.send_list_message(phone, header_text, body_text, footer_text, button_text, sections)
            
            return {"success": result["success"], "error": result.get("error", ""), "phone": phone}
        
        # Enviar mensajes simultáneamente usando ThreadPoolExecutor
        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=min(len(recipients), max_workers)) as executor:
            # Enviar todas las tareas al pool de threads
            future_to_recipient = {executor.submit(send_list_to_recipient, recipient): recipient for recipient in recipients}
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_recipient):
                recipient = future_to_recipient[future]
                phone = recipient.get('phone')
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Error para {phone}: {result['error']}")
                except Exception as exc:
                    results["failed"] += 1
                    results["errors"].append(f"Error para {phone}: {str(exc)}")
        
        return results
    
    def send_list_message(self, to: str, header_text: str, body_text: str, footer_text: str, button_text: str, sections: List[Dict]) -> Dict:
        """Envía un mensaje interactivo de lista"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            if response.status_code == 200:
                logger.info(f"Mensaje de lista enviado exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando mensaje de lista: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Excepción enviando mensaje de lista: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_button_message(self, to: str, header_type: str = None, header_content: str = None,
                           body_text: str = None, buttons: List[Dict] = None, footer_text: str = None) -> Dict:
        """Envía un mensaje con botones de respuesta"""
        
        if not buttons or len(buttons) == 0:
            return {"success": False, "error": "Se requiere al menos un botón"}
        
        if len(buttons) > 3:
            return {"success": False, "error": "Máximo 3 botones permitidos"}
        
        # Validar estructura de botones
        for i, button in enumerate(buttons):
            if not isinstance(button, dict):
                return {"success": False, "error": f"Botón {i+1} debe ser un objeto"}
            
            if not button.get('id'):
                return {"success": False, "error": f"Botón {i+1} debe tener un 'id'"}
            
            if not button.get('title'):
                return {"success": False, "error": f"Botón {i+1} debe tener un 'title'"}
            
            # Validar longitud del título (máximo 20 caracteres)
            if len(button['title']) > 20:
                return {"success": False, "error": f"Título del botón {i+1} debe tener máximo 20 caracteres"}
        
        # Estructura del mensaje interactivo con botones
        interactive_data = {
            "type": "button",
            "body": {
                "text": body_text or "Mensaje con botones"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": button["id"],
                            "title": button["title"]
                        }
                    } for button in buttons
                ]
            }
        }
        
        # Agregar header si se proporciona
        if header_type and header_content:
            if header_type == "text":
                interactive_data["header"] = {
                    "type": "text",
                    "text": header_content
                }
            elif header_type in ["image", "video", "document"]:
                # Determinar si es URL o base64
                if header_content.startswith(('http://', 'https://')):
                    # Es una URL
                    interactive_data["header"] = {
                        "type": header_type,
                        header_type: {
                            "link": header_content
                        }
                    }
                else:
                    # Es base64 - necesitamos subirlo primero
                    logger.info(f"Detectado base64, subiendo archivo...")
                    media_id = self.upload_media_from_base64(header_content, header_type)
                    
                    if media_id:
                        interactive_data["header"] = {
                            "type": header_type,
                            header_type: {
                                "id": media_id
                            }
                        }
                    else:
                        logger.error("No se pudo subir el archivo base64")
                        # Continuar sin header si falla el upload
                        pass
        
        # Agregar footer si se proporciona
        if footer_text:
            interactive_data["footer"] = {
                "text": footer_text
            }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive_data
        }
        
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Mensaje con botones enviado exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando mensaje con botones: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Excepción enviando mensaje con botones: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_bulk_button_messages(self, recipients: List[Dict], header_type: str = None, header_content: str = None,
                                 buttons: List[Dict] = None, footer_text: str = None) -> Dict:
        """Envía mensajes con botones personalizados a múltiples números"""
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Validar botones comunes
        if not buttons or len(buttons) == 0:
            results["errors"].append("Se requiere al menos un botón")
            results["failed"] = len(recipients)
            return results
        
        # Si es base64, subir una sola vez y reutilizar el media_id
        media_id = None
        if header_type and header_content and header_type in ["image", "video", "document"]:
            if not header_content.startswith(('http://', 'https://')):
                logger.info(f"Detectado base64, subiendo archivo una sola vez...")
                media_id = self.upload_media_from_base64(header_content, header_type)
                if not media_id:
                    logger.error("No se pudo subir el archivo base64")
                    results["errors"].append("No se pudo subir el archivo base64")
                    results["failed"] = len(recipients)
                    return results
        
        # Función para enviar mensaje a un solo destinatario
        def send_to_recipient(recipient):
            phone = recipient.get('phone')
            body_text = recipient.get('body_text')
            
            if not phone or not body_text:
                return {"success": False, "error": "Datos incompletos: phone y body_text son requeridos", "phone": phone}
            
            # Usar media_id si ya se subió, o header_content original si es URL
            final_header_content = media_id if media_id else header_content
            
            result = self.send_button_message(
                phone, header_type, final_header_content, body_text, buttons, footer_text
            )
            
            return {"success": result["success"], "error": result.get("error", ""), "phone": phone}
        
        # Enviar mensajes simultáneamente usando ThreadPoolExecutor
        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=min(len(recipients), max_workers)) as executor:
            # Enviar todas las tareas al pool de threads
            future_to_recipient = {executor.submit(send_to_recipient, recipient): recipient for recipient in recipients}
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_recipient):
                recipient = future_to_recipient[future]
                phone = recipient.get('phone')
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Error para {phone}: {result['error']}")
                except Exception as exc:
                    results["failed"] += 1
                    results["errors"].append(f"Error para {phone}: {str(exc)}")
        
        return results
    
    def send_broadcast_interactive_message(self, phones: List[str], header_type: str = None, header_content: str = None,
                                          body_text: str = None, button_text: str = None, button_url: str = None,
                                          footer_text: str = None) -> Dict:
        """Envía el mismo mensaje interactivo a múltiples números de forma simultánea"""
        results = {
            "total": len(phones),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Si es base64, subir una sola vez y reutilizar el media_id
        media_id = None
        if header_type and header_content and header_type in ["image", "video", "document"]:
            if not header_content.startswith(('http://', 'https://')):
                logger.info(f"Detectado base64 para broadcast, subiendo archivo una sola vez...")
                media_id = self.upload_media_from_base64(header_content, header_type)
                if not media_id:
                    logger.error("No se pudo subir el archivo base64 para broadcast")
                    return {
                        "total": len(phones),
                        "successful": 0,
                        "failed": len(phones),
                        "errors": ["No se pudo subir el archivo base64"]
                    }
        
        # Función para enviar mensaje a un solo número
        def send_to_phone(phone):
            if not phone:
                return {"success": False, "error": "Número vacío o inválido", "phone": phone}
            
            # Usar media_id si ya se subió, o header_content original si es URL
            final_header_content = media_id if media_id else header_content
            
            result = self.send_interactive_message(
                phone, header_type, final_header_content, body_text, 
                button_text, button_url, footer_text
            )
            
            return {"success": result["success"], "error": result.get("error", ""), "phone": phone}
        
        # Enviar mensajes simultáneamente usando ThreadPoolExecutor
        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=min(len(phones), max_workers)) as executor:
            # Enviar todas las tareas al pool de threads
            future_to_phone = {executor.submit(send_to_phone, phone): phone for phone in phones}
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_phone):
                phone = future_to_phone[future]
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Error para {phone}: {result['error']}")
                except Exception as exc:
                    results["failed"] += 1
                    results["errors"].append(f"Error para {phone}: {str(exc)}")
        
        return results
    
    def upload_media_from_base64(self, base64_data: str, media_type: str = "image") -> Optional[str]:
        """Sube un archivo multimedia desde base64 y devuelve el media_id"""
        try:
            # Determinar el tipo MIME
            mime_types = {
                "image": "image/jpeg",
                "video": "video/mp4",
                "document": "application/pdf"
            }
            
            # Extraer el base64 sin el prefijo data: si lo tiene
            if base64_data.startswith('data:'):
                # Formato: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...
                base64_part = base64_data.split(',')[1]
                # Extraer el tipo MIME del prefijo
                mime_type = base64_data.split(';')[0].split(':')[1]
            else:
                # Solo base64 sin prefijo
                base64_part = base64_data
                mime_type = mime_types.get(media_type, "image/jpeg")
            
            # Decodificar base64
            file_data = base64.b64decode(base64_part)
            
            # URL para subir media
            upload_url = f"{self.base_url}/{self.version}/{self._get_phone_number_id()}/media"
            
            # Headers para upload (sin Content-Type json)
            headers = {
                'Authorization': f'Bearer {self._get_access_token()}'
            }
            
            # Preparar el archivo para upload
            files = {
                'file': ('media_file', io.BytesIO(file_data), mime_type),
                'messaging_product': (None, 'whatsapp')
            }
            
            response = requests.post(upload_url, headers=headers, files=files)
            
            if response.status_code == 200:
                media_id = response.json().get('id')
                logger.info(f"Media subido exitosamente: {media_id}")
                return media_id
            else:
                logger.error(f"Error subiendo media: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción subiendo media: {str(e)}")
            return None
    
    def send_location_request_message(self, to: str, body_text: str) -> Dict:
        """Envía un mensaje de solicitud de ubicación"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": to,
            "interactive": {
                "type": "location_request_message",
                "body": {
                    "text": body_text
                },
                "action": {
                    "name": "send_location"
                }
            }
        }
        
        try:
            response = requests.post(
                self._get_url(),
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Solicitud de ubicación enviada exitosamente a {to}")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Error enviando solicitud de ubicación: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Excepción enviando solicitud de ubicación: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_media_url(self, media_id: str) -> Optional[str]:
        """Obtiene la URL de un archivo multimedia"""
        url = f"{self.base_url}/{self.version}/{media_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json().get('url')
            else:
                logger.error(f"Error obteniendo media URL: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción obteniendo media URL: {str(e)}")
            return None
