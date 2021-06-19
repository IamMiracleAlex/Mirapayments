from django.urls import path

from users import views

urlpatterns = [
    path('list/', views.UserListView.as_view(), name='users'),
   
]
