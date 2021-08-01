from django.urls import path

from users import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('signup/', views.SignUpView.as_view()),
    path('me/', views.UserDetailUpdateView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('logoutall/', views.LogoutAllView.as_view()),
    path('verify-email/<str:uidb64>/<str:token>/', views.VerifyEmail.as_view()),
    path('send-verification-email/', views.SendVerificationEmail.as_view()),
]
