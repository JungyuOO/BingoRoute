from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('send-email-verification/', views.send_email_verification, name='send_email_verification'),
    path('verify-email-code/', views.verify_email_code_view, name='verify_email_code'),
    path('session/', views.session_view, name='session'),
    path('find-id/', views.find_id_view, name='find_id'),
    path('password-reset/send-code/', views.password_reset_send_code, name='password_reset_send_code'),
    path('password-reset/verify-code/', views.password_reset_verify_code, name='password_reset_verify_code'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]
