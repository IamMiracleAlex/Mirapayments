from django.contrib import admin

from knox import models


@admin.register(models.AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('test_token', 'user', 'created',)
    fields = ()
    raw_id_fields = ('user',)
