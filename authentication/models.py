import secrets
import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class AuthToken(models.Model):
    key = models.CharField(max_length=64, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="auth_tokens", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        if not self.expires_at:
            ttl = getattr(settings, "AUTH_TOKEN_TTL_SECONDS", 604800)
            self.expires_at = timezone.now() + timedelta(seconds=ttl)
        return super().save(*args, **kwargs)
    def is_valid(self):
        return self.expires_at > timezone.now()

class VerificationCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.used) and (self.expires_at > timezone.now())

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])
class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=64, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(32)
        if not self.expires_at:
            ttl = getattr(settings, "PASSWORD_RESET_TTL_SECONDS", 3600)  # default 1 hour
            self.expires_at = timezone.now() + timedelta(seconds=ttl)
        return super().save(*args, **kwargs)

    def is_valid(self):
        return (not self.used) and (self.expires_at > timezone.now())

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])

