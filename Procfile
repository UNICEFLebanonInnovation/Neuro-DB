web: gunicorn config.wsgi:application
worker: celery worker --app=internos.taskapp --loglevel=info
