#!/usr/bin/env python3
"""
Worker script para ejecutar tareas de Celery
"""

from services.queue_service import celery_app

if __name__ == '__main__':
    # Ejecutar el worker de Celery
    celery_app.start(['worker', '--loglevel=info', '--concurrency=4'])
