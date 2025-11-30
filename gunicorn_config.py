"""
Configuración de Gunicorn para Socket.IO con gevent.
"""

# Configuración de workers
workers = 1  # Socket.IO requiere 1 worker con gevent
worker_class = "gevent"  # Usar gevent para WebSockets
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
