import logging

from django.db import models
from django.utils.translation import gettext_lazy as _


LOG_LEVELS = (
    (logging.NOTSET, _('NotSet')),
    (logging.INFO, _('Info')),
    (logging.WARNING, _('Warning')),
    (logging.DEBUG, _('Debug')),
    (logging.ERROR, _('Error')),
    (logging.FATAL, _('Fatal')),
)

class DatabaseLog(models.Model):
    logger_name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.ERROR, db_index=True)
    msg = models.TextField()
    trace = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    def __str__(self):
        return self.msg

    class Meta:
        ordering = ('-create_datetime',)



class DashboardLog(models.Model):
    user = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    traceback = models.TextField(null=True)
    meta_info = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
