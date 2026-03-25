import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('GUNICORN_WORKERS', max(2, multiprocessing.cpu_count() // 2)))
threads = int(os.getenv('GUNICORN_THREADS', 4))
timeout = int(os.getenv('GUNICORN_TIMEOUT', 60))
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
