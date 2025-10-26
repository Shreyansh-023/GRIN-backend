import multiprocessing
import os

# Gunicorn config variables
workers = 1  # For Render's free tier memory limit
threads = 8
worker_class = "uvicorn.workers.UvicornWorker"
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
timeout = 300
keepalive = 120

# For faster startup
preload_app = True

# SSL Configuration
keyfile = None
certfile = None

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "lumera_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """
    Server initialization.
    """
    pass

def when_ready(server):
    """
    Called just after the server is started.
    """
    pass