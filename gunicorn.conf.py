import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.getenv('WEBHOOK_PORT', '5050')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
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
preload_app = True
max_requests = 1000
max_requests_jitter = 50

# Configuración de límites
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    server.log.info("Servidor listo para recibir conexiones")

def worker_int(worker):
    worker.log.info("Worker recibió INT o QUIT señal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker recibió SIGABRT señal")
