cd ..
celery -A vinda.api.worker.celery_tasks worker -E --pool=solo --loglevel=info --logfile=/tmp/celery.log