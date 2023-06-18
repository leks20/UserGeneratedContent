from conf.config import settings

bind = f'{settings.bind_ip}:{settings.bind_port}'
workers = settings.web_concurrency
worker_class = 'uvicorn.workers.UvicornWorker'
wsgi_app = 'webapp.main:create_app'
