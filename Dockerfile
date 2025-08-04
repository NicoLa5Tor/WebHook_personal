# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn
RUN pip install --no-cache-dir gunicorn

# Copiar el código de la aplicación
COPY . .

# Crear directorio para SQLite y logs
RUN mkdir -p /app/data /var/log/supervisor /var/run

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && chown -R app:app /var/log/supervisor \
    && chown -R app:app /var/run

# Cambiar a usuario app
USER app

# Exponer el puerto
EXPOSE 5050

# Comando por defecto usando supervisor
CMD ["supervisord", "-c", "supervisord.conf"]
