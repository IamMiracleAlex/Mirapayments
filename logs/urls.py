from django.urls import path

from logs.views import __gen_500_errors

urlpatterns = [
    path('__gen_500/', __gen_500_errors)
]