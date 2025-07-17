import os
import logging
from typing import Dict, List
from celery import Celery
from .whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

# Configurar Celery
celery_app = Celery('whatsapp_tasks')
celery_app.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


class QueueService:
    def __init__(self):
        self.celery = celery_app
    
    def send_message_async(self, to: str, message: str):
        """Envía un mensaje de forma asíncrona"""
        return send_message_task.delay(to, message)
    
    def send_bulk_messages_async(self, recipients: List[Dict]):
        """Envía mensajes masivos de forma asíncrona"""
        return send_bulk_messages_task.delay(recipients)
    
    def send_template_async(self, to: str, template_name: str, language: str = "es", parameters: List[str] = None):
        """Envía una plantilla de forma asíncrona"""
        return send_template_task.delay(to, template_name, language, parameters)
    
    def send_interactive_message_async(self, to: str, header_type: str = None, header_content: str = None,
                                       body_text: str = None, button_text: str = None, button_url: str = None,
                                       footer_text: str = None):
        """Envía un mensaje interactivo de forma asíncrona"""
        return send_interactive_message_task.delay(to, header_type, header_content, body_text, button_text, button_url, footer_text)
    
    def send_bulk_interactive_messages_async(self, recipients: List[Dict]):
        """Envía mensajes interactivos masivos de forma asíncrona"""
        return send_bulk_interactive_messages_task.delay(recipients)
    
    def send_broadcast_interactive_message_async(self, phones: List[str], header_type: str = None, header_content: str = None,
                                                body_text: str = None, button_text: str = None, button_url: str = None,
                                                footer_text: str = None):
        """Envía el mismo mensaje interactivo a múltiples números de forma asíncrona"""
        return send_broadcast_interactive_message_task.delay(phones, header_type, header_content, body_text, button_text, button_url, footer_text)
    
    def send_personalized_broadcast_messages_async(self, recipients: List[Dict], header_type: str = None, header_content: str = None,
                                                  button_text: str = None, button_url: str = None, footer_text: str = None):
        """Envía mensajes interactivos personalizados de forma asíncrona"""
        return send_personalized_broadcast_messages_task.delay(recipients, header_type, header_content, button_text, button_url, footer_text)
    
    def get_task_status(self, task_id: str):
        """Obtiene el estado de una tarea"""
        result = self.celery.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None
        }


@celery_app.task(bind=True, max_retries=3)
def send_message_task(self, to: str, message: str):
    """Tarea para enviar un mensaje"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_text_message(to, message)
        
        if result['success']:
            logger.info(f"Mensaje enviado en cola exitosamente a {to}")
            return result
        else:
            logger.error(f"Error enviando mensaje en cola: {result['error']}")
            raise Exception(result['error'])
            
    except Exception as e:
        logger.error(f"Error en tarea de envío: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando envío... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_bulk_messages_task(self, recipients: List[Dict]):
    """Tarea para enviar mensajes masivos"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_bulk_messages(recipients)
        
        logger.info(f"Envío masivo completado: {result['successful']}/{result['total']}")
        return result
        
    except Exception as e:
        logger.error(f"Error en tarea de envío masivo: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando envío masivo... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_template_task(self, to: str, template_name: str, language: str = "es", parameters: List[str] = None):
    """Tarea para enviar una plantilla"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_template_message(to, template_name, language, parameters)
        
        if result['success']:
            logger.info(f"Plantilla enviada en cola exitosamente a {to}")
            return result
        else:
            logger.error(f"Error enviando plantilla en cola: {result['error']}")
            raise Exception(result['error'])
            
    except Exception as e:
        logger.error(f"Error en tarea de envío de plantilla: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando envío de plantilla... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_interactive_message_task(self, to: str, header_type: str = None, header_content: str = None,
                                  body_text: str = None, button_text: str = None, button_url: str = None,
                                  footer_text: str = None):
    """Tarea para enviar un mensaje interactivo"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_interactive_message(
            to, header_type, header_content, body_text, button_text, button_url, footer_text
        )
        
        if result['success']:
            logger.info(f"Mensaje interactivo enviado en cola exitosamente a {to}")
            return result
        else:
            logger.error(f"Error enviando mensaje interactivo en cola: {result['error']}")
            raise Exception(result['error'])
            
    except Exception as e:
        logger.error(f"Error en tarea de envío de mensaje interactivo: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando envío de mensaje interactivo... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_bulk_interactive_messages_task(self, recipients: List[Dict]):
    """Tarea para enviar mensajes interactivos masivos"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_bulk_interactive_messages(recipients)
        
        logger.info(f"Envío masivo interactivo completado: {result['successful']}/{result['total']}")
        return result
        
    except Exception as e:
        logger.error(f"Error en tarea de envío masivo interactivo: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando envío masivo interactivo... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_broadcast_interactive_message_task(self, phones: List[str], header_type: str = None, header_content: str = None,
                                           body_text: str = None, button_text: str = None, button_url: str = None,
                                           footer_text: str = None):
    """Tarea para enviar el mismo mensaje interactivo a múltiples números"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_broadcast_interactive_message(
            phones, header_type, header_content, body_text, button_text, button_url, footer_text
        )
        
        logger.info(f"Broadcast interactivo completado: {result['successful']}/{result['total']}")
        return result
        
    except Exception as e:
        logger.error(f"Error en tarea de broadcast interactivo: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando broadcast interactivo... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def send_personalized_broadcast_messages_task(self, recipients: List[Dict], header_type: str = None, header_content: str = None,
                                             button_text: str = None, button_url: str = None, footer_text: str = None):
    """Tarea para enviar mensajes interactivos personalizados"""
    try:
        # Forzar recarga de .env en el worker con path absoluto
        from dotenv import load_dotenv
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path, override=True)  # Forzar recarga completa
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_personalized_broadcast_messages(
            recipients, header_type, header_content, button_text, button_url, footer_text
        )
        
        logger.info(f"Broadcast personalizado completado: {result['successful']}/{result['total']}")
        return result
        
    except Exception as e:
        logger.error(f"Error en tarea de broadcast personalizado: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando broadcast personalizado... Intento {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        else:
            return {'success': False, 'error': str(e)}
