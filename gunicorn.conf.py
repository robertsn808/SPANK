# Gunicorn configuration for SPANKKS Construction
import os
import signal

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "spankks-construction"

# Server mechanics
preload_app = True
reload = True
daemon = False

# SSL (if needed in production)
# keyfile = None
# certfile = None

# Worker signal handling - ignore SIGWINCH to prevent log spam
def when_ready(server):
    """Called just after the server is started."""
    # Ignore SIGWINCH (window change) signals to prevent log spam
    signal.signal(signal.SIGWINCH, signal.SIG_IGN)
    server.log.info("SPANKKS Construction server started - SIGWINCH ignored")

def worker_init(worker):
    """Called just after a worker has been forked."""
    # Also ignore SIGWINCH in worker processes
    signal.signal(signal.SIGWINCH, signal.SIG_IGN)

# Performance tuning for Replit environment
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190