
from datetime import timedelta

from django.utils import timezone

from django_celery_results.models import TaskResult
from celery import shared_task
from request.models import Request

from logs.models import DatabaseLog, DashboardLog


@shared_task
def clear_old_request_logs():
    'clears Request Logs older than 14 days'
    
    time_threshold = timezone.now() - timedelta(days=14)
    old_logs = Request.objects.filter(time__lte=time_threshold)
    count = old_logs.count()
    #time__gte is django's magic way of saying time is greater than or equal to
    old_logs.delete()

    print("{} stale Request logs cleared!".format(count))
    print("TASK COMPLETE!")


@shared_task
def clear_old_dashboard_logs():
    'clears DashboardLog Logs older than 30 days'
    
    time_threshold = timezone.now() - timedelta(days=30)
    old_logs = DashboardLog.objects.filter(time__lte=time_threshold)
    count = len(old_logs)
    old_logs.delete()

    print("{} stale Dashboard logs cleared!".format(count))
    print("TASK COMPLETE!")


@shared_task
def clear_old_database_logs():
    'clears DatabaseLog Logs older than 30 days'
    
    time_threshold = timezone.now() - timedelta(days=30)
    old_logs = DatabaseLog.objects.filter(create_datetime__lte=time_threshold)
    count = len(old_logs)
    #time__gte is django's magic way of saying time is greater than or equal to
    old_logs.delete()

    print("{} stale Database logs cleared!".format(count))
    print("TASK COMPLETE!")


@shared_task
def clear_old_celery_result_logs():
    'clears Celery TaskResult logs older than 30 days'
    
    time_threshold = timezone.now() - timedelta(days=30)
    old_logs = TaskResult.objects.filter(date_created__lte=time_threshold)
    count = len(old_logs)
    #time__gte is django's magic way of saying time is greater than or equal to
    old_logs.delete()

    print("{} stale Celery Task Result Logs cleared!".format(count))
    print("TASK COMPLETE!")