from django.urls import path
from . import views

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/register/verify/", views.register_verify, name="register-verify"),
    path("auth/login/", views.login, name="login"),
    path("auth/me/", views.me, name="me"),
    path("auth/logout/", views.logout, name="logout"),
    # Password reset endpoints
    path("auth/password-reset/", views.password_reset_request, name="password-reset"),
    path("auth/password-reset/confirm/", views.password_reset_confirm, name="password-reset-confirm"),
]
