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
    path('password-reset-request/', views.ResetPasswordRequest.as_view()),
    path('reset-password-validate-token/', views.ResetPasswordValidateToken.as_view()),
    path('reset-password-confirm/', views.ResetPasswordConfirm.as_view()),
    path('invite/', views.UserInvitationView.as_view()),
    path('list/<str:account_number>/', views.ListAccountUsersView.as_view()),
    path('me/accounts/', views.ListUserAccountsView.as_view()),
    path('activate/', views.ActivateInvitedUser.as_view()),
]
