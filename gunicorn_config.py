"""
Configuración de Gunicorn para Socket.IO con eventlet.
"""

# Configuración de workers
workers = 1  # Socket.IO requiere 1 worker con eventlet
worker_class = "eventlet"  # Usar eventlet para WebSockets
worker_connections = 1000

# Bind
bind = "0.0.0.0:8080"

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app
preload_app = True
