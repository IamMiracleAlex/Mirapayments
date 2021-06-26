import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mirapayments.settings')

app = Celery('mirapayments')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# crontabs
app.conf.update(
    timezone='Africa/Lagos',
    enable_utc=True,
)

app.conf.beat_schedule = {
      
    # "update_labelled_urls": {
    #     "task": "annotation.schedules.update_labelled_urls.handle",
    #     "schedule": crontab(minute=0, hour=0)  # every day at midnight
    # },    
    # "events_and_unique_urls_status": {
    #     "task": "annotation.schedules.events_and_unique_urls_status.handle",
    #     "schedule": crontab(minute=0, hour=0)  # every day at midnight
    # },    
    # "rds_internet_archive": {
    #     "task": "annotation.schedules.rds_internet_archive.handle",
    #     "schedule": crontab(minute='*/15')  # every 15 mins
    # },    
    # "delete_node_permanently": {
    #     "task": "classification.schedules.delete_node_permanently.handle",
    #     'schedule': crontab(minute=0, hour=0, day_of_month=(2, 15)),  # every 2nd and 15th of the month
    # },    
    "clear_old_request_logs": {
        "task": "logs.tasks.clear_old_request_logs",
        'schedule': crontab(minute=0, hour=0, day_of_month=(2, 15)),  # every 2nd and 15th of the month
    },
    "clear_old_dashboard_logs": {
        "task": "logs.tasks.clear_old_dashboard_logs",
        'schedule': crontab(minute=0, hour=0, day_of_month=(2, 15)),  # every 2nd and 15th of the month
    },
    "clear_old_database_logs": {
        "task": "logs.tasks.clear_old_database_logs",
        'schedule': crontab(minute=0, hour=0, day_of_month=(2, 15)),  # every 2nd and 15th of the month
    },
    "clear_old_celery_result_logs": {
        "task": "logs.tasks.clear_old_celery_result_logs",
        'schedule': crontab(minute=0, hour=0, day_of_month=(2, 15)),  # every 2nd and 15th of the month
    },
}
