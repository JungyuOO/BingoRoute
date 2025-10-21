from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('send-email-verification/', views.send_email_verification, name='send_email_verification'),
    path('verify-email-code/', views.verify_email_code_view, name='verify_email_code'),
]
