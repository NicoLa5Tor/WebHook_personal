import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.getenv('WEBHOOK_PORT', '5050')}"
workers = 1  # UN SOLO WORKER para threading y FIFO queue
worker_class = "gthread"  # THREADED WORKER
threads = 4  # THREADS en lugar de múltiples procesos
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de archivos
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configuración de logging
errorlog = "-"  # stderr
accesslog = "-"  # stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = "info"

# Configuración de procesos
daemon = False
reload = False
preload_app = True  # IMPORTANTE: Cargar app una vez para FIFO queue
max_requests = 1000
max_requests_jitter = 50

# Configuración para funcionar sin supervisord
worker_tmp_dir = "/dev/shm"  # Usar memoria compartida para mejor rendimiento
worker_class = "gthread"  # Mantener threads para mejor compatibilidad
threads = 4  # Número de threads por worker

# Configuración de límites
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    server.log.info("🚀 Servidor listo para recibir conexiones")
    server.log.info("🔧 Configuración: 1 worker, 4 threads, preload_app=True")

def worker_int(worker):
    worker.log.info("⚠️ Worker recibió INT o QUIT señal")

def pre_fork(server, worker):
    server.log.info("🔄 Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    worker.log.info("✅ Worker spawned (pid: %s) - iniciando FIFO queue", worker.pid)
    try:
        from services.message_queue_service import MessageQueueService
        MessageQueueService().restart_processor()
        worker.log.info("✅ Procesador FIFO iniciado en worker %s", worker.pid)
    except Exception as e:
        worker.log.warning("No se pudo iniciar el procesador FIFO: %s", e)

def worker_abort(worker):
    worker.log.info("❌ Worker recibió SIGABRT señal")

def on_starting(server):
    server.log.info("🎯 Gunicorn iniciando con configuración FIFO optimizada")

def on_reload(server):
    server.log.info("🔄 Gunicorn recargando...")

def pre_exec(server):
    server.log.info("📋 Pre-exec: Preparando para ejecutar worker")
