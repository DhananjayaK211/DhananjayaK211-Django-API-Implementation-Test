from django.contrib import admin
from .models import AuthToken, VerificationCode

@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created_at", "expires_at")
    search_fields = ("key", "user__username", "user__email")

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "created_at", "expires_at", "used")
    search_fields = ("email", "code")
