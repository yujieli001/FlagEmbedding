import multiprocessing
import os

# 绑定地址
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:10010')

# Worker 配置
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# 进程命名
proc_name = "flagmodel-embedder"

# 日志配置
accesslog = os.environ.get('ACCESS_LOG', '-')
errorlog = os.environ.get('ERROR_LOG', '-')
loglevel = os.environ.get('LOG_LEVEL', 'info')

# 启用工兵模式（可选）
# capture_output = True
# enable_stdio_inheritance = True
